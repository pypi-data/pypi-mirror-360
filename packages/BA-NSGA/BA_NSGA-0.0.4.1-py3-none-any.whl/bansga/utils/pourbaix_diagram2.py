from __future__ import annotations
"""
Generic, data-driven Pourbaix/phase-diagram engine (chemistry agnostic).

▸ **Species**   – immutable container for name, charge, composition, concentration.
▸ **Reaction**  – sparse stoichiometry + reference ΔG°.
▸ **PhaseDiagram** – numerics (ridge regression), grid cache, quick Pourbaix map.
▸ **distance_to_hull()** – vertical distance of arbitrary structures to the lower convex
  hull (composition–energy space).
▸ **plot_energy_planes()** – render μᵢ(pH,U) surfaces in a single 3-D scene.

No element-specific logic is hard-wired; extend to any system by registering species and
reactions at runtime.
"""

# ============================================================================
# Imports
# ============================================================================
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Iterable, Optional
import re
from collections import defaultdict

import numpy as np
from numpy.typing import ArrayLike
from sklearn.linear_model import Ridge
from scipy.spatial import ConvexHull

import time
from joblib import Parallel, delayed

import numpy as np

# ============================================================================
# LA functions
# ============================================================================
def plane_from_points(p1, p2, p3):
    """
    Given three 3D points, return (n, d) for the plane
      n·x + d = 0
    with n normalized to unit length.
    """
    p1, p2, p3 = p1.astype(float), p2.astype(float), p3.astype(float)
    v1 = p2 - p1
    v2 = p3 - p1
    n = np.cross(v1, v2)
    n /= np.linalg.norm(n)
    d = -n.dot(p1)
    return n, d

def compute_min_distances(planes, x_range, y_range, nx=100, ny=100):
    """
    Calcula la distancia mínima vertical de cada plano al plano de referencia
    (el de menor z) muestreando una malla de nx×ny puntos en el rectángulo.

    Parámetros:
      planes: array (N,3,3) con puntos de cada plano
      x_range: (x_min, x_max)
      y_range: (y_min, y_max)
      nx, ny: número de muestras en x e y

    Devuelve:
      ref_idx: índice del plano de referencia
      distances: array (N,) con la mínima separación vertical ≥ 0
    """
    planes = planes.astype(float)
    N = planes.shape[0]

    # 1) Ajuste de cada plano
    normals = np.zeros((N,3))
    ds      = np.zeros(N)
    for i in range(N):
        normals[i], ds[i] = plane_from_points(*planes[i])

    # 2) Muestreo de la malla en x,y
    x_min, x_max = x_range
    y_min, y_max = y_range
    xs = np.linspace(x_min, x_max, nx)
    ys = np.linspace(y_min, y_max, ny)
    X, Y = np.meshgrid(xs, ys)

    # 3) Evaluar z para cada plano en toda la malla
    Zs = np.zeros((N, ny, nx))
    for i in range(N):
        n, d = normals[i], ds[i]
        Zs[i] = -(n[0]*X + n[1]*Y + d) / n[2]

    # 4) Calcular la envolvente inferior (mínimo local en cada punto)
    Z_env = Zs.min(axis=0)  # shape (ny, nx)

    # 5) Para cada plano, diferencias a la envolvente en toda la malla
    distances = np.zeros(N)
    for i in range(N):
        dz = Zs[i] - Z_env
        distances[i] = max(0.0, dz.min())

    return distances

