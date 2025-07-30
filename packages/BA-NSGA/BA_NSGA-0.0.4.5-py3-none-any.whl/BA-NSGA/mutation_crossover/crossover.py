import numpy as np
import copy

def align_and_crossover(parentA, parentB, crossover_func=None):
    """
    Align two parent structures (via translation, PCA rotation, and fine RMSD minimization),
    then perform a crossover to produce two children.

    Parameters
    ----------
    parentA, parentB : objects
        Parent structures, each with:
            - parent.AtomPositionManager.atomPositions: np.ndarray of shape (N, 3)
            - parent.AtomPositionManager.atomLabelsList: array-like of length N
            - .remove_atom(indices) : removes specified atom indices
            - .add_atom(atomLabels=..., atomPosition=...) : adds new atoms
    crossover_func : function, optional
        A function that takes (alignedA, alignedB) and returns (childA, childB).
        If None, defaults to a single-plane cut crossover.

    Returns
    -------
    childA, childB : objects
        New “child” structures obtained after alignment + crossover.
    """

    # 1) Copy the parents so we do not modify them directly
    A = copy.deepcopy(parentA)
    B = copy.deepcopy(parentB)

    # 2) Translate to center of mass and apply PCA rotation (for each structure independently)
    A = translate_to_center(A)
    B = translate_to_center(B)
    A = align_principal_axes(A)
    B = align_principal_axes(B)

    # 3) Fine alignment to minimize RMSD by pairing the smaller structure's atoms
    #    with nearest neighbors in the larger structure, then applying Kabsch.
    A, B = fine_align_by_minimizing_rmsd(A, B)

    # 4) Perform the actual crossover. If the user didn’t supply a crossover function,
    #    use a simple single-plane (single-cut) crossover as an example.
    if crossover_func is None:
        crossover_func = single_cut_crossover  # fallback default
    childA, childB = crossover_func(A, B)

    return childA, childB


# ------------------------------------------------------------------
# Step A: Translate a structure so that its center (mean position) is at the origin.
def translate_to_center(container):
    """
    Translates the structure so its centroid (mean of positions) is at the origin (0, 0, 0).
    """
    positions = container.AtomPositionManager.atomPositions
    centroid = np.mean(positions, axis=0)
    container.AtomPositionManager.atomPositions = positions - centroid
    return container

# ------------------------------------------------------------------
# Step B: Align a structure's principal axes to the Cartesian axes via PCA.
def align_principal_axes(container):
    """
    Rotates the structure so that its principal axes (from PCA) align with the
    global x, y, z axes.

    We compute the covariance of atom positions, perform an eigen-decomposition,
    and then rotate accordingly.
    """
    positions = container.AtomPositionManager.atomPositions

    # Compute covariance
    cov = np.cov(positions, rowvar=False)  # shape (3,3)

    # Eigen-decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort eigenvectors by descending eigenvalue
    sort_idx = np.argsort(eigenvalues)[::-1]
    principal_axes = eigenvectors[:, sort_idx]  # shape (3,3)

    # Rotate positions
    positions_aligned = positions.dot(principal_axes)
    container.AtomPositionManager.atomPositions = positions_aligned
    return container


