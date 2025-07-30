# terrakio_core/__init__.py
"""
Terrakio Core

Core components for Terrakio API clients.
"""

__version__ = "0.3.9"

from .async_client import AsyncClient
from .sync_client import SyncClient as Client

__all__ = [
    "AsyncClient", 
    "Client"
]