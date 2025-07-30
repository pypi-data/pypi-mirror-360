"""
HACS API Service

FastAPI service providing REST endpoints for HACS operations including
validation, conversion, CRUD operations, and search with Actor authentication.
"""

__version__ = "0.1.0"

from .auth import get_current_actor
from .main import app

__all__ = [
    "app",
    "get_current_actor",
]
