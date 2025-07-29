import hashlib
import spglib
from scipy.spatial import KDTree, cKDTree
import copy 
import unittest

def _serialize_kdtree_node(node):
    r"""
    Recursively serialize a KDTree node into a compact, deterministic string.

    - **Leaf nodes** expose a set of point indices \(\{i_j\}\). We serialize as:
      .. math::
         L = \"L[i_1,i_2,\dots,i_m]\"
    - **Inner nodes** are defined by a split dimension \(d\) and split value \(s\),
      with left and right subtrees. We clamp \(s\) to 8 decimal places and serialize as:
      .. math::
         I = \"I{d}:{s}(...)(...)\"
      where the parentheses recursively contain the serialized children.

    :param node:
        A KDTree node, with attributes:
        - `.idx` (numpy array) for leaves
        - `.split_dim`, `.split`, `.less`, `.greater` for inner nodes
    :type node: KDTree.node
    :returns:
        A deterministic string encoding of the tree structure.
    :rtype: str
    """

    # Leaf?
    if hasattr(node, "idx"):
        # node.idx is a numpy array of indices
        idx_list = ",".join(map(str, node.idx.tolist()))
        return f"L[{idx_list}]"

    # Inner node._node
    # Always format the split coordinate to a fixed precision
    split_dim = node.split_dim
    split_val = f"{node.split:.2f}"
    left  = _serialize_kdtree_node(node.less)
    right = _serialize_kdtree_node(node.greater)
    return f"I{split_dim}:{split_val}({left})({right})"

def serialize_kdtree(tree):
    r"""
    Produce a deterministic serialization of either a KDTree or cKDTree.

    - If given a `cKDTree`, we first rebuild a pure-Python `KDTree`:
      .. code-block:: python
        data = tree.data
        tree = KDTree(data, leafsize=tree.leafsize or 10)

    - The resulting structure `tree.tree` is traversed via `_serialize_kdtree_node`.

    :param tree:
        A `KDTree` or `cKDTree` instance.
    :type tree: KDTree or cKDTree
    :returns:
        A string encoding the splitting hierarchy of the tree.
    :rtype: str
    """
    # If it's a cKDTree, rebuild as pure-Python KDTree
    if isinstance(tree, cKDTree):
        data     = tree.data
        leafsize = getattr(tree, "leafsize", None)
        # default leafsize=10 if not set
        tree = KDTree(data, leafsize=leafsize or 10)

    # Now walk the KDTree.tree
    return _serialize_kdtree_node(tree.tree)

