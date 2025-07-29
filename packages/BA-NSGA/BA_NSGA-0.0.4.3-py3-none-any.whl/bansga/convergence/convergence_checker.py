import numpy as np
import time

class ConvergenceChecker:
    r"""
    A convergence monitor for generational optimization that tracks both objective-value improvements
    and, optionally, information-driven novelty.

    Convergence criterion
    ---------------------
    Let :math:`M` be the ``stall_threshold``. For each generation :math:`t`, define

    .. math::
       I_{\mathrm{obj}}(t) =
         \begin{cases}
           1, & \text{if any new objective value } o_t(i)
                 \text{ strictly improves the previously recorded best for feature } f_i, \\
           0, & \text{otherwise.}
         \end{cases}

    If :paramref:`information_driven` is ``True``, define similarly

    .. math::
       I_{\mathrm{info}}(t) =
         \begin{cases}
           1, & \text{if information novelty has improved at generation } t, \\
           0, & \text{otherwise.}
         \end{cases}

    Convergence is declared when (for ``convergence_type=='and'``)

    .. math::
       \underbrace{\sum_{k=t-M+1}^t \bigl(1 - I_{\mathrm{obj}}(k)\bigr)}_{\ge M}
       \;\wedge\;
       \underbrace{\sum_{k=t-M+1}^t \bigl(1 - I_{\mathrm{info}}(k)\bigr)}_{\ge M}

    or (for ``convergence_type=='or'``) when either of the above sums alone satisfies

    .. math::
       \sum_{k=t-M+1}^t \bigl(1 - I_{\mathrm{obj or info}}(k)\bigr) \;\ge\; M.

    Parameters
    ----------
    logger : logging.Logger or None
        Optional logger for informational messages.
    detailed_record : bool
        If True, stores the full per-generation history of objective vectors.
    stall_threshold : int
        Number of consecutive generations without improvement before declaring convergence.
    information_driven : bool
        If True, uses a parallel stall counter for information-driven novelty.

    Attributes
    ----------
    _objectives_for_features_history : dict[tuple, dict]
        Maps each feature-tuple to a dict containing:
        - ``"best_objective"`` (np.ndarray): the best objective seen so far.
        - ``"history"`` (dict[int, list[np.ndarray]]): per-generation records if ``detailed_record``.
    _no_improvement_count_objectives : int
        Number of consecutive generations with no objective improvement.
    _no_improvement_count_information : int
        Number of consecutive generations with no information improvement.
    _convergence_type : str
        Logical operator for combining criteria; either ``'and'`` or ``'or'``.
    """
    def __init__(self, logger=None, detailed_record=False, stall_threshold:int=5, information_driven:bool=True):
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
        self._no_improvement_count_objectives = 0
        self._no_improvement_count_information = 0
        self._no_improvement_count = 0

        self._stall_threshold = stall_threshold
        self._information_driven = information_driven
        self._convergence_type = 'and'

    def _record_objective_for_feature(self, feature_key, generation, current_obj):
        """
        Update the per‐feature best‐objective record and optionally the full history.

        This routine ensures that for each feature combination:
        \[
          b_{t}(f) = \min\bigl(b_{t-1}(f), \, o_t(f)\bigr)
        \]
        and if `detailed_record` is enabled,
        appends \(o_t(f)\) into the history at index `generation`.

        :param feature_key: Immutable tuple representing the feature vector \(f\).
        :type feature_key: tuple
        :param generation: Current generation index \(t\).
        :type generation: int
        :param current_obj: Objective vector \(o_t(f)\) for the structure.
        :type current_obj: np.ndarray
        :returns: None
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

    def check_convergence(self, generation, objectives, features, debug=False, information_novelty_has_improved:bool=False, generation_start=None, time_log=None):
        r"""
        Check whether the optimization run has converged at generation :math:`t`.

        The convergence monitor uses “stall counters” on both objective improvements
        and, if enabled, information-driven novelty.  Let
        :math:`M = \texttt{stall_threshold}`.  Define the indicator functions:

        .. math::
           I_{\mathrm{obj}}(t) =
             \begin{cases}
               1, & \exists\,i:\;o_t(i) < b_{t-1}\bigl(f_i\bigr),\\
               0, & \text{otherwise,}
             \end{cases}

        and, if :paramref:`information_driven` is True,

        .. math::
           I_{\mathrm{info}}(t) =
             \begin{cases}
               1, & \text{if information novelty improved at } t,\\
               0, & \text{otherwise.}
             \end{cases}

        We then maintain rolling stall counts over the window
        :math:`\{t-M+1,\dots,t\}`:

        .. math::
           S_{\mathrm{obj}}(t) = \sum_{k=t-M+1}^t \bigl(1 - I_{\mathrm{obj}}(k)\bigr),
           \quad
           S_{\mathrm{info}}(t) = \sum_{k=t-M+1}^t \bigl(1 - I_{\mathrm{info}}(k)\bigr).

        Convergence is declared when

        - **AND mode** (:math:`\texttt{convergence_type}='and'`):

          .. math::
             S_{\mathrm{obj}}(t) \;\ge\; M
             \quad\wedge\quad
             S_{\mathrm{info}}(t) \;\ge\; M,

        - **OR mode** (:math:`\texttt{convergence_type}='or'`):

          .. math::
             S_{\mathrm{obj}}(t) \;\ge\; M
             \quad\lor\quad
             S_{\mathrm{info}}(t) \;\ge\; M.

        The method proceeds in these steps:

        1. **Array normalization**  
           Ensure `objectives` and `features` are at least 1D; reshape to 2D
           if needed:
           .. code:: python

               objectives_arr = np.atleast_1d(objectives).reshape(-1, k)
               features_arr   = np.atleast_1d(features).reshape(-1, d)

        2. **Improvement detection**  
           For each structure index :math:`i` in :math:`0\le i<n`:
           - Let :math:`f =` tuple of `features_arr[i]`.  
           - If :math:`f` was seen before, compare :math:`o_t(i)` to the stored best
             :math:`b_{t-1}(f)`.  Otherwise treat as improvement.  
           - Record new best via ``_record_objective_for_feature``.

        3. **Stall‐counter update**  
           - Increment :math:`\text{stall_obj}` by 1 if no objective improvement,
             else reset to 0.  
           - If `information_driven`, similarly update
             :math:`\text{stall_info}` based on `information_novelty_has_improved`.
           - Clip each counter to the range :math:`[0,\,M]`.

        4. **Convergence decision**  
           Apply the chosen logical operator (`and`/`or`) to
           :math:`\bigl[\text{stall_obj}\ge M,\;\text{stall_info}\ge M\bigr]`.

        5. **Logging & timing**  
           - If `generation_start` is provided, compute elapsed time
             :math:`\Delta = \text{time.time}() - \text{generation_start}`.
           - If `time_log` dict is given, store under key `'generation'`.  
           - If `logger` is set and `debug` is True, emit detailed info.

        Returns
        -------
        Dict[str, object]
            - **'converge'** (`bool`): True if convergence criterion met.  
            - **'improvement_found'** (`bool`): True if any objective improved.  
            - **'stall_count_objetive'** (`int`): Current objective stall counter.  
            - **'stall_count_information'** (`int`): Current information stall counter.

        Raises
        ------
        ValueError
            If feature and objective array lengths do not match.
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


        # Update objective stall count
        self._no_improvement_count_objectives = (
            0 if improvement_found 
            else self._no_improvement_count_objectives + 1
        )
        self._no_improvement_count_objectives = min( self._no_improvement_count_objectives, self._stall_threshold )

        # If using information-driven convergence, update info stall count
        if self._information_driven:
            self._no_improvement_count_information = (
                0 if not information_novelty_has_improved
                else self._no_improvement_count_information + 1
            )
            self._no_improvement_count_information = min( self._no_improvement_count_information, self._stall_threshold )

        # Determine convergence
        conv_type = self._convergence_type.lower()
        if self._information_driven:
            # Pair counts for [objectives, information]
            counts = (
                self._no_improvement_count_objectives,
                self._no_improvement_count_information
            )
            # Map 'and' → all, 'or' → any; default to any if unrecognized
            op = {'and': all, 'or': any}.get(conv_type, any)
            converge = op(count >= self._stall_threshold for count in counts)
        else:
            converge = self._no_improvement_count_objectives >= self._stall_threshold
            counts = self._no_improvement_count_objectives
            
        self._no_improvement_count = np.min( counts ) 

        elapsed_time = time.time() - generation_start if generation_start else 0.0
        if time_log is not None:
            time_log['generation'] = elapsed_time

        if self.logger:
            if self._information_driven:
                self.logger.info(f"[Gen={generation}] improvement={improvement_found}, stall_count={self._no_improvement_count_objectives}/{self._stall_threshold} (obj) {self._no_improvement_count_information}/{self._stall_threshold} (info), converged={converge}, time={elapsed_time:.2f}s")
            else:
                self.logger.info(f"[Gen={generation}] improvement={improvement_found}, stall_count={self._no_improvement_count_objectives}/{self._stall_threshold}, converged={converge}, time={elapsed_time:.2f}s")

        return {
            'converge': converge,
            'improvement_found': improvement_found,
            'stall_count_objetive': self._no_improvement_count_objectives,
            'stall_count_information': self._no_improvement_count_information,
        }
