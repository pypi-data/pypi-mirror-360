from __future__ import annotations

import importlib.util
import logging
import os
import sys
from types import MappingProxyType
from typing import Any, Dict


import importlib
import pkgutil

# Package that groups all built‑in generator modules
from connexity_pipecat.core.generators import functions as _functions_pkg

# --------------------------------------------------------------------------- #
#   Generator registry                                                        #
# --------------------------------------------------------------------------- #


# Helper to discover all public callables in the given package (recursively)
def _discover_package_callables(pkg) -> dict[str, Any]:
    """
    Walk through every .py module in *pkg* (recursively) and return all
    top‑level callables that are defined *inside* those modules
    (re‑exports are ignored).
    """
    discovered: dict[str, Any] = {}

    for _loader, mod_name, _is_pkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        module = importlib.import_module(mod_name)

        for name, attr in module.__dict__.items():
            if name.startswith("_") or not callable(attr):
                continue
            if getattr(attr, "__module__", None) != module.__name__:
                continue  # skip re‑exports

            if name in discovered:
                # later modules override earlier ones, mirroring handler logic
                logging.getLogger(__name__).warning(
                    "Duplicate generator '%s' found in %s; keeping the last one",
                    name,
                    mod_name,
                )
            discovered[name] = attr

    return discovered

# --------------------------------------------------------------------------- #
#   Generator registry                                                        #
# --------------------------------------------------------------------------- #


#: read‑only mapping (string → callable) initialised with every public
#: function found in *all* modules under `connexity_pipecat.core.tools.functions`
GENERATOR_REGISTRY: MappingProxyType[str, Any] = MappingProxyType(
    _discover_package_callables(_functions_pkg)
)


def get_generators() -> Dict[str, Any]:
    """
    Return a **copy** of the current generator registry.

    A copy is returned so callers can mutate their local dict without
    accidentally touching the global read-only mapping.
    """
    return dict(GENERATOR_REGISTRY)


def register_custom_generators(generators_path: str) -> None:
    """
    Load every ``*.py`` file in *generators_path* and merge its top-level
    callables into ``GENERATOR_REGISTRY``.

    ▸ Only callables actually *defined* in that module are included
      (re-exports are skipped).

    ▸ If a name already exists we log a warning and override it.

    Args
    ----
    generators_path:
        Directory that contains Python files with generator functions.

    Raises
    ------
    ValueError
        If *generators_path* is not a valid directory.
    """
    global GENERATOR_REGISTRY

    if not os.path.isdir(generators_path):
        raise ValueError(f"{generators_path!r} is not a valid directory.")

    logger = logging.getLogger(__name__)
    custom_gens: Dict[str, Any] = {}

    for filename in os.listdir(generators_path):
        if filename.startswith("_") or not filename.endswith(".py"):
            continue

        module_name = filename[:-3]
        file_path = os.path.join(generators_path, filename)

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            continue

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)  # type: ignore[arg-type]

        for name, attr in module.__dict__.items():
            # keep only *directly defined* callables
            if name.startswith("_") or not callable(attr):
                continue
            if getattr(attr, "__module__", None) != module.__name__:
                continue

            if name in custom_gens:
                logger.warning(
                    "Duplicate generator %s found in %s; keeping the last one",
                    name,
                    generators_path,
                )
            custom_gens[name] = attr

    if not custom_gens:
        logger.warning("No custom generators discovered in %s", generators_path)
        return

    merged = dict(GENERATOR_REGISTRY)
    for name, func in custom_gens.items():
        if name in merged:
            logger.warning(
                "The generator name '%s' is overridden by a custom generator.",
                name,
            )
        merged[name] = func

    # Freeze the merged mapping to make it read-only and threadsafe
    GENERATOR_REGISTRY = MappingProxyType(merged)