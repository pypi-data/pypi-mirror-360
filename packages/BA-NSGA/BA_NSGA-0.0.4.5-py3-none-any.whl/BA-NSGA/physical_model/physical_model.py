from sage_lib.partition.Partition import Partition
import numpy as np

def physical_model(structures, physical_model_func, logger=None, debug=False):
    """
    Runs molecular dynamics simulations on the provided structures.

    Parameters
    ----------
    structures : list
        List of structure objects to be simulated.
    debug : bool, optional
        If True, enables debug mode and prints additional messages.

    Returns
    -------
    None
        The structures are updated in place with simulation results.
    """
    logger.info(f"Starting MD simulations on structures ({len(structures)}).")

    partitions_physical_model = Partition()
    partitions_physical_model.containers = structures

    for idx, structure in enumerate( partitions_physical_model.containers ):

        structure.AtomPositionManager.charge = None
        structure.AtomPositionManager.magnetization = None
        
        if not  debug:
            # Run MD simulation
            positions, symbols, cell, energy = physical_model_func(
                symbols=structure.AtomPositionManager.atomLabelsList,
                positions=structure.AtomPositionManager.atomPositions,
                cell=structure.AtomPositionManager.latticeVectors
            )
        else: 

            positions = structure.AtomPositionManager.atomPositions 
            symbols = structure.AtomPositionManager.atomLabelsList
            cell = structure.AtomPositionManager.latticeVectors
            energy = -157.2 + np.random.rand()*6

        structure.AtomPositionManager.atomPositions = positions
        structure.AtomPositionManager.atomLabelsList = symbols
        structure.AtomPositionManager.latticeVectors = cell
        structure.AtomPositionManager.E = energy

    logger.info(f"MD simulations completed. {idx+1} Structures processed.") 
    return partitions_physical_model

def EMT(positions, symbols, cell):
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