# ------------------------------------------------------------------
# Step C: Fine alignment to minimize RMSD between the “smaller” structure's atoms
# and a matched subset in the “larger” structure.
def fine_align_by_minimizing_rmsd(containerA, containerB):
    """
    Finds the smaller set of atoms among containerA and containerB, pairs each atom
    in the smaller set with its nearest neighbor in the larger set, and then uses
    the Kabsch algorithm to minimize RMSD. We apply the resulting transformation
    to the smaller structure.

    Returns
    -------
    newA, newB : objects
        The updated containers after alignment.
        (Usually we transform only the smaller structure.)
    """
    A = copy.deepcopy(containerA)
    B = copy.deepcopy(containerB)
    posA = A.AtomPositionManager.atomPositions
    posB = B.AtomPositionManager.atomPositions

    # Determine which container is smaller
    nA = posA.shape[0]
    nB = posB.shape[0]

    if nA <= nB:
        # A is smaller or equal in size => align A onto B
        matchedA, matchedB = pair_atoms_nearest(posA, posB)
        R, t = kabsch_transform(matchedA, matchedB)
        # Apply to all positions in A
        posA_new = (posA - matchedA.mean(axis=0)).dot(R) + matchedB.mean(axis=0)
        A.AtomPositionManager.atomPositions = posA_new
        return A, B
    else:
        # B is smaller => align B onto A
        matchedB, matchedA = pair_atoms_nearest(posB, posA)
        R, t = kabsch_transform(matchedB, matchedA)
        # Apply to all positions in B
        posB_new = (posB - matchedB.mean(axis=0)).dot(R) + matchedA.mean(axis=0)
        B.AtomPositionManager.atomPositions = posB_new
        return A, B


def pair_atoms_nearest(smallPos, largePos):
    """
    For each atom in 'smallPos', find the nearest neighbor in 'largePos' and pair them up.

    NOTE: This is a naive approach: multiple atoms in 'smallPos' may end up paired
    to the same atom in 'largePos' if that one is nearest to multiple points.

    Returns
    -------
    matched_small, matched_large : np.ndarray
        Arrays of equal length with the matched coordinates.
    """
    matched_small = []
    matched_large = []

    for vec in smallPos:
        # Find the index j in largePos that is closest to vec
        diffs = largePos - vec
        dists = np.sum(diffs**2, axis=1)
        jmin = np.argmin(dists)
        matched_small.append(vec)
        matched_large.append(largePos[jmin])

    return np.array(matched_small), np.array(matched_large)


def kabsch_transform(X, Y):
    """
    Kabsch algorithm: given two sets of points X, Y (same shape (N,3)) that
    are paired, compute the rotation matrix R that best aligns X to Y in a
    least-squares sense. The translation can be handled outside by centering
    the points.

    Returns
    -------
    R, t : np.ndarray
        R is the 3x3 rotation matrix
        t is the translation vector (not strictly needed if we handle centering externally)

    Usage example for alignment:
        Xc = X.mean(axis=0)
        Yc = Y.mean(axis=0)
        Xp = X - Xc
        Yp = Y - Yc
        R, t = kabsch_transform(Xp, Yp)
        Xp_aligned = Xp.dot(R)
        # Then final positions = Xp_aligned + Yc
    """
    # 1) Center is typically subtracted outside this function,
    #    but let's do the standard approach with the data as-is.
    Xc = X.mean(axis=0)
    Yc = Y.mean(axis=0)
    Xp = X - Xc
    Yp = Y - Yc

    # 2) Covariance matrix
    #    H = Xp^T * Yp
    H = Xp.T.dot(Yp)

    # 3) SVD of H
    U, S, Vt = np.linalg.svd(H)

    # 4) Compute rotation
    #    Potential reflection fix if det < 0
    R_ = Vt.T.dot(U.T)
    if np.linalg.det(R_) < 0:
        # Flip the sign of the last row of Vt
        Vt[-1, :] *= -1
        R_ = Vt.T.dot(U.T)

    # 5) Translation
    t_ = Yc - R_.dot(Xc)
    return R_, t_


