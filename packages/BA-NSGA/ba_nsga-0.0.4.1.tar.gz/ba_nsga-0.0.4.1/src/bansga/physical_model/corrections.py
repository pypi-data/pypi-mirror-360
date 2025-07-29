import numpy as np
import math
from ase import units
# If ASE Vibrations is available for normal-mode analysis:
try:
    from ase.vibrations import Vibrations
    has_vibrations = True
except ImportError:
    has_vibrations = False

# Constants
ħ = 1.0545718e-34  # Reduced Planck constant, J·s
kB = 1.38064852e-23  # Boltzmann constant, J/K

# ---------------------------------------------
# 1) Schlitter's configurational entropy bound
# ---------------------------------------------
# Formula:
#   S_schlitter <= (kB/2) * ln det[I + (kB T / ħ^2) * C]
# where C is the mass-weighted positional covariance:
#   C_ij = <(x_i - <x_i>)(x_j - <x_j>)>

def compute_schlitter_entropy(positions, masses, temperature):
    """
    Upper bound on configurational entropy via positional covariance.

    positions: (N_frames, N_atoms, 3) array of coordinates (m)
    masses:     (N_atoms,) array of masses (kg)
    temperature: float, system temperature (K)
    Returns:
      S_schlitter: float, entropy estimate (J/K)
    """
    # Center positions
    x = positions - positions.mean(axis=0, keepdims=True)
    # Mass-weighting: X = sqrt(m) * x
    mw = np.sqrt(masses)[None, :, None]
    X = (x * mw).reshape(positions.shape[0], -1)
    # Covariance
    C = np.cov(X, rowvar=False)
    # Schlitter matrix: M = I + (kB T / ħ^2) * C
    factor = (kB * temperature) / (ħ**2)
    M = np.eye(C.shape[0]) + factor * C
    sign, logdet = np.linalg.slogdet(M)
    if sign <= 0:
        raise ValueError("Non-positive determinant in Schlitter matrix")
    return 0.5 * kB * logdet


# ----------------------------------------------------------
# 2) Vibrational entropy from velocity density of states (DOS)
# ----------------------------------------------------------
# Classical formula:
#   S_vib = kB ∫ g(ω) [1 - ln(β ħ ω)] dω,  β = 1/(kB T)

def compute_vibrational_entropy(velocities, masses, temperature, dt):
    """
    Estimate vibrational entropy from MD velocities via DOS.

    velocities: (N_frames, N_atoms, 3) array of velocities (m/s)
    masses:      (N_atoms,) array of masses (kg)
    temperature: float, (K)
    dt:          time step between frames (s)

    Returns:
      S_vib: float, vibrational entropy (J/K)
    """
    # Flatten mass-weighted velocities
    v = (velocities * np.sqrt(masses)[None,:,None]).reshape(velocities.shape[0], -1)
    # VACF(t) = <v(0)·v(t)> / N
    n = v.shape[0]
    vacf = np.correlate(v.mean(axis=1), v.mean(axis=1), mode='full')[n-1:] / n
    # FFT to get DOS
    dos = np.fft.rfft(vacf)
    freqs = np.fft.rfftfreq(n, dt)
    beta = 1.0 / (kB * temperature)
    omega = 2 * math.pi * freqs + 1e-30
    integrand = dos * (1 - np.log(beta * ħ * omega))
    return kB * np.trapz(integrand, freqs)


# ------------------------------------------------
# 3) Thermodynamic integration from heat capacity
# ------------------------------------------------
# C_V = (<E^2> - <E>^2) / (kB T^2)
# S(T_i)-S(T_{i-1}) = ∫_{T_{i-1}}^{T_i} C_V/T dT

def compute_entropy_TI(energies, temperatures):
    """
    Compute entropy vs. temperature via thermodynamic integration.

    energies: list of arrays of instantaneous total energies at T_i
    temperatures: list of floats T_i (K)

    Returns:
      S: array of entropies at T_i relative to S(T0)=0 (J/K)
    """
    C_V = [(np.var(E) / (kB * T**2)) for E, T in zip(energies, temperatures)]
    S = [0.0]
    for i in range(1, len(temperatures)):
        T0, T1 = temperatures[i-1], temperatures[i]
        CV0, CV1 = C_V[i-1], C_V[i]
        delta_S = 0.5 * ((CV0 / T0) + (CV1 / T1)) * (T1 - T0)
        S.append(S[-1] + delta_S)
    return np.array(S)


# --------------------------------------------------------
# 4) Radial Distribution Function (g(r)) and Coordination
# --------------------------------------------------------
# g(r) = (1/(4πr^2 ρ N)) ⟨Σ_i Σ_{j≠i} δ(r - r_{ij})⟩
# Compute histogram of pairwise distances over frames.

