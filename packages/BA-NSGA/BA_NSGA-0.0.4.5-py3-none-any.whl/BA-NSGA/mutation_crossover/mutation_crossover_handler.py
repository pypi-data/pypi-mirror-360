# mutation_crossover_handler.py
import copy
import random
import numpy as np
from typing import List, Any, Optional, Union
import time

from ..utils.helper_functions import combined_rate, solver_integer_local

class MutationCrossoverHandler:
    """
    A class encapsulating the mutation and crossover workflow, 
    along with associated utility methods.
    """

    def __init__(self, mutation_funcs=None, crossover_funcs=None, lineage_tracker=None, logger=None, mutation_rate_params=None, debug:bool=False):
        """
        Parameters
        ----------
        lineage_tracker : object
            Object responsible for tracking lineages (assign_lineage_info, etc.).
        logger : object
            Logging object with at least .info(...) available.
        mutation_rate_params : dict, optional
            Parameters controlling the mutation rate, by default None.
        debug : bool, optional
            If True, enables debug prints, by default False.
        """
        self.lineage_tracker = lineage_tracker
        self.logger = logger
        self.mutation_rate_params = mutation_rate_params or {}
        self.crossover_rate = 1
        self.debug = debug

        self.mutation_funcs = mutation_funcs or []
        self.crossover_funcs = crossover_funcs or []

        # Track usage and success/failure of each mutation function
        self._mutation_attempt_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_fails_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_success_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_unsuccess_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_hashcolition_counts = np.zeros(len(self.mutation_funcs), dtype=int)

        self._max_prob = self.mutation_rate_params['max_prob']
        self._min_prob = self.mutation_rate_params['min_prob']
        self._use_magnitude_scaling = self.mutation_rate_params['use_magnitude_scaling']
        self._alpha = self.mutation_rate_params['alpha']

        # Track usage and success/failure of each mutation function
        self._crossover_attempt_counts = np.zeros(len(self.crossover_funcs), dtype=int)
        self._crossover_fails_counts = np.zeros(len(self.crossover_funcs), dtype=int)
        self._crossover_success_counts = np.zeros(len(self.crossover_funcs), dtype=int)
        self._crossover_unsuccess_counts = np.zeros(len(self.crossover_funcs), dtype=int)

        # Initialize uniform probabilities for each mutation function
        if len(self.mutation_funcs) > 0:
            self._mutation_probabilities = np.ones(len(self.mutation_funcs)) / len(self.mutation_funcs)
        else:
            self._mutation_probabilities = []

        # Initialize uniform probabilities for each mutation function
        if len(self.crossover_funcs) > 0:
            self._crossover_probabilities = np.ones(len(self.crossover_funcs)) / len(self.crossover_funcs)
        else:
            self._crossover_probabilities = []

        self._mutation_feature_effects = None

    @property
    def mutation_feature_effects(self):
        """Gets the _mutation_feature_effects."""
        return self._mutation_feature_effects

    def apply_mutation_and_crossover(self, structures, generation, objectives):
        """
        Applies mutation and crossover operations to a list of structures, 
        adjusting mutation usage probabilities based on post-mutation objective values.

        Parameters
        ----------
        structures : list
            The structures to be mutated and crossed.
        generation : int
            Current generation index.
        objectives : np.ndarray
            Multi-objective array of shape (len(structures), n_objectives) for each structure.

        Returns
        -------
        crossed_structures : list
            Final list of structures after mutation and crossover.
        mutation_rate_array : np.ndarray
            Number of mutations applied to each structure (same length as 'structures').
        """

        # 1) Determine how many mutations to apply per structure
        mutation_rate_array = combined_rate(generation, structures, objectives, params=self.mutation_rate_params)
        if self.debug:
            self.logger.info(f"[DEBUG] Mutation rate array: {np.min(mutation_rate_array)} -> {np.max(mutation_rate_array)}")

        # 2) Mutation step (with objective-based probability adjustment)
        mutated_structures = self._mutate(structures, mutation_rate_array, objectives, generation)

        # 3) Crossover step
        crossover_pairs = self._generate_crossover_indices(structures, probability=0.2)
        crossed_structures = self._cross_over(structures, crossover_pairs, generation)

        self.logger.info("Mutation and crossover completed.")

        return mutated_structures, crossed_structures, mutation_rate_array

    def _mutate(self, structures, mutation_count_array, objectives, generation):
        """
        Applies a certain number of mutations to each structure, choosing a mutation function
        based on current mutation probabilities. If the structure's objective gets worse, 
        that mutation function's probability is decreased (and vice-versa).

        Parameters
        ----------
        structures : list
            Original set of structures.
        mutation_count_array : np.ndarray
            Number of times each structure should be mutated.
        objectives : np.ndarray
            The objective array for each original structure.
        generation : int
            Current generation index, used for lineage tracking.

        Returns
        -------
        mutated_structures : list
            The newly mutated structures (same length as 'structures').
        """
        mutated_structures = []

        for idx, parent in enumerate(structures):
            # We copy the structure so as not to overwrite the parent
            new_structure = copy.deepcopy(parent)
            new_structure.magnetization = None
            new_structure.charge = None

            # Parent objective (could be multi-objective). We'll just take the sum as an example
            obj_before = np.sum(objectives[idx]) if objectives is not None else 0.0

            # Apply the requested number of mutations
            num_mutations = int(mutation_count_array[idx])
            mutation_list = []

            for _ in range(num_mutations):
                if len(self.mutation_funcs) == 0:
                    # No mutation functions are defined
                    break

                # Choose which mutation function to apply, weighted by _mutation_probabilities
                chosen_mut_idx = np.random.choice(len(self.mutation_funcs), p=self._mutation_probabilities)
                chosen_mutation_func = self.mutation_funcs[chosen_mut_idx]

                # Attempt the mutation
                self._mutation_attempt_counts[chosen_mut_idx] += 1
                try:    
                    candidate_structure = chosen_mutation_func(new_structure)
                    mutation_list.append(chosen_mut_idx)
                except Exception as e:
                    self._mutation_fails_counts[chosen_mut_idx] += 1
                    candidate_structure = None

                    if self.debug:
                        import traceback
                        print("[DEBUG] An error occurred:", e)
                        traceback.print_exc()
    
                # Update 'new_structure' to the mutated version
                if candidate_structure is None:
                    continue
                else:
                    new_structure = candidate_structure

            if self.debug:
                self.logger.info(
                    f"[DEBUG] Mutation ; Parent {parent.AtomPositionManager.metadata["id"]} Mutation list ({num_mutations}) {mutation_list} "
                )
            if new_structure is None:
                continue           

            # Store lineage information
            # Record who was mutated and which mutation was applied
            lineage_parents = [parent.AtomPositionManager.metadata["id"]]
            self.lineage_tracker.assign_lineage_info(new_structure, generation, lineage_parents, "mutation", mutation_list=mutation_list)

            mutated_structures.append(new_structure)

        return mutated_structures

    def _adjust_mutation_probabilities(
        self,
        structures: Optional[List[Any]] = None,
        objectives: Optional[List[Union[float, np.ndarray]]] = None,
        features: Any = None,  # Unused parameter; reserved for future use
    ) -> np.ndarray:
        """
        Adjust mutation probabilities based on the difference in objectives between structures and their parents.

        This version includes:
            1. Consistency with the docstring: if the child is better (delta < 0), increase mutation probabilities.
            2. Bounding options (min_prob / max_prob).
            3. Optional magnitude scaling of alpha by |delta| to reward bigger improvements more strongly.

        Parameters:
            structures (List[Any]): A list of structure objects. Each structure must have an attribute 
                'AtomPositionManager.metadata', which is a dictionary containing at least:
                    - "generation": An integer indicating the generation of the structure.
                    - "id": A unique identifier for the structure.
                    - "parents": A list where the first element is the identifier of the parent structure.
                    - "mutation_list": A list of mutation operation keys.
                    - "operation": A string indicating the type of operation (e.g., "mutation").
            objectives (List[Union[float, np.ndarray]]): A list of objective values corresponding to each structure.
                A smaller objective value is considered better.
            features: Unused parameter (reserved for future extensions).
            alpha (float): The base adjustment factor used for scaling mutation probabilities (default is 0.01).
            use_magnitude_scaling (bool): If True, multiplies alpha by abs(delta / parent_obj).
                For larger improvements, we boost probabilities more.
            min_prob (float): If not None, ensures no mutation probability falls below this threshold.
            max_prob (float): If not None, ensures no mutation probability exceeds this threshold.

        Returns:
            np.ndarray: The updated and normalized mutation probabilities.

        Raises:
            ValueError: If the structures list is empty or if its length does not match the length of the objectives list.
        """

        # Validate input parameters
        if not structures:
            raise ValueError("The structures list is empty.")
        if objectives is None or len(structures) != len(objectives):
            raise ValueError("The number of structures must match the number of objectives.")

        # Retrieve the generation number of the most recent structure.
        last_gen = structures[-1].AtomPositionManager.metadata.get("generation", 0)

        if last_gen > 0:
            # Create a mapping from each structure's unique id to its corresponding objective value.
            objectives_dict = {
                s.AtomPositionManager.metadata["id"]: obj
                for s, obj in zip(structures, objectives)
            }

            # Iterate over structures in reverse (most recent first)
            for structure in reversed(structures):
                meta = structure.AtomPositionManager.metadata
                if meta.get("generation") == last_gen:
                    parents = meta.get("parents", [])
                    if not parents:
                        continue  # Skip if no parent

                    parent_id = parents[0]
                    current_obj = objectives_dict.get(meta["id"])
                    parent_obj = objectives_dict.get(parent_id, 0)
                    # Delta < 0 means the child is better (if minimizing the objective)
                    delta = current_obj - parent_obj

                    # Proceed only if the structure was generated via a mutation operation.
                    if meta.get("operation") == "mutation":
                        # Optionally log debug info
                        if self.debug:
                            if self.logger is not None:
                                self.logger.debug(meta)

                        # Possibly scale alpha by magnitude of the change (relative improvement/deterioration)
                        effective_alpha = self._alpha
                        if self._use_magnitude_scaling and abs(parent_obj).any() > 1e-12:
                            effective_alpha *= abs(delta / parent_obj)

                        #print(23112344132, effective_alpha, delta, self._alpha, abs(delta / parent_obj), parent_obj)
                        # reescale normalize needeed
                        for ea, d in zip(effective_alpha, delta):
                            # If delta < 0 => improvement => multiply probability by (1 + alpha).
                            # If delta >= 0 => no improvement => multiply probability by (1 - alpha).
                            # This follows the docstring's logic for "better is negative delta => increase probability."
                            if d < 0:
                                for mutation in meta.get("mutation_list", []):
                                    self._mutation_probabilities[mutation] *= (1.0 + ea)
                                    self._mutation_success_counts[mutation] += 1
                            else:
                                for mutation in meta.get("mutation_list", []):
                                    self._mutation_probabilities[mutation] *= (1.0 - ea)
                                    self._mutation_unsuccess_counts[mutation] += 1
                else:
                    # Assuming structures are ordered by generation, stop at an older generation
                    break

        # (Optional) Enforce min and max probability bounds if desired
        self._mutation_probabilities = np.maximum(self._mutation_probabilities, self._min_prob)
        self._mutation_probabilities = np.minimum(self._mutation_probabilities, self._max_prob)

        # Re-normalize the mutation probabilities so they sum to 1
        total_probability = np.sum(self._mutation_probabilities)
        if total_probability > 1e-12:
            self._mutation_probabilities /= total_probability

        # Log the updated mutation probabilities if debugging is enabled
        if self.debug and self.logger is not None:
            self.logger.info(f"[DEBUG] Updated mutation probabilities: {self._mutation_probabilities}")

        return self._mutation_probabilities

    def _generate_crossover_indices(self, population, probability):
        """
        Generates pairs of indices randomly, with at least one pair selected for crossover.

        Parameters
        ----------
        population : list
            List of structures in the current population.
        probability : float
            Probability of performing crossover for a chosen pair.

        Returns
        -------
        list of tuples
            Index pairs selected for crossover.
        """
        crossover_pairs = []
        indices = list(range(len(population)))

        while len(indices) > 1:
            i, j = random.sample(indices, 2)
            indices.remove(i)
            indices.remove(j)
            if random.random() < probability:
                crossover_pairs.append((i, j))

        # Ensure at least one crossover happens if possible
        if not crossover_pairs and len(population) > 1:
            i, j = random.sample(range(len(population)), 2)
            crossover_pairs.append((i, j))

        return crossover_pairs

    def _cross_over(self, containers, crossover_pairs, generation):
        """
        Perform crossover between pairs of containers. The chosen crossover function
        is assumed to be the first or random from self.crossover_funcs, but you can 
        adapt the logic to choose from multiple crossover functions (similar to 
        mutation probability approach).

        Parameters
        ----------
        containers : list
            A list of container objects (structures).
        crossover_pairs : list of tuples
            A list of index pairs (i, j) of containers to perform crossover.
        generation : int
            Current generation index, used for lineage tracking.

        Returns
        -------
        list
            The list of containers after performing crossover.
        """
        if not self.crossover_funcs:
            # If no crossover functions exist, do nothing
            return containers

        # Example: always use the first crossover function
        crossover_structures = []
    
        for (i, j) in crossover_pairs:

            childA, childB = containers[i], containers[j]

            for n in range(self.crossover_rate):

                if self.debug and self.logger is not None:
                    self.logger.info(f"[DEBUG] Performing crossover on indices {i} and {j}.")

                # Choose which mutation function to apply, weighted by _mutation_probabilities
                chosen_co_idx = np.random.choice(len(self.crossover_funcs), p=self._crossover_probabilities)
                chosen_crossover_func = self.crossover_funcs[chosen_co_idx]

                # Attempt the mutation
                self._crossover_attempt_counts[chosen_co_idx] += 1
                try:
                    childA_new, childB_new = chosen_crossover_func(childA, childB)
                except:
                    self._crossover_fails_counts[chosen_co_idx] += 1
                    childA_new, childB_new = None, None

                if childA_new is None or childB_new is None:
                    childA_new, childB_new = childA, childB



            if childA is None or childB is None:
                childA_new, childB_new = childA, childB

            else:
                # Assign lineage
                parents = [containers[i].AtomPositionManager.metadata["id"], containers[j].AtomPositionManager.metadata["id"]]
                self.lineage_tracker.assign_lineage_info(childA, generation, parents, "crossover")
                self.lineage_tracker.assign_lineage_info(childB, generation, parents, "crossover")
                crossover_structures += [childA, childB]

        return crossover_structures

    def hash_colition_penalization(self, container):
        """
        Applies a penalty to the mutation or crossover probabilities
        if 'container' triggered a hash collision (duplicate structure).

        Parameters
        ----------
        container : object
            The structure that caused a hash collision. We retrieve its
            metadata to see which operator produced it and penalize accordingly.
        """
        # Retrieve metadata for operation type, mutation list, etc.
        meta = container.AtomPositionManager.metadata
        operation = meta.get("operation", None)

        # We only apply penalties if the structure has a recorded operation
        if operation == "mutation":
            # The structure was generated by mutation
            mutation_indices = meta.get("mutation_list", [])
            for m_idx in mutation_indices:
                # Track how many collisions this mutation function caused
                self._mutation_hashcolition_counts[m_idx] += 1

                # Penalize by reducing the mutation probability by a factor (1 - alpha)
                # If you use an array for alpha, you might do self._alpha[m_idx]
                self._mutation_probabilities[m_idx] *= (1.0 - self._alpha)

            # Enforce minimum and maximum probability bounds
            self._mutation_probabilities = np.maximum(self._mutation_probabilities, self._min_prob)
            self._mutation_probabilities = np.minimum(self._mutation_probabilities, self._max_prob)

            # Re-normalize so probabilities sum to 1
            total_probability = np.sum(self._mutation_probabilities)
            if total_probability > 1e-12:
                self._mutation_probabilities /= total_probability

            if self.debug and self.logger is not None:
                self.logger.info(
                    f"[DEBUG] Penalized mutation probabilities due to hash collision: "
                    f"{self._mutation_probabilities}"
                )

        elif operation == "crossover":
            # The structure was generated by crossover
            # If you store which crossover function was used, penalize that index similarly
            # For example, let's assume there's a "crossover_idx" in metadata:
            co_idx = meta.get("crossover_idx", None)
            if co_idx is not None:
                # Track collision count
                self._crossover_fails_counts[co_idx] += 1

                # Penalize the crossover probability
                self._crossover_probabilities[co_idx] *= (1.0 - self._alpha)

                # Enforce min/max, then re-normalize
                self._crossover_probabilities = np.maximum(self._crossover_probabilities, self._min_prob)
                self._crossover_probabilities = np.minimum(self._crossover_probabilities, self._max_prob)

                total_probability = np.sum(self._crossover_probabilities)
                if total_probability > 1e-12:
                    self._crossover_probabilities /= total_probability

                if self.debug and self.logger is not None:
                    self.logger.info(
                        f"[DEBUG] Penalized crossover probabilities due to hash collision: "
                        f"{self._crossover_probabilities}"
                    )

    def evaluate_mutation_feature_change(
        self,
        structure,
        feature_func,
        n: int = 40,
        debug: bool = False
    ):
        """
        Randomly applies mutations `n` times to a copy of the given `structure`,
        tracking changes in a specified feature. Then uses the collected data
        (feature deltas and hot-encoded mutation choices) to estimate a
        per-mutation 'rate of change' in that feature via linear least squares.

        Parameters
        ----------
        structure : Any
            The original structure to mutate.
        feature_func : callable
            A function that computes the feature of interest, e.g.:
                feature_value = feature_func(some_structure)
        n : int, optional
            How many consecutive random mutations are applied to measure the change.
            Default is 5.
        debug : bool, optional
            If True, prints/logs debugging information.

        Returns
        -------
        List[dict]
            A list of dictionaries, each containing:
                {
                    "mutation_index": int,
                    "mutation_name": str,
                    "estimated_effect": float
                }
            where `estimated_effect` is the best-fit contribution of that mutation
            to the overall change in the feature, using a linear least-squares estimate.

        Notes
        -----
        - Each of the `n` iterations picks one mutation function at random (hot-encoded).
        - `data_delta_features[i]` stores the feature difference from the *original* (base)
          structure after the i-th mutation has been applied.
        - We solve `X @ w = y` in a least-squares sense, where X is the hot-encoded
          mutation matrix, y is the vector of observed feature deltas.
        - The final fitted weights `w` represent the approximate effect each mutation
          contributes to changing the feature (assuming linear additivity).
        """

        if not self.mutation_funcs:
            if debug and self.logger is not None:
                self.logger.info("[DEBUG] No mutation functions found.")
            return []

        # 1) Compute the base (original) feature value
        base_feature_value = feature_func(structure)
        num_features = base_feature_value.shape[0]
        prev_feature_value = base_feature_value

        # 2) Prepare arrays to store random-mutation data
        #    data_mutation: one-hot for which mutation was chosen on each iteration
        #    data_delta_features: feature delta from the base after each iteration
        num_mutations = len(self.mutation_funcs)
        data_mutation = np.zeros((n, num_mutations), dtype=float)
        data_delta_features = np.zeros( (n, num_features), dtype=float)

        # Work on a deep copy of the original so we don't overwrite it
        test_struct = copy.deepcopy(structure)

        # 3) Apply random mutations n times and record data
        for i in range(n):
            # Randomly choose a mutation from the list
            mut_choice = np.random.choice(num_mutations)
            chosen_mut_func = self.mutation_funcs[mut_choice]

            # Attempt the mutation
            mutated = chosen_mut_func(test_struct)
            if mutated is not None:
                test_struct = mutated  # If successful, update test_struct
            else:
                continue

            # Compute new feature after applying this mutation
            current_feature_value = feature_func(test_struct)

            # Record hot-encode for the chosen mutation
            data_mutation[i, mut_choice] = 1.0

            # Record the feature delta relative to the *original* structure
            data_delta_features[i] = current_feature_value - prev_feature_value
            prev_feature_value = current_feature_value

        # 4) Estimate the rate of change for each mutation using a linear fit
        #    data_delta_features = data_mutation @ effect_vector
        #    Solve for effect_vector in least squares sense
        X = data_mutation  # shape (n, num_mutations)
        y = data_delta_features  # shape (n,)

        # effect_vector will be the best-fit effect for each mutation
        effect_vector, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)

        # 5) (Optional) Save raw data and the fitted effects in the class for later use
        #    You could store them in some persistent lists/dicts as needed.
        if not hasattr(self, "_feature_data_records"):
            self._feature_data_records = []
        self._feature_data_records.append({
            "data_mutation": data_mutation,
            "data_delta_features": data_delta_features,
            "base_feature_value": base_feature_value,
            "effect_vector": effect_vector
        })

        self._mutation_feature_effects = effect_vector  # e.g. store the final array

        # 6) Build a more user-friendly result list
        results = []
        for i, eff in enumerate(effect_vector):
            mut_name = getattr(self.mutation_funcs[i], "__name__", f"mutation_func_{i}")
            results.append({
                "mutation_index": i,
                "mutation_name": mut_name,
                "estimated_effect": eff
            })

        if debug and self.logger is not None:
            self.logger.info(f"[DEBUG] Mutation effect estimates (LS fit): {results}")

        return results

    def foreigners_generation(
        self,
        structure,
        feature_func,
        design_points,
        tolerance: float = 0.01,
        max_iterations: int = 50,
        debug: bool = False
    ):
        """
        Generate new 'foreigner' structures aiming for specified feature values.

        Parameters
        ----------
        structure : Any
            The starting reference structure.
        feature_func : callable
            A function that computes the feature of interest: 
                feature_value = feature_func(some_structure)
        design_points : list of float
            List of desired target feature values.
        tolerance : float, optional
            If the final structure's feature is within +/- tolerance of the design point,
            we consider it a success. Default is 0.01.
        max_iterations : int, optional
            The maximum number of mutations to apply in the iterative approach
            before giving up. Default is 50.
        debug : bool, optional
            If True, prints/logging additional debug information.

        Returns
        -------
        structures : list
            A list of newly generated structures that meet the tolerance criterion.
        """

        # 1) Ensure we have an up-to-date 'mutation_feature_effects' vector
        #    If not, run `evaluate_mutation_feature_change` once.
        if getattr(self, "_mutation_feature_effects", None) is None:
            # Example: evaluate on some "template" structure from partitions, or just on the passed-in structure
            self.evaluate_mutation_feature_change(
                structure=structure,              # Or a "template" structure if you prefer
                feature_func=feature_func,
                n=50,
                debug=debug
            )

        # Quick references
        effect_vector = self.mutation_feature_effects
        mutation_funcs = self.mutation_funcs
        if effect_vector is None or len(effect_vector) == 0 or len(mutation_funcs) == 0:
            if debug and self.logger is not None:
                self.logger.info(
                    "[DEBUG] No effect vector or mutation funcs available; returning empty list."
                )
            return []

        # 2) For collecting the resulting structures
        structures = []

        # Statistics to keep track of
        n_success = 0
        n_fail = 0
        max_final_diff = 0.0
        max_iterations = 10
        max_iterations_count = 0

        # 3) For each desired design point, attempt to mutate toward that feature
        for dp_i, dp in enumerate(design_points):
            # Make a fresh copy of the reference structure
            test_struct = copy.deepcopy(structure)
            current_feature = feature_func(test_struct)

            # We'll track how close we are
            diff = dp - current_feature
            iteration_count = 0

            # Iteratively apply mutations until close enough or max_iterations exceeded
            while np.abs(diff).any() > tolerance and iteration_count < max_iterations:
                iteration_count += 1
                coefficient = solver_integer_local(effect_vector.T, diff)

                if np.sum(coefficient) > 0:
                    for c_idx, c in enumerate(coefficient):
                        
                        for c_i in range(c):

                            test_struct_mutated = mutation_funcs[c_idx](test_struct)

                            if test_struct_mutated is not None:
                                test_struct = test_struct_mutated  # If successful, update test_struct
                            else:
                                pass

                # Update our current feature and diff
                current_feature = feature_func(test_struct)
                diff = dp - current_feature

            max_iterations_count = max_iterations_count if iteration_count < max_iterations_count else iteration_count

            # After the loop, see how close we got
            max_final_diff = np.max( np.abs(diff) )

            if not np.abs(diff).any() > tolerance:
                # Accept this structure
                structures.append(test_struct)
                n_success += 1
            else:
                n_fail += 1

        # 4) Print or log summary if desired
        msg = (f"Foreigners generation complete. "
               f"Design points: {len(design_points)} | "
               f"Success: {n_success} | Fail: {n_fail} | "
               f"Max final difference: {max_final_diff:.1f}"
               f"Max iterations: {max_iterations_count:.1f}")

        if debug and self.logger is not None:
            self.logger.info(f"[DEBUG] {msg}")
        else:
            print(msg)

        return structures








