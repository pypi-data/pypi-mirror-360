"""
Musical Ledger System
🎸 JamAI: Creating harmonic documentation for development sessions

Integrates music generation with session tracking using:
- ABC notation for session melodies
- Musical representation of code patterns  
- Rhythmic analysis of development flow
"""

import json
import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import re


@dataclass
class MusicalEntry:
    """Single musical ledger entry."""
    timestamp: str
    session_id: str
    activity_type: str  # 'analysis', 'implementation', 'testing', 'refactoring'
    description: str
    abc_notation: Optional[str] = None
    rhythmic_pattern: Optional[str] = None
    harmonic_context: Optional[str] = None
    team_member: Optional[str] = None  # ♠️🌿🎸🧵


@dataclass 
class SessionMelody:
    """Complete session melody composition."""
    session_id: str
    title: str
    abc_notation: str
    composition_notes: str
    tempo: int = 120
    key_signature: str = "C"
    time_signature: str = "4/4"


class MusicalLedger:
    """Musical ledger for tracking development sessions with harmonic integration."""
    
    def __init__(self, ledger_file: Optional[str] = None):
        """Initialize musical ledger."""
        self.ledger_file = Path(ledger_file or "testing/MUSICAL_LEDGER.json")
        self.ledger_file.parent.mkdir(exist_ok=True)
        
        self.entries: List[MusicalEntry] = []
        self.session_melodies: Dict[str, SessionMelody] = {}
        self.current_session_id: Optional[str] = None
        
        self._load_ledger()
    
    def _load_ledger(self) -> None:
        """Load existing ledger from file."""
        if self.ledger_file.exists():
            try:
                with open(self.ledger_file, 'r') as f:
                    data = json.load(f)
                
                # Load entries
                self.entries = [
                    MusicalEntry(**entry) for entry in data.get('entries', [])
                ]
                
                # Load session melodies
                melodies_data = data.get('session_melodies', {})
                self.session_melodies = {
                    session_id: SessionMelody(**melody_data)
                    for session_id, melody_data in melodies_data.items()
                }
                
                self.current_session_id = data.get('current_session_id')
                
            except (json.JSONDecodeError, TypeError) as e:
                print(f"⚠️ Warning: Could not load musical ledger: {e}")
    
    def _save_ledger(self) -> None:
        """Save ledger to file."""
        data = {
            'entries': [asdict(entry) for entry in self.entries],
            'session_melodies': {
                session_id: asdict(melody) 
                for session_id, melody in self.session_melodies.items()
            },
            'current_session_id': self.current_session_id,
            'last_updated': datetime.datetime.now().isoformat()
        }
        
        with open(self.ledger_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_session(self, session_title: str) -> str:
        """Start new musical session."""
        timestamp = datetime.datetime.now()
        session_id = f"session_{timestamp.strftime('%y%m%d_%H%M%S')}"
        
        self.current_session_id = session_id
        
        # Create initial session melody
        self.session_melodies[session_id] = SessionMelody(
            session_id=session_id,
            title=session_title,
            abc_notation="",  # Will be built progressively
            composition_notes=f"Musical session: {session_title}",
            tempo=120,
            key_signature="C",
            time_signature="4/4"
        )
        
        # Add opening entry
        self.add_entry(
            activity_type="session_start",
            description=f"🎼 Musical session started: {session_title}",
            team_member="🎸"
        )
        
        self._save_ledger()
        return session_id
    
    def add_entry(
        self, 
        activity_type: str,
        description: str,
        abc_notation: Optional[str] = None,
        rhythmic_pattern: Optional[str] = None,
        harmonic_context: Optional[str] = None,
        team_member: Optional[str] = None
    ) -> None:
        """Add musical entry to ledger."""
        
        if not self.current_session_id:
            self.start_session("Default Session")
        
        entry = MusicalEntry(
            timestamp=datetime.datetime.now().isoformat(),
            session_id=self.current_session_id,
            activity_type=activity_type,
            description=description,
            abc_notation=abc_notation,
            rhythmic_pattern=rhythmic_pattern,
            harmonic_context=harmonic_context,
            team_member=team_member
        )
        
        self.entries.append(entry)
        
        # Update session melody if ABC notation provided
        if abc_notation and self.current_session_id in self.session_melodies:
            melody = self.session_melodies[self.current_session_id]
            if melody.abc_notation:
                melody.abc_notation += f"\\n{abc_notation}"
            else:
                melody.abc_notation = abc_notation
        
        self._save_ledger()
    
    def get_session_entries(self, session_id: Optional[str] = None) -> List[MusicalEntry]:
        """Get all entries for a session."""
        target_session = session_id or self.current_session_id
        if not target_session:
            return []
        
        return [entry for entry in self.entries if entry.session_id == target_session]
    
    def generate_session_summary(self, session_id: Optional[str] = None) -> str:
        """Generate musical summary of session."""
        target_session = session_id or self.current_session_id
        if not target_session:
            return "No active session"
        
        entries = self.get_session_entries(target_session)
        melody = self.session_melodies.get(target_session)
        
        summary = f"🎼 Musical Session Summary: {target_session}\\n"
        summary += "=" * 50 + "\\n\\n"
        
        if melody:
            summary += f"**Title**: {melody.title}\\n"
            summary += f"**Key**: {melody.key_signature} **Tempo**: {melody.tempo} **Time**: {melody.time_signature}\\n\\n"
        
        # Activity breakdown
        activity_counts = {}
        team_activities = {}
        
        for entry in entries:
            activity_counts[entry.activity_type] = activity_counts.get(entry.activity_type, 0) + 1
            if entry.team_member:
                if entry.team_member not in team_activities:
                    team_activities[entry.team_member] = []
                team_activities[entry.team_member].append(entry.activity_type)
        
        summary += "**🎵 Rhythmic Analysis:**\\n"
        for activity, count in activity_counts.items():
            summary += f"- {activity}: {count} measures\\n"
        
        summary += "\\n**👥 Team Harmonies:**\\n"
        for member, activities in team_activities.items():
            summary += f"- {member}: {', '.join(set(activities))}\\n"
        
        if melody and melody.abc_notation:
            summary += f"\\n**🎼 Session ABC Notation:**\\n```\\n{melody.abc_notation}\\n```\\n"
        
        return summary
    
    def export_abc_file(self, session_id: Optional[str] = None, output_file: Optional[str] = None) -> str:
        """Export session melody as ABC file."""
        target_session = session_id or self.current_session_id
        if not target_session or target_session not in self.session_melodies:
            raise ValueError("No melody found for session")
        
        melody = self.session_melodies[target_session]
        output_path = Path(output_file or f"assembly_session_melody_{target_session}.abc")
        
        abc_content = f"""X:1
T:{melody.title}
M:{melody.time_signature}
L:1/8
Q:{melody.tempo}
K:{melody.key_signature}
{melody.abc_notation}
"""
        
        with open(output_path, 'w') as f:
            f.write(abc_content)
        
        return str(output_path)
    
    def add_team_activity(self, team_member: str, activity: str, description: str, abc_fragment: Optional[str] = None) -> None:
        """Add team member activity with musical notation."""
        rhythmic_patterns = {
            "♠️": "X-x-X-x-",  # Nyro: Structural patterns
            "🌿": "~~o~~o~~",   # Aureon: Flowing patterns  
            "🎸": "G-D-A-E-",   # JamAI: Harmonic patterns
            "🧵": "|-|-|-|-"    # Synth: Terminal patterns
        }
        
        self.add_entry(
            activity_type=activity,
            description=f"{team_member} {description}",
            abc_notation=abc_fragment,
            rhythmic_pattern=rhythmic_patterns.get(team_member),
            team_member=team_member
        )