def compute_rdf(positions, r_max, dr, atom_types=None, box=None):
    """
    Compute radial distribution function g(r).

    positions: (N_frames, N_atoms, 3) array (m)
    r_max: float, maximum distance (m)
    dr:    float, bin width (m)
    atom_types: (N_atoms,) optional indices to select subset
    box:   None or (3,3) array for periodic box vectors (m)

    Returns:
      r:    array of bin centers
      g_r:  array of g(r)
    """
    N_frames, N_atoms, _ = positions.shape
    if atom_types is None:
        inds = np.arange(N_atoms)
    else:
        inds = atom_types
    n_sel = len(inds)
    rho = n_sel / (np.linalg.det(box) if box is not None else (positions.ptp(axis=(0,1)).prod()))
    nbins = int(r_max / dr)
    hist = np.zeros(nbins)
    for frame in positions:
        coords = frame[inds]
        for i in range(n_sel):
            diffs = coords - coords[i]
            if box is not None:
                diffs = diffs - box.dot(np.round(np.linalg.solve(box, diffs.T)).T)
            dists = np.linalg.norm(diffs, axis=1)
            # ignore zero distance
            dists = dists[dists > 1e-12]
            bins = (dists / dr).astype(int)
            valid = bins < nbins
n            hist[bins[valid]] += 1
    # Normalize
    r = (np.arange(nbins) + 0.5) * dr
    shell_vol = 4 * np.pi * r**2 * dr
    norm = rho * n_sel * N_frames
    g_r = hist / norm / shell_vol
    return r, g_r


# ------------------------------------------------
# 5) Mean Squared Displacement (MSD) & Diffusion
# ------------------------------------------------
# MSD(t) = ⟨|r_i(t) - r_i(0)|^2⟩
# D = lim_{t→∞} MSD(t) / (6 t)

