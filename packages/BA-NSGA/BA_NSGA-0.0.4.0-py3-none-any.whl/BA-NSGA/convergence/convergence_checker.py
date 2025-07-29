import numpy as np
import time

class ConvergenceChecker:
    def __init__(self, logger=None, detailed_record=False, stall_threshold:int=5):
        """
        Initializes the ConvergenceChecker with optional logging and a flag to maintain detailed records.

        Parameters
        ----------
        logger : logging.Logger, optional
            A logger instance to record events.
        detailed_record : bool, optional
            If True, a detailed history of objective values is stored.
        """
        self.logger = logger
        self.detailed_record = detailed_record
        self._objectives_for_features_history = {}
        self._no_improvement_count = 0
        self._stall_threshold = stall_threshold

    def _record_objective_for_feature(self, feature_key, generation, current_obj):
        """
        Records and updates the objective history for a given feature combination.

        Parameters
        ----------
        feature_key : tuple
            A hashable tuple representing the structure's features.
        generation : int
            The current generation index.
        current_obj : np.ndarray
            The objective vector for the structure.
        """
        if feature_key not in self._objectives_for_features_history:
            self._objectives_for_features_history[feature_key] = {
                "best_objective": current_obj.copy(),
            }
        record = self._objectives_for_features_history[feature_key]
        if self.detailed_record:
            if 'history' not in record:
                record['history'] = {}
            if generation not in record['history']:
                record['history'][generation] = []
            record['history'][generation].append(current_obj)
        prev_best = record["best_objective"]
        if np.any(current_obj < prev_best):
            record["best_objective"] = np.minimum(prev_best, current_obj)

    def check_convergence(self, generation, objectives, features, debug=False, generation_start=None, time_log=None):
        """
        Checks convergence based on objective improvements over consecutive generations.
        
        The rule is:
          "If for M (stall_threshold) consecutive generations, no structure has a strictly
           better (lower) objective for any previously seen combination of features, 
           the search is considered converged."
        
        Parameters
        ----------
        generation : int
            The current generation index.
        objectives : np.ndarray
            Array of objective values, either shape (n_structures,) or (n_structures, k).
        features : np.ndarray
            Array of feature values, either shape (n_structures,) or (n_structures, d).
        debug : bool, optional
            If True, enables additional logging.
        generation_start : float, optional
            The start time of the current generation (used to compute elapsed time).
        time_log : dict, optional
            A dictionary to log timing information.
        
        Returns
        -------
        dict
            A dictionary with the following keys:
                - 'converge': bool, True if convergence is reached.
                - 'improvement_found': bool, True if any improvement was detected in the current generation.
                - 'stall_count': int, the current count of consecutive generations without improvement.
        """
        if self.logger:
            self.logger.info("Checking stall-based convergence with feature-objective mapping...")

        # Ensure objectives and features are at least 1D arrays
        objectives_arr = np.atleast_1d(objectives)
        features_arr = np.atleast_1d(features)

        n_structures = objectives_arr.shape[0]
        if features_arr.shape[0] != n_structures:
            if self.logger:
                self.logger.warning("Mismatch in number of structures between objectives and features!")

        # Reshape arrays if necessary
        if objectives_arr.ndim == 1:
            objectives_arr = objectives_arr.reshape(-1, 1)
        if features_arr.ndim == 1:
            features_arr = features_arr.reshape(-1, 1)

        improvement_found = False

        for i in range(n_structures):
            feature_key = tuple(features_arr[i, :])
            current_obj = objectives_arr[i, :]
            if feature_key in self._objectives_for_features_history:
                prev_best = self._objectives_for_features_history[feature_key]["best_objective"]
                if np.any(current_obj < prev_best):
                    improvement_found = True
            else:
                improvement_found = True
            self._record_objective_for_feature(feature_key, generation, current_obj)

        if improvement_found:
            self._no_improvement_count = 0
        else:
            self._no_improvement_count += 1

        converge = (self._no_improvement_count >= self._stall_threshold)
        elapsed_time = time.time() - generation_start if generation_start else 0.0
        if time_log is not None:
            time_log.setdefault('generation', []).append(elapsed_time)
        if self.logger:
            self.logger.info(f"[Gen={generation}] improvement={improvement_found}, stall_count={self._no_improvement_count}/{self._stall_threshold}, converged={converge}, time={elapsed_time:.2f}s")

        return {
            'converge': converge,
            'improvement_found': improvement_found,
            'stall_count': self._no_improvement_count
        }
