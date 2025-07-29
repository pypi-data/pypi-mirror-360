import importlib.metadata

from miniduct.datasources import DataSource, HttpDataSource, PythonDataSource  # noqa: F401
from miniduct.outputs import GCSOutput, Output  # noqa: F401
from miniduct.pipeline import run_pipeline  # noqa: F401

try:
    # This will read the version from the installed package metadata
    __version__ = importlib.metadata.version("miniduct")
except importlib.metadata.PackageNotFoundError:
    # This is a fallback for when the package is not installed (e.g., running from source)
    __version__ = "0.0.0-dev"