# ------------------------------------------------------------------
#  ------------          CrossOver functions              ---------
# ------------------------------------------------------------------
def crossover_planes_exchange():

    def func(containers_A, containers_B):
        """
        Perform crossover between pairs of containers by exchanging layers of atoms.

        Parameters
        ----------
        containers_A, containers_B 

        Returns
        -------
        list
            The modified list of containers after performing crossover.
        """
        
        # Identify planes in container i
        indices_A, plane_ids_A = identify_planes(
            containers_A.AtomPositionManager.atomLabelsList,
            containers_A.AtomPositionManager.atomPositions
        )

        # Identify planes in container j
        indices_B, plane_ids_B = identify_planes(
            containers_B.AtomPositionManager.atomLabelsList,
            containers_B.AtomPositionManager.atomPositions
        )

        max_planes_A = np.max(plane_ids_A) + 1
        max_planes_B = np.max(plane_ids_B) + 1
        max_planes = max(max_planes_A, max_planes_B)

        # Sort planes by mean y-coordinate (example approach)
        layer_order_index_A = []
        layer_order_index_B = []
        for n in range(max_planes_A):
            coords_plane = containers_A.AtomPositionManager.atomPositions[indices_A[plane_ids_A == n]]
            layer_order_index_A.append(np.mean(coords_plane[:, 1]) if len(coords_plane) > 0 else float('inf'))

        for n in range(max_planes_B):
            coords_plane = containers_B.AtomPositionManager.atomPositions[indices_B[plane_ids_B == n]]
            layer_order_index_B.append(np.mean(coords_plane[:, 1]) if len(coords_plane) > 0 else float('inf'))

        as_A = np.argsort(layer_order_index_A)
        as_B = np.argsort(layer_order_index_B)

        exchanged_layers = 0
        remove_index_store_A = []
        remove_index_store_B = []
        atom_position_store_A = np.empty((0, 3))
        atom_position_store_B = np.empty((0, 3))
        atom_label_store_A = []
        atom_label_store_B = []

        for n in range(max_planes):
            if n < max_planes_A and n < max_planes_B:
                # Randomly decide whether to swap plane n
                if np.random.randint(2) == 1:
                    selA = indices_A[plane_ids_A == as_A[n]]
                    selB = indices_B[plane_ids_B == as_B[n]]

                    coordsA = containers_A.AtomPositionManager.atomPositions[selA]
                    coordsB = containers_B.AtomPositionManager.atomPositions[selB]
                    labelsA = containers_A.AtomPositionManager.atomLabelsList[selA]
                    labelsB = containers_B.AtomPositionManager.atomLabelsList[selB]

                    remove_index_store_A = np.concatenate((remove_index_store_A, selA))
                    remove_index_store_B = np.concatenate((remove_index_store_B, selB))

                    atom_position_store_A = np.concatenate((atom_position_store_A, coordsB), axis=0)
                    atom_position_store_B = np.concatenate((atom_position_store_B, coordsA), axis=0)

                    atom_label_store_A = np.concatenate((atom_label_store_A, labelsB))
                    atom_label_store_B = np.concatenate((atom_label_store_B, labelsA))
                    exchanged_layers += 1

        # Ensure at least one layer is exchanged
        if exchanged_layers == 0 and max_planes_A > 0 and max_planes_B > 0:
            n = np.random.randint(min(max_planes_A, max_planes_B))
            selA = indices_A[plane_ids_A == as_A[n]]
            selB = indices_B[plane_ids_B == as_B[n]]
            coordsA = containers_A.AtomPositionManager.atomPositions[selA]
            coordsB = containers_B.AtomPositionManager.atomPositions[selB]
            labelsA = containers_A.AtomPositionManager.atomLabelsList[selA]
            labelsB = containers_B.AtomPositionManager.atomLabelsList[selB]

            remove_index_store_A = np.concatenate((remove_index_store_A, selA))
            remove_index_store_B = np.concatenate((remove_index_store_B, selB))

            atom_position_store_A = np.concatenate((atom_position_store_A, coordsB), axis=0)
            atom_position_store_B = np.concatenate((atom_position_store_B, coordsA), axis=0)

            atom_label_store_A = np.concatenate((atom_label_store_A, labelsB))
            atom_label_store_B = np.concatenate((atom_label_store_B, labelsA))

        # Remove old atoms and add the swapped ones
        containers_A.AtomPositionManager.remove_atom(remove_index_store_A)
        containers_B.AtomPositionManager.remove_atom(remove_index_store_B)

        containers_A.AtomPositionManager.add_atom(atomLabels=atom_label_store_A,
                                                   atomPosition=atom_position_store_A)
        containers_B.AtomPositionManager.add_atom(atomLabels=atom_label_store_B,
                                                   atomPosition=atom_position_store_B)

        return containers_A, containers_B

    return func

