"""
CLI Module for Nyro Package
♠️ Nyro: Interactive interface consolidation

Unifies all bash script menu systems into Python CLI:
- menu.sh patterns
- redis-mobile.sh interactive system  
- Profile switching interfaces
- Garden metaphor interactions
"""

from .interactive import InteractiveCLI
from .main import main

__all__ = ["InteractiveCLI", "main"]