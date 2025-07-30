from importlib_metadata import version, PackageNotFoundError

__version__: str
try:
    __version__ = version('qmenta-core')
except PackageNotFoundError:
    # Package not installed. Using a local dev version.
    __version__ = "0.0dev0"

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
