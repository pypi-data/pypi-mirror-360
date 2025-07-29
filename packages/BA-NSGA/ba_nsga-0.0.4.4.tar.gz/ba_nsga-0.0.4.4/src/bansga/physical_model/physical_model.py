from sage_lib.partition.Partition import Partition
import numpy as np
from tqdm import tqdm
from typing import List, Callable, Optional, Tuple, Literal
from multiprocessing import Process, Queue, current_process, Manager
import os

import multiprocessing as mp
import torch
from threading import Thread
from queue import Queue, Empty

INTERPOLATION_PREC = 256
TMode = Literal["sampling", "random", "uniform"]

def worker_loop_func(
    task_queue: Queue,
    result_queue: Queue,
    run_func: Callable[
        [List[str], np.ndarray, np.ndarray, float, str],
        Tuple[np.ndarray, List[str], np.ndarray, float]
    ],
    suffix: str,
    debug: bool
) -> None:
    """
    Hilo de trabajo que lee tareas y llama a run_func. Cada hilo opera en su propia GPU.

    Parameters
    ----------
    task_queue : queue.Queue
        Items: (idx, symbols, positions, cell, sampling_temperature, output_dir, generation)
    result_queue : queue.Queue
        Items: (idx, new_positions, new_symbols, new_cell, energy)
    run_func : callable
        Función run_mace devuelta por mage_run_factory_for_gpu.
    suffix : str
        Identificador como "GPU0", "GPU1", etc.
    debug : bool
        Si True, produce datos falsos.
    """
    thread_name = f"Worker-{suffix}"
    print(f"[{thread_name}] Iniciado.")

    while True:
        try:
            idx, symbols, positions, cell, samp_temp, out_dir, generation = task_queue.get(timeout=1.0)
        except Empty:
            print(f"[{thread_name}] No hay más tareas; saliendo.")
            break

        if idx is None:
            print(f"[{thread_name}] Señal de terminación; saliendo.")
            break

        out_file = os.path.join(out_dir, f"{suffix}_struct{idx}_gen{generation}.xyz")

        if debug:
            new_pos = positions.copy()
            new_sym = symbols[:]
            new_cell = cell.copy()
            energy = -1000.0 + np.random.rand() * 10.0
        else:
            try:
                new_pos, new_sym, new_cell, energy = run_func(
                    symbols, positions, cell, samp_temp, out_file
                )
            except Exception as e:
                print(f"[{thread_name}] ERROR idx={idx}: {e}")
                new_pos = positions.copy()
                new_sym = symbols[:]
                new_cell = cell.copy()
                energy = float("nan")

        result_queue.put((idx, new_pos, new_sym, new_cell, energy))

    print(f"[{thread_name}] Finalizado.")

def linear_interpolation(data, N):
    """
    Generates N linearly interpolated points over M input points.

    Parameters
    ----------
    data : int, float, list, tuple, or numpy.ndarray
        Input data specifying M control points. If scalar or of length 1,
        returns a constant array of length N.
    N : int
        Number of points to generate. Must be a positive integer and at least
        as large as the number of control points when M > 1.

    Returns
    -------
    numpy.ndarray
        Array of N linearly interpolated points.

    Raises
    ------
    ValueError
        If N is not a positive integer, N < M (when M > 1), or data is invalid.
    """
    # Validate N
    if not isinstance(N, int) or N <= 0:
        raise ValueError("N must be a positive integer.")
    
    # Handle scalar input
    if isinstance(data, (int, float)):
        return np.full(N, float(data))
    
    # Convert sequence input to numpy array
    try:
        arr = np.asarray(data, dtype=float).flatten()
    except Exception:
        raise ValueError("Data must be an int, float, list, tuple, or numpy.ndarray of numeric values.")
    
    M = arr.size
    if M == 0:
        raise ValueError("Input data sequence must contain at least one element.")
    if M == 1:
        return np.full(N, arr[0])
    
    # Ensure N >= M for piecewise interpolation
    if N < M:
        raise ValueError(f"N ({N}) must be at least the number of input points M ({M}).")
    
    # Define original and target sample positions
    xp = np.arange(M)
    xi = np.linspace(0, M - 1, N)
    
    # Perform piecewise linear interpolation
    yi = np.interp(xi, xp, arr)
    
    return yi