# Example: Single-plane (single-cut) crossover
def crossover_single_cut(containerA, containerB):
    """
    Performs a single-plane cut crossover along a random axis (x, y, or z).
    Child A inherits the “below cut” portion from A and the “above cut”
    portion from B; child B does the reverse.
    """
    import copy
    # Copy the parents
    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # 1) Choose random axis
    axis = np.random.choice([0, 1, 2])

    # 2) Determine global min/max along this axis (so the cut is guaranteed within range)
    min_coord = min(posA[:, axis].min(), posB[:, axis].min())
    max_coord = max(posA[:, axis].max(), posB[:, axis].max())

    # 3) Pick a random cut position
    cut_position = np.random.uniform(min_coord, max_coord)

    # 4) Identify “below” and “above” for each parent
    maskA_below = posA[:, axis] <= cut_position
    maskB_below = posB[:, axis] <= cut_position

    # 5) Remove old atoms in children
    childA.AtomPositionManager.remove_atom(np.arange(posA.shape[0]))
    childB.AtomPositionManager.remove_atom(np.arange(posB.shape[0]))

    # 6) Reconstruct childA
    # A below + B above
    new_positions_A = np.concatenate([posA[maskA_below], posB[~maskB_below]])
    new_labels_A = np.concatenate([labelsA[maskA_below], labelsB[~maskB_below]])
    childA.AtomPositionManager.add_atom(atomLabels=new_labels_A, atomPosition=new_positions_A)

    # 7) Reconstruct childB
    # B below + A above
    new_positions_B = np.concatenate([posB[maskB_below], posA[~maskA_below]])
    new_labels_B = np.concatenate([labelsB[maskB_below], labelsA[~maskA_below]])
    childB.AtomPositionManager.add_atom(atomLabels=new_labels_B, atomPosition=new_positions_B)

    return childA, childB

def crossover_two_cut(containerA, containerB):
    """
    Performs a two-cut crossover along a random axis:
    1) Randomly pick two planes (cut1 < cut2) along the chosen axis.
    2) Child A = Parent A's outer regions + Parent B's middle region
    3) Child B = Parent B's outer regions + Parent A's middle region
    """
    import copy
    import numpy as np

    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # Pick an axis
    axis = np.random.choice([0, 1, 2])

    # Choose two cut positions along that axis
    min_coord = min(posA[:, axis].min(), posB[:, axis].min())
    max_coord = max(posA[:, axis].max(), posB[:, axis].max())
    cut1, cut2 = np.sort(np.random.uniform(min_coord, max_coord, size=2))

    # Identify below, middle, above for parent A
    belowA = posA[:, axis] < cut1
    middleA = (posA[:, axis] >= cut1) & (posA[:, axis] <= cut2)
    aboveA = posA[:, axis] > cut2

    # Identify below, middle, above for parent B
    belowB = posB[:, axis] < cut1
    middleB = (posB[:, axis] >= cut1) & (posB[:, axis] <= cut2)
    aboveB = posB[:, axis] > cut2

    # Remove old atoms in children
    childA.AtomPositionManager.remove_atom(np.arange(posA.shape[0]))
    childB.AtomPositionManager.remove_atom(np.arange(posB.shape[0]))

    # childA = A(below + above) + B(middle)
    newA_positions = np.concatenate([posA[belowA], posA[aboveA], posB[middleB]])
    newA_labels = np.concatenate([labelsA[belowA], labelsA[aboveA], labelsB[middleB]])
    childA.AtomPositionManager.add_atom(atomLabels=newA_labels, atomPosition=newA_positions)

    # childB = B(below + above) + A(middle)
    newB_positions = np.concatenate([posB[belowB], posB[aboveB], posA[middleA]])
    newB_labels = np.concatenate([labelsB[belowB], labelsB[aboveB], labelsA[middleA]])
    childB.AtomPositionManager.add_atom(atomLabels=newB_labels, atomPosition=newB_positions)

    return childA, childB


