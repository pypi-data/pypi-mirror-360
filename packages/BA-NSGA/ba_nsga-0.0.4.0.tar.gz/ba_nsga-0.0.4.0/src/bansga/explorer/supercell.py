from .explorer import EvolutionaryStructureExplorer
import os
import copy
import pickle
from ..utils.logger import WorkflowLogger
from typing import Any, Dict, Tuple, List, Optional
from sage_lib.partition.Partition import Partition

# =============================================================================
# Higher-Level Manager to Run Multiple Supercell Instances
# =============================================================================
class SupercellEvolutionManager:
    """
    Manages multiple evolutionary structure exploration instances across
    a series of supercell dimensions. For each defined supercell dimension,
    an instance of EvolutionaryStructureExplorer is created, executed, and
    its results stored for further analysis.
    
    Additional functionality includes result retrieval, listing processed
    supercells, saving state to disk, and resetting the manager state.
    """
    def __init__(self,                  
                 params_base: dict, 
                 dataset_path: Optional[str] = None, 
                 template_path: Optional[str] = None,
                 output_path: str = '.', 
                 supercell_list: List[Tuple[int, int, int]] = [(1, 1, 1)], 
                 params_supercell: Optional[Dict[str, List[Any]]] = None,
                 restart: bool = True,
                 debug: bool = False):
        """
        Initializes the SupercellEvolutionManager with the necessary parameters.
        
        Parameters
        ----------
        params_base : dict
            Base evolutionary parameters that will be shared and updated for each explorer instance.
        dataset_path : str, optional
            File path to the dataset of initial structures.
        template_path : str, optional
            File path to the template structures.
        output_path : str
            Directory where outputs and logs are stored.
        supercell_list : list of tuple(int, int, int)
            List of supercell dimensions (e.g., [(1,1,1), (2,1,1), (2,2,1), ...]).
        params_supercell : dict, optional
            Parameters specific to each supercell. For each key, a list corresponding to each supercell dimension is expected.
        debug : bool, optional
            If True, enables debug logging.
            
        Raises
        ------
        AssertionError
            If the provided parameters do not conform to the expected types or lengths.
        ValueError
            If any of the supercell dimensions is not a tuple of three integers.
        """
        # Basic type validations
        assert isinstance(params_base, dict), "params_base must be a dictionary."
        assert isinstance(supercell_list, list), "supercell_list must be a list of 3-tuples."
        supercell_list = [
            tuple(dim) if isinstance(dim, list) else dim
            for dim in supercell_list
        ]

        for dim in supercell_list:
            assert isinstance(dim, (tuple,list)) and len(dim) == 3, f"Each supercell dimension must be a tuple of 3 integers. Found: {dim} type {type(dim)}"

        # If supercell-specific parameters are provided, ensure they match the number of supercells.
        if params_supercell is not None:
            assert isinstance(params_supercell, dict), "params_supercell must be a dictionary if provided."
            for key, value in params_supercell.items():
                if not isinstance(value, list):
                    raise ValueError(f"Value for key '{key}' in params_supercell must be a list.")
                if len(value) < len(supercell_list):
                    raise ValueError(
                        f"Invalid params_supercell for key '{key}': received list length {len(value)}; expected {len(supercell_list)}."
                    )
        else:
            params_supercell = {}

        self.params_base = params_base
        self.params_supercell = params_supercell
        
        self.dataset_path = dataset_path
        self.template_path = template_path
        self.output_path = output_path
        self.sync_params = None

        self.supercell_list = supercell_list
        self.debug = debug
        self.logger = WorkflowLogger.setup_logger('SupercellEvolutionManager', self.output_path)

        # Dictionaries to store each explorer instance and its results.
        self.explorer_instances: Dict[Tuple[int, int, int], EvolutionaryStructureExplorer] = {}
        self.results: Dict[Tuple[int, int, int], Any] = {}
        self.templates: Dict[Tuple[int, int, int], Any] = {}
        self.restart = restart

    def read_supercell(self, output_path: str, sc_dim: list) -> Tuple[Optional[Any], bool]:
        """
        Checks if the folder corresponding to the given partition_path exists.
        If the folder exists and is considered complete (e.g., a file "results.pkl" exists), 
        reads and returns the results and a flag indicating completion as True.
        If the folder exists but is incomplete (assumed to be the last generated folder),
        returns None and a flag indicating that re-initialization is needed (False).
        If the folder does not exist, returns (None, False).

        Parameters
        ----------
        partition_path : str
            The output folder path for a specific supercell.

        Returns
        -------
        Tuple[Optional[Any], bool]
            A tuple where the first element is the loaded results (or None) and the second 
            is a boolean flag indicating whether the folder is complete.
        """
        partition_path = f'supercell_{sc_dim[0]}_{sc_dim[1]}_{sc_dim[2]}'
        full_path = os.path.join(output_path, partition_path)

        if os.path.exists(full_path):
            # Check if the folder contains a results file (assumed indicator of completeness)
            results_file = os.path.join(full_path, "config.xyz")
            template_file = os.path.join(full_path, "generation", "config.xyz")
            if os.path.exists(results_file):

                try:
                    partition_dataset = Partition()
                    partition_dataset.read_files(
                        file_location=results_file,
                        source='xyz',
                        verbose=True
                    )
                except Exception as e:
                    self.logger.info(f"Error detected at {full_path}. Error while reading {results_file}")
                    return None, None, False, 0

                partition_template = Partition()
                try:
                    partition_template.read_files(
                        file_location=template_file,
                        source='xyz',
                        verbose=True
                    )
                except Exception as e:
                    self.logger.info(f"Warning detected at {full_path}. Error while reading {template_file}")

                self.logger.info(f"Found complete folder at {full_path}. Reading results.")
                return partition_dataset, partition_template, True, 0

            else:
                try:
                    partition_dataset = Partition()
                    list_generation_dir = os.listdir( os.path.join(full_path, 'generation'))
                    for element in list_generation_dir:
                        results_file = os.path.join(full_path, 'generation', element, "config.xyz")
                        if os.path.exists(results_file) and element.startswith("gen"):
                            partition_dataset.read_files(
                                file_location=results_file,
                                source='xyz',
                                verbose=True
                            )
                    self.logger.info(f"Incomplete folder detected at {full_path}. Reinitializing explorer.")
                    return partition_dataset, None, False, len(list_generation_dir)

                except:
                    self.logger.info(f"Error detected at {full_path}.")
                    return None, None, False, 0

        else:
            return None, None, False, 0

    def run_all_supercells(self):
        r"""
        Execute evolutionary exploration for each supercell dimension and collect results.

        Let 
        \[
            S = \{\,\mathbf{s}_1, \mathbf{s}_2, \dots, \mathbf{s}_m\},
            \quad \mathbf{s}_i = (a_i, b_i, c_i)
        \]
        be the list of supercell dimensions. We construct a mapping
        \(\mathcal{R}: S \to \texttt{Partition}\) by performing, for each \(\mathbf{s}\in S\):

        1. **Dimension validation**  
           Ensure \(\mathbf{s}\in\mathbb{Z}^3\) and \(\|\mathbf{s}\|=3\).  
           Raises `ValueError` if invalid.

        2. **Restart logic**  
           If `self.restart=True`, attempt to locate an existing output folder
           \(P(\mathbf{s})\).  
           - If a complete results file exists, load \(\mathrm{Partition}\) and set
             \(\mathcal{R}(\mathbf{s})\) immediately.  
           - If incomplete, record `restart_dataset` and `restart_template` for re-initialization.

        3. **Best‐candidate preloading**  
           Define the candidate set
           \[
             C(\mathbf{s}) = \{\mathbf{s}'\in \mathrm{dom}(\mathcal{R})
                               \mid \mathbf{s} \bmod \mathbf{s}' = (0,0,0)\}.
           \]
           Select
           \[
             \mathbf{s}^* = \arg\max_{\mathbf{s}'\in C(\mathbf{s})}
                             \bigl(a'\,b'\,c'\bigr),
           \]
           where \(\mathrm{vol}(\mathbf{s}')=a'\,b'\,c'\).  If \(\mathbf{s}^*\) exists,
           its partition data will be deep‐copied and up‐scaled by
           \(\mathbf{s}/\mathbf{s}^*\) via 
           `AtomPositionManager.generate_supercell`.

        4. **Parameter composition**  
           Build \(\mathrm{params}_{\mathbf{s}}\) by copying `self.params_base` and:
           - Overriding `dataset_path`, `template_path`, and `output_path` to
             subdirectory `"supercell_{a}_{b}_{c}"`.  
           - Injecting any `params_supercell[key][i]` corresponding to index \(i\) for \(\mathbf{s}_i\).

        5. **Explorer instantiation**  
           \[
             E_{\mathbf{s}} = \mathrm{EvolutionaryStructureExplorer}
                              \bigl(\mathrm{params}_{\mathbf{s}},\,\mathrm{debug}\bigr).
           \]
           If a best candidate \(\mathbf{s}^*\) was found, preload its
           container lists into
           `E_{\mathbf{s}}._containers_preload['dataset']` and
           `...['template']`.

        6. **Run exploration**  
           Execute
           \[
             D_{\mathbf{s}} = E_{\mathbf{s}}.\mathrm{run}(\mathrm{debug}),
           \]
           obtaining the final dataset partition for supercell \(\mathbf{s}\).

        7. **Result storage**  
           Store:
           \[
             \mathcal{R}(\mathbf{s}) = D_{\mathbf{s}},\quad
             \mathrm{templates}[\mathbf{s}] = E_{\mathbf{s}}._partitions['template'],\quad
             \mathrm{instances}[\mathbf{s}] = E_{\mathbf{s}}.
           \]

        After processing all \(\mathbf{s}\in S\), return the mapping \(\mathcal{R}\).

        Returns
        -------
        Dict[Tuple[int, int, int], Partition]
            Mapping from each supercell dimension tuple to its resulting `Partition`.

        Raises
        ------
        ValueError
            If any supercell tuple is not of length 3 or contains non‐integer entries.
        AssertionError
            If `params_supercell` lists do not match the length of `supercell_list`.
        RuntimeError
            If an explorer instance fails catastrophically and cannot complete.
        """
        total_supercells = len(self.supercell_list)
        self.logger.info(f"Starting evolutionary exploration for {total_supercells} supercell configuration(s).")
        
        for sc_dim_i, sc_dim in enumerate(self.supercell_list):
            self.logger.info(f"Processing supercell {sc_dim_i + 1}/{total_supercells}: Dimension {sc_dim}")

            # Validate that each supercell dimension is a 3-tuple.
            if not isinstance(sc_dim, tuple) or len(sc_dim) != 3:
                error_message = f"Invalid supercell dimensions: {sc_dim}. Expected a tuple of 3 integers."
                self.logger.error(error_message)
                raise ValueError(error_message)

            # Check if the partition folder already exists and, if so, read its results.
            if self.restart:
                restart_dataset, restart_template, is_complete, last_generation = self.read_supercell(self.output_path, sc_dim)

                if restart_dataset is not None and is_complete:
                    self.logger.info(f"Results for supercell {sc_dim} already exist. Skipping exploration for this dimension.")
                    self.results[sc_dim] = restart_dataset
                    self.templates[sc_dim] = restart_template
                    continue

                elif restart_dataset is not None:
                    partition_path = f'supercell_{sc_dim[0]}_{sc_dim[1]}_{sc_dim[2]}'
                    self.logger.info(f"Reinitializing exploration for incomplete folder at {partition_path}.")

                self.restart = False
            else:
                is_complete, last_generation = False, 0
                restart_dataset, restart_template = None, None

            # Determine the best candidate from previously computed results.
            best_candidate = None
            best_candidate_size = 0
            self.logger.info("Searching for a compatible candidate among previous results.")
            # Iterate through available candidate dimensions in self.results to find a suitable candidate.
            for candidate_dim in self.results.keys():
                if (sc_dim[0] % candidate_dim[0] == 0 and
                    sc_dim[1] % candidate_dim[1] == 0 and
                    sc_dim[2] % candidate_dim[2] == 0):
                    candidate_size = candidate_dim[0] * candidate_dim[1] * candidate_dim[2]
                    if candidate_size > best_candidate_size:
                        best_candidate = candidate_dim
                        best_candidate_size = candidate_size

            if best_candidate is not None:
                self.logger.info(f"Candidate found: {best_candidate} as a submultiple of {sc_dim} with volume {best_candidate_size}.")
            else:
                self.logger.info("No compatible candidate found for preloading data.")

            # Construct a partition identifier incorporating the supercell dimensions.
            partition_path = f'supercell_{sc_dim[0]}_{sc_dim[1]}_{sc_dim[2]}'
            self.logger.info(f"Output partition set to: {partition_path}.")
            # Note: partition_path is defined here and can be used later for saving outputs.

            # Instantiate a new evolutionary explorer instance for the current supercell.
            if sc_dim_i > 0:
                self.params_base['dataset_path'] = None
                self.params_base['output_path'] = None
            params_updated = self.params_base.copy()

            # Set output path: ensure outputs are stored in a subdirectory specific to the supercell.
            if isinstance(self.output_path, str):
                params_updated['output_path'] = os.path.join(self.output_path, partition_path)
            else:
                params_updated['output_path'] = partition_path

            # Set output path: ensure sync_params are stored in a subdirectory specific to the supercell.
            if isinstance(params_updated.get('sync_params', None), dict):
                if isinstance(params_updated['sync_params'].get('shared_dir', None), str):
                    if self.sync_params is None:
                        self.sync_params = copy.copy(params_updated['sync_params']['shared_dir'])
                    params_updated['sync_params']['shared_dir'] = os.path.join(self.sync_params, partition_path)

            # Update any supercell-specific parameters.
            for key, value_list in self.params_supercell.items():
                params_updated[key] = value_list[sc_dim_i]
                self.logger.info(f"Parameter '{key}' set to {value_list[sc_dim_i]} for current supercell.")

            # Instantiate the evolutionary explorer.
            self.logger.info("Instantiating EvolutionaryStructureExplorer instance.")
            explorer = EvolutionaryStructureExplorer(params=params_updated, debug=self.debug)
            explorer.logger.info(f"Starting exploration for supercell dimension: {sc_dim}")

            explorer._containers_preload['dataset'] = []
            explorer._containers_preload['template'] = []

            if restart_dataset is not None:
                explorer._containers_preload['dataset'] += restart_dataset.containers

            if restart_template is not None:
                explorer._containers_preload['template'] += restart_template.containers

            # If a best candidate is found, attempt to transfer its data.
            if best_candidate is not None:
                explorer.logger.info(
                    f"Found previously explored supercell {best_candidate} as a submultiple of {sc_dim}. "
                    "Transferring candidate structure data."
                )
                #try:
                # Deep copy the candidate results to avoid unintended side effects.
                best_candidate_results = copy.deepcopy(self.results[best_candidate])
                # For every container in the candidate's results, update atom positions to reflect the new supercell.
                for container in best_candidate_results.containers:
                    container.AtomPositionManager.generate_supercell( repeat= tuple( int(sc/bc+.1) for sc, bc in zip(sc_dim, best_candidate)) )
                # Preload the dataset for the explorer with the updated candidate containers.
                explorer._containers_preload['dataset'] += best_candidate_results.containers 

                # Deep copy the candidate results to avoid unintended side effects.
                best_template_instances = copy.deepcopy(self.templates[best_candidate])
                # For every container in the candidate's results, update atom positions to reflect the new supercell.
                for container in best_template_instances.containers:
                    container.AtomPositionManager.generate_supercell( repeat= tuple( int(sc/bc+.1) for sc, bc in zip(sc_dim, best_candidate)) )
                # Preload the dataset for the explorer with the updated candidate containers.
                explorer._containers_preload['template'] += best_template_instances.containers

                #except Exception as e:
                #    explorer.logger.error(f"Error transferring candidate results for candidate {best_candidate}: {e}")
            else:
                explorer.logger.info("No compatible candidate found; starting exploration without preloaded data.")

            # Run the evolutionary exploration.
            try:
                self.logger.info(f"Running evolutionary exploration for supercell | iteration {sc_dim_i}/{len(self.supercell_list)} | dimension {sc_dim} |")
                explorer.set_initial_generation( last_generation )
                result_partition = explorer.run(debug=self.debug)
                self.logger.info(f"Exploration completed successfully for supercell {sc_dim}.")
            except Exception as e:
                explorer.logger.error(f"Exploration failed for supercell {sc_dim}: {e}", exc_info=True)
                continue

            # Save the current explorer instance and its result.
            self.explorer_instances[sc_dim] = explorer
            self.results[sc_dim] = result_partition
            self.templates[sc_dim] = explorer._partitions['template']

            self.logger.info(f"Results for supercell {sc_dim} stored successfully. ( {result_partition.N} new strucutres )")

        self.logger.info("Completed exploration for all supercells.")
        return self.results

    run = run_all_supercells










