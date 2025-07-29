"""
Nyro - Unified Redis Operations Package
♠️🌿🎸🧵 G.Music Assembly Consolidation

Consolidates 13+ bash scripts into unified Python package with:
- Multi-database Upstash Redis support
- Profile-based credential management  
- Interactive CLI and programmatic API
- Musical ledger integration
- Massive data handling capabilities
"""

__version__ = "0.1.0"
__author__ = "Jerry ⚡ G.Music Assembly Team"

from .core.client import RedisClient
from .core.profiles import ProfileManager
from .core.operations import RedisOperations
from .cli.interactive import InteractiveCLI

__all__ = ["RedisClient", "ProfileManager", "RedisOperations", "InteractiveCLI"]