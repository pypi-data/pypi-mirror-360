"""
mutation.py
-----------

Implements functions that mutate structures by changing atom types, adding or removing
solvents, etc.
"""

import copy
import random
import numpy as np
from sage_lib.partition.Partition import Partition

def component_greater_than( component:int, threshold: float ):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is strictly greater than the given threshold.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param threshold: Threshold value to compare against.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        return structure.AtomPositionManager.atomPositions[idx, component] >= threshold
    return _check

def component_less_than(component: int, threshold: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is strictly less than the given threshold.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param threshold: Threshold value to compare against.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        return structure.AtomPositionManager.atomPositions[idx, component] < threshold
    return _check

def component_in_range(component: int, min_val: float, max_val: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position falls within the provided [min_val, max_val] range.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param min_val: Lower bound of the allowed range.
    :param max_val: Upper bound of the allowed range.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        value = structure.AtomPositionManager.atomPositions[idx, component]
        return min_val <= value <= max_val
    return _check


def distance_from_origin_less_than(threshold: float):
    """
    Returns a constraint function that checks if an atom’s distance from the
    coordinate origin (0, 0, 0) is less than a specified threshold.

    :param threshold: The maximum allowed distance from the origin.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        dist_squared = pos[0]**2 + pos[1]**2 + pos[2]**2
        return dist_squared < threshold**2
    return _check

def distance_from_origin_greater_than(threshold: float):
    """
    Returns a constraint function that checks if an atom’s distance from the
    coordinate origin (0, 0, 0) is greater than a specified threshold.

    :param threshold: The minimum allowed distance from the origin.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        dist_squared = pos[0]**2 + pos[1]**2 + pos[2]**2
        return dist_squared > threshold**2
    return _check

def component_close_to_value(component: int, target: float, tolerance: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is within a certain tolerance of a target value.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param target: The desired coordinate value.
    :param tolerance: Allowed deviation from the target value.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        value = structure.AtomPositionManager.atomPositions[idx, component]
        return abs(value - target) <= tolerance
    return _check

def label_is(label: str):
    """
    Returns a constraint function that checks if the atom’s label matches
    the specified label exactly.

    :param label: Desired atomic label (e.g., 'C', 'H', 'O', 'Fe').
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        return structure.AtomPositionManager.atomLabelsList[idx] == label
    return _check

def label_in(label_set: set):
    """
    Returns a constraint function that checks if the atom’s label is a member
    of the given set of labels.

    :param label_set: A set of valid labels (e.g., {'H', 'He', 'Li'}).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        return structure.AtomPositionManager.atomLabelsList[idx] in label_set
    return _check

def component_ratio_less_than(x_component: int, y_component: int, ratio: float):
    """
    Returns a constraint function that verifies whether the ratio of the specified
    x_component to y_component is less than a given ratio, for an atom's position.

    :param x_component: The component acting as the numerator.
    :param y_component: The component acting as the denominator.
    :param ratio: The ratio threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    x_component = {'x':0, 'y':1, 'z':2}[x_component] if isinstance(x_component, str) else x_component
    y_component = {'x':0, 'y':1, 'z':2}[y_component] if isinstance(y_component, str) else y_component
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        if abs(pos[y_component]) < 1e-12:  # Avoid division by zero
            return False
        return (pos[x_component] / pos[y_component]) < ratio
    return _check

def component_ratio_greater_than(x_component: int, y_component: int, ratio: float):
    """
    Returns a constraint function that verifies whether the ratio of the specified
    x_component to y_component is greater than a given ratio, for an atom's position.

    :param x_component: The component acting as the numerator.
    :param y_component: The component acting as the denominator.
    :param ratio: The ratio threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    x_component = {'x':0, 'y':1, 'z':2}[x_component] if isinstance(x_component, str) else x_component
    y_component = {'x':0, 'y':1, 'z':2}[y_component] if isinstance(y_component, str) else y_component
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        if abs(pos[y_component]) < 1e-12:
            return False
        return (pos[x_component] / pos[y_component]) > ratio
    return _check


def distance_between_atoms_less_than(atom_idx_b: int, threshold: float):
    """
    Returns a constraint function that checks if the distance between the current atom
    (idx) and another reference atom (atom_idx_b) is less than the given threshold.

    :param atom_idx_b: Index of the reference atom.
    :param threshold: Threshold distance.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos_a = structure.AtomPositionManager.atomPositions[idx]
        pos_b = structure.AtomPositionManager.atomPositions[atom_idx_b]
        dist_squared = (pos_a[0] - pos_b[0])**2 + (pos_a[1] - pos_b[1])**2 + (pos_a[2] - pos_b[2])**2
        return dist_squared < threshold**2
    return _check

def distance_between_atoms_greater_than(atom_idx_b: int, threshold: float):
    """
    Returns a constraint function that checks if the distance between the current atom
    (idx) and another reference atom (atom_idx_b) is greater than the given threshold.

    :param atom_idx_b: Index of the reference atom.
    :param threshold: Threshold distance.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos_a = structure.AtomPositionManager.atomPositions[idx]
        pos_b = structure.AtomPositionManager.atomPositions[atom_idx_b]
        dist_squared = (pos_a[0] - pos_b[0])**2 + (pos_a[1] - pos_b[1])**2 + (pos_a[2] - pos_b[2])**2
        return dist_squared > threshold**2
    return _check


def z_greater_than_fraction_of_lattice(fraction: float):
    """
    Returns a constraint function that checks if the z-component of an atom's position
    is greater than a specified fraction of the c-lattice vector length.

    :param fraction: Fraction of the c-lattice vector (structure.AtomPositionManager.latticeVectors[2,2]).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        c_length = structure.AtomPositionManager.latticeVectors[2, 2]
        z_pos = structure.AtomPositionManager.atomPositions[idx, 2]
        return z_pos > fraction * c_length
    return _check


def x_plus_y_less_than(threshold: float):
    """
    Returns a constraint function that checks if the sum of x- and y-components of
    an atom's position is less than the given threshold.

    :param threshold: Sum threshold for x + y.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        return (pos[0] + pos[1]) < threshold
    return _check


def y_minus_z_greater_than(threshold: float):
    """
    Returns a constraint function that checks if the difference (y - z) for an atom's
    position exceeds the specified threshold.

    :param threshold: The minimum allowed value for (y - z).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        return (pos[1] - pos[2]) > threshold
    return _check

def component_sum_greater_than(components: list, threshold: float):
    """
    Returns a constraint function that checks if the sum of specified components
    (e.g., [0, 1] for x+y) of an atom's position is greater than a given threshold.

    :param components: List of indices of the position components to sum.
    :param threshold: The minimum sum threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    for c_i, c in enumerate(components):
        components[c_i] = {'x':0, 'y':1, 'z':2}[c] if isinstance(c, str) else c
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        total = sum(pos[c] for c in components)
        return total > threshold
    return _check


def component_sum_less_than(components: list, threshold: float):
    """
    Returns a constraint function that checks if the sum of specified components
    (e.g., [1, 2] for y+z) of an atom's position is less than a given threshold.

    :param components: List of indices of the position components to sum.
    :param threshold: The maximum sum threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    for c_i, c in enumerate(components):
        components[c_i] = {'x':0, 'y':1, 'z':2}[c] if isinstance(c, str) else c
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        total = sum(pos[c] for c in components)
        return total < threshold
    return _check

# from sage_lib.partition.Partition import Partition
# from your_code.utils import get_element_counts, ...
def validate(idx, structure, constraints:list, logic:str = "all") -> bool:
    """
    Checks whether the provided feature vector satisfies
    the constraints according to the specified logic.
    
    Returns
    -------
    bool
        True if constraints pass, False otherwise.
    """
    if logic == "all":
        return all(constraint(idx, structure) for constraint in constraints)
    elif logic == "any":
        return any(constraint(idx, structure) for constraint in constraints)
    return False

def mutate_structures(containers_initial, num_mutations, mutation_funcs):
    """
    Applies mutations to the provided structures.

    Parameters
    ----------
    containers_initial : list
        List of Container objects representing the structures to be mutated.
    num_mutations : int or array-like
        Number of mutations to apply to each structure (can be a list of integers).

    Returns
    -------
    list
        List of mutated structures.
    """
    containers_mutated = []

    for container_idx, container in enumerate(containers_initial):
        # Create a new Partition object to handle mutation if needed
        # Here we assume container is enough, or you might adapt your logic
        new_structure = copy.deepcopy(container)
        new_structure.magnetization = None
        new_structure.charge = None

        # Apply the requested number of mutations
        for _ in range(int(num_mutations[container_idx])):
            new_structure = mutation_funcs( new_structure )

        containers_mutated.append(new_structure)

    return containers_mutated

def change_atom_type(structure, ID_initial, ID_final, N:int=1, constraints:list=[], verbose:bool=False, ):
    """
    Changes one atom of type 'ID_initial' to 'ID_final'.
    """
    if isinstance(ID_initial, str):     
        atom_indices = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == ID_initial)[0]
    elif isinstance(ID_initial, list) or isinstance(ID_initial, np.ndarray): 
        atom_indices = ID_initial

    atom_indices_filtered = []
    for idx in atom_indices:
        if validate(idx, structure, constraints):
            atom_indices_filtered.append( idx )

    atom_indices = atom_indices_filtered

    if len(atom_indices) == 0:
        return None, None

    selected_atom_index = random.choice(atom_indices)

    partition = Partition()
    partition.containers = [structure]

    partition.handleAtomIDChange({
     'atom_index': {
         'search': 'exact',
         'atom_index': 'atom_index',
         'atom_ID': [selected_atom_index],
         'new_atom_ID': [ID_final],
         'N': N,
         'weights': [1],
         'seed': 1,
         'verbose': verbose
     }
    })

    return partition.containers[0], selected_atom_index

def remove_atom_groups(structure, atom_groups, iterations):
    """
    Removes specified atom groups from the structure.
    """
    values = {
        'iterations': iterations,
        'repetitions': 1,
        'distribution': 'uniform',
        'fill': False,
        'atom_groups': atom_groups,
        'group_numbers': None,
        'Nw': 1,
    }

    partition = Partition()
    partition.containers = [structure]

    partition.generate_configurational_space(values=values, verbose=verbose)

    return partition.containers[0]

def add_species(structure, species, bound:list =None, collision_tolerance:float=2.0, constraints: list=[], verbose:bool=False ):
    species = species if isinstance(species, list) else [species]

    partition = Partition()
    partition.containers = copy.deepcopy([structure])

    if isinstance(bound, (list, np.ndarray)):
        values = {
            'adsobate': species,
            'padding':.9,
            'resolution':40,
            'd':collision_tolerance*1.06,
            'ID': bound,
            'collision_tolerance': collision_tolerance,
            'molecules_number':np.ones( len(species) ),
            'translation': None,
            'wrap': True,
            'max_iteration':1000,
            'seed':None,
            'verbose':verbose,
        }
        try:
            partition.handleCLUSTER( values= {'ADD_ADSOBATE':values}  )
        except: return None

    else:
        values = {
            'density': None,
            'solvent': species,
            'slab': False,
            'shape': 'cell',
            'size': None,
            'vacuum_tolerance': None,
            'collision_tolerance': collision_tolerance,
            'molecules_number': np.ones( len(species) ),
            'translation': None,
            'wrap': True,
            'max_iteration':1000,
            'seed':None,
            'verbose':verbose
        }
        try:
            partition.handleCLUSTER( values= {'ADD_SOLVENT':values}  )
        except: return None

    return partition.containers[0]

# ------------------------------------------------------------------
#  ------------          Mutations functions              ---------
# ------------------------------------------------------------------
def mutation_swap(ID1: str, ID2: str, constraints: list=[], N: int=1):
    def func(structure):
        idx1_list = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == ID1)[0]
        idx2_list = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == ID2)[0]
        if len(idx1_list) > 0 and len(idx2_list) > 0:
            structure, idx = change_atom_type(structure=structure, ID_initial=ID1, ID_final=ID2, N=N, constraints=constraints)
            structure, idx = change_atom_type(structure=structure, ID_initial=idx2_list, ID_final=ID1, N=N, constraints=constraints)
        else: return None
        return structure

    return func

def mutation_change_ID(ID_initial: str, ID_final: str, constraints: list=[], N: int=1):
    
    def func(structure):
        structure, _ = change_atom_type(structure=structure, ID_initial=ID_initial, ID_final=ID_final, N=N, constraints=constraints)
        return structure

    return func

def mutation_remove(IDs: str, constraints: list=[], N:int=1):
    def func(structure):
        structure = remove_atom_groups(structure, atom_groups=IDs, iterations=N)
        return structure
    return func

def mutation_add(species: list, bound:list =None, collision_tolerance:float=2.0, constraints: list=[]):
    def func(structure):
        structure = add_species(structure=structure, species=species, bound=bound, collision_tolerance=collision_tolerance)
        return structure

    return func

def mutation_rattle(std: str, constraints: list=[]):
    def func(structure):
        structure.AtomPositionManager.rattle(stdev=values['std'], seed=n)
        return structure
    return func

def mutation_compress(compress_factor: float, constraints: list=[]):
    def func(structure):
        structure.AtomPositionManager.compress(compress_factor=compress_factor, verbose=False)
        return structure
    return func

'''
a = mutation_swap('a', 'b')
resultado = a(structure=1)
print(resultado)  # Salida: (1, 'a', 'b')
'''