def min_vertical_distances(planes, x_range, y_range, nx=100, ny=100):
    """
    Compute the minimum vertical distance ≥0 from each plane in `planes` to
    the lower envelope over a sampled (x,y) grid.

    Parameters
    ----------
    planes : ndarray, shape (N, 3, 3)
        Three (x,y,z) points defining each of N planes.
    x_range : tuple (x_min, x_max)
    y_range : tuple (y_min, y_max)
    nx, ny : int, optional
        Number of sampling points in x and y (defaults to 100 each).

    Returns
    -------
    distances : ndarray, shape (N,)
        For each plane i the minimal vertical separation to the envelope.
    """
    # Ensure float dtype
    P = np.asarray(planes, dtype=float)
    N = P.shape[0]

    # 1) Compute plane normals and offsets in bulk
    #   v1, v2 are edge vectors of each triangle
    v1 = P[:,1,:] - P[:,0,:]     # shape (N,3)
    v2 = P[:,2,:] - P[:,0,:]     # shape (N,3)
    #   raw normals by cross-product
    normals = np.cross(v1, v2)   # shape (N,3)
    #   normalize to unit length
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals /= lengths
    #   plane offset d: n·x + d = 0  ⇒  d = −n·p1
    ds = -np.einsum('ij,ij->i', normals, P[:,0,:])  # shape (N,)

    # 2) Sample the (x,y) grid
    xs = np.linspace(x_range[0], x_range[1], nx)
    ys = np.linspace(y_range[0], y_range[1], ny)
    X, Y = np.meshgrid(xs, ys, indexing='xy')      # both shape (ny,nx)

    # 3) Compute Z for every plane at every (x,y) via broadcasting
    #    Z[i,:,:] = −(n_i0*X + n_i1*Y + d_i)/n_i2
    a = normals[:, 0][:, None, None]  # shape (N,1,1)
    b = normals[:, 1][:, None, None]
    c = normals[:, 2][:, None, None]
    d = ds[:,            None, None]
    Zs = -(a*X + b*Y + d) / c         # shape (N,ny,nx)

    # 4) Determine the lower envelope over all planes
    Z_env = Zs.min(axis=0)            # shape (ny,nx)

    # 5) Compute per-plane vertical separations and pick the minimum
    dz = Zs - Z_env[None, :, :]       # shape (N,ny,nx)
    min_dz = dz.min(axis=(1,2))       # shape (N,)

    # 6) Enforce non-negativity
    return np.maximum(min_dz, 0.0)
# ============================================================================
# Lightweight Hill-notation parser (supports nested parentheses & trailing charge)
# ============================================================================
_element_pat = re.compile(r"([A-Z][a-z]?)(\d*)")
_charge_pat = re.compile(r"([0-9]*[+-])$")


def _parse_species(txt: str) -> Tuple[int, Dict[str, int]]:
    """Return *(charge, composition_dict)* extracted from *txt*."""
    txt = txt.strip()
    m = _charge_pat.search(txt)
    if m:
        charge_tok = m.group(1)
        body = txt[: m.start()].strip()
    else:
        charge_tok = "0"
        body = txt

    sign = +1 if "+" in charge_tok else -1 if "-" in charge_tok else 0
    mag = int(charge_tok.rstrip("+-") or "1") if sign else 0
    charge = sign * mag

    def _block(block: str) -> Dict[str, int]:
        out: Dict[str, int] = defaultdict(int)
        for elem, digits in _element_pat.findall(block):
            out[elem] += int(digits) if digits else 1
        return out

    def _expand(formula: str) -> Dict[str, int]:
        if "(" not in formula:
            return _block(formula)
        res: Dict[str, int] = defaultdict(int)
        patt = re.compile(r"\(([^)]*)\)(\d*)")
        pos = 0
        while True:
            m = patt.search(formula, pos)
            if not m:
                break
            for k, v in _block(formula[pos:m.start()]).items():
                res[k] += v
            inner, mult_txt = m.groups()
            mult = int(mult_txt) if mult_txt else 1
            for k, v in _expand(inner).items():
                res[k] += v * mult
            pos = m.end()
        for k, v in _block(formula[pos:]).items():
            res[k] += v
        return res

    return charge, dict(sorted(_expand(body).items()))

# Alias for internal parser
parse_species = _parse_species

# ============================================================================
# Domain objects: Species & Reaction
# ============================================================================

dataclass_kwargs = dict(frozen=False, slots=True)


@dataclass(**dataclass_kwargs)
class Species:
    """Immutable container for a chemical species."""

    name: str
    charge: Optional[int] = None
    concentration: float = 1.0
    composition: Optional[Dict[str, int]] = None
    energy: Optional[float] = None

    _formal_charge: int = field(init=False, repr=False)
    _composition: Dict[str, int] = field(init=False, repr=False)
    hull_min_distance: Optional[float] = None
    G: float = None

    def __post_init__(self):
        c, comp = _parse_species(self.name)
        object.__setattr__(self, "_formal_charge", c if self.charge is None else self.charge)
        object.__setattr__(self, "_composition", comp if self.composition is None else self.composition)

    @property
    def formal_charge(self) -> int:
        return self._formal_charge

    @property
    def elem(self) -> Dict[str, int]:
        return self._composition

    def __getitem__(self, element: str) -> int:
        return self._composition.get(element, 0)


@dataclass(slots=True)
class Reaction:
    """User-friendly Reaction: reactants + products + ΔG° (eV)."""

    reactants: Dict[str, float]
    products: Dict[str, float]
    delta_g0: float
    stoichiometry: Dict[str, float] = field(init=False, repr=False)

    def __post_init__(self):
        st: Dict[str, float] = defaultdict(float)
        for sp, coeff in self.reactants.items(): st[sp] += coeff
        for sp, coeff in self.products.items(): st[sp] -= coeff
        object.__setattr__(self, 'stoichiometry', dict(st))

    def vector(self, index: Dict[str, int], n_sp: int) -> np.ndarray:
        v = np.zeros(n_sp)
        for sp, coeff in self.stoichiometry.items():
            if sp not in index:
                raise KeyError(f"Species '{sp}' not registered.")
            v[index[sp]] = coeff
        return v

