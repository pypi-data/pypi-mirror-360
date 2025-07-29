#!/usr/bin/env python3
"""bansga.main – CLI entry for the Bayesian‑Annealed NSGA explorer.
Full description omitted for brevity (see previous revision)."""
from __future__ import annotations

import argparse
import importlib
import inspect
import json
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List

import numpy as np

try:
    import yaml  # type: ignore

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# -----------------------------------------------------------------------------
# Core BANS‑GA imports (absolute)                                              
# -----------------------------------------------------------------------------
from .explorer.explorer import EvolutionaryStructureExplorer
from .explorer.supercell import SupercellEvolutionManager
from .utils.helper_functions import *
from .mutation_crossover.mutation import *
from .selection.objective import *
from .selection.features import *
from .DoE.DoE import *
from .thermostat.thermostat import *
from .bayesian_optimization.bayesian_optimization import *
from .physical_model.physical_model import *

# Built‑in mutation module (contains many factories as attributes) ------------
# Built‑in mutation factories live here
from .mutation_crossover import mutation as builtin_mut

# Objective & feature factory shortcuts ---------------------------------------
from .selection.objective import objective_min_distance_to_hull, objective_similarity
from .selection.features import feature_composition_vector

# -----------------------------------------------------------------------------
# Helper maps                                                                  
# -----------------------------------------------------------------------------
BUILTIN_OBJECTIVES: Dict[str, Any] = {
    "min_distance_to_hull": objective_min_distance_to_hull,
    "similarity": objective_similarity,
}

BUILTIN_FEATURES: Dict[str, Any] = {
    "composition": feature_composition_vector,
}

DEFAULT_SUPERCELLS: List[tuple[int, int, int]] = [
    (1, 1, 1),
]

# -----------------------------------------------------------------------------
# Generic utilities                                                            
# -----------------------------------------------------------------------------

def load_config(path: str | Path) -> Dict[str, Any]:
    """Load YAML or JSON into a plain dict."""
    path = Path(path)
    with path.open("r", encoding="utf‑8") as fh:
        if _HAS_YAML and path.suffix.lower() in {".yml", ".yaml"}:
            return yaml.safe_load(fh)  # type: ignore[no-any-return]
        return json.load(fh)  # type: ignore[no-any-return]


def _import_from_path(path: str) -> Any:
    module_name, attr = path.rsplit(".", 1)
    mod: ModuleType = importlib.import_module(module_name)
    return getattr(mod, attr)

# -----------------------------------------------------------------------------
# Factories: objectives, features, mutations                                   
# -----------------------------------------------------------------------------

def _build_objectives(cfg: Dict[str, Any]) -> List[Any]:
    objs: List[Any] = []
    for entry in cfg.get("objectives", []):
        name = entry["name"]
        params = entry.get("params", {})
        if name in BUILTIN_OBJECTIVES:
            objs.append(BUILTIN_OBJECTIVES[name](**params))
        else:
            factory = _import_from_path(entry["fn_path"])
            objs.append(factory(**params))
    return objs


def _build_features(cfg: Dict[str, Any]) -> List[Any]:
    feats: List[Any] = []
    for entry in cfg.get("features", []):
        name = entry["name"]
        params = entry.get("params", {})
        if name in BUILTIN_FEATURES:
            feats.append(BUILTIN_FEATURES[name](params))
        else:
            factory = _import_from_path(entry["fn_path"])
            feats.append(factory(**params))

    return feats[0]


def _resolve_factory(name: str) -> Any:
    if hasattr(builtin_mut, name):
        return getattr(builtin_mut, name)
    return _import_from_path(name)


def _build_inline_constraints(items: List[Any]) -> List[Any]:
    built: List[Any] = []
    for it in items:
        if isinstance(it, dict):
            if len(it) != 1:
                raise ValueError("Inline constraint mapping must have exactly one key")
            cname, cparams = next(iter(it.items()))
            factory = _resolve_factory(cname)
            built.append(factory(**cparams))
        elif isinstance(it, str):
            built.append(_resolve_factory(it)())
        else:
            raise TypeError("Constraint spec must be dict or str")
    return built


