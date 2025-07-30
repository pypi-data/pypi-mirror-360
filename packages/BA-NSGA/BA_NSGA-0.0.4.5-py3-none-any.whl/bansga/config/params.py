import warnings

def features_composition(structures):
    """
    Computes a composition-count matrix for a given list of structures.

    Each row i corresponds to 'structures[i]'.
    Each column j corresponds to a unique atom label found across all structures.
    The entry (i, j) is the count of that label in the i-th structure.

    Parameters
    ----------
    structures : list
        List of structures (each having structure.AtomPositionManager.atomLabelsList).
    
    Returns
    -------
    feats : np.ndarray
        2D array of shape (N, D), where N = number of structures,
        D = number of unique atom labels across all structures.
    """
    # You can optionally use the Partition class to gather all unique labels:
    partition = Partition()
    partition.containers = structures

    # 'partition.uniqueAtomLabels' is a set/list of all atom labels across these structures
    atom_labels = partition.uniqueAtomLabels

    # Build a composition vector for each structure, counting how many atoms of each label it has
    feats = np.array([
        [
            np.count_nonzero(structure.AtomPositionManager.atomLabelsList == label)
            for label in atom_labels
        ]
        for structure in structures
    ])

    return feats

def objective_Ef(structures):
    """
    Computes two objective values for each structure:
      1) Anomaly (based on Mahalanobis distance in composition space),
      2) Formation energy (via linear regression on composition).

    Returns a 2D array of shape (N, 2), with columns:
      [ anomaly, formation_energy ] for each structure.

    Parameters
    ----------
    structures : list
        List of structures, each with:
            - structure.AtomPositionManager.E (raw energy)
            - structure.AtomPositionManager.atomLabelsList (atom labels)

    Returns
    -------
    objectives : np.ndarray
        Shape (N, 2). The first column is anomaly, the second is formation energy.
        N = number of structures.
    """
    import numpy as np

    N = len(structures)
    if N == 0:
        return np.zeros((0, 2))

    # 1) Build composition matrix X (N x D)
    X = features(structures)

    # 2) Extract raw energies into y
    y = np.array([s.AtomPositionManager.E for s in structures])

    # 3) Compute formation energy:
    #    Fit a Ridge model to find chemical potentials, then formation = y - X @ chemical_potentials
    model = Ridge(alpha=1e-5, fit_intercept=False)
    model.fit(X, y)
    chemical_potentials = model.coef_
    formation_energies = y - X.dot(chemical_potentials)

    # 4) Compute anomaly:
    #    We do a Mahalanobis distance for each structure's composition row in X.
    #    "Lower anomaly" means it is 'typical'; "Higher anomaly" means it's more 'outlier'.
    #    For demonstration, we treat all structures as a single distribution.

    # Normalize X (z-score). If a column is constant, it becomes 0.0
    X_norm = zscore(X, axis=0)
    X_norm = np.nan_to_num(X_norm, nan=0.0)
    mean_vec = np.mean(X_norm, axis=0)
    # Small ridge term for stability
    cov_inv = inv(np.cov(X_norm, rowvar=False) + 1e-12 * np.eye(X_norm.shape[1]))

    # Mahalanobis distance => anomaly
    anomalies = np.array([
        mahalanobis(row, mean_vec, cov_inv) for row in X_norm
    ])

    # 5) Pack into a (N,2) result: columns = [ anomaly, formation_energy ]
    objectives = np.column_stack([anomalies, formation_energies])

    return objectives