# ============================================================================
# Phase-diagram engine
# ============================================================================

class PhaseDiagram:
    """Build μᵢ(pH,U) grid and visualisations."""

    def __init__(
        self,
        kb=8.617333262e-5,
        T=298.15,
        pH_range=(0.0, 14.0, 100),
        U_range=(-2.0, 2.0, 200),
        ridge_alpha=1e-8,
    ):
        self.kb, self.T = kb, T
        self.kbT = kb * T
        self.pH_min, self.pH_max, self.n_pH = pH_range
        self.U_min, self.U_max, self.n_U = U_range
        self._species: Dict[str, Species] = {}
        self._reactions: List[Reaction] = []
        self._solver = Ridge(alpha=ridge_alpha, fit_intercept=False)
        self._mu: Optional[np.ndarray] = None
        self._K: Optional[np.ndarray] = None

        self._candidate_species: Dict[str, Species] = {}
        self._name_counts: defaultdict[str, int] = defaultdict(int)

        self.elements: set[str] = set()

    def specie_by_idx(self, idx):
        idx = int(idx)
        species_list = [spc_key for spc_key, spc_item in self._species.items()]
        return species_list[idx]

    def add_species(self, sp: Species) -> None:
        if sp.name in self._species:
            raise ValueError(f"Species '{sp.name}' already registered.")

        self._species[sp.name] = sp
        self.elements.update(sp.elem.keys())

    def add_candidate_species(self, sp: Species) -> None:
        base = sp.name
        count = self._name_counts[base]
        unique_name = f"{base}_{count}" if count else base
        self._name_counts[base] += 1
        sp.name = unique_name

        self._candidate_species[unique_name] = sp
        self.elements.update(sp.elem.keys())

    def add_reaction(self, rxn: Reaction) -> None:
        for sp in rxn.stoichiometry:
            if sp not in self._species:
                raise KeyError(f"Unknown species '{sp}'.")
        self._reactions.append(rxn)

    def build(self, *, parallel=True) -> None:
        if not self._species or not self._reactions:
            raise RuntimeError("Register species & reactions before build().")
        sp_idx = {n:i for i,n in enumerate(self._species)}
        n_sp = len(sp_idx)
        R = np.vstack([rxn.vector(sp_idx,n_sp) for rxn in self._reactions])
        dG0 = np.array([rxn.delta_g0 for rxn in self._reactions])
        conc0 = np.array([sp.concentration for sp in self._species.values()])
        self._mu = np.zeros((self.n_U,self.n_pH,n_sp))
        self._K  = np.zeros((self.n_U,self.n_pH,len(self._reactions)))
        pH_vals = np.linspace(self.pH_min,self.pH_max,self.n_pH)
        U_vals  = np.linspace(self.U_min,self.U_max,self.n_U)

        def _solve(idx_flat):
            iU, ipH = divmod(idx_flat,self.n_pH)
            pH, U = pH_vals[ipH], U_vals[iU]
            dG = dG0.copy(); conc = conc0.copy()
            if "H+" in sp_idx: conc[sp_idx["H+"]] = 10**(-pH)
            dG += R @ (self.kbT * np.log(conc))
            if "e-" in sp_idx:
                pot = np.zeros(n_sp); pot[sp_idx["e-"]] = -U
                dG += R @ pot
            self._solver.fit(R,dG)
            mu = self._solver.coef_.astype(float)
            return idx_flat, mu, R @ mu

        from joblib import Parallel, delayed
        out = Parallel(n_jobs=-1 if parallel else 1)(delayed(_solve)(i) for i in range(self.n_U*self.n_pH))
        for idx_flat, mu_vec, K_vec in out:
            iU, ipH = divmod(idx_flat,self.n_pH)
            self._mu[iU,ipH,:] = mu_vec
            self._K[iU,ipH,:]  = K_vec

        # expose everything Mosaic_Stacking expects
        self.mu_pH_U = self._mu.transpose(1, 0, 2)
        self.species  = list(self._species)
        self.states   = { name: (i,) for i, name in enumerate(self.species) }
        self.regularization_strength = self._solver.alpha

    @property
    def mu(self) -> np.ndarray:
        if self._mu is None: raise RuntimeError("Call build() first.")
        return self._mu

    @property
    def K(self) -> np.ndarray:
        if self._K is None: raise RuntimeError("Call build() first.")
        return self._K

    def pourbaix_map(self, species_names: Iterable[str], *, ax=None, cmap="tab20"):
        import matplotlib.pyplot as plt
        if self._mu is None:
            raise RuntimeError("Call build() first.")
        idx = [list(self._species).index(n) for n in species_names]
        μ_sel = self._mu[...,idx]
        stable = μ_sel.argmin(axis=-1)
        stable = self.stable[:,:,1]

        if ax is None: ax = plt.gca()
        im = ax.imshow(stable.T, origin="lower",
                       extent=[self.pH_min,self.pH_max,self.U_min,self.U_max],
                       aspect="auto", cmap=cmap)
        cbar = plt.colorbar(im, ax=ax, ticks=range(len(species_names)))
        cbar.ax.set_yticklabels(species_names)
        ax.set_xlabel("pH"); ax.set_ylabel("U / V vs. SHE");
        ax.set_title("Most stable species")
        return ax

    def plot_energy_planes(self, species_names: Optional[Iterable[str]] = None,
                           *, stride=4, alpha=0.6, cmap="viridis", ax=None):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
        from matplotlib import cm
        if self._mu is None: raise RuntimeError("Call build() first.")
        if species_names is None: species_names = list(self._species)
        species_names = list(species_names)
        idx = [list(self._species).index(n) for n in species_names]
        colours = cm.get_cmap(cmap,len(idx))
        pH_vals = np.linspace(self.pH_min,self.pH_max,self.n_pH)[::stride]
        U_vals  = np.linspace(self.U_min,self.U_max,self.n_U)[::stride]
        pH_grid,U_grid = np.meshgrid(pH_vals,U_vals)
        if ax is None:
            fig = plt.figure(figsize=(8,6)); ax = fig.add_subplot(111,projection="3d")
        else: fig = ax.figure
        for k,sp_i in enumerate(idx):
            μ = self._mu[::stride,::stride,sp_i]
            surf = ax.plot_surface(pH_grid, U_grid, μ,
                                   rstride=1, cstride=1,
                                   color=colours(k), edgecolor="none",
                                   alpha=alpha)
            surf._facecolors2d = surf._facecolor3d
            surf._edgecolors2d = surf._edgecolor3d
        ax.set_xlabel("pH"); ax.set_ylabel("U / V"); ax.set_zlabel("μ / eV")
        ax.set_title("Energy planes")
        ax.legend(species_names, loc="upper left", bbox_to_anchor=(1.05,1.0))
        fig.tight_layout()
        return ax

    def Mosaic_Stacking(
        self,
        relevant_species: List[str],
        parallel: bool = True,
        reference_idx: Optional[int] = None,
        iterations: int = 2
    ) -> Tuple[np.ndarray, Dict[str, int]]:
        """
        Compute the most stable species index at each point in a mu-pH-U grid by comparing
        free-energy changes through reaction stoichiometries.

        This routine uses an optional dynamic reference update over multiple iterations
        and can run in parallel across grid points.

        Parameters
        ----------
        relevant_species : List[str]
            List of element symbols to evaluate stability for.
        parallel : bool, default True
            If True, run grid evaluations in parallel using joblib.
        reference : Optional[np.ndarray]
            Dynamic reference array, if applying multi-iteration refinements.
        reference_idx : Optional[int]
            Index of reference in the dynamic array, if applicable.
        iterations : int, default 2
            Number of refinement iterations when using a dynamic reference.

        Returns
        -------
        stable_index_array : np.ndarray
            Array of shape (n_pH, n_U, n_relevant) giving the index of the
            lowest-free-energy species at each grid point.
        stable_index_idx : Dict[str, int]
            Mapping from each relevant species to its index in the last axis.
        """

        # initial references per element
        initial_ref: Dict[str, str] = {}
        for sp in self.elements:
            if sp == 'O':
                initial_ref[sp] = 'H2O'
            elif sp == 'H':
                initial_ref[sp] = 'H+'
            else:
                for i, (state_name, state_data) in enumerate( self._species.items() ):
                    cp = state_data._composition
                    if cp.get(sp, 0) > 0:
                        initial_ref[sp] = state_data.name
                        break

        # assemble state info
        states_info: List[Dict[str, any]] = []
        for nm, (idx,) in self.states.items():
            ch, cp = self._species[nm]._formal_charge, self._species[nm]._composition
            states_info.append({'name': nm, 'idx': idx, 'charge': ch, 'comp': cp})

        n_rel = len(relevant_species)
        n_pH, n_U, n_mu = self.mu_pH_U.shape
        stable = np.zeros((n_pH, n_U, n_rel), dtype=int)
        rel_map = {sp: i for i, sp in enumerate(relevant_species)}

        # initial minima
        min_charge = np.zeros(n_rel)
        min_comp: List[Dict[str, int]] = [{} for _ in range(n_rel)]
        min_idx = np.zeros(n_rel, dtype=int)
        for i, rs in enumerate(relevant_species):
            for st in states_info:
                if rs in st['comp'] and st['comp'].get(rs, 0) > 0:
                    min_charge[i] = st['charge']
                    min_comp[i] = st['comp'].copy()
                    min_idx[i] = st['idx']
                    break  

        def eval_point(rs_i: int, ipH: int, iU: int) -> Tuple[int, int, int, int]:
            lc = min_charge[rs_i]
            comp_ref = min_comp[rs_i].copy()
            idx_ref = min_idx[rs_i]
            
            for st in (s for s in states_info if relevant_species[rs_i] in s['comp'] and s['comp'].get(relevant_species[rs_i], 0) > 0):
                # stoichiometry vector R
                ratio = st['comp'].get(relevant_species[rs_i], 0) / comp_ref.get(relevant_species[rs_i], 0)
                R_vec = np.zeros(n_mu)
                R_vec[st['idx']] += 1.0
                R_vec[idx_ref] += -ratio

                # composition & charge deltas
                delta_comp = {
                    sp: st['comp'].get(sp, 0) - comp_ref.get(sp, 0) * ratio
                    for sp in self.elements
                }
                delta_charge = st['charge'] - lc * ratio

                # build regression matrix
                # electron row first
                rows = [ [0.0]*len(self.elements)+[-1.0] ]

                # reference states per elements
                for sp in self.elements:
                    rnm =  self.specie_by_idx(stable[ipH, iU, rel_map[sp] ]) if sp in rel_map else initial_ref[sp]
                    ch_ref, comp_ref_sp = self._species[rnm]._formal_charge, self._species[rnm]._composition 
                    rows.append([comp_ref_sp.get(x, 0) for x in self.elements] + [ch_ref])

                A = np.array(rows).T
                b = -np.array([delta_comp.get(x, 0) for x in self.elements] + [delta_charge])

                model = Ridge(alpha=self.regularization_strength, fit_intercept=False)
                model.fit(A, b)
                coefs = model.coef_
                # update R_vec
                idx_e = self.states['e-'][0]
                R_vec[idx_e] += coefs[0]
                for k, sp in enumerate(self.elements, start=1):
                    name = self.specie_by_idx(stable[ipH, iU, rel_map[sp]]) if sp in rel_map else initial_ref[sp]
                    idx_s = self.states[name][0] 
                    R_vec[idx_s] += coefs[k]

                dG = R_vec @ self.mu_pH_U[ipH, iU]

                if it == iterations - 1:
                    current = self._species[st['name']].hull_min_distance
                    if not isinstance(current, (int, float)) or current > dG:
                        self._species[st['name']].hull_min_distance = dG

                if dG <= 0:
                    lc = st['charge']
                    comp_ref = st['comp'].copy()
                    idx_ref = st['idx']

            return rs_i, ipH, iU, idx_ref

        for it in range(iterations):

            if parallel:
                tasks = [(ri, ph, u) for ri in range(n_rel) for ph in range(n_pH) for u in range(n_U)]
                results = Parallel(n_jobs=-1)(delayed(eval_point)(*t) for t in tasks)
            else:
                results = [eval_point(ri, ph, u) for ri in range(n_rel) for ph in range(n_pH) for u in range(n_U)]

            for rs_i, ph, u, best in results:
                stable[ph, u, rs_i] = best

        self.stable = stable

        return stable, rel_map

    def convex_hull(
        self, 
        reference_species:dict=None,
        baseline_specie:dict=None,
        ):
        """
        """

        if baseline_specie:
            composition_baseline = baseline_specie._composition
            charge_baseline = baseline_specie._formal_charge
            G_ref = baseline_specie.G
        else:
            composition_baseline = {}
            charge_baseline = 0
            G_ref = 0

        n_pH, n_U, n_mu = self.mu_pH_U.shape

        hull_face_pts = np.zeros( (len(self._candidate_species), 3, 3) ) 

        pH_vals = np.linspace(self.pH_min,self.pH_max,self.n_pH)
        U_vals  = np.linspace(self.U_min,self.U_max,self.n_U)

        pH_U_idx = [ (0,0), (self.n_pH-1, 0), (0,self.n_U-1) ]

        hull_face_pts = np.zeros( (len(self._candidate_species), 3, 3) ) 

        for pi, p in enumerate( pH_U_idx ):

            for i, (state_name, state_data) in enumerate( self._candidate_species.items() ):

                charge, composition = state_data._formal_charge, state_data._composition

                R_vec = np.zeros(n_mu)
                G_state = state_data.G

                delta_dict = {
                    s: float(composition.get(s, 0)) - float(composition_baseline.get(s, 0))
                    for s in self.elements
                }
                delta_charge = charge - charge_baseline

                # build regression matrix
                # electron row first
                rows = [ [0.0]*len(self.elements)+[-1.0] ]

                # reference states per elements
                for re in reference_species:
                    ch_ref, comp_ref_sp = re._formal_charge, re._composition
                    rows.append([comp_ref_sp.get(x, 0) for x in self.elements] + [ch_ref])

                A = np.array(rows).T
                b = -np.array([delta_dict.get(x, 0) for x in self.elements] + [delta_charge])

                model = Ridge(alpha=self.regularization_strength, fit_intercept=False)
                model.fit(A, b)
                coefs = model.coef_

                idx_e = self.states['e-'][0]
                R_vec[idx_e] += coefs[0]
                for k, re in enumerate(reference_species, start=1):
                    ch_ref, name_ref = re._formal_charge, re.name
                    idx_s = self.states[name_ref][0] 
                    R_vec[idx_s] += coefs[k]

                dG = (G_state + R_vec @ self.mu_pH_U[p[0], p[1], :] - G_ref) 
                hull_face_pts[i, pi, :]  = pH_vals[p[0]], U_vals[p[1]], dG

        return hull_face_pts

    def distance_convex_hull(
        self,
        reference_species: list,
        baseline_specie=None,
        nx: int = 100,
        ny: int = 100,
    ) -> np.ndarray:
        """
        Computes the minimum distance from each (pH,U) grid point
        to the three facet planes defined by convex_hull().
        """
        hull_face_pts = self.convex_hull(
            reference_species=reference_species,
            baseline_specie=baseline_specie
        )
        distances = compute_min_distances(
            hull_face_pts,
            (self.pH_min, self.pH_max),
            (self.U_min, self.U_max),
            nx=nx,
            ny=ny
        )
        return distances


    def plot_phase_diagrams(self, ans, name):
        """
        Plots the 2D array 'ans' using the 'Blues' colormap.
        Labels each species once at the centroid of its occurrences.
        Configures the axes to represent pH and Potential (U) ranges.

        Parameters
        ----------
        ans : np.ndarray
            2D array of species indices with shape (U_points, pH_points).
        """
        import matplotlib.pyplot as plt

        # ----- Step 1: Map unique values to consecutive integers -----
        # Use np.unique to obtain unique values and their inverse indices
        ans = ans.T
        unique_values, inverse_indices = np.unique(ans, return_inverse=True)
        num_species = len(unique_values)
        
        # Reshape the inverse indices to get the array with consecutive numbers
        consecutive_array = inverse_indices.reshape(ans.shape)
        
        # ----- Step 2: Create a discrete color map -----
        cmap = plt.get_cmap('Blues', num_species)
        
        # ----- Step 3: Create the figure and axes -----
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # ----- Step 4: Display the matrix with imshow using the color map -----
        extent = [self.pH_min, self.pH_max, self.U_min, self.U_max]  # [xmin, xmax, ymin, ymax]
        im = ax.imshow(consecutive_array, cmap=cmap, origin='lower', extent=extent, aspect='auto')
        
        # ----- Step 5: Add a colorbar -----
        # The colorbar ticks correspond to the mapped indices
        cbar = fig.colorbar(im, ax=ax, ticks=np.arange(num_species), fraction=0.046, pad=0.04)
        cbar.set_label('Species', fontsize=12)
        
        # Assign original labels to the colorbar ticks
        labels = [self.specie_by_idx(sp) for sp in unique_values]
        cbar.set_ticklabels(labels)
        
        # ----- Step 6: Configure axis ticks based on pH and U ranges -----
        num_ticks = 10
        ax.set_xticks(np.linspace(self.pH_min, self.pH_max, num_ticks))
        ax.set_yticks(np.linspace(self.U_min, self.U_max, num_ticks))
        
        # ----- Step 7: Add grid lines for better readability -----
        ax.grid(which='both', color='white', linestyle='-', linewidth=0.5, alpha=0.7)
        
        # ----- Step 8: Calculate and add labels for each species at their centroid -----
        for mapped_idx, sp_idx in enumerate(unique_values):
            # Find the coordinates where the original species appears
            coords = np.argwhere(ans == sp_idx)
            if coords.size == 0:
                continue  # Skip if there are no occurrences
            
            # Calculate the mean of the coordinates to find the centroid
            row_mean = np.mean(coords[:, 0])
            col_mean = np.mean(coords[:, 1])
            
            # Convert matrix indices to actual pH and U values
            pH_center = self.pH_min + (col_mean / (self.n_pH - 1)) * (self.pH_max - self.pH_min)
            U_center = self.U_min + (row_mean / (self.n_U - 1)) * (self.U_max - self.U_min)
            
            # Get the species name
            species_name = self.specie_by_idx(int(sp_idx))
            
            # Add the text label at the centroid with a semi-transparent background for readability
            ax.text(
                pH_center,
                U_center,
                species_name,
                ha='center',
                va='center',
                fontsize=10,
                color='black',
                weight='bold',
                bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1)
            )
        
        # ----- Step 9: Set labels and title -----
        ax.set_xlabel('pH', fontsize=12)
        ax.set_ylabel('Potential (U)', fontsize=12)
        ax.set_title('Phase Diagram of Chemical Species', fontsize=14)
        
        # ----- Step 10: Adjust layout to accommodate the colorbar and labels -----
        plt.tight_layout()
        plt.savefig(f'phase_diagram_{name}.png', dpi=300)

        # ----- Step 11: Display the plot -----
        plt.show()

