import importlib
import importlib.util


def import_from(module, function):
    md = importlib.import_module(module)
    cls = getattr(md, function)
    return cls


def import_module(name, package=None):
    return importlib.import_module(name, package)


def get_location(module):
    spec = importlib.util.find_spec(module)
    return spec.origin


find_spec = importlib.util.find_spec
