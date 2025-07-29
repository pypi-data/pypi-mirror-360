"""
Thoth SQL Database Manager Package
"""
from .ThothDbManager import ThothDbManager
from .impl.ThothPgManager import ThothPgManager
from .impl.ThothSqliteManager import ThothSqliteManager

__all__ = [
    "ThothDbManager",
    "ThothPgManager",
    "ThothSqliteManager",
]

__version__ = "0.1.0" # Match the version in pyproject.toml
