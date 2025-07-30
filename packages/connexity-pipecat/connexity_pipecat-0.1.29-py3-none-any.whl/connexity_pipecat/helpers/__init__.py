import os
import importlib
import inspect
from pathlib import Path

# Get the current directory
_dir = Path(__file__).parent

# Dynamically import all functions from all .py files in the directory
for py_file in os.listdir(_dir):
    if py_file.endswith(".py") and py_file != "__init__.py":
        module_name = py_file[:-3]
        module = importlib.import_module(f".{module_name}", package=__name__)

        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                globals()[name] = obj