def mace_calculator(
        calc_path:str='MACE_model.model',
        nvt_steps: int = None, 
        fmax: float = 0.05, 
        hydrostatic_strain: bool = False,
        constant_volume: bool = True,
        device: str = 'cuda',
        default_dtype: str = 'float32',
        T:float = 300,
        T_ramp:bool=False,
        optimizer:str='FIRE',
        fixed_height = None, 
        debug=False
    ):
    r"""
    Create and return a two‐stage Langevin MD + final relaxation routine using a MACE model.

    This factory returns a function `run(symbols, positions, cell, sampling_temperature)`
    which performs:

    1. **Stage I – NVT Langevin dynamics**  
       A constant‐friction Langevin integrator at gradually ramped temperature  
       .. math::
          m_i \\frac{d^2 \\mathbf{r}_i}{dt^2} = -\\nabla_i V(\\{\\mathbf{r}\\}) - \\gamma m_i \\frac{d\\mathbf{r}_i}{dt}
            + \\sqrt{2 m_i \\gamma k_B T(t)}\\;\\boldsymbol{\\xi}_i(t),
       where:
       - \\(T(t)\\) is the thermostat schedule (here constant at \\(T\\) K),  
       - \\(\\gamma=0.01\\) fs⁻¹ is the friction coefficient,  
       - \\(k_B\\) is Boltzmann’s constant,  
       - \\(\\boldsymbol{\\xi}_i(t)\\) is unit‐variance Gaussian noise.  
       The number of steps  
       .. math::
          N_{\\rm MD} = N_{\\min} + P\\,(N_{\\max}-N_{\\min}),
       with  
       \\[
         P = \\texttt{sampling\_temperature} \\in [0,1],
         \\quad N_{\\min} = \\texttt{nvt\_steps\_min}, 
         \\quad N_{\\max} = \\texttt{nvt\_steps\_max}.
       \\]

    2. **Stage II – Geometry optimization**  
       Conjugate‐gradient / FIRE relaxation to force tolerance  
       .. math::
          f_{\\max} = f_{\\min} + P\\,(f_{\\max}^{\\rm tol}-f_{\\min}),  
       where \\(f_{\\min}\\), \\(f_{\\max}^{\\rm tol}\\) are inputs.

    3. **I/O**  
       - Trajectory and final frame written to `output_path` in XYZ format.  
       - Returns updated `(positions, symbols, cell, final_energy)`.

    **Parameters**
    ----------
    calc_path : str, optional
        Path to the trained MACE model file.
    output_path : str, optional
        File path to write the final structure (`.xyz`).
    nvt_steps : int
        Maximum NVT steps when `sampling_temperature=1`.
    fmax : float
        Minimum force‐convergence threshold (eV/Å) when `sampling_temperature=0`.
    device : str, optional
        Device for MACE (`'cpu'` or `'cuda'`).
    default_dtype : str, optional
        Floating‐point precision for MACE predictions.
    T : float, optional
        Target temperature (K) for the Langevin thermostat.
    debug : bool, optional
        If True, skip MD and return mock results immediately.

    **Returns**
    -------
    function
        A function with signature  
        ```python
        run(symbols, positions, cell, sampling_temperature) -> (pos, sym, cell, energy)
        ```
        which executes the two‐stage MD and relaxation as described.

    **Raises**
    ------
    RuntimeError
        If the MACE model cannot be loaded or MD/optimization fails irrecoverably.
    """
    from mace.calculators.mace import MACECalculator
    import ase.io
    from ase import Atoms, units
    from ase.md.langevin import Langevin
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
    from ase.optimize import BFGS, FIRE
    from ase.optimize.precon.fire import PreconFIRE
    from ase.optimize.precon import Exp
    from ase.filters import FrechetCellFilter

    from ase.units import fs
    from ase.constraints import FixAtoms
    import time

    calc = MACECalculator(model_paths=calc_path, device=device, default_dtype=default_dtype)

    nvt_steps = (
        linear_interpolation(nvt_steps, INTERPOLATION_PREC)
        if nvt_steps is not None
        else None
    )

    T = (
        linear_interpolation(T, INTERPOLATION_PREC)
        if T is not None
        else None
    )

    fmax = (
        linear_interpolation(fmax, INTERPOLATION_PREC)
        if fmax is not None
        else None
    )

    def run(
        symbols: np.ndarray,
        positions: np.ndarray,
        cell: np.ndarray,
        sampling_temperature:float=0.0,
        output_path:str='MD_out.xyz',
        ):
        """
        Executes two‐stage MD + relaxation for one structure.

        Parameters
        ----------
        symbols : ndarray or list
            Chemical symbols for each atom.
        positions : ndarray
            Atomic positions, shape (N, 3).
        cell : ndarray
            Lattice vectors, shape (3, 3).
        sampling_temperature : float, optional
            Fraction ∈ [0,1] selecting points in precomputed schedules.
        output_path : str, optional
            Path to append this trajectory’s XYZ frame.

        Returns
        -------
        tuple
            (new_positions, new_symbols, new_cell, energy)
        """

        # 1) Validate inputs
        if not isinstance(symbols, (list, np.ndarray)):
            raise TypeError("`symbols` must be a list or numpy array of strings")
        positions = np.asarray(positions, dtype=float)
        if positions.ndim != 2 or positions.shape[1] != 3:
            raise ValueError("`positions` must be an array of shape (N, 3)")
        cell = np.asarray(cell, dtype=float)
        if cell.shape != (3, 3):
            raise ValueError("`cell` must be a 3×3 array")
        if not isinstance(sampling_temperature, (int, float)):
            raise TypeError("`sampling_temperature` must be a number")
        if not isinstance(output_path, str):
            raise TypeError("`output_path` must be a string path")

        # 2) Ensure output directory exists
        out_dir = os.path.dirname(output_path) or '.'
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Could not create directory `{out_dir}`: {e}")


        def printenergy(dyn, start_time=None):
            """
            Prints potential, kinetic, and total energy for the current MD step.

            Parameters
            ----------
            dyn : ase.md.md.MDLogger
                The MD dynamics object.
            start_time : float, optional
                Start time for elapsed-time measurement, by default None.
            """
            a = dyn.atoms
            epot = a.get_potential_energy() / len(a)
            ekin = a.get_kinetic_energy() / len(a)
            elapsed_time = 0 if start_time is None else time.time() - start_time
            temperature = ekin / (1.5 * units.kB)
            total_energy = epot + ekin
            print(
                f"{elapsed_time:.1f}s: Energy/atom: Epot={epot:.3f} eV, "
                f"Ekin={ekin:.3f} eV (T={temperature:.0f}K), "
                f"Etot={total_energy:.3f} eV, t={dyn.get_time()/units.fs:.1f} fs, "
                f"Eerr={a.calc.results.get('energy', 0):.3f} eV, "
                f"Ferr={np.max(np.linalg.norm(a.calc.results.get('forces', np.zeros_like(a.get_forces())), axis=1)):.3f} eV/Å",
                flush=True,
            )

        def temperature_ramp(T, total_steps):
            """
            Generates a linear temperature ramp function.

            Parameters
            ----------
            initial_temp : float
                Starting temperature (K).
            final_temp : float
                Ending temperature (K).
            total_steps : int
                Number of MD steps over which to ramp.

            Returns
            -------
            function
                A function ramp(step) -> temperature at the given MD step.
            """
            if T_ramp:
                def ramp(step):

                    return T[ int( min( [(float(step)/total_steps)*INTERPOLATION_PREC, INTERPOLATION_PREC-1]))]
            else:
                def ramp(step):
                    return T[ int( min( [(float(sampling_temperature))*INTERPOLATION_PREC, INTERPOLATION_PREC-1]))]

            return ramp

        if debug:
            # Skip actual MD
            print(f"DEBUG mode: skipping MD calculations. Returning input positions.")
            return positions, symbols, cell, -2000.0

        # Atoms objects:
        atoms = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=True)
        if isinstance(fixed_height, (int, float) ):
            fix_index = [atom.index for atom in atoms if atom.position[2] < fixed_height]
            atoms.set_constraint(FixAtoms(indices=fix_index))
        atoms.calc = calc

        sampling_temperature_fraction =  int( min( [ (float(sampling_temperature) / 1.0 )*INTERPOLATION_PREC, INTERPOLATION_PREC-1] ) )

        #  ---- Stage 1: Molecular Dynamic ----
        nvt_steps_arr = np.asarray(nvt_steps, dtype=float) if nvt_steps is not None else None
        if nvt_steps_arr is not None:
            # sample one element (or a sub-array)
            nvt_steps_act = nvt_steps_arr[sampling_temperature_fraction]
            # proceed only if every selected value is > 0
            if (nvt_steps_act > 0).all():

                # Stage 1: NVT with first model
                temp_ramp = temperature_ramp(T, nvt_steps_act)
                MaxwellBoltzmannDistribution( atoms, temperature_K=temp_ramp(0) )
                dyn = Langevin(
                    atoms=atoms,
                    timestep=1 * fs,
                    temperature_K=temp_ramp(0),
                    friction=0.1
                )

                dyn.attach(lambda d=dyn: d.set_temperature(temperature_K=temp_ramp(d.nsteps)), interval=10)
                dyn.attach(printenergy, interval=5000, dyn=dyn, start_time=time.time())
                dyn.run(nvt_steps_act)
                ase.io.write(output_path, atoms, append=True)

        if not constant_volume:
            ecf = FrechetCellFilter(
                atoms,
                hydrostatic_strain=hydrostatic_strain,   # allow full shape + volume change
                constant_volume=constant_volume,      # set True if you want ΔV = 0
                scalar_pressure=0.0)        # target external pressure (GPa)

        #  ---- Stage 2: Geometry Optimization ----
        fmax_arr = np.asarray(fmax, dtype=float) if fmax is not None else None
        if fmax_arr is not None:
            fmax_act = fmax_arr[sampling_temperature_fraction]
            if (fmax_act > 0).all():

                if optimizer == 'BFGS':
                    relax = BFGS(atoms, logfile=None, maxstep=0.2) if constant_volume else BFGS(ecf, logfile=None)
                else:
                    relax = FIRE(atoms, logfile=None) if constant_volume else FIRE(ecf, logfile=None)
                
                relax.run(fmax=fmax_act, steps=200, )


        #precon = Exp(A=1)
        #relax = PreconFIRE(atoms, precon=precon,)# logfile=None)
        #relax.run(fmax=fmax, steps=200)
        return np.array(atoms.get_positions()), np.array(atoms.get_chemical_symbols()), np.array(atoms.get_cell()), float(atoms.get_potential_energy())

    return run