def validate_evolution_parameters(params: dict = None) -> dict:
    r"""
    Validate and correct evolutionary workflow hyperparameters.

    Mathematically, let
    :math:`\mathrm{defaults}` be the mapping of required keys to their default values,
    and let
    :math:`\mathrm{params}` be the (possibly empty) override mapping.
    We construct the merged mapping
    .. math::
       \mathrm{validated\_params}(k) =
         \begin{cases}
           \mathrm{params}(k), & k \in \mathrm{dom}(\mathrm{params}),\\
           \mathrm{defaults}(k), & \text{otherwise.}
         \end{cases}

    The validation pipeline is as follows:

    1. **Initialization**  
       Set
       :math:`\mathrm{P}_0 = \mathrm{defaults}`.
       If `params` is `None`, treat it as the empty mapping.

    2. **Top‐Level Merge**  
       For each top‐level key :math:`k` in
       :math:`\mathcal{K}_{\mathrm{top}}`, update
       .. math::
          \mathrm{P}_1(k) =
            \begin{cases}
              \mathrm{params}(k), & k \in \mathrm{dom}(\mathrm{params}),\\
              \mathrm{P}_0(k),     & \text{otherwise.}
            \end{cases}

    3. **Type Assertions and Corrections**  
       For each :math:`k \in \mathcal{K}_{\mathrm{top}}`, assert
       .. math::
          \mathrm{type}\bigl(\mathrm{P}_1(k)\bigr) = T_k,
       where :math:`T_k` is the expected Python type.  
       If a value is convertible (e.g., float → int for ‘foreigners’), perform the coercion:
       .. math::
          \mathrm{P}_1(\text{'foreigners'}) \leftarrow \mathrm{int}\bigl(\mathrm{P}_1(\text{'foreigners'})\bigr).

    4. **Nested‐Dictionary Validation**  
       For each nested parameter group :math:`n\in\{\text{'mutation_rate_params', 'convergence_params', ...}\}`, let
       :math:`\mathrm{defaults}^{(n)}` and
       :math:`\mathrm{params}^{(n)}` be the default and override sub‐mappings.
       Merge them analogously:
       .. math::
          \mathrm{P}_1^{(n)}(j) =
            \begin{cases}
              \mathrm{params}^{(n)}(j), & j \in \mathrm{dom}(\mathrm{params}^{(n)}),\\
              \mathrm{defaults}^{(n)}(j), & \text{otherwise.}
            \end{cases}
       and assert
       :math:`\mathrm{type}\bigl(\mathrm{P}_1^{(n)}(j)\bigr)=T_{j}^{(n)}` for each expected sub‐key :math:`j`.
       Missing sub‐keys generate a :func:`warnings.warn` and are filled from defaults.

    5. **Inter‐Parameter Consistency**  
       Enforce relational constraints such as
       .. math::
          \mathrm{validated\_params}[\text{'min_size_for_filter'}]
          \;\ge\;
          \mathrm{validated\_params}[\text{'multiobjective_params'}]['size'].
       Violations trigger a warning and automatic correction.

    6. **Extra‐Key Warnings**  
       For any :math:`k \in \mathrm{dom}(\mathrm{params}) \setminus \mathrm{dom}(\mathrm{defaults})`,
       issue a :func:`warnings.warn` noting the unrecognized hyperparameter.

    Parameters
    ----------
    params : dict, optional
        Override hyperparameter mapping. May contain any subset of the
        top‐level keys:
        {'max_generations', 'min_size_for_filter', 'dataset_size_limit', 'save_logs', 'collision_factor',
         'filter_duplicates', 'foreigners', 'dataset_path',
         'template_path', 'output_path', 'objective_funcs',
         'features_funcs', 'mutation_funcs', 'crossover_funcs', 'DoE',
         'generative_model', 'immigrants', 'thermostat', 'physical_model_func'} and nested groups
        {'mutation_rate_params', 'convergence_params', 'multiobjective_params',
         'thermostat_params', 'information_metric'}.

    Returns
    -------
    dict
        A fully‐populated, type‐corrected parameter mapping containing all
        required keys and nested groups.

    Raises
    ------
    AssertionError
        If a parameter cannot be coerced to its expected type.
    """

    # Define default parameters

    defaults = {
        'max_generations': 100,
        'min_size_for_filter': 10,
        'dataset_size_limit': None,
        'save_logs': True,

        'mutation_rate_params': {
            'min_mutation_rate': 1,
            'initial_mutation_rate': 100.0,
            'max_prob': 0.9,
            'min_prob': 0.1,
            'alpha':0.01,
            'use_magnitude_scaling':True,
            'crossover_probability':0.1,  
        },
        'convergence_params': {
            'objective_threshold': 0.01,
            'feature_threshold': 0.01,
            'stall_threshold': 5,  
            'information_driven':False,
            'detailed_record': True,
        },
        'multiobjective_params':{
            'weights': None,
            'repulsion_weight': 1.0,
            'repetition_penalty': False,
            'objective_temperature':1.0, 
            'size': 20,
            'repulsion_mode': 'min',
            'metric': 'euclidean',
            'random_seed': 73,
            'steepness': 10.0,
            'max_count': 100,
            'cooling_rate': 0.1,
            'normalize_objectives': True,
            'sampling_temperature':1.0,
            'selection_method': 'stochastic',
            'divisions':12,
        },
        'thermostat_params':{
            'initial_temperature': 1.0,
            'decay_rate': 0.005,
            'period': 30,
            'temperature_bounds': (0.0, 1.1),
            'max_stall_offset': 1.0,
            'stall_growth_rate': 0.01,
            'constant_temperature':False,
        },
        'information_metric':{
            'auto_percentile': 15,   
            'metric': 'entropy_gain',   
            'components': 5,   
            'r_cut': 4.0,   
            'n_max': 2,   
            'l_max': 2,   
            'sigma': 0.5,   
            'max_clusters': 10,   
        },
        'sync_params':{
            'backend':      'hash',
            'shared_dir':   None,
            'shard_width':  2,
            'persist_seen': False,
            'poll_interval': 2.0,
            'auto_publish': True,  
            'max_buffer':   5 ,  
            'max_retained': 200, 
        },
        'collision_factor': 0.4,
        'filter_duplicates': True,
        'foreigners': 0,
        'dataset_path': 'config.xyz',
        'template_path': None,
        'output_path': '.',
        'objective_funcs': objective_Ef,
        'features_funcs': features_composition,
        'mutation_funcs': None,
        'crossover_funcs': None,
        'DoE': None,
        'generative_model': None,   # Default None
        'immigrants':None,
        'thermostat': None,
        'physical_model_func': {
            'T_mode': 'sampling',   
            'calculator': None,   
        },
    }

    # If no parameters provided, use an empty dictionary
    if params is None:
        params = {}

    # Create a copy of defaults to update and return
    validated_params = defaults.copy()

    # Update top-level parameters with provided values, if any
    top_level_keys = [
        'max_generations', 'min_size_for_filter', 'dataset_size_limit', 'save_logs', 'collision_factor', 'filter_duplicates',
        'foreigners', 'dataset_path', 'template_path', 'output_path',
        'objective_funcs', 'features_funcs', 'mutation_funcs', 'crossover_funcs',
        'DoE', 'generative_model', 'immigrants', 'thermostat', 'physical_model_func', 
    ]
    for key in top_level_keys:
        if key in params:
            validated_params[key] = params[key]

    # Validate top-level parameters
    assert isinstance(validated_params['max_generations'], int), (
        f"'max_generations' must be an int, got {type(validated_params['max_generations']).__name__}"
    )
    assert isinstance(validated_params["min_size_for_filter"], int), (
        f"'min_size_for_filter' must be an int or None, got {type(validated_params['min_size_for_filter']).__name__}"
    )
    assert (validated_params["dataset_size_limit"] is None) or isinstance(validated_params['dataset_size_limit'], int), (
        f"'dataset_size_limit' must be an int or None, got {type(validated_params['dataset_size_limit']).__name__}"
    )
    assert isinstance(validated_params['save_logs'], bool), (
        f"'save_logs' must be an int, got {type(validated_params['save_logs']).__name__}"
    )
    assert isinstance(validated_params['collision_factor'], float), (
        f"'collision_factor' must be a float, got {type(validated_params['collision_factor']).__name__}"
    )
    assert isinstance(validated_params['filter_duplicates'], bool), (
        f"'filter_duplicates' must be a bool, got {type(validated_params['filter_duplicates']).__name__}"
    )

    if isinstance(validated_params['foreigners'], float):
        warnings.warn("Parameter 'foreigners' provided as float. Converting to int.")
        validated_params['foreigners'] = int(validated_params['foreigners'])
    assert isinstance(validated_params['foreigners'], int), (
        f"'foreigners' must be an int, got {type(validated_params['foreigners']).__name__}"
    )
    for path_key in ['dataset_path', 'output_path']:
        value = validated_params[path_key]
        assert value is None or isinstance(value, str) and value, (
            f"'{path_key}' must be a non-empty string."
        )
    tpl = validated_params['template_path']
    assert tpl is None or (isinstance(tpl, str) and tpl), ("'template_path' must be either None or a non-empty string.")

    # Validate mutation_rate_params
    mutation_defaults = defaults['mutation_rate_params']
    validated_params['mutation_rate_params'] = params.get('mutation_rate_params', mutation_defaults)
    assert isinstance(validated_params['mutation_rate_params'], dict), (
        f"'mutation_rate_params' must be a dict, got {type(validated_params['mutation_rate_params']).__name__}"
    )
    expected_mutation_keys = {
        'min_mutation_rate': int,
        'initial_mutation_rate': float,
        'max_prob': float,
        'min_prob': float,
        'alpha':float,
        'use_magnitude_scaling':bool,
        'crossover_probability':float
        ,  
    }
    for key, expected_type in expected_mutation_keys.items():
        if key not in validated_params['mutation_rate_params']:
            warnings.warn(f"Key '{key}' missing in 'mutation_rate_params'. Using default value: {mutation_defaults[key]}")
            validated_params['mutation_rate_params'][key] = mutation_defaults[key]
        else:
            assert isinstance(validated_params['mutation_rate_params'][key], expected_type), (
                f"Key '{key}' in 'mutation_rate_params' must be {expected_type.__name__}, "
                f"got {type(validated_params['mutation_rate_params'][key]).__name__}"
            )

    # ----- Validate convergence_params -----
    conv_defaults = defaults['convergence_params']
    validated_params['convergence_params'] = params.get('convergence_params', conv_defaults)
    assert isinstance(validated_params['convergence_params'], dict), (
        f"'convergence_params' must be a dict, got {type(validated_params['convergence_params']).__name__}"
    )
    expected_conv_keys = {
        'objective_threshold': (float, int),
        'feature_threshold': (float, int),
        'stall_threshold': int,
        'information_driven': bool,
        'detailed_record': bool,
    }
    for key, expected_type in expected_conv_keys.items():
        if key not in validated_params['convergence_params']:
            warnings.warn(f"Key '{key}' missing in 'convergence_params'. Using default value: {conv_defaults[key]}")
            validated_params['convergence_params'][key] = conv_defaults[key]
        else:
            assert isinstance(validated_params['convergence_params'][key], expected_type), (
                f"Key '{key}' in 'convergence_params' must be {expected_type.__name__}, "
                f"got {type(validated_params['convergence_params'][key]).__name__}"
            )

    # ----- Validate sync_params -----
    sync_defaults = defaults['sync_params']
    validated_params['sync_params'] = params.get('sync_params', sync_defaults)
    assert isinstance(validated_params['sync_params'], dict), (
        f"'sync_params' must be a dict, got {type(validated_params['sync_params']).__name__}"
    )
    expected_sync_keys = {
        'backend':       (str),
        'shared_dir':    (str, type(None)),
        'shard_width':   (float, int),
        'persist_seen':  (bool),
        'poll_interval': (float, int),
        'auto_publish':   bool,  
        'max_buffer':    (float, int),
        'max_retained':  (float, int),
    }
    for key, expected_type in expected_sync_keys.items():
        if key not in validated_params['sync_params']:
            warnings.warn(f"Key '{key}' missing in 'sync_params'. Using default value: {sync_defaults[key]}")
            validated_params['sync_params'][key] = sync_defaults[key]
        else:
            assert isinstance(validated_params['sync_params'][key], expected_type), (
                f"Key '{key}' in 'sync_params' must be {expected_type.__name__}, "
                f"got {type(validated_params['sync_params'][key]).__name__}"
            )

    # ----- Validate multiobjective_params -----
    multi_defaults = defaults['multiobjective_params']
    validated_params['multiobjective_params'] = params.get('multiobjective_params', multi_defaults)
    assert isinstance(validated_params['multiobjective_params'], dict), (
        f"'multiobjective_params' must be a dict, got {type(validated_params['multiobjective_params']).__name__}"
    )

    expected_multi_keys = {
        'weights': (type(None), list, tuple),
        'repulsion_weight': (float, int),
        'repetition_penalty': bool,
        'objective_temperature': (float, int),
        'size': int,
        'repulsion_mode': str,
        'metric': str,
        'random_seed': int,
        'steepness': (float, int),
        'max_count': (float, int),
        'cooling_rate': (float, int),
        'sampling_temperature': (float, int),
        'normalize_objectives': bool,
        'selection_method': str,
        'divisions': (float, int),
    }
    for key, expected_type in expected_multi_keys.items():
        if key not in validated_params['multiobjective_params']:
            warnings.warn(f"Key '{key}' missing in 'multiobjective_params'. Using default value: {multi_defaults[key]}")
            validated_params['multiobjective_params'][key] = multi_defaults[key]
        else:
            if isinstance(expected_type, tuple):
                if not isinstance(validated_params['multiobjective_params'][key], expected_type):
                    raise AssertionError(
                        f"Key '{key}' in 'multiobjective_params' must be one of types {[t.__name__ for t in expected_type]}, "
                        f"got {type(validated_params['multiobjective_params'][key]).__name__}"
                    )
            else:
                assert isinstance(validated_params['multiobjective_params'][key], expected_type), (
                    f"Key '{key}' in 'multiobjective_params' must be {expected_type.__name__}, "
                    f"got {type(validated_params['multiobjective_params'][key]).__name__}"
                )

    # Retrieve size from multiobjective_params
    size = validated_params['multiobjective_params']['size']

    # ----- Validate thermostat_params -----
    thermo_defaults = defaults['thermostat_params']
    validated_params['thermostat_params'] = params.get('thermostat_params', thermo_defaults)
    assert isinstance(validated_params['thermostat_params'], dict), (
        f"'thermostat_params' must be a dict, got {type(validated_params['thermostat_params']).__name__}"
    )

    expected_thermo_keys = {
        'initial_temperature': (float, int),
        'decay_rate': (float, int),
        'period': (float, int),
        'temperature_bounds': (type(None), list, tuple),
        'max_stall_offset': (float, int),
        'stall_growth_rate': (float, int),
        'constant_temperature': bool
    }
    for key, expected_type in expected_thermo_keys.items():
        if key not in validated_params['thermostat_params']:
            warnings.warn(f"Key '{key}' missing in 'thermostat_params'. Using default value: {thermo_defaults[key]}")
            validated_params['thermostat_params'][key] = thermo_defaults[key]
        else:
            if isinstance(expected_type, tuple):
                if not isinstance(validated_params['thermostat_params'][key], expected_type):
                    raise AssertionError(
                        f"Key '{key}' in 'thermostat_params' must be one of types {[t.__name__ for t in expected_type]}, "
                        f"got {type(validated_params['thermostat_params'][key]).__name__}"
                    )
            else:
                assert isinstance(validated_params['thermostat_params'][key], expected_type), (
                    f"Key '{key}' in 'thermostat_params' must be {expected_type.__name__}, "
                    f"got {type(validated_params['thermostat_params'][key]).__name__}"
                )

    # ----- Validate information_metric -----
    information_defaults = defaults['information_metric']
    validated_params['information_metric'] = params.get('information_metric', information_defaults)
    assert isinstance(validated_params['information_metric'], dict), (
        f"'information_metric' must be a dict, got {type(validated_params['information_metric']).__name__}"
    )

    expected_info_keys = {
        'auto_percentile': (float, int),
        'metric': str,
        'components': int,    
        'r_cut': (float, int),
        'n_max': int,
        'l_max': int,
        'sigma': (float, int),
        'max_clusters': int,
    }
    for key, expected_type in expected_info_keys.items():
        if key not in validated_params['information_metric']:
            warnings.warn(f"Key '{key}' missing in 'information_metric'. Using default value: {information_defaults[key]}")
            validated_params['information_metric'][key] = information_defaults[key]
        else:
            if isinstance(expected_type, tuple):
                if not isinstance(validated_params['information_metric'][key], expected_type):
                    raise AssertionError(
                        f"Key '{key}' in 'information_metric' must be one of types {[t.__name__ for t in expected_type]}, "
                        f"got {type(validated_params['information_metric'][key]).__name__}"
                    )
            else:
                assert isinstance(validated_params['information_metric'][key], expected_type), (
                    f"Key '{key}' in 'information_metric' must be {expected_type.__name__}, "
                    f"got {type(validated_params['information_metric'][key]).__name__}"
                )

    # Check if min_size_for_filter is less than size and update if necessary
    if validated_params['min_size_for_filter'] < size:
        warnings.warn(
            f"'min_size_for_filter' ({validated_params['min_size_for_filter']}) is less than "
            f"'size' ({size}). Setting 'min_size_for_filter' to {size}."
        )
        validated_params['min_size_for_filter'] = size

    # ----- Validate physical_model_func -----
    model_defaults = defaults['physical_model_func']
    validated_params['physical_model_func'] = params.get('physical_model_func', model_defaults)
    assert isinstance(validated_params['physical_model_func'], dict), (
        f"'Physical_model_func' must be a dict, got {type(validated_params['physical_model_func']).__name__}"
    )
    expected_model_keys = {
        'T_mode': (str),
        'calculator': object,
    }
    for key, expected_type in expected_model_keys.items():
        if key not in validated_params['physical_model_func']:
            warnings.warn(f"Key '{key}' missing in 'physical_model_func'. Using default value: {model_defaults[key]}")
            validated_params['physical_model_func'][key] = model_defaults[key]
        else:
            if isinstance(expected_type, tuple):
                if not isinstance(validated_params['physical_model_func'][key], expected_type):
                    raise AssertionError(
                        f"Key '{key}' in 'physical_model_func' must be one of types {[t.__name__ for t in expected_type]}, "
                        f"got {type(validated_params['physical_model_func'][key]).__name__}"
                    )
            else:
                assert isinstance(validated_params['physical_model_func'][key], expected_type), (
                    f"Key '{key}' in 'physical_model_func' must be {expected_type.__name__}, "
                    f"got {type(validated_params['physical_model_func'][key]).__name__}"
                )

    # --- Additional check for unrecognized hyperparameters ---

    # Top-level: warn about any extra keys in params that are not defined in defaults.
    for key in params:
        if key not in defaults:
            warnings.warn(f"Unrecognized hyperparameter '{key}' provided. It will be ignored.")

    # For nested dictionaries: check for extra keys in 'mutation_rate_params'
    if 'mutation_rate_params' in params and isinstance(params['mutation_rate_params'], dict):
        for key in params['mutation_rate_params']:
            if key not in expected_mutation_keys:
                warnings.warn(f"Unrecognized hyperparameter 'mutation_rate_params->{key}' provided. It will be ignored.")

    # For nested dictionaries: check for extra keys in 'convergence_params'
    if 'convergence_params' in params and isinstance(params['convergence_params'], dict):
        for key in params['convergence_params']:
            if key not in expected_conv_keys:
                warnings.warn(f"Unrecognized hyperparameter 'convergence_params->{key}' provided. It will be ignored.")

    # For nested dictionaries: check for extra keys in 'parallelization'
    if 'parallelization' in params and isinstance(params['parallelization'], dict):
        for key in params['parallelization']:
            if key not in expected_conv_keys:
                warnings.warn(f"Unrecognized hyperparameter 'parallelization->{key}' provided. It will be ignored.")

    # For nested dictionaries: check for extra keys in 'multiobjective_params'
    if 'multiobjective_params' in params and isinstance(params['multiobjective_params'], dict):
        for key in params['multiobjective_params']:
            if key not in expected_multi_keys:
                warnings.warn(f"Unrecognized hyperparameter 'multiobjective_params->{key}' provided. It will be ignored.")

    # For nested dictionaries: check for extra keys in 'thermostat_params'
    if 'thermostat_params' in params and isinstance(params['thermostat_params'], dict):
        for key in params['thermostat_params']:
            if key not in expected_thermo_keys:
                warnings.warn(f"Unrecognized hyperparameter 'thermostat_params->{key}' provided. It will be ignored.")

    # For nested dictionaries: check for extra keys in 'information_metric'
    if 'information_metric' in params and isinstance(params['information_metric'], dict):
        for key in params['information_metric']:
            if key not in expected_info_keys:
                warnings.warn(f"Unrecognized hyperparameter 'information_metric->{key}' provided. It will be ignored.")

    # For nested dictionaries: check for extra keys in 'multiobjective_params'
    if 'physical_model_func' in params and isinstance(params['physical_model_func'], dict):
        for key in params['physical_model_func']:
            if key not in expected_model_keys:
                warnings.warn(f"Unrecognized hyperparameter 'physical_model_func->{key}' provided. It will be ignored.")

    # ------------------------------------------------------------------------
    # 7) Verify that DoE / generative_model / immigrants implement .generate(...)
    # ------------------------------------------------------------------------
    """
    Ensure that any user‐supplied DoE or generative_model object
    implements the expected methods, warning if they are missing or non‐callable.
    """
    COMPONENT_KEYS = ('DoE', 'generative_model')
    REQUIRED_METHODS = ('generate', 'validate', 'initialization')

    for key in COMPONENT_KEYS:
        obj = validated_params.get(key)
        if obj is None:
            continue

        # Check each required method once
        for method in REQUIRED_METHODS:
            attr = getattr(obj, method, None)
            if not callable(attr):
                warnings.warn(
                    f"Parameter '{key}' does not implement a callable '{method}' method; "
                    f"calls to {method}() will fail unless you add one."
                )

        # The original code issued a second warning specifically for
        # `generative_model.generate()`. Replicate that here:
        # For generative_model, lack of generate() is a hard error
        if key == 'generative_model':
            gen = getattr(obj, 'generate', None)
            if not callable(gen):
                raise AttributeError(
                    "Parameter 'generative_model' must implement a callable "
                    "'generate' method."
                )
                
    return validated_params