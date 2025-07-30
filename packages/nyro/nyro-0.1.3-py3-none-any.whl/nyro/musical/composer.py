"""
Session Composer Module
🎸 JamAI: Musical composition for development sessions

Provides advanced composition features for:
- Session-specific melody generation
- Team harmony orchestration  
- Pattern-based musical motifs
- ABC notation composition
"""

from typing import Dict, List, Optional
from .ledger import MusicalLedger, MusicalEntry


class SessionComposer:
    """Advanced session composition and musical generation."""
    
    def __init__(self, musical_ledger: MusicalLedger):
        """Initialize composer with musical ledger."""
        self.ledger = musical_ledger
    
    def compose_team_harmony(self, session_id: str) -> str:
        """Compose harmony based on team activities."""
        entries = self.ledger.get_session_entries(session_id)
        
        # Group by team member
        team_activities = {}
        for entry in entries:
            if entry.team_member:
                if entry.team_member not in team_activities:
                    team_activities[entry.team_member] = []
                team_activities[entry.team_member].append(entry)
        
        # Generate harmony for each voice
        harmony_parts = []
        
        for member, activities in team_activities.items():
            part = self._generate_member_voice(member, activities)
            harmony_parts.append(f"% {member} Voice\\n{part}")
        
        return "\\n\\n".join(harmony_parts)
    
    def _generate_member_voice(self, member: str, activities: List[MusicalEntry]) -> str:
        """Generate musical voice for team member."""
        # Simple pattern generation based on member type
        patterns = {
            "♠️": "G2B2 d2B2",  # Structured patterns
            "🌿": "F2A2 c2A2",  # Flowing patterns
            "🎸": "C2E2 G2E2",  # Harmonic patterns  
            "🧵": "D2F#2 A2F#2" # Technical patterns
        }
        
        base_pattern = patterns.get(member, "C2E2 G2C2")
        
        # Extend pattern based on activity count
        activity_count = len(activities)
        measures = []
        
        for i in range(min(activity_count, 4)):
            measures.append(base_pattern)
            
        return f"|: {' | '.join(measures)} :|"
    
    def generate_session_theme(self, session_id: str) -> str:
        """Generate main theme for session."""
        melody = self.ledger.session_melodies.get(session_id)
        if not melody:
            return "C4 E4 G4 c4"  # Default theme
            
        # Extract key signature and build theme
        key = melody.key_signature
        
        # Simple theme generation based on key
        themes = {
            "C": "C4 E4 G4 c4",
            "G": "G4 B4 d4 g4", 
            "F": "F4 A4 c4 f4",
            "D": "D4 F#4 A4 d4"
        }
        
        return themes.get(key, "C4 E4 G4 c4")
    
    def export_full_composition(self, session_id: str) -> str:
        """Export complete ABC composition for session."""
        melody = self.ledger.session_melodies.get(session_id)
        if not melody:
            return ""
            
        composition = f"""X:1
T:{melody.title}
C:♠️🌿🎸🧵 G.Music Assembly  
M:{melody.time_signature}
L:1/8
K:{melody.key_signature}
Q:{melody.tempo}

% Main Session Theme
{self.generate_session_theme(session_id)}

% Team Harmony
{self.compose_team_harmony(session_id)}

% Session Progression
{melody.abc_notation}
"""
        
        return composition