def physical_model(
    structures: List,
    physical_model_func: Callable,
    temperature:float=1.0, 
    T_mode: TMode = "sampling",
    generation: Optional[int] = None,
    output_path: str = ".",
    logger: object = None,
    debug: bool = False
    ):
    """
    Runs molecular dynamics simulations on the provided structures, with robust
    validation of user inputs to prevent misconfiguration.

    Parameters
    ----------
    structures : list
        List of structure objects to be simulated.
    physical_model_func : callable
        Function performing MD on a single structure.
    temperature : float, optional
        Base sampling temperature if T_mode == "sampling", by default 1.0.
    T_mode : {"sampling", "random", "uniform"}, optional
        Temperature assignment mode, by default "sampling".
    generation : int or None, optional
        Generation index used to name output files, by default None.
    output_path : str, optional
        Directory to write MD output files under `output_path/MD/`, by default ".".
    logger : object or None, optional
        Logger with methods info(), warning(), debug(), error(). If None, a dummy logger is used.
    debug : bool, optional
        If True, skip actual MD calls and return mock results, by default False.

    Returns
    -------
    Partition
        Partition containing the updated structures.

    Raises
    ------
    TypeError
        If any parameter is of an unexpected type.
    ValueError
        If any parameter has an invalid value or if output directory cannot be created.
    """
    logger.info(f"Starting MD simulations on structures ({len(structures)}). T = {temperature}")

    # Validate structures list
    if not isinstance(structures, (list, tuple)):
        raise TypeError("`structures` must be a list or tuple of structure objects.")
    n_struct = len(structures)
    #if n_struct == 0:
    #    raise ValueError("`structures` list is empty; at least one structure is required.")

    # Validate physical_model_func
    if not callable(physical_model_func):
        raise TypeError("`physical_model_func` must be a callable factory/function.")

    # Validate temperature
    if not isinstance(temperature, (int, float)):
        raise TypeError("`temperature` must be an int or float.")
    if temperature < 0:
        raise ValueError("`temperature` must be non-negative.")

    # Validate T_mode
    valid_modes = ("sampling", "random", "uniform")
    if T_mode not in valid_modes:
        raise ValueError(f"`T_mode` must be one of {valid_modes}, got {T_mode!r}.")

    # Validate generation
    if generation is not None and not isinstance(generation, (int, float)):
        raise TypeError("`generation` must be an int or None.")

    # Validate output_path and create MD subdirectory
    if not isinstance(output_path, str):
        raise TypeError("`output_path` must be a string path.")
    md_dir = os.path.join(output_path, "MD")
    try:
        os.makedirs(md_dir, exist_ok=True)
    except Exception as e:
        raise ValueError(f"Cannot create output directory `{md_dir}`: {e}")

    n_struct = len(structures)

    partitions_physical_model = Partition()
    partitions_physical_model.containers = structures

    # 1) Generate the temperature array # sampling", "random", "uniform
    if T_mode == "uniform":
        temps = np.linspace(0.0, 1.0, num=n_struct, dtype=float)
    elif T_mode == "random":
        temps = np.random.uniform(0.0, 1.0, size=n_struct)
    elif T_mode == "sampling":
        temps = np.full(n_struct, temperature, dtype=float)
    else:
        raise ValueError(f"Unsupported T_mode: {T_mode!r}")

    for idx, (structure, T_i) in enumerate(
        tqdm(zip(partitions_physical_model.containers, temps),
             total=len(partitions_physical_model.containers),
             desc="Simulations"),
        start=1
    ):
        try:
            structure.AtomPositionManager.charge = None
            structure.AtomPositionManager.magnetization = None
            
            if not debug:
                # Run MD simulation
                positions, symbols, cell, energy = physical_model_func(
                    symbols=structure.AtomPositionManager.atomLabelsList,
                    positions=structure.AtomPositionManager.atomPositions,
                    cell=structure.AtomPositionManager.latticeVectors,
                    sampling_temperature = T_i,
                    output_path=f'{output_path}/MD/MD_gen{generation}.xyz'
                )
            else: 

                positions = structure.AtomPositionManager.atomPositions 
                symbols = structure.AtomPositionManager.atomLabelsList
                cell = structure.AtomPositionManager.latticeVectors
                energy = -657.2 + np.random.rand()*6

            structure.AtomPositionManager.atomPositions = positions
            structure.AtomPositionManager.atomLabelsList = symbols
            structure.AtomPositionManager.latticeVectors = cell
            structure.AtomPositionManager.E = energy

        except Exception as e:
            logger.error(f"Error processing structure {idx}/{n_struct}: {e}")
            # Optionally continue to next structure or re-raise:
            continue

    logger.info(f"MD simulations completed. {len(partitions_physical_model.containers)} Structures processed.") 
    return partitions_physical_model