# ============================================================================
# Toy demo when executed directly
# ============================================================================

if __name__ == "__main__":
    # Build tiny Ni/O/H system ------------------------------------------------
    pd = PhaseDiagram(pH_range=(-3, 15, 50), U_range=(-2, 3, 50))

    pd.add_species(Species("H2"))
    pd.add_species(Species("O2"))

    pd.add_species(Species("H2O"))
    pd.add_species(Species("H+", charge=+1))
    pd.add_species(Species("e-", charge=-1))






    from sage_lib.partition.Partition import Partition
    from sage_lib.miscellaneous.data_mining import *
    import pandas as pda

    def add_state_LDH(Fe:int, Ni:int, V:int, K:int, H:int, O:int, E, q:0, pd):
        name = f'Fe{Fe}Ni{Ni}V{V}K{K}H{H}O{O}'
        Species(f"{name}", charge=q, concentration=1e-6)
        pd.add_candidate_species(Species(name, charge=q, G=E ))  
        #pd.add_species(Species(name))
        return pd

    file_path = '/Users/dimitry/Documents/Data/LDH/Sampling/metadata_111_full.dat'
    dataset_partition = Partition()
    Fel, Nil, Vl, Hl, Kl, Ol, El = [], [], [], [], [], [], []
    df = pda.read_csv(file_path, usecols=["Fe", "Ni", "V", "H", "K", "O", "E"])

    Fel = df["Fe"].astype(float).tolist()
    Nil = df["Ni"].astype(float).tolist()
    Vl  = df["V"].astype(float).tolist()
    Hl  = df["H"].astype(float).tolist()
    Kl  = df["K"].astype(float).tolist()
    Ol  = df["O"].astype(float).tolist()
    El  = df["E"].astype(float).tolist()
    

    lower_composition_dict = {}
    for c_i, c in enumerate(El):
        f = 1
        Fe, Ni, V, H, K, O = Fel[c_i]*f, Nil[c_i]*f, Vl[c_i]*f, Hl[c_i]*f, Kl[c_i]*f, Ol[c_i]*f 
        name = f'{Fe}{Ni}{V}{H}{K}{O}'
        E = El[c_i]*f 
        if len(pd._candidate_species) < 6300:
            pd = add_state_LDH(Fe=Fe, Ni=Ni, V=V, O=O, H=H, K=K, q=0, E=E,pd=pd) 

        if E < lower_composition_dict.get(name, [np.inf,0] )[0]:
            lower_composition_dict[f'{Fe}{Ni}{V}{H}{K}{O}'] = [E, {'Fe':Fe, 'Ni':Ni, 'V':V, 'H':H, 'K':K, 'O':O}] 
        # [Fe, Ni, V, H, K, O] [-0.85082353  3.12226329 -5.4095259  -3.13808807 -0.78452201 -7.84521677]

    for lcd_key, lcd_item in lower_composition_dict.items():
        Fe, Ni, V, H, K, O = np.array([ lcd_item[1][a] for a in ['Fe', 'Ni', 'V', 'H', 'K', 'O'] ])
        pd = add_state_LDH(Fe=Fe, Ni=Ni, V=V, O=O, H=H, K=K, q=0, E=lcd_item[0],pd=pd) 
    
    print( len(pd._candidate_species) )

    pd.add_species(Species("Fe"))
    pd.add_species(Species("K"))
    pd.add_species(Species("V"))

    pd.add_species(Species("Ni"))
    pd.add_species(Species("NiO"))
    pd.add_species(Species("Ni2+", charge=+2, concentration=1e-6))

    pd.add_species(Species('NiO2', 0) )             # Óxido de níquel (IV)
    pd.add_species(Species('Ni(OH)3 -', charge=-1, concentration=1e-6))              # Ion níquel (II)
    pd.add_species(Species('Ni3O4', 0)       )      # Óxido de níquel (III)
    pd.add_species(Species('Ni2O3', 0))             # Óxido de níquel (III)
    pd.add_species(Species('HNiO2 -', charge=-1, concentration=1e-6))           # Oxohidróxido de níquel   
    pd.add_species(Species('NiOOH', ))

    fact = -1.0/23060.5
    pd.add_reaction(Reaction({'Ni': 1, 'O2': .5, },          {'NiO': 1, }, -51610*fact ))
    pd.add_reaction(Reaction({'Ni': 3, 'O2': 2},             {'Ni3O4': 1}, -170150*fact))
    pd.add_reaction(Reaction({'Ni': 2, 'O2': 1.5},           {'Ni2O3': 1}, -112270*fact ))
    pd.add_reaction(Reaction({'Ni': 1, 'O2': 1},             {'NiO2': 1 }, -51420*fact))
    pd.add_reaction(Reaction({'Ni': 1, },                    {'Ni2+': 1, 'e-': 2}, -11530*fact))
    pd.add_reaction(Reaction({'Ni': 1, 'H2': .5, 'O2': 1, 'e-': 1},     {'HNiO2 -': 1}, -83465*fact))
    pd.add_reaction(Reaction({'Ni': 2, 'O2': 2, 'H2': 1},    {'NiOOH': 2, }, 3.406*2))

    pd.add_reaction(Reaction({'H+': 2, 'e-': 2},             {'H2': 1}, 0.0))
    pd.add_reaction(Reaction({'H+': 4, 'e-': 4, 'O2': 1},    {'H2O': 2}, 4.92))

    pd.add_reaction(Reaction({'Fe': 1, },          {}, -0.85082353 ))
    pd.add_reaction(Reaction({'Ni': 1, },          {},  3.12226329 ))
    pd.add_reaction(Reaction({'V': 1, },           {}, -5.4095259 ))
    pd.add_reaction(Reaction({'K': 1, },           {}, -0.78452201 ))
    pd.add_reaction(Reaction({'H2O': 1, },          {}, -14.2 ))
    pd.add_reaction(Reaction({'H2': 1, },          {}, -7.01 ))

    print(112, pd._species)

    T1 = time.time()
    pd.build(parallel=False)
    print(132123, time.time() -T1, )

    '''
    T1 = time.time()
    stable, rel_map = pd.Mosaic_Stacking(
        relevant_species=['Ni', 'Fe', 'V'], 
        parallel=True, 
        iterations=2,
    )
    print(time.time() -T1, pd._species)

    pd.plot_phase_diagrams( stable[:,:,0], name=f'H_LDH')
    pd.plot_phase_diagrams( stable[:,:,2], name=f'H_LDH')
    '''

    '''
    # 2-D map ---------------------------------------------------------------
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(4, 3))
    pd.pourbaix_map(["H2", "H2O", "O2"], ax=ax)
    plt.show()

    # 3-D planes ------------------------------------------------------------
    pd.plot_energy_planes(["H2", "H2O", "O2"], stride=3, alpha=0.5)
    plt.show()
    '''

    # Hull distance demo ----------------------------------------------------
    references_species = ( Species('H2O'), Species('H+'), Species('NiO'), Species('Fe'), Species('K'), Species('V'), )
    T1 = time.time()
    distances = pd.distance_convex_hull( reference_species=references_species, baseline_specie=None )
    print(time.time() -T1, distances)
    #3.3813529014587402 [0.         0.39749552 0.44229704 ... 1.91797905 3.09087811 4.64047089]

    '''
    0.035845041275024414 [0.         0.37826944 0.41541105 0.7331319  0.67688972 0.39870846
     1.04264524 0.98692186 0.63324011 0.5450918  1.20984726 1.27450046
     0.91799583 0.67783947 0.         1.05023861 1.0588005  0.67548618
     0.54121055 0.09594555 0.         0.50179027 0.46842101 0.26642688
     0.0593058  0.10062832 0.32874893 0.98954777 0.1902796  0.2028393
     0.28194258 0.39225008 0.5347994  0.98153269 1.74682371 2.83296129
     0.         0.10237293 0.2015873  0.45656338 0.70671768 1.16205693
     1.91797905 3.09087811 4.64047089]
    '''
