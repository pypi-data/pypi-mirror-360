"""
Musical Ledger System for G.Music Assembly
🎸 JamAI: Harmonic integration of development sessions

Provides musical documentation and composition features for:
- Session melodies in ABC notation
- Musical representation of code patterns
- Harmonic ledger tracking
- Development rhythm analysis
"""

from .ledger import MusicalLedger
from .composer import SessionComposer

__all__ = ["MusicalLedger", "SessionComposer"]