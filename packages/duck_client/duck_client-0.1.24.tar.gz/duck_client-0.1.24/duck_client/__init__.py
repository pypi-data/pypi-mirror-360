
from duck_client.db import DataBase
from importlib import metadata

try:
    __version__ = metadata.version("duckdb-connector")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"


__all__ = ["DataBase"]
