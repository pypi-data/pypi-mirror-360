from importlib.metadata import version

__version__ = version("lims_utils")
del version

__all__ = ["__version__"]
