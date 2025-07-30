import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
from scipy.stats import norm
import random
import warnings
from typing import List, Optional, Callable

# ------------------------------------------------------------------
# Modified BayesianOptimization Class with Constraints
# ------------------------------------------------------------------
class BayesianOptimization:
    def __init__(self,
                 surrogate_models=None,
                 active_model_key='gp',
                 acquisition_func=None,
                 gp_alpha=1e-1,
                 weights=None,
                 bounds=None,
                 strategy:str='boltzmann',
                 n_candidates:int=1,
                 constraints: Optional[List] = None,
                 discrete_levels: Optional[List[np.ndarray]] = None, 
                 logic: str = "all",
                 temperature:float = None):
        """
        A Bayesian Optimization framework that supports:
        
        - Multiple surrogate models (default is a Gaussian Process Regressor).
        - Various acquisition functions (EI, UCB, exploration, exploitation, and a new Boltzmann-based approach).
        - Constraints on the feature space.
        - Discrete or continuous sampling of candidate points.
        
        Parameters
        ----------
        surrogate_models : dict, optional
            Dictionary of surrogate models, keyed by string. 
            Defaults to a simple GP if None is provided.
        active_model_key : str, optional
            Key to indicate which surrogate model to use for predictions/acquisitions.
            Default is 'gp'.
        acquisition_func : callable, optional
            A custom acquisition function. If None, defaults to `self.expected_improvement`.
        gp_alpha : float, optional
            Regularization alpha for the default Gaussian Process. Default is 1e-6.
        weights : np.ndarray, optional
            If doing multi-objective optimization, specify the weights for each objective
            to reduce it to a single objective.
        bounds : np.ndarray, optional
            An array of shape (n_features, 2) specifying the search space bounds. 
        strategy : str, optional
            One of "ei", "ucb", "exploration", "exploitation", or the new "boltzmann". 
            Default is "ei".
        n_candidates : int, optional
            Number of candidates to recommend on each call. Default is 1.
        constraints : List[FeatureConstraint], optional
            List of constraint objects. Each must have `is_valid(x)` returning bool.
        discrete_levels : List[np.ndarray], optional
            If not None, each entry in the list is a 1D array with possible discrete 
            values for the corresponding dimension.
        logic : str, optional
            Either "all" or "any", controlling whether we require all constraints 
            to be satisfied or at least one. Default is "all".
        temperature : float optional
        """
        valid_modes = ["all", "any"]
        if logic not in valid_modes:
            raise ValueError(
                f"Invalid logic='{logic}'. Must be one of {valid_modes}."
            )
        self.logic = logic

        # 1. If no surrogate models are provided, create a default Gaussian Process.
        if surrogate_models is None:
            kernel = (
                ConstantKernel(constant_value=1.0, constant_value_bounds=(1e-3, 1e3)) *
                Matern(nu=2.5, length_scale=50.0, length_scale_bounds=(1e-2, 1e3)) +
                WhiteKernel(noise_level=1e-6, noise_level_bounds=(1e-8, 1e-1))
            )
            gp_model = GaussianProcessRegressor( 
                alpha=gp_alpha, 
                kernel=kernel,
                normalize_y=True, 
                n_restarts_optimizer=5 
            )
            surrogate_models = {'gp': gp_model}
        self.surrogate_models = surrogate_models
        self.active_model_key = active_model_key
        
        # 2. Default acquisition = Expected Improvement if none is provided
        if acquisition_func is None:
            self.acquisition_func = self.expected_improvement
        else:
            self.acquisition_func = acquisition_func

        # 3. Multi-objective weighting
        self.weights = weights

        # 4. Internal storage
        self._trained_objective_values = None
        self.bounds = bounds
        self.strategy = strategy
        self.n_candidates = n_candidates

        # 5. Constraints support
        self.constraints = constraints if constraints else []
        
        # 6. Discrete levels for each dimension. If provided, will sample from these discrete sets.
        self.discrete_levels = discrete_levels
        self.temperature = temperature

    def _aggregate_objectives(self, objectives: np.ndarray) -> np.ndarray:
        # same as your original code
        if objectives.ndim == 1:
            return objectives
        n_obj = objectives.shape[1]
        if self.weights is None:
            return np.mean(objectives, axis=1)
        else:
            if len(self.weights) != n_obj:
                raise ValueError(f"Mismatch: 'weights' length {len(self.weights)} != # of objectives {n_obj}.")
            return objectives @ self.weights

    def fit(self, features: np.ndarray, objectives: np.ndarray):
        """
        Fit the surrogate model(s) to the provided features and objectives.
        
        Parameters
        ----------
        features : np.ndarray
            Shape (n_samples, n_features).
        objectives : np.ndarray
            Shape (n_samples,) or (n_samples, n_objectives).
        
        Raises
        ------
        ValueError
            If features or objectives have incompatible shapes or dimensions.
        """
        if features.ndim != 2:
            raise ValueError("Expected 'features' to be 2D (n_samples, n_features).")
        if objectives.ndim not in [1, 2]:
            raise ValueError("Expected 'objectives' to be 1D or 2D.")

        # Convert possibly multi-objective data into a single 1D vector
        aggregated_y = self._aggregate_objectives(objectives)

        model = self.surrogate_models[self.active_model_key]
        model.fit(features, aggregated_y)
        self._trained_objective_values = aggregated_y

    def predict_with_uncertainty(self, features: np.ndarray):
        """
        Predict mean and standard deviation of the objective at the given features.
        
        Parameters
        ----------
        features : np.ndarray
            Shape (n_points, n_features).
        
        Returns
        -------
        tuple of np.ndarray
            (mean, std) each of shape (n_points,).
        
        Raises
        ------
        NotImplementedError
            If the active surrogate model does not support uncertainty estimation.
        """
        model = self.surrogate_models[self.active_model_key]
        try:
            mean, std = model.predict(features, return_std=True)
        except TypeError:
            # e.g. for RandomForestRegressor
            if hasattr(model, "estimators_"):
                predictions = np.array([est.predict(features) for est in model.estimators_])
                mean = np.mean(predictions, axis=0)
                std = np.std(predictions, axis=0)
            else:
                raise NotImplementedError(
                    "The active surrogate model does not support uncertainty estimation."
                )
        return mean, std

    def expected_improvement(self, features: np.ndarray, xi: float = 0.01):
        """
        Compute the Expected Improvement (EI) acquisition at the provided features.
        
        EI is defined as:
            EI(x) = E[max(0, f_best - f(x) - xi)]
                  = (f_best - mu - xi) * Phi(Z) + sigma * phi(Z)
        where Z = (f_best - mu - xi) / sigma,
              Phi and phi are the CDF and PDF of the standard normal distribution,
              mu and sigma are the GP posterior mean and std at x,
              f_best is the best (minimum) objective observed so far.
        
        Parameters
        ----------
        features : np.ndarray
            Shape (n_points, n_features).
        xi : float, optional
            Exploration parameter that increases the margin for improvement.
        
        Returns
        -------
        np.ndarray
            EI values for each feature vector, shape (n_points,).
        
        Raises
        ------
        ValueError
            If the model is not yet trained (no observed data).
        """
        mean, std = self.predict_with_uncertainty(features)
        if self._trained_objective_values is None:
            raise ValueError("Model must be trained before calling expected_improvement().")

        best_y = np.min(self._trained_objective_values)
        improvement = best_y - mean - xi
        with np.errstate(divide='warn'):
            Z = improvement / std
            ei = improvement * norm.cdf(Z) + std * norm.pdf(Z)
            ei[std == 0.0] = 0.0
        return ei

    def upper_confidence_bound(self, features: np.ndarray, kappa: float = 2.576):
        """
        Compute the Upper Confidence Bound (UCB) acquisition function for minimization.
        
        For a minimization objective, the standard "Upper" CB becomes:
            UCB = mu - kappa * sigma
        
        Parameters
        ----------
        features : np.ndarray
            Shape (n_points, n_features).
        kappa : float
            Controls the exploration/exploitation balance; higher kappa → more exploration.
        
        Returns
        -------
        np.ndarray
            UCB values for each feature vector, shape (n_points,).
        """
        mean, std = self.predict_with_uncertainty(features)
        return mean - kappa * std

    def predict_uncertainty_only(self, features: np.ndarray):
        """
        Return only the predicted standard deviation at the given features.
        
        This can be useful for pure exploration strategies.
        
        Parameters
        ----------
        features : np.ndarray
            Shape (n_points, n_features).
        
        Returns
        -------
        np.ndarray
            Standard deviation of predictions, shape (n_points,).
        """
        _, std = self.predict_with_uncertainty(features)
        return std

    # ----------------------------------------------------------------
    # New helper to check constraints
    # ----------------------------------------------------------------
    def _passes_constraints(self, point: np.ndarray) -> bool:
        """
        Returns True if 'point' satisfies all constraints in self.constraints.
        For 'all' logic, you might do:
            return all(c.is_valid(point) for c in self.constraints)
        """
        # Example: require all constraints to pass:
        return all(c.is_valid(point) for c in self.constraints)

    def validate(self, features: np.ndarray) -> bool:
        """
        Checks whether the provided feature vector satisfies
        the constraints according to the specified logic.
        
        Returns
        -------
        bool
            True if constraints pass, False otherwise.
        """
        if self.logic == "all":
            return all(constraint(features) for constraint in self.constraints)
        elif self.logic == "any":
            return any(constraint(features) for constraint in self.constraints)
        return False

    # ----------------------------------------------------------------
    # Modified recommend_candidates to handle constraints & discrete
    # ----------------------------------------------------------------
    def recommend_candidates(self,
                             bounds: np.ndarray = None,
                             n_candidates: int = None,
                             n_restarts: int = 10,
                             strategy: str = None,
                             candidate_multiplier:int = 10,
                             discrete_design:bool = True,
                             avoid_repetitions: bool=True,
                             **kwargs) -> np.ndarray:
        """
        Recommend new candidate points based on the chosen strategy, constraints, 
        and discrete vs. continuous design.
        
        This method:
        1. Generates or samples many candidate points within the given bounds.
        2. Filters them by constraints (if any).
        3. Computes the specified acquisition function (EI, UCB, exploration, 
           exploitation, or boltzmann).
        4. Selects the top n_candidates among the feasible candidates.
        
        Parameters
        ----------
        bounds : np.ndarray, optional
            Shape (n_features, 2). Defaults to self.bounds if None.
        n_candidates : int, optional
            How many points to recommend. Defaults to self.n_candidates if None.
        n_restarts : int, optional
            Not used in this simple design; for advanced global optimization 
            or random restarts, adjust accordingly.
        strategy : str, optional
            Which strategy to use. If None, defaults to self.strategy.
            Possible values: "exploration", "exploitation", "ei", "ucb", "boltzmann".
        candidate_multiplier : int, optional
            How many candidate points to generate (multiplier for n_candidates).
        discrete_design : bool, optional
            If True, integer sampling from the bounds or from the discrete_levels. 
            If False, uniform real sampling.
        avoid_repetitions : bool, optional
            If True, avoid returning duplicate points.
        **kwargs
            Additional keyword arguments are passed to the chosen acquisition function.
            - For "boltzmann", expects "temperature" (float).
        
        Returns
        -------
        np.ndarray
            An array of shape (n_candidates, n_features) with the recommended points.
        
        Raises
        ------
        RuntimeError
            If not enough valid candidate points can be generated to satisfy constraints.
        ValueError
            If no feasible points are found.
        """
        strategy = strategy if strategy is not None else self.strategy
        bounds = bounds if bounds is not None else self.bounds
        n_candidates = n_candidates if n_candidates is not None else self.n_candidates
        n_features = bounds.shape[0]

        # Decide which acquisition function to use
        if strategy == "exploration":
            # Maximize standard deviation
            def acquisition_func(x):
                return self.predict_uncertainty_only(x)
            mode = "max"
        elif strategy == "exploitation":
            # Minimize mean => we can maximize -mean
            def acquisition_func(x):
                mean, _ = self.predict_with_uncertainty(x)
                return -mean
            mode = "max"
        elif strategy == "ei":
            def acquisition_func(x):
                return self.expected_improvement(x, **kwargs)
            mode = "max"
        elif strategy == "ucb":
            def acquisition_func(x):
                return -self.upper_confidence_bound(x, **kwargs)
            mode = "max"
        
        elif strategy == "boltzmann":
            # Define transition parameters
            T = kwargs.get("temperature", 1.0)  # current temperature value
            T0 = kwargs.get("T0", 0.5)            # transition temperature
            k  = kwargs.get("k", 10.0)             # steepness of the transition
            
            def acquisition_func(x):
                mean, std = self.predict_with_uncertainty(x)

                # Compute interpolation weight w(T)
                w = 0.5 * (1.0 + np.tanh(k * (T - T0)))
                # Interpolate between -mean (exploitation for minimization) and +mean (for maximization)
                mean_component = (2.0 * w - 1.0) * mean
                # Exploration component remains proportional to uncertainty and temperature
                exploration_component = T * std
                return mean_component + exploration_component

            def acquisition_func(x):
                # 1) Predict mean and std for the feasible points x
                mean, std = self.predict_with_uncertainty(x)
                
                # 2) Normalize mean and std over this candidate set
                #    (Compute min and max among all feasible points you evaluate)
                min_mu, max_mu = np.min(mean), np.max(mean)
                min_std, max_std = np.min(std), np.max(std)
                
                mu_range  = max_mu - min_mu if (max_mu - min_mu)!=0 else 1e-9
                std_range = max_std - min_std if (max_std - min_std)!=0 else 1e-9
                
                mu_norm  = (mean - min_mu) / mu_range
                std_norm = (std  - min_std) / std_range

                # 3) Define a logistic-based weighting
                #    logistic in [0,1], so for T << T0 => near 0, T >> T0 => near 1
                sigmoid_T = 1.0 / (1.0 + np.exp(-k * (T - T0)))
                
                # Let's define:
                #   C(T) = 1 - sigmoid_T
                #   B(T) = sigmoid_T
                # so the sum is 1 at all times.
                C_T = 1.0 - sigmoid_T
                B_T = sigmoid_T

                # 4) Weighted sum
                # "mean_component" = prefer lower mean if you're minimizing => use negative sign if desired
                # But here let's assume we want to keep mean in [0,1] where 0=lowest, 1=highest
                # If you want to do a minimization approach, you might invert mu_norm => 1 - mu_norm
                mean_component = (1 - mu_norm)   # or (1 - mu_norm) for pure minimization
                exploration_component = std_norm

                # Combine
                acquisition_values = C_T * mean_component + B_T * exploration_component
                return acquisition_values

            mode = "max"

        else:
            # fallback to self.acquisition_func
            def acquisition_func(x):
                return self.acquisition_func(x, **kwargs)
            mode = "max"

        # We store final chosen candidates here
        chosen_candidates = []

        # ------------------------------------------------------------
        # 1) We'll do multiple random restarts to find the best single candidate
        # ------------------------------------------------------------

        candidate_count = candidate_multiplier * n_candidates
        candidates = []
        unique_candidates = set()
        max_attempts = candidate_count * 100
        attempts = 0

        # Generate candidate pool of valid points
        while len(candidates) < candidate_count and attempts < max_attempts:
            if discrete_design:
                if self.discrete_levels is not None:
                    # Sample from discrete_levels
                    candidate = []
                    for dim_idx, (low, high) in enumerate(bounds):
                        possible_values = self.discrete_levels[dim_idx]
                        # Filter those within [low, high]
                        valid_vals = possible_values[(possible_values >= low) & (possible_values <= high)]
                        if len(valid_vals) == 0:
                            raise RuntimeError(f"No discrete values in dimension {dim_idx} fit within the bounds {low, high}.")
                        candidate.append(np.random.choice(valid_vals))
                    candidate = np.array(candidate, dtype=float)
                else:
                    # Sample integer in [low, high]
                    # If no discrete_levels, just sample integer in [low, high]
                    candidate = np.array([random.randint(int(low), int(high)) for (low, high) in bounds], dtype=float)
            else:
                # Continuous sampling
                candidate = np.array([random.uniform(low, high) for (low, high) in bounds], dtype=float)

            # Check constraints
            if self.validate(candidate):
                # Check repetitions
                if avoid_repetitions:
                    candidate_tuple = tuple(candidate)  
                    if candidate_tuple not in unique_candidates:
                        unique_candidates.add(candidate_tuple)
                        candidates.append(candidate)
                else:
                    candidates.append(candidate)

            attempts += 1

        if len(candidates) < n_candidates:
            raise RuntimeError("Not enough valid candidate points were generated.")
        
        feasible_points = np.array(candidates)

        # If no feasible points found, we can't propose anything
        if len(feasible_points) == 0:
            raise ValueError("No feasible points found under the given constraints.")

        # ------------------------------------------------------------
        # Evaluate the acquisition over all feasible points
        # ------------------------------------------------------------

        # Evaluate acquisition over all feasible points
        feasible_points_array = np.array(feasible_points)
        acq_vals = acquisition_func(feasible_points_array)

        # Depending on whether we are maximizing or minimizing, pick best
        if mode == "max":
            # Sort by acquisition value (descending if mode='max')
            sorted_indices = np.argsort(-acq_vals)
        else:
            sorted_indices = np.argsort(acq_vals)

        feasible_points_sorted = feasible_points[sorted_indices]
        acq_vals_sorted = acq_vals[sorted_indices]

        # -----------------------------
        # 2) Select top n_candidates while enforcing minimum distance
        # -----------------------------
        min_distance = 1
        chosen_candidates = []
        chosen_acq_vals = []

        def distance(x, y):
            return np.linalg.norm(x - y)

        for i, point in enumerate(feasible_points_sorted):
            if len(chosen_candidates) == 0:
                # Always pick the first best
                chosen_candidates.append(point)
                chosen_acq_vals.append(acq_vals_sorted[i])
            else:
                # Check distance constraints against already chosen
                too_close = any(distance(point, c) < min_distance for c in chosen_candidates)
                if not too_close:
                    chosen_candidates.append(point)
                    chosen_acq_vals.append(acq_vals_sorted[i])

            if len(chosen_candidates) >= n_candidates:
                break

        # In case we can't find enough candidates spaced out, we fill up randomly 
        # or simply accept fewer. For simplicity, let's just accept what we have.
        chosen_candidates = np.array(chosen_candidates)
        return chosen_candidates


    def evaluate_BO_over_generations(self, temperature:list=None, max_generations: int=1000) -> List[float]:
        """
        Predicts how the temperature would evolve over a specified number
        of generations. This is useful for plotting or debugging to see how
        oscillation and decay would behave in isolation (i.e., ignoring real-time
        performance-based updates).

        Parameters
        ----------
        max_generations : int
            Number of generations to simulate.

        Returns
        -------
        List[float]
            A list of temperature values for each generation from 0 to max_generations-1.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # Example definitions (adjust as needed)
        max_generations = temperature.shape[0]

        # Synthetic training data
        X_train = np.random.rand(5, 2) * 100   # 10 samples in 2D
        Y_train = (X_train[:, 0] - 50)**2/2500 + (X_train[:, 1] - 50)**2/2500  + np.random.rand(5)*0.9

        # Create a grid for the background gradient representing the objective response
        x_grid = np.linspace(0, 100, 200)
        y_grid = np.linspace(0, 100, 200)
        XX, YY = np.meshgrid(x_grid, y_grid)
        Z = (XX - 50)**2/2500 + (YY - 50)**2/2500  # Compute the objective function on the grid

        plt.figure(figsize=(8, 6))

        # Plot the background gradient using contourf
        bg = plt.contourf(XX, YY, Z, levels=100, cmap='viridis')
        plt.colorbar(bg, label='Objective value (background)')
        mean_responde_array = np.zeros(max_generations)
        bo = BayesianOptimization(bounds=np.array([[0, 100], [0, 100]]))
        bo.fit(X_train, Y_train)
        # Loop over generations and accumulate candidate points
        for i, (g, t) in enumerate(zip(range(1, max_generations + 1), temperature)):
            # Instantiate and fit the BayesianOptimization model
            # (Assuming BayesianOptimization is defined/imported elsewhere)
            
            

            # Get candidate points with a Boltzmann sampling strategy
            new_candidates = bo.recommend_candidates(strategy="boltzmann",
                                                     n_candidates=10,
                                                     temperature=t)
            # Compute objective response for each candidate point
            responses = (new_candidates[:, 0] - 50)**2/2500 + (new_candidates[:, 1] - 50)**2/2500  + np.random.rand(10)*0.9

            # Scale marker size based on temperature (adjust scaling as needed)
            # Here, we scale relative to the maximum temperature value.
            marker_size = 400 * (t / max(temperature))
            
            # Plot the candidate points on the same figure
            sc = plt.scatter(new_candidates[:, 0],
                             new_candidates[:, 1],
                             c=responses,
                             cmap='viridis',
                             s=marker_size,
                             edgecolor='k',
                             label=f'Gen {g}, T={t:.2f}',
                             alpha=0.8)
            
            # Optionally, annotate each candidate with its generation number
            for (x, y) in new_candidates:
                plt.text(x, y, f'{g}', fontsize=8, color='white', ha='center', va='center')
                    
            X_train = np.concatenate((X_train, new_candidates), axis=0)
            Y_train = np.concatenate((Y_train, responses), axis=0)
            mean_responde_array[i] = np.mean(responses)
            bo.fit(X_train, Y_train)

        plt.xlabel('X1')
        plt.ylabel('X2')
        plt.title('Evolution of Candidate Points over Generations')
        #plt.legend(title="Generation & Temperature", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        print(mean_responde_array)
        plt.show()

        plt.plot(temperature, mean_responde_array)
        plt.show()

        return generations_array, mutation_rate_array




# ----------------------------------------------------------------
# Example usage if you run this as a script
# ----------------------------------------------------------------
if __name__ == "__main__":
    # Example usage with constraints & discrete levels
    np.random.seed(0)

    # Suppose we have 2D features in [0, 5]
    example_bounds = np.array([[0, 5],
                               [0, 5]], dtype=float)

    # Example constraint: x[0] + x[1] <= 6
    def sum_constraint(x):
        return (x[0] + x[1]) <= 6.0

    # Another example constraint: x[0] >= 1
    def min_constraint(x):
        return x[0] >= 1.0

    # Wrap in FeatureConstraint
    constraints = [
        #FeatureConstraint(sum_constraint, name="Sum <= 6"),
        #FeatureConstraint(min_constraint, name="x0 >= 1")
    ]

    # If we want discrete levels for each dimension, define them
    discrete_levels = [
        np.array([1,2,3,4,5]),
        np.array([0,1,2,3,4,5])
    ]

    # Create some synthetic training data that meets the dimension shape
    X_train = np.random.rand(10, 2) * 5   # 10 samples in 2D
    Y_train = (X_train[:,0]-2.5)**2 + (X_train[:,1]-2.5)**2  # e.g. some 1D objective

    # Instantiate BO with constraints & discrete levels
    bo = BayesianOptimization(
        bounds=example_bounds,
        constraints=constraints,
        discrete_levels=discrete_levels
    )
    bo.fit(X_train, Y_train)

    # Request 3 new candidates using the "boltzmann" strategy 
    # with a specified temperature for balancing exploitation/exploration
    temperature = 2.0
    new_candidates_boltzmann = bo.recommend_candidates(
        strategy="boltzmann", 
        n_candidates=10, 
        temperature=temperature  # High T => more exploration
    )
    print(f"Feasible candidates using 'boltzmann' strategy (T={temperature}):\n", new_candidates_boltzmann)