class CanonicalHashMap:
    """
    A manager for storing canonical hashes of periodic crystal structures
    indexed by composition. This allows efficient duplicate detection
    among structures with the *same* composition.

    In practice, you create an instance of this class, and for each
    structure (with a known composition):
        1) Compute the canonical hash via spglib standardization
        2) Store or check if it has already been stored
    using the provided methods.

    Attributes
    ----------
    symprec : float
        Symmetry tolerance used by spglib for standardizing the cell.
    _hash_map : dict
        Internal dictionary: composition_key -> set of canonical hashes.

        Each 'composition_key' is derived from a dictionary of elements
        mapping to their integer amounts (e.g., {"Fe": 2, "Co": 1})
        turned into a string such as 'Co1-Fe2'.
    """

    def __init__(self, symprec: float = 1e-2, include_tree:bool=True, debug: bool = False):
        """
        Initialize the CompositionHashMap with a chosen symmetry precision.

        Parameters
        ----------
        symprec : float, optional (default=1e-2)
            Symmetry detection tolerance for spglib.standardize_cell(). 
            Larger values are more lenient; smaller values are stricter.
        """
        self.symprec = symprec
        self._hash_map = {}  # { 'comp_key': set([hash1, hash2, ...]) }
        self._include_tree = include_tree
        self.debug = debug
        
    @staticmethod
    def _composition_key(composition: dict) -> str:
        r"""
        Convert a composition dict into a unique, sorted key string.

        Given stoichiometry \(C = \{(e_k, n_k)\}\), sort by element symbol
        and join:
        .. math::
           \mathrm{key} = "-".join\bigl[e_1 n_1, e_2 n_2, \dots\bigr]

        :param composition:
            Mapping element symbol to integer count.
        :type composition: dict[str, int]
        :returns:
            A canonical string such as "Co1-Fe2".
        :rtype: str
        """
        # Sort by element symbol to ensure a consistent order
        items_sorted = sorted(composition.items())  
        # Build a string like "Co1-Fe2" for the composition
        return "-".join(f"{elem}{amt}" for elem, amt in items_sorted)
 
    def _canonical_hash(self, container) -> str:
        r"""
        Compute a symmetry‐invariant SHA256 fingerprint of a periodic structure.

        1. **Standardize cell** via spglib:
           .. math::
              (L',P',S') = \mathrm{spglib.standardize\_cell}(L,P,S)
           with tolerance \(\varepsilon=\texttt{self.symprec}\).

        2. **Quantize fractional coordinates** to grid \(\varepsilon\):
           .. math::
              \tilde{p}_{i\alpha} = \mathrm{round}(p_{i\alpha}/\varepsilon)\,\varepsilon.

        3. **Sort sites** by \((s_i,\tilde{p}_{i1},\tilde{p}_{i2},\tilde{p}_{i3})\) lexicographically.

        4. **Flatten lattice** and site list into a string fingerprint:
           .. code-block:: text
              fingerprint = ",".join("{L'_{ab}:.8f}" for all a,b)
                           + "|"
                           + ";".join(f"{s_i}:{x_i:.8f},{y_i:.8f},{z_i:.8f}")

        5. **Optionally** append a serialized KDTree of atomic positions.

        6. Return:  
           .. math::
              H = \mathrm{SHA256}(\mathrm{fingerprint}).

        :param container:
            Must provide:
            - `container.AtomPositionManager.latticeVectors` (3×3 array)
            - `atomPositions_fractional` (N×3 array)
            - `get_atomic_numbers()` → length‑N list
        :type container: Any
        :returns:
            Hexadecimal SHA256 hash string.
        :rtype: str
        """

        # Extract lattice and atomic data (must match your container's API)
        container.AtomPositionManager.wrap()
        lattice_matrix = container.AtomPositionManager.latticeVectors
        frac_coords    = container.AtomPositionManager.atomPositions_fractional
        species_list   = container.AtomPositionManager.get_atomic_numbers()

        # Prepare data for spglib
        cell = (lattice_matrix, frac_coords, species_list)
        #print(cell)
        # -- Option A: Niggli reduction --
        # spglib modifies the array in-place, so make a copy if needed
        # The function returns lattice, positions, and species in a single
        # updated 'cell' variable
        #spglib.niggli_reduce(cell, eps=self.symprec)

        # After Niggli reduction, we still have to be sure the fractional coords
        # are wrapped in [0,1), so let's do that:
        #lattice, positions, species = cell
        #positions = positions % 1.0  # wrap back to 0-1

        # Alternatively:
        # -- Option B: standardize_cell --
        try:
            lattice, positions, species = spglib.standardize_cell(
                 cell,
                 to_primitive=False,   # produce the primitive cell
                 no_idealize=False,   # "idealize" can unify nearly-identical cells
                 symprec=self.symprec,
                 # angle_tolerance=0.5, # if needed
             )
        except:
            lattice, positions, species = lattice_matrix, frac_coords, species_list

        # Build a stable, sorted representation
        data_list = []
        for s, coord in zip(species, positions):
            # Sort or round to some precision
            data_list.append((
                s, 
                round(coord[0] / self.symprec) * self.symprec, 
                round(coord[1] / self.symprec) * self.symprec,
                round(coord[2] / self.symprec) * self.symprec 
            ))
        # Sort by (species, x, y, z)
        data_list.sort(key=lambda x: (x[0], x[1], x[2], x[3]))

        # Flatten the lattice
        lat_str = ",".join(f"{val:.8f}" for row in lattice for val in row)
        # Flatten the sorted site data
        coords_str = ";".join(f"{site[0]}:{site[1]:.8f},{site[2]:.8f},{site[3]:.8f}" for site in data_list)

        E = container.AtomPositionManager.E if isinstance(container.AtomPositionManager.E, (float, int)) else 0.0
        E_str = f"{round(container.AtomPositionManager.E / self.symprec) * self.symprec:.8f}"

        # Final fingerprint
        fingerprint = lat_str + "|" + coords_str + "|" + E_str 

        if self._include_tree:
            try:
                # Reset any old tree so that building will actually occur
                container.AtomPositionManager.kdtree = None
                # Attempt to build (or copy) the new tree
                tree = copy.copy(container.AtomPositionManager.kdtree)

                # Attempt serialization
                tree_repr = serialize_kdtree(tree)

            except Exception as exc:
                # Log the failure and use a sentinel value in the fingerprint
                print( f"KD-tree generation failed: {exc!r}" )
                #logger.warning(f"KD-tree generation failed: {exc!r}")
                tree_repr = "ERROR"

            finally:
                # Always clear the manager’s kdtree so you don’t leave stale state
                container.AtomPositionManager.kdtree = None

            # Append either the real tree or the error‐marker
            fingerprint += f"|TREE:{tree_repr}"

        return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()

    def add_structure(self, container) -> bool:
        r"""
        Register a new structure hash under its composition key.

        Let:
        - \(\kappa = \mathrm{_composition\_key}(\mathrm{comp})\).
        - \(h = \mathrm{_canonical\_hash}(\mathrm{container})\).

        If \(h\) is already in \(M[\kappa]\), return False. Otherwise,
        add \(h\) to \(M[\kappa]\) and return True.

        :param container:
            Structure whose hash will be computed and stored.
        :type container: Any
        :returns:
            True if added (new), False if duplicate.
        :rtype: bool
        """
        # Build a canonical key for the composition
        comp_key = self._composition_key( container.AtomPositionManager.atomCountDict )
        # Compute the canonical hash
        hval = self._canonical_hash(container)

        # If no entry for this composition yet, create one
        if comp_key not in self._hash_map:
            self._hash_map[comp_key] = set()

        if not hasattr(container.AtomPositionManager, 'metadata'):
              container.AtomPositionManager.metadata = {}
        if not isinstance(container.AtomPositionManager.metadata, dict):
            container.AtomPositionManager.metadata = {}

        container.AtomPositionManager.metadata['hash'] = hval

        # Check if the hash is already known
        if hval in self._hash_map[comp_key]:
            # Duplicate for that composition
            return False
        else:
            # This is a new structure hash
            self._hash_map[comp_key].add(hval)
            return True

    def already_visited(self, container) -> bool:
        r"""
        Test whether this structure (by its canonical hash) is already stored.

        Returns True if the computed \(h\) lies in \(M[\kappa]\), without adding.

        :param container:
            Structure to test for prior registration.
        :type container: Any
        :returns:
            True if seen before under same composition.
        :rtype: bool
        """
        # Build the composition key
        comp_key = self._composition_key(container.AtomPositionManager.atomCountDict)
        # If composition not seen, it can't be visited
        if comp_key not in self._hash_map:
            return False

        # Compute hash
        hval = self._canonical_hash(container)
        # Return True if it exists in the set, else False
        return (hval in self._hash_map[comp_key])

    def get_num_structures_for_composition(self, composition: dict) -> int:
        """
        Retrieve how many *unique* structures have been registered under 'composition'.

        Parameters
        ----------
        composition : dict
            The composition to query, e.g. {"Fe":2, "Co":1}.

        Returns
        -------
        int
            The count of distinct structure hashes for that composition.
        """
        comp_key = self._composition_key(composition)
        if comp_key not in self._hash_map:
            return 0
        return len(self._hash_map[comp_key])

    def total_compositions(self) -> int:
        """
        Return how many distinct compositions are currently registered.

        Returns
        -------
        int
            The number of unique composition keys in this HashMap.
        """
        return len(self._hash_map)