def crossover_spherical(containerA, containerB):
    """
    Spherical region crossover:
    - Pick random center and radius.
    - Child A gets the inside-sphere atoms from A and outside-sphere atoms from B.
    - Child B gets inside-sphere from B and outside-sphere from A.
    """
    import copy
    import numpy as np

    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # Random sphere center from extremes of both parents
    all_pos = np.vstack([posA, posB])
    mins = all_pos.min(axis=0)
    maxs = all_pos.max(axis=0)
    center = np.array([
        np.random.uniform(mins[0], maxs[0]),
        np.random.uniform(mins[1], maxs[1]),
        np.random.uniform(mins[2], maxs[2])
    ])

    # Random radius in a range (e.g., 1/4 of bounding box diagonal)
    diag = np.linalg.norm(maxs - mins)
    radius = np.random.uniform(0.0, 0.5 * diag)

    # Distances of each atom from the center
    distA = np.linalg.norm(posA - center, axis=1)
    distB = np.linalg.norm(posB - center, axis=1)

    insideA = distA < radius
    insideB = distB < radius

    # Remove old
    childA.AtomPositionManager.remove_atom(np.arange(posA.shape[0]))
    childB.AtomPositionManager.remove_atom(np.arange(posB.shape[0]))

    # ChildA = A-inside + B-outside
    newA_positions = np.concatenate([posA[insideA], posB[~insideB]])
    newA_labels = np.concatenate([labelsA[insideA], labelsB[~insideB]])
    childA.AtomPositionManager.add_atom(atomLabels=newA_labels, atomPosition=newA_positions)

    # ChildB = B-inside + A-outside
    newB_positions = np.concatenate([posB[insideB], posA[~insideA]])
    newB_labels = np.concatenate([labelsB[insideB], labelsA[~insideA]])
    childB.AtomPositionManager.add_atom(atomLabels=newB_labels, atomPosition=newB_positions)

    return childA, childB


def crossover_uniform_atom_level(containerA, containerB):
    """
    For each atom index i, randomly pick whether child A gets A[i] or B[i].
    Child B gets the other parent's corresponding atom.

    NOTE: This simple version assumes both parents have the same number of atoms 
    and that index i refers to “corresponding” positions. If the two parents 
    differ in size or in how atoms are indexed, you must define a matching 
    scheme (e.g., nearest neighbor matching).
    """
    import copy
    import numpy as np

    # If parents differ in number of atoms, adapt accordingly
    nA = containerA.AtomPositionManager.atomPositions.shape[0]
    nB = containerB.AtomPositionManager.atomPositions.shape[0]
    if nA != nB:
        raise ValueError("Parents must have the same number of atoms for uniform crossover!")

    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # Remove existing atoms
    childA.AtomPositionManager.remove_atom(np.arange(nA))
    childB.AtomPositionManager.remove_atom(np.arange(nB))

    # Build lists for the children
    new_positions_A = []
    new_labels_A = []
    new_positions_B = []
    new_labels_B = []

    for i in range(nA):
        if np.random.rand() < 0.5:
            # childA inherits A[i], childB inherits B[i]
            new_positions_A.append(posA[i])
            new_labels_A.append(labelsA[i])
            new_positions_B.append(posB[i])
            new_labels_B.append(labelsB[i])
        else:
            # childA inherits B[i], childB inherits A[i]
            new_positions_A.append(posB[i])
            new_labels_A.append(labelsB[i])
            new_positions_B.append(posA[i])
            new_labels_B.append(labelsA[i])

    # Convert to arrays
    new_positions_A = np.array(new_positions_A)
    new_labels_A = np.array(new_labels_A)
    new_positions_B = np.array(new_positions_B)
    new_labels_B = np.array(new_labels_B)

    childA.AtomPositionManager.add_atom(atomLabels=new_labels_A, atomPosition=new_positions_A)
    childB.AtomPositionManager.add_atom(atomLabels=new_labels_B, atomPosition=new_positions_B)

    return childA, childB