def physical_model(
    structures: List[object],
    physical_model_func: Callable[
        [List[str], np.ndarray, np.ndarray, float, str],
        Tuple[np.ndarray, List[str], np.ndarray, float]
    ],
    temperature: float = 1.0,
    T_mode: str = "sampling",
    generation: Optional[int] = None,
    output_path: str = ".",
    logger: Optional[object] = None,
    debug: bool = False,
    device: str = "cpu"
) -> None:
    """
    Execute MD + relaxation simulations for a list of structures, distributing
    tasks across GPUs if available or on CPU if device='cpu'.

    If device='cuda', spawns one worker per GPU, each binding to a different GPU
    via CUDA_VISIBLE_DEVICES. Workers dynamically pull tasks from a queue and
    process them as soon as their GPU is free. If device='cpu', runs tasks
    sequentially in the main process without spawning additional workers.

    Parameters
    ----------
    structures : List[object]
        List of structures. Each structure must have:
            structure.AtomPositionManager.atomLabelsList  -> List[str]
            structure.AtomPositionManager.atomPositions   -> np.ndarray (N,3)
            structure.AtomPositionManager.latticeVectors  -> np.ndarray (3,3)
            structure.AtomPositionManager.E               -> float (to be overwritten)
    physical_model_func : Callable
        Function to run MD + relaxation on one structure. Signature:
            (symbols, positions, cell, sampling_temperature, output_path)
            -> (new_positions, new_symbols, new_cell, energy)
    temperature : float, default=1.0
        Fraction ∈ [0,1] used as sampling_temperature for each call.
    T_mode : str, default="sampling"
        Temperature mode (currently 'sampling' only).
    generation : Optional[int], default=None
        Generation index for naming output files. If None, defaults to 0.
    output_path : str, default="."
        Directory to write per-structure XYZ outputs.
    logger : Optional[object], default=None
        Logger with `.info(str)` and `.error(str)` methods. If provided,
        progress and errors are logged.
    debug : bool, default=False
        If True, skip actual calls to physical_model_func and return mock data.
    device : str, default="cuda"
        'cuda' to use GPUs (one worker per GPU), 'cpu' to run sequentially on CPU.

    Raises
    ------
    RuntimeError
        If device='cuda' but no GPUs are detected via torch.cuda.
    """
    logger.info(f"Starting MD simulations on structures ({len(structures)}). T = {temperature}")
    if logger is None:
        class DummyLog:
            @staticmethod
            def info(msg): print(f"[INFO] {msg}")
            @staticmethod
            def error(msg): print(f"[ERROR] {msg}")
        logger = DummyLog()

    # Validate structures list
    if not isinstance(structures, (list, tuple)):
        raise TypeError("`structures` must be a list or tuple of structure objects.")
    n_struct = len(structures)
    #if n_struct == 0:
    #    raise ValueError("`structures` list is empty; at least one structure is required.")

    # Validate physical_model_func
    if not isinstance(physical_model_func, (list, tuple)) and not callable(physical_model_func):
        raise TypeError("`physical_model_func` must be a callable factory/function.")

    # Validate temperature
    if not isinstance(temperature, (int, float)):
        raise TypeError("`temperature` must be an int or float.")
    if temperature < 0:
        raise ValueError("`temperature` must be non-negative.")

    # Validate T_mode
    valid_modes = ("sampling", "random", "uniform")
    if T_mode not in valid_modes:
        raise ValueError(f"`T_mode` must be one of {valid_modes}, got {T_mode!r}.")

    # Validate generation
    if generation is not None and not isinstance(generation, (int, float)):
        raise TypeError("`generation` must be an int or None.")

    # Validate output_path and create MD subdirectory
    if not isinstance(output_path, str):
        raise TypeError("`output_path` must be a string path.")
    md_dir = os.path.join(output_path, "MD")
    try:
        os.makedirs(md_dir, exist_ok=True)
    except Exception as e:
        raise ValueError(f"Cannot create output directory `{md_dir}`: {e}")

    # 1) Validate device choice and detect GPUs if needed
    if device == "cuda" and generation == 0:
        try:
            import torch
            n_gpus = torch.cuda.device_count()
            if n_gpus < 1:
                raise RuntimeError("No CUDA-compatible GPUs detected.")
        except ImportError:
            raise RuntimeError("PyTorch not installed; cannot detect GPUs.")
    else:
        # CPU mode: only one “worker” in main process
        n_gpus = 0

    partitions_physical_model = Partition()
    partitions_physical_model.add_container( structures )

    total_structures = len(structures)
    generation_idx = generation if generation is not None else 0

    # 1) Generate the temperature array # sampling", "random", "uniform
    if T_mode == "uniform":
        temps = np.linspace(0.0, 1.0, num=n_struct, dtype=float)
    elif T_mode == "random":
        temps = np.random.uniform(0.0, 1.0, size=n_struct)
    elif T_mode == "sampling":
        temps = np.full(n_struct, temperature, dtype=float)
    else:
        raise ValueError(f"Unsupported T_mode: {T_mode!r}")

    # 2) If device='cpu', run tasks sequentially in the main process
    if device == "cpu" or callable(physical_model_func):
        if logger:
            logger.info(f"Running all simulations on {device} sequentially.")
        else:
            print(f"Running all simulations on {device} sequentially.")

        for idx, (structure, T_i) in enumerate(
            tqdm(zip(partitions_physical_model.containers, temps),
                 total=len(partitions_physical_model.containers),
                 desc="Simulations"),
            start=1
        ):
            structure.AtomPositionManager.charge = None
            structure.AtomPositionManager.magnetization = None
            
            symbols = structure.AtomPositionManager.atomLabelsList
            positions = np.asarray(structure.AtomPositionManager.atomPositions, dtype=float)
            cell = np.asarray(structure.AtomPositionManager.latticeVectors, dtype=float)

            out_file = os.path.join(
                output_path,
                f"MD/MD_gen{generation}.xyz"
            )

            if debug:
                new_positions = positions.copy()
                new_symbols = symbols[:]
                new_cell = cell.copy()
                energy = -1000.0 + np.random.rand() * 10.0
            else:
                try:
                    new_positions, new_symbols, new_cell, energy = physical_model_func(
                        symbols=symbols,
                        positions=positions,
                        cell=cell,
                        sampling_temperature=T_i,
                        output_path=out_file
                    )
                except Exception as e:
                    print(f"[{device}] ERROR in physical_model_func for structure {idx}: {e}")
                    new_positions = positions.copy()
                    new_symbols = symbols[:]
                    new_cell = cell.copy()
                    energy = float("nan")

            # Update structure in-place
            structure.AtomPositionManager.atomPositions = new_positions
            structure.AtomPositionManager.atomLabelsList = new_symbols
            structure.AtomPositionManager.latticeVectors = new_cell
            structure.AtomPositionManager.E = energy
            
            if logger:
                logger.info(f"Structure {idx}/{total_structures} on {device} → Energy: {energy:.4f}")
            else:
                print(f"[{device}] Completed {idx}/{total_structures}, Energy: {energy:.4f}")

        return partitions_physical_model  # Done with CPU mode

    # Parallel mode: one thread per function (GPU)
    logger.info(f"Parallel execution on {num_funcs} GPUs.")
    task_queue = Queue()
    result_queue = Queue()

    # Enqueue tasks
    for idx, (struct, T_i) in enumerate(zip(partitions_physical_model.containers, temps), start=1):
        symbols = struct.AtomPositionManager.atomLabelsList
        pos_arr = np.asarray(struct.AtomPositionManager.atomPositions, dtype=float)
        cell_arr = np.asarray(struct.AtomPositionManager.latticeVectors, dtype=float)
        # Each task is a tuple of:
        # (index, symbols, positions array, cell array, sampling temperature, output directory, generation index)
        task_queue.put((idx, symbols, pos_arr, cell_arr, T_i, md_dir, gen_idx))

    threads: List[Thread] = []
    for i, run_mace in enumerate(physical_model_funcs):
        suffix = f"GPU{i}"
        # Create a worker thread for each run_mace function (each bound to a different GPU)
        t = Thread(
            target=worker_loop_func,
            args=(task_queue, result_queue, run_mace, suffix, debug),
            name=f"Thread-{suffix}"
        )
        t.daemon = True  # Daemon threads will shut down when the main program exits
        t.start()
        threads.append(t)

    # Collect results
    completed = 0
    try:
        with tqdm(total=num_struct, desc="Parallel Simulations") as pbar:
            while completed < num_struct:
                try:
                    # Attempt to get a result from the result_queue with a timeout of 1 second
                    idx, new_pos, new_sym, new_cell, energy = result_queue.get(timeout=1.0)
                except Empty:
                    # If no result arrives within 1 second, check if any thread is still alive
                    if not any(t.is_alive() for t in threads):
                        break
                    continue

                # Update the corresponding structure with the new positions, symbols, cell, and energy
                struct = structures[idx - 1]
                struct.AtomPositionManager.atomPositions = new_pos
                struct.AtomPositionManager.atomLabelsList = new_sym
                struct.AtomPositionManager.latticeVectors = new_cell
                struct.AtomPositionManager.E = energy

                logger.info(f"[Parallel] Structure {idx}/{num_struct} → Energy: {energy:.4f}")
                completed += 1
                pbar.update(1)

    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: terminating worker threads.")
        raise

    # Wait for all threads to finish
    for t in threads:
        t.join(timeout=0)

    # Optionally discard any leftover results still in result_queue
    leftover = []
    while not result_queue.empty():
        leftover.append(result_queue.get())
    if leftover:
        logger.info(f"Collected {len(leftover)} leftover results.")

    logger.info("All simulations completed.")
    return partitions_physical_model