class TestCanonicalHashMap(unittest.TestCase):

    def setUp(self):
        import numpy as np
        from sage_lib.partition.Partition import Partition
        from sage_lib.single_run.SingleRun import SingleRun
        import random

        self.symprec = 1e-2
        self.map = StructureHashMap(method="rdf", r_max=5.0, bin_width=0.02)

        # Base structure: simple cubic two atoms
        self.base = Partition()

        N = np.random.randint(5)+1
        self.lattice = np.eye(3)
        self.coords = np.random.rand( N,3 )
        self.species = random.choices(['A', 'B'], k=N)

        sr = SingleRun()
        sr.AtomPositionManager.configure(self.coords, self.species, self.lattice)
        self.base.add_container( sr )

    def test_random_permutation_invariance(self):
        """
        Permuting the order of atoms should not change the hash.
        """
        h0 = self.map._canonical_hash(self.base)

        for n in range(1):
            N = np.random.randint(5)+1
            self.lattice = np.eye(3)
            self.coords = np.random.rand( N,3 )
            self.species = random.choices(['A', 'B'], k=N)

            sr = SingleRun()
            sr.AtomPositionManager.configure(self.coords, self.species, self.lattice)

            h1 = self.map._canonical_hash(cont)
            self.assertEqual(h0, h1, "Hash should be invariant under atom order permutations.")

    def test_translation_invariance(self):
        """
        Translating all coordinates by a random vector (mod 1) should not affect the hash.
        """
        h0 = self.map._canonical_hash(self.base)

        StructureHashMap(method="rdf", r_max=5.0, bin_width=0.02)
        self.hash_map.add_structure( container )

        for _ in range(10):
            t = np.random.rand(3)
            coords_t = (np.array(self.coords) + t) % 1.0
            cont = make_fake_container(self.lattice, coords_t, self.species)
            cont.AtomPositionManager.wrap()


            h1 = self.map._canonical_hash(cont)
            self.assertEqual(h0, h1, "Hash should be invariant under translations.")

    def test_rotation_invariance(self):
        """
        Applying a random rotation to fractional coords should preserve the hash,
        after wrapping back into [0,1) and restandardization.
        """
        h0 = self.map._canonical_hash(self.base)
        for _ in range(10):
            # generate random rotation matrix via QR of random normal
            M = np.random.randn(3,3)
            Q, R = np.linalg.qr(M)
            # ensure proper rotation (determinant = +1)
            if np.linalg.det(Q) < 0:
                Q[:,0] *= -1
            coords_r = (np.dot(self.coords, Q.T)) % 1.0
            cont = make_fake_container(self.lattice, coords_r, self.species)
            cont.AtomPositionManager.wrap()
            h1 = self.map._canonical_hash(cont)
            self.assertEqual(h0, h1, "Hash should be invariant under rotations modulo periodicity.")

    def test_perturbation_within_tolerance(self):
        """
        Small random perturbations within symprec should not change the hash.
        """
        h0 = self.map._canonical_hash(self.base)
        for _ in range(10):
            delta = (np.random.rand(*np.array(self.coords).shape) - 0.5) * self.symprec * 0.9
            coords_p = np.array(self.coords) + delta
            cont = make_fake_container(self.lattice, coords_p, self.species)
            h1 = self.map._canonical_hash(cont)
            self.assertEqual(h0, h1, "Hash should be invariant under small perturbations within tolerance.")

if __name__ == '__main__':
    unittest.main()




