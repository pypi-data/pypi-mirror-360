"""Route registration utilities for the Voice-Agent API layer.

This module:

1. Loads HTTP & WebSocket route definitions from every project config that
   was parsed at startup (`connexity_pipecat.core.config_parser.configs`).
2. Resolves handler strings to real callables by inspecting
   `connexity_pipecat.api.handlers`.
3. Exposes `register_routes(app)` – a convenience function that attaches all
   discovered routes to a `FastAPI` instance.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from types import MappingProxyType
from typing import Any, Dict, List

from fastapi import FastAPI

from connexity_pipecat.api import handlers as _handlers
from connexity_pipecat.core.config import get_config, list_config_names

# --------------------------------------------------------------------------- #
# Handler registry (string → callable)                                         #
# --------------------------------------------------------------------------- #

HANDLER_REGISTRY: MappingProxyType[str, Any] = MappingProxyType(
    {
        name: getattr(_handlers, name)
        for name in dir(_handlers)
        if not name.startswith("_") and callable(getattr(_handlers, name))
    }
)


def _resolve_handlers(routes: List[Dict[str, Any]]) -> None:
    """Replace each string `handler` in *routes* with its real callable.

    Args:
        routes: A list of route dictionaries where `"handler"` may still be a
            string. The list is mutated in-place.
    """
    for route in routes:
        if isinstance(route.get("handler"), str):
            route["handler"] = HANDLER_REGISTRY[route["handler"]]


# --------------------------------------------------------------------------- #
# Utilities                                                                   #
# --------------------------------------------------------------------------- #

def register_config_routes(app: FastAPI, config_name: str = "default") -> FastAPI:
    """Attach all discovered HTTP & WS routes to *app*.

    Args:
        config_name:
        app: An instantiated `FastAPI` application.

    Returns:
        The same `app` instance, allowing call-chaining.
    """
    route_cfg = get_config(config_name)["routes"]
    routers: List[Dict[str, Any]] = route_cfg.get("routers")
    websockets: List[Dict[str, Any]] = route_cfg.get("websockets")

    for section in routers:
        _resolve_handlers(section["routes"])
    for section in websockets:
        _resolve_handlers(section["routes"])

    for router_section in routers:
        prefix = router_section["prefix"] if router_section["prefix"] else None
        tag = f"[Agent]"
        tag += f"[{prefix.replace('_', ' ').replace('/', '').title()}]" if prefix else ''

        for route in router_section["routes"]:
            raw = route["path"].lstrip("/")
            app.add_api_route(
                path=f"/{{prefix}}/{raw}" if prefix else f"/{raw}",
                endpoint=route["handler"],
                methods=route["methods"],
                name=route["handler"].__name__,
                tags=[tag],
            )

    for ws_section in websockets:
        prefix = ws_section["prefix"] if ws_section["prefix"] else None
        for ws in ws_section["routes"]:
            raw = ws["path"].lstrip("/")
            app.add_api_websocket_route(
                    path=f"/{{prefix}}/{raw}" if prefix else f"/{raw}",
                    endpoint=ws["handler"],
                    name=ws["handler"].__name__,
                )

    return app

def register_routes(app: FastAPI) -> FastAPI:
    """
    Registers all routes from all loaded configs into the FastAPI app.

    Args:
        app: FastAPI instance

    Returns:
        The same app instance.
    """
    for config_name in list_config_names():
        register_config_routes(app, config_name=config_name)
    return app

def register_custom_handlers(handlers_path: str) -> None:
    """
    Load every *.py file in *handlers_path* and merge its top-level callables
    into ``HANDLER_REGISTRY``.

    – Only callables defined in that module are included (no re-exports).
    – If a name already exists we log a warning, then override it.
    """
    global HANDLER_REGISTRY

    if not os.path.isdir(handlers_path):
        raise ValueError(f"{handlers_path!r} is not a valid directory.")

    logger = logging.getLogger(__name__)
    custom_funcs: Dict[str, Any] = {}

    for filename in os.listdir(handlers_path):
        if filename.startswith("_") or not filename.endswith(".py"):
            continue

        module_name = filename[:-3]
        file_path = os.path.join(handlers_path, filename)

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            continue

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)  # type: ignore[arg-type]

        for name, attr in module.__dict__.items():
            if name.startswith("_") or not callable(attr):
                continue
            if getattr(attr, "__module__", None) != module.__name__:
                continue  # skip re-exported names

            if name in custom_funcs:
                logger.warning(
                    "Duplicate handler %s found in %s; keeping the last one",
                    name,
                    handlers_path,
                )
            custom_funcs[name] = attr

    if not custom_funcs:
        logger.warning("No custom handlers discovered in %s", handlers_path)
        return

    merged = dict(HANDLER_REGISTRY)
    for name, func in custom_funcs.items():
        if name in merged:
            logger.warning(
                "The handler name '%s' is overridden by a custom handler.", name
            )
        merged[name] = func

    HANDLER_REGISTRY = MappingProxyType(merged)
