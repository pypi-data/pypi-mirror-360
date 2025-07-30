try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("pacli-tool")
except PackageNotFoundError:
    __version__ = "unknown"
