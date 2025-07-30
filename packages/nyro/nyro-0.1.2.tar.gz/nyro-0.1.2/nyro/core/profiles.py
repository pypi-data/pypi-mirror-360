"""
Profile Management Module
♠️ Nyro: Structural unification of profile switching logic

Consolidates the profile management patterns from:
- redis-mobile.sh (lines 20-45)
- redis-rest.sh (lines 19-44) 
- All script env loading patterns
"""

import os
from typing import Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProfileConfig:
    """Configuration for a Redis database profile."""
    url: str
    token: str
    name: str
    description: Optional[str] = None


class ProfileManager:
    """Manages multiple Redis database profiles and credentials."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize profile manager with environment file."""
        self.env_file = env_file or self._find_env_file()
        self.profiles: Dict[str, ProfileConfig] = {}
        self.current_profile: Optional[str] = None
        self._load_profiles()
    
    def _find_env_file(self) -> str:
        """Find .env file following bash script patterns."""
        candidates = [
            ".env",
            "/workspace/.env", 
            os.path.expanduser("~/.nyro/.env")
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
                
        raise FileNotFoundError("No .env file found. Run install.sh or create manually.")
    
    def _load_profiles(self) -> None:
        """Load all profiles from environment file."""
        if not os.path.exists(self.env_file):
            raise FileNotFoundError(f"Environment file not found: {self.env_file}")
        
        env_vars = {}
        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes from values
                    clean_value = value.strip().strip('"').strip("'")
                    env_vars[key.strip()] = clean_value
        
        # Load default profile
        default_url = env_vars.get('KV_REST_API_URL') or env_vars.get('REDIS_URL')
        default_token = env_vars.get('KV_REST_API_TOKEN') or env_vars.get('REDIS_TOKEN')
        
        if default_url and default_token:
            self.profiles['default'] = ProfileConfig(
                url=default_url,
                token=default_token, 
                name='default',
                description='Default Redis database'
            )
            self.current_profile = 'default'
        
        # Load named profiles (PROFILE_X_URL, PROFILE_X_TOKEN pattern)
        profile_names = set()
        for key in env_vars:
            if key.startswith('PROFILE_') and key.endswith('_URL'):
                profile_name = key[8:-4].lower()  # Remove PROFILE_ and _URL
                profile_names.add(profile_name)
        
        for profile_name in profile_names:
            url_key = f'PROFILE_{profile_name.upper()}_URL'
            token_key = f'PROFILE_{profile_name.upper()}_TOKEN'
            
            url = env_vars.get(url_key)
            token = env_vars.get(token_key)
            
            if url and token:
                self.profiles[profile_name] = ProfileConfig(
                    url=url,
                    token=token,
                    name=profile_name,
                    description=f'Redis profile: {profile_name}'
                )
    
    def list_profiles(self) -> Dict[str, ProfileConfig]:
        """Get all available profiles."""
        return self.profiles.copy()
    
    def get_profile(self, name: str) -> Optional[ProfileConfig]:
        """Get specific profile configuration."""
        return self.profiles.get(name)
    
    def switch_profile(self, name: str) -> bool:
        """Switch to specified profile."""
        if name not in self.profiles:
            return False
        
        self.current_profile = name
        return True
    
    def get_current_profile(self) -> Optional[ProfileConfig]:
        """Get currently active profile."""
        if self.current_profile:
            return self.profiles.get(self.current_profile)
        return None
    
    def validate_profile(self, name: str) -> bool:
        """Validate that profile has required credentials."""
        profile = self.profiles.get(name)
        return profile is not None and bool(profile.url) and bool(profile.token)