def compute_msd(positions, dt):
    """
    Compute mean squared displacement (MSD) and estimate diffusion coefficient.

    positions: (N_frames, N_atoms, 3) array (m)
    dt:        float, time step between frames (s)

    Returns:
      times: array of times (s)
      msd:   array of MSD(t)
      D:     float, diffusion coefficient estimate (m^2/s)
    """
    N_frames, N_atoms, _ = positions.shape
    max_tau = N_frames // 2
    msd = np.zeros(max_tau)
    for tau in range(1, max_tau):
        disp = positions[tau:] - positions[:-tau]
        sq = (disp**2).sum(axis=2)
        msd[tau] = sq.mean()
    times = np.arange(max_tau) * dt
    # Linear fit to MSD = 6 D t at long times
    fit_range = slice(max_tau//4, max_tau)
    p = np.polyfit(times[fit_range], msd[fit_range], 1)
    D = p[0] / 6.0
    return times, msd, D


# ------------------------------------------------
# 6) Velocity Autocorrelation Function (VACF)
# ------------------------------------------------
# VACF(t) = ⟨v(0)·v(t)⟩ / ⟨v^2⟩

def compute_vacf(velocities, dt):
    """
    Compute normalized VACF and extract characteristic times.

    velocities: (N_frames, N_atoms, 3) array (m/s)
    dt:         float, time step (s)

    Returns:
      times: array (s)
      vacf:  array normalized VACF
    """
    n_frames, N_atoms, _ = velocities.shape
    v_flat = velocities.reshape(n_frames, -1)
    mean_v = v_flat.mean(axis=1)
    raw = np.correlate(mean_v, mean_v, mode='full')[n_frames-1:]
    vacf = raw / raw[0]
    times = np.arange(len(vacf)) * dt
    return times, vacf


# -----------------------------------------------
# 7) Heat Capacity & Bulk Modulus from Fluctuations
# -----------------------------------------------
# C_V = (<E^2> - <E>^2) / (kB T^2)
# B_T = kB T <V> / <(δV)^2>

def compute_heat_capacity(energies, temperature):
    """
    Compute heat capacity at constant volume.

    energies: array of instantaneous total energies (J)
    temperature: float (K)
    Returns:
      C_V: float (J/K)
    """
    varE = np.var(energies)
    return varE / (kB * temperature**2)


def compute_bulk_modulus(volumes, temperature, mean_volume=None):
    """
    Compute isothermal bulk modulus via volume fluctuations.

    volumes: array of instantaneous volumes (m^3)
    temperature: float (K)
    mean_volume: optional float for <V>. If None, uses np.mean(volumes).
    Returns:
      B_T: float, bulk modulus (Pa)
    """
    if mean_volume is None:
        mean_volume = volumes.mean()
    varV = np.var(volumes)
    return kB * temperature * mean_volume / varV


# ----------------------------------------------
# 8) Thermal Expansion Coefficient from NPT runs
# ----------------------------------------------
# α_p = (1/V)(∂V/∂T)_p via finite differences

def compute_thermal_expansion(avg_volumes, temperatures):
    """
    Compute thermal expansion coefficient at constant pressure.

    avg_volumes: list/array of <V> at each T (m^3)
    temperatures: list/array of T (K) same length

    Returns:
      alpha: float (K^-1)
    """
    # Simple linear fit: V = aT + b  => α = a / V_avg
    p = np.polyfit(temperatures, avg_volumes, 1)
    a = p[0]
    V0 = np.mean(avg_volumes)
    return a / V0


# -------------------------------------------------------
# 9) Stress Tensor Fluctuations for Elastic Constants
# -------------------------------------------------------
# C_ij ~ V/(kB T) [<σ_i σ_j> - <σ_i><σ_j>]

def compute_stress_fluctuations(stresses, temperature, volume):
    """
    Compute elastic/stress-related metrics from stress fluctuations.

    stresses: (N_frames, 6) array of stress tensor components (Voigt) (Pa)
    temperature: float (K)
    volume: float (m^3)

    Returns:
      C: (6,6) array, fluctuation-based elastic constants (Pa)
    """
    # stresses rows: [σ_xx, σ_yy, σ_zz, σ_yz, σ_xz, σ_xy]
    mean = stresses.mean(axis=0)
    delta = stresses - mean
    cov = np.dot(delta.T, delta) / len(stresses)
    return volume * cov / (kB * temperature)


# ---------------------------------------------------
# 10) Local Order Parameters (Steinhardt Q_l)
# ---------------------------------------------------
# Q_l(i) = sqrt((4π/(2l+1)) Σ_m |q_{lm}(i)|^2)
# where q_{lm}(i) = (1/Nb(i)) Σ_j Y_{lm}(θ_ij, φ_ij)

def compute_steinhardt_Q_l(positions, neighbors, l=6):
    """
    Compute Steinhardt local order Q_l for each atom.

    positions: (N_atoms, 3) array (m)
    neighbors: list of neighbor index lists per atom
    l: integer, angular momentum number

    Returns:
      Q: (N_atoms,) array of Q_l values
    """
    # Requires spherical harmonics; here is a placeholder for actual Y_lm
    from scipy.special import sph_harm
    N_atoms = positions.shape[0]
    Q = np.zeros(N_atoms)
    for i in range(N_atoms):
        nbrs = neighbors[i]
        Nb = len(nbrs)
        q_lm = np.zeros(2*l+1, dtype=complex)
        for j in nbrs:
            vec = positions[j] - positions[i]
            r, theta, phi = cartesian_to_spherical(vec)
            for m in range(-l, l+1):
                q_lm[m+l] += sph_harm(m, l, phi, theta)
        q_lm /= Nb
        Q[i] = np.sqrt((4*math.pi)/(2*l+1) * np.sum(np.abs(q_lm)**2))
    return Q

# Helper: Cartesian to spherical

def cartesian_to_spherical(vec):
    x, y, z = vec
    r = np.linalg.norm(vec)
    theta = np.arccos(z / r) if r != 0 else 0
    phi = np.arctan2(y, x)
    return r, theta, phi


# ----------------------------------------------------------------
# 11) Normal-mode analysis via ASE Vibrations (as before)
# ----------------------------------------------------------------
def compute_normal_modes(atoms, workdir='vib'):
    """
    Compute normal modes using ASE Vibrations.

    atoms: ASE Atoms object for the system
    workdir: directory prefix for displacement calculations

    Returns:
      freqs: array of frequencies (cm^-1)
      modes: (N_modes, N_atoms, 3) array of mode vectors
    """
    if not has_vibrations:
        raise RuntimeError("ASE Vibrations module not available")
    vib = Vibrations(atoms, name=workdir)
    vib.run()
    freqs = vib.get_frequencies()
    modes = vib.get_modes()
    vib.clean()
    return freqs, modes

# ----------------------------------------------------------
# Usage: in GA MD loop, after collecting:
# positions, velocities, energies, volumes, stresses, neighbors
# masses = atoms.get_masses() * atomic_mass_unit (kg)
# dt = time step (s)
# T = temperature (K)
# Compute:
#   S_schl = compute_schlitter_entropy(positions, masses, T)
#   S_vib   = compute_vibrational_entropy(velocities, masses, T, dt)
#   S_TI    = compute_entropy_TI(energies_list, temps_list)
#   r, g_r  = compute_rdf(positions, r_max, dr, atom_types, box)
#   times, msd, D = compute_msd(positions, dt)
#   times_v, vacf = compute_vacf(velocities, dt)
#   C_V = compute_heat_capacity(energies, T)
#   B_T = compute_bulk_modulus(volumes, T)
#   alpha = compute_thermal_expansion(avg_volumes, temps)
#   C_elastic = compute_stress_fluctuations(stresses, T, mean_volume)
#   Q6 = compute_steinhardt_Q_l(positions[-1], neighbors_list, l=6)
#   freqs, modes = compute_normal_modes(atoms)

# Todos los resultados se pueden combinar en el vector de características del GA.
