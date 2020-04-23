import importlib
import pkgutil
import sys

from .base import ToyAI


def import_modules(package_name):
    """Dynamically imports submodules"""
    exclude = {"base", "utils"}

    package = sys.modules[package_name]
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if name not in exclude:
            importlib.import_module(package_name + "." + name)


# imports submodules to populate ToyAI subclasses list
import_modules(__name__)
TOY_AIS = ToyAI.__subclasses__()