def _build_mutations(cfg: Dict[str, Any]) -> List[Any]:
    muts: List[Any] = []
    for entry in cfg.get("mutation", {}).get("functions", []):
        if not isinstance(entry, dict) or len(entry) != 1:
            raise ValueError("Each mutation entry must be a single‑key mapping")
        fname, params = next(iter(entry.items()))
        params = params or {}
        # Resolve nested constraints
        if "constraints" in params:
            params["constraints"] = _build_inline_constraints(params["constraints"])
                # Leave parameters as‑is; user can quote literals like "4*sp" when they
        # explicitly want evaluation elsewhere. Here we assume mutation factories
        # know how to handle string parameters (e.g., species="Cu").
        factory = _resolve_factory(fname)
        muts.append(factory(**params))

    return muts

def _physical_model(cfg: Dict[str, Any]) -> Dict[Any]:
    phics: Dict[Any] = {}

    if 'T_mode' in cfg.get("physical_model", {}):
        phics['T_mode'] = cfg.get("physical_model", {}).get('T_mode')

    if cfg.get("physical_model", {}).get('name', '') == 'MACE':
        calc = mace_calculator( **cfg.get("physical_model", {}).get('params', '') )
        phics['calculator'] = calc

    return phics

# -----------------------------------------------------------------------------
# Constraint instantiation                                                     
# -----------------------------------------------------------------------------

def instantiate_constraint(cfg_entry: Dict[str, Any], ctx: Dict[str, Any]) -> FeatureConstraint:
    """Create a :class:`FeatureConstraint` from a YAML entry.

    *Auto‑detects* any static method in :class:`ConstraintGenerator`.
    Accepts the following YAML aliases to minimise user errors:
      * `feature_index` ↔ `feature_idx`
      * `numerator_index` / `denominator_index` ↔ `*_idx`
      * any `<name>_indices` list ↔ `<name>_idxs` / `<name>_idx_list`
    Also supports ``expression``/``expr`` and ``custom`` types.
    """
    ctype: str = cfg_entry["type"]
    name = cfg_entry.get("name", "")
    desc = cfg_entry.get("description", "")

    # ----------------------------- alias helper -----------------------------
    def _lookup(key: str) -> Any:
        """Return cfg_entry value matching *key* or one of its common aliases."""
        # direct match
        if key in cfg_entry:
            return cfg_entry[key]
        # keyword aliases for indices
        if key.endswith("_idx") and (alt := key[:-3] + "index") in cfg_entry:
            return cfg_entry[alt]
        if key.endswith("_index") and (alt := key[:-6] + "idx") in cfg_entry:
            return cfg_entry[alt]
        # plural forms
        if key.endswith("_indices") and (alt := key[:-8] + "idxs") in cfg_entry:
            return cfg_entry[alt]
        if key.endswith("_idxs") and (alt := key[:-4] + "indices") in cfg_entry:
            return cfg_entry[alt]
        # threshold alias: allow threshold_expr for threshold
        if key == "threshold" and "threshold_expr" in cfg_entry:
            return cfg_entry["threshold_expr"]
        # inverse: threshold_expr expected for high-level expression type
        if key == "expr" and "expression" in cfg_entry:
            return cfg_entry["expression"]
        raise KeyError(key)

    # ------------------------------------------------------------------
    # 1) Static method in ConstraintGenerator
    # ------------------------------------------------------------------
    if hasattr(ConstraintGenerator, ctype):
        gen_func = getattr(ConstraintGenerator, ctype)
        sig = inspect.signature(gen_func)
        bound_args: List[Any] = []
        for param in sig.parameters.values():
            if param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
                try:
                    raw_val = _lookup(param.name)
                except KeyError:
                    raise KeyError(
                        f"Missing parameter '{param.name}' (or alias) for constraint type '{ctype}'."
                    ) from None
                val = eval(raw_val, {}, ctx) if isinstance(raw_val, str) else raw_val  # noqa: S307
                bound_args.append(val)
        check_fn = gen_func(*bound_args)

    # ------------------------------------------------------------------
    # 2) Expression‑based constraint
    # ------------------------------------------------------------------
    elif ctype in {"expr", "expression"}:
        expr = cfg_entry["expr"]

        def check_fn(features, _expr=expr, _ctx=ctx):  # type: ignore[override]
            return eval(_expr, {"np": np}, {"features": features, **_ctx})  # noqa: S307

    # ------------------------------------------------------------------
    # 3) Custom factory path
    # ------------------------------------------------------------------
    elif ctype == "custom":
        factory = _import_from_path(cfg_entry["fn_path"])
        args = [eval(a, {}, ctx) if isinstance(a, str) else a for a in cfg_entry.get("args", [])]  # noqa: S307
        check_fn = factory(*args)

    else:
        raise ValueError(f"Unknown constraint type '{ctype}'.")

    return FeatureConstraint(check_func=check_fn, name=name, description=desc)