def crossover_species_proportion(containerA, containerB, proportions=None):
    """
    For each species, pick a fraction p in [0,1]. Then childA obtains ~p% of that 
    species from parentA, and ~ (1-p)% from parentB. ChildB gets the complementary set.
    
    The 'proportions' dict can look like:
        { 'Ni': 0.6, 'Fe': 0.5, 'V': 0.2, ... }
    If a species is not listed in 'proportions', we pick p=0.5 by default.
    
    NOTE: A simple approach: if parentA has X_i atoms of species i, we select
    floor(p * X_i) from parentA for childA, the rest from parentB, etc.
    You can pick them at random or keep e.g. the first in an index. 
    Here we do a random selection approach for the “p% of parentA’s atoms”.
    """
    import copy
    import numpy as np

    if proportions is None:
        proportions = {}  # default: 0.5 each species

    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # Combine all species from both parents to ensure we handle everything
    all_species = set(labelsA).union(set(labelsB))

    # We will collect positions/labels for each child in lists, then remove+add
    new_posA = []
    new_labA = []
    new_posB = []
    new_labB = []

    # Remove old
    childA.AtomPositionManager.remove_atom(np.arange(len(labelsA)))
    childB.AtomPositionManager.remove_atom(np.arange(len(labelsB)))

    for sp in all_species:
        p = proportions.get(sp, 0.5)

        # Indices of species sp in parent A
        idxA = np.where(labelsA == sp)[0]
        # Indices of species sp in parent B
        idxB = np.where(labelsB == sp)[0]

        # Shuffle them so we pick random subsets
        np.random.shuffle(idxA)
        np.random.shuffle(idxB)

        # Number from parent A to child A
        nA_to_A = int(np.floor(p * len(idxA)))
        # Number from parent B to child A
        # We want to keep childA's total count for sp = (some fraction) * (lenA + lenB)
        # but a simpler approach is: childA takes nA_to_A from A, plus some fraction from B.
        total_sp = len(idxA) + len(idxB)
        # overall fraction for sp: 
        total_A_need = int(np.floor(p * total_sp))
        # so from B, we want total_A_need - nA_to_A 
        nB_to_A = max(0, total_A_need - nA_to_A)

        # The rest go to childB
        # from A => len(idxA) - nA_to_A
        # from B => len(idxB) - nB_to_A

        # Take these atoms from A to childA
        a_selA = idxA[:nA_to_A]
        # Take these atoms from B to childA
        b_selA = idxB[:nB_to_A]

        # The leftover
        a_selB = idxA[nA_to_A:]
        b_selB = idxB[nB_to_A:]

        # Add to new arrays
        new_posA.append(posA[a_selA])
        new_labA.append(labelsA[a_selA])
        new_posA.append(posB[b_selA])
        new_labA.append(labelsB[b_selA])

        new_posB.append(posA[a_selB])
        new_labB.append(labelsA[a_selB])
        new_posB.append(posB[b_selB])
        new_labB.append(labelsB[b_selB])

    # Concatenate
    new_posA = np.concatenate(new_posA) if len(new_posA) else np.zeros((0,3))
    new_labA = np.concatenate(new_labA) if len(new_labA) else np.array([])
    new_posB = np.concatenate(new_posB) if len(new_posB) else np.zeros((0,3))
    new_labB = np.concatenate(new_labB) if len(new_labB) else np.array([])

    # Now add them
    childA.AtomPositionManager.add_atom(atomLabels=new_labA, atomPosition=new_posA)
    childB.AtomPositionManager.add_atom(atomLabels=new_labB, atomPosition=new_posB)

    return childA, childB


