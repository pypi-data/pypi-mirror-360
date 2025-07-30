
try:
    import importlib.metadata as version_reader
except ImportError:
    import importlib_metadata as version_reader

try:
    __version__ = version_reader.version("sibi-dst")
except version_reader.PackageNotFoundError:
    __version__ = "unknown"