# -----------------------------------------------------------------------------
# Object builders                                                               
# -----------------------------------------------------------------------------

def build_objects(cfg: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    params_base: Dict[str, Any] = {
        "max_generations": cfg["ga"]["max_generations"],
        "min_size_for_filter": cfg["ga"]["min_size_for_filter"],
        "thermostat": Thermostat(**cfg["thermostat"]),
        #"mutation_rate_params": cfg["mutation"],
        "multiobjective_params": cfg["multiobjective"],
        "convergence_params": cfg["convergence"],
        "collision_factor": cfg.get("collision_factor", 0.4),
        "dataset_path": cfg["paths"]["dataset"],
        "template_path": cfg.get("paths", None).get("template", None),
        "output_path": cfg["paths"]["output"],
        "objective_funcs": _build_objectives(cfg),
        "features_funcs": _build_features(cfg),
        "mutation_funcs": _build_mutations(cfg),
        "crossover_funcs": [],
        "physical_model_func": _physical_model(cfg),
    }
    print(params_base)
    # Build BO per supercell ---------------------------------------------------
    BO_list: List[BayesianOptimization] = []
    for si, cell in enumerate(cfg.get("supercells", [])):
        sp = int(np.prod(cell))
        ctx = {"sp": sp, "si": si}
        constraints = [instantiate_constraint(c, ctx) for c in cfg.get("constraints", [])]

        if "DoE" in cfg:
            doe_cfg = cfg["DoE"]
            doe = DesignOfExperiments(
                design=generate_space_filling(**doe_cfg["space_filling"]),
                logic=doe_cfg.get("logic", "all"),
            )
            for fc in constraints:
                doe.add(fc)
            params_base["DoE"] = doe

        bo_cfg = cfg["bayesian_optimization"]
        BO_list.append(
            BayesianOptimization(
                weights=np.asarray(bo_cfg["weights"]),
                bounds=np.asarray(bo_cfg["bounds"]),
                constraints=constraints,
                n_objectives=bo_cfg["n_objectives"],
            )
        )

    return params_base, {"BO_list": BO_list}

# -----------------------------------------------------------------------------
# CLI                                                                          
# -----------------------------------------------------------------------------
def main() -> None:  # noqa: D401
    parser = argparse.ArgumentParser(description="Run BANS‑GA evolutionary explorer")
    parser.add_argument("config", help="Path to YAML/JSON configuration file")
    parser.add_argument("--out", dest="output_path", metavar="DIR", help="Override output directory")
    args = parser.parse_args()

    cfg = load_config(args.config)
    params_base, params_super = build_objects(cfg)

    if args.output_path:
        params_base["output_path"] = args.output_path

    supercells = cfg.get("supercells", [])

    if supercells:
        manager = SupercellEvolutionManager(
            params_base=params_base,
            params_supercell={"BO": params_super["BO_list"]},
            supercell_list=supercells,
            output_path=params_base["output_path"],
            debug=cfg.get("debug", False),
            restart=cfg.get("restart", False),
        )
        manager.run_all_supercells()
    else:
        explorer = EvolutionaryStructureExplorer(params=params_base, debug=cfg.get("debug", False))
        explorer.run()


if __name__ == "__main__":
    main()
