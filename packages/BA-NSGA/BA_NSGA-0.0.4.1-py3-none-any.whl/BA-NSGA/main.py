import argparse
import json
import os
import importlib

def parse_args():
    parser = argparse.ArgumentParser(
        description="Evolutionary Structure Explorer - Command Line Interface"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (JSON format)",
        default=None
    )
    parser.add_argument(
        "--task",
        type=str,
        help="Task type (e.g., single-agent, multi-agent)",
        default="single-agent"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    return parser.parse_args()

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def get_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\nInput interrupted. Exiting.")
        exit(1)

def import_function(function_path):
    """Dynamically import a function from a given module path string."""
    module_path, function_name = function_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, function_name)

def main():
    args = parse_args()
    
    # Load configuration from file if provided, otherwise use interactive input
    if args.config and os.path.exists(args.config):
        params = load_config(args.config)
    else:
        # Interactive input for configuration parameters
        task = get_input("Enter task type (default 'single-agent'): ") or "single-agent"
        params = {
            'task': task,
            'max_generations': 30,
            'min_size_for_filter': 10,
            'mutation_rate_params': {
                'period': 40,
                'decay_rate': 0.01,
                'temperature': 1.0,
                'min_mutation_rate': 1,
                'initial_mutation_rate': 1.0,
            },
            'multiobjective_params': {
                'weights': None,
                'repulsion_weight': 1.0,
                'temperature': 1.0,
                'num_select': 10,
                'repulsion_mode': 'avg',
                'metric': 'euclidean',
                'random_seed': 73,
            },
            'convergence_params': {
                'objective_threshold': 0.01,
                'feature_threshold': 0.01,
            },
            'collision_factor': 0.4,
            'md_params': {},
            'foreigners': 0,
            # File paths
            'dataset_path': 'config_init.xyz',
            'template_path': 'config.xyz',
            'output_path': '.',
            # Function placeholders; these can be set interactively
            'objective_funcs': None,
            'features_funcs': None,
            'mutation_funcs': None,
            'crossover_funcs': None,
            'doe_funcs': None,
            'foreigners_generation_funcs': None,
            'physical_model_func': None,
            'supercell_steps': [[1,1,1], [2,1,1], [1,2,1], [1,1,2]]
        }
        
        # Optionally prompt for a function input (e.g., objective function)
        func_input = get_input("Enter the full module path for the objective function (or press enter to skip): ")
        if func_input:
            try:
                params['objective_funcs'] = import_function(func_input)
                print("Objective function imported successfully.")
            except (ImportError, AttributeError) as e:
                print(f"Error importing function: {e}")
    
    # Override the task from CLI if provided
    params['task'] = args.task

    if params.get('task', 'single-agent') == 'single-agent':
        from explorer.explorer import EvolutionaryStructureExplorer  # Adjust import as needed
        explorer = EvolutionaryStructureExplorer(params=params)
        explorer.run(debug=args.debug)
        # Optionally, uncomment the following to generate plots:
        # from visualization.plot_evolution import plot_evolution_data
        # plot_evolution_data(logger_dir='path/to/logger', output_dir='path/to/plot')
    else:
        raise NotImplementedError(f"Task type '{params.get('task')}' is not implemented yet.")

if __name__ == '__main__':
    main()