def EMT(positions, symbols, cell):
    r"""
    Perform a quick EMT relaxation and return updated atomic data.

    1. **Initialize Atoms:**  
       \\(\\mathrm{Atoms}(symbols, positions, cell, pbc=True)\\)

    2. **Maxwell–Boltzmann velocities:**  
       Sample initial velocities at 400 K  
       via  
       .. math::
         \tfrac12 m_i \langle v_i^2 \\rangle = \tfrac32 k_B T.

    3. **Minimization:**  
       Use BFGS to minimize forces to  
       .. math::
         \\max_i |F_i| < 0.05\\,\\mathrm{eV/Å}.

    **Parameters**
    ----------
    positions : ndarray, shape (N,3)
        Initial atomic positions.
    symbols : list of str
        Atomic symbols.
    cell : ndarray, shape (3,3)
        Lattice vectors.

    **Returns**
    -------
    tuple
        `(new_positions, new_symbols, new_cell, energy)`.
    """

    from ase.calculators.emt import EMT
    from ase import Atoms, units
    from ase.md.langevin import Langevin
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
    from ase.optimize import BFGS

    atoms = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=True)
    MaxwellBoltzmannDistribution(atoms, temperature_K=400)

    atoms.calc = EMT()
    print('Relaxing starting candidate')
    dyn = BFGS(atoms, trajectory=None, logfile=None)
    dyn.run(fmax=0.05, steps=100)
    #atoms.info['key_value_pairs']['raw_score'] = -a.get_potential_energy()

    return atoms.get_positions(), atoms.get_chemical_symbols(), atoms.get_cell(), atoms.get_potential_energy()
