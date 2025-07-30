"""
Unified Redis Client Module  
🧵 Synth: Terminal orchestration of all Redis connection patterns

Consolidates connection logic from:
- get-key.sh, set-key.sh (TLS detection lines 29-36)
- redis-mobile.sh, redis-rest.sh (REST API patterns)
- All script Redis CLI and curl implementations
"""

import requests
import subprocess
import os
from typing import Optional, Any, Dict, List, Union
from urllib.parse import urlparse
import json
import tempfile
from pathlib import Path

from .profiles import ProfileManager, ProfileConfig


class RedisConnectionError(Exception):
    """Redis connection related errors."""
    pass


class RedisClient:
    """Unified Redis client supporting both CLI and REST API operations."""
    
    def __init__(self, profile_manager: Optional[ProfileManager] = None):
        """Initialize Redis client with profile manager."""
        self.profile_manager = profile_manager or ProfileManager()
        self.temp_dir = Path(tempfile.gettempdir()) / "nyro-temp"
        self.temp_dir.mkdir(exist_ok=True)
        
    def _get_current_config(self) -> ProfileConfig:
        """Get current profile configuration."""
        config = self.profile_manager.get_current_profile()
        if not config:
            raise RedisConnectionError("No active profile. Use switch_profile() first.")
        return config
    
    def _is_tls_url(self, url: str) -> bool:
        """Check if Redis URL requires TLS (rediss://)."""
        return url.startswith('rediss://')
    
    def _is_rest_url(self, url: str) -> bool:
        """Check if URL is REST API endpoint."""
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https')
    
    def _execute_redis_cli(self, command: List[str]) -> str:
        """Execute Redis CLI command with proper TLS handling."""
        config = self._get_current_config()
        
        if self._is_rest_url(config.url):
            raise RedisConnectionError("Cannot use Redis CLI with REST API URL. Use REST methods instead.")
        
        # Build Redis CLI command with TLS support
        cli_cmd = ['redis-cli']
        
        if self._is_tls_url(config.url):
            cli_cmd.extend(['--tls', '-u', config.url, '--no-auth-warning'])
        else:
            cli_cmd.extend(['-u', config.url, '--no-auth-warning'])
        
        cli_cmd.extend(command)
        
        try:
            result = subprocess.run(
                cli_cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RedisConnectionError(f"Redis CLI error: {e.stderr}")
        except FileNotFoundError:
            raise RedisConnectionError("redis-cli not found. Install Redis CLI or use REST API methods.")
    
    def _execute_rest_api(self, endpoint: str, data: Optional[Dict] = None, method: str = 'POST') -> Any:
        """Execute REST API call with proper authentication."""
        config = self._get_current_config()
        
        if not self._is_rest_url(config.url):
            raise RedisConnectionError("Cannot use REST API with Redis CLI URL. Use CLI methods instead.")
        
        # For Upstash, commands go to base URL directly
        url = config.url.rstrip('/')
        headers = {
            'Authorization': f'Bearer {config.token.strip("\'\"\"\'").strip()}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            else:
                # Upstash expects Redis commands as arrays
                if endpoint == 'set' and data:
                    command = ["SET", data['key'], data['value']]
                elif endpoint == 'get' and data:
                    command = ["GET", data['key']]
                elif endpoint == 'del' and data:
                    command = ["DEL", data['key']]
                elif endpoint == 'scan' and data:
                    command = ["SCAN", str(data.get('cursor', 0)), "MATCH", data.get('match', '*'), "COUNT", str(data.get('count', 100))]
                elif endpoint == 'ping':
                    command = ["PING"]
                elif endpoint == 'lpush' and data:
                    command = ["LPUSH", data['key'], data['element']]
                elif endpoint == 'rpush' and data:
                    command = ["RPUSH", data['key'], data['element']]
                elif endpoint == 'lrange' and data:
                    command = ["LRANGE", data['key'], str(data['start']), str(data['stop'])]
                elif endpoint == 'llen' and data:
                    command = ["LLEN", data['key']]
                elif endpoint == 'xadd' and data:
                    # XADD stream_name id field1 value1 field2 value2...
                    command = ["XADD", data['key'], data.get('id', '*')]
                    for field, value in data.get('fields', {}).items():
                        command.extend([field, str(value)])
                elif endpoint == 'xrange' and data:
                    command = ["XRANGE", data['key'], data.get('start', '-'), data.get('end', '+')]
                    if 'count' in data:
                        command.extend(["COUNT", str(data['count'])])
                else:
                    # Generic command format
                    command = data if isinstance(data, list) else [endpoint]
                
                response = requests.post(url, headers=headers, json=command, timeout=30)
            
            response.raise_for_status()
            
            # Handle different response types
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                result = response.json()
                # Upstash returns {"result": value} format
                return result
            else:
                return response.text
                
        except requests.exceptions.RequestException as e:
            raise RedisConnectionError(f"REST API error: {e}")
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to specified profile."""
        return self.profile_manager.switch_profile(profile_name)
    
    def list_profiles(self) -> Dict[str, ProfileConfig]:
        """List all available profiles."""
        return self.profile_manager.list_profiles()
    
    def get_current_profile_name(self) -> Optional[str]:
        """Get current profile name."""
        return self.profile_manager.current_profile
    
    def test_connection(self) -> bool:
        """Test connection to current Redis instance."""
        try:
            config = self._get_current_config()
            
            if self._is_rest_url(config.url):
                # Test REST API connection with Upstash
                result = self._execute_rest_api('ping')
                return result.get('result') == 'PONG' if isinstance(result, dict) else str(result).upper() == 'PONG'
            else:
                # Test Redis CLI connection  
                result = self._execute_redis_cli(['PING'])
                return result.upper() == 'PONG'
            
        except RedisConnectionError:
            return False
    
    # Basic Redis Operations (unified interface)
    def set_key(self, key: str, value: str) -> bool:
        """Set a Redis key-value pair."""
        config = self._get_current_config()
        
        try:
            if self._is_rest_url(config.url):
                result = self._execute_rest_api('set', {'key': key, 'value': value})
                return result.get('result') == 'OK'
            else:
                result = self._execute_redis_cli(['SET', key, value])
                return result == 'OK'
        except RedisConnectionError:
            return False
    
    def get_key(self, key: str) -> Optional[str]:
        """Get value for Redis key."""
        config = self._get_current_config()
        
        try:
            if self._is_rest_url(config.url):
                result = self._execute_rest_api('get', {'key': key})
                return result.get('result')
            else:
                result = self._execute_redis_cli(['GET', key])
                return result if result != '(nil)' else None
        except RedisConnectionError:
            return None
    
    def delete_key(self, key: str) -> bool:
        """Delete a Redis key."""
        config = self._get_current_config()
        
        try:
            if self._is_rest_url(config.url):
                result = self._execute_rest_api('del', {'key': key})
                return result.get('result', 0) > 0
            else:
                result = self._execute_redis_cli(['DEL', key])
                return int(result) > 0
        except (RedisConnectionError, ValueError):
            return False
    
    def scan_keys(self, pattern: str = '*', count: int = 100) -> List[str]:
        """Scan Redis keys with pattern."""
        config = self._get_current_config()
        
        try:
            if self._is_rest_url(config.url):
                result = self._execute_rest_api('scan', {
                    'cursor': 0, 
                    'match': pattern, 
                    'count': count
                })
                return result.get('result', [])
            else:
                result = self._execute_redis_cli(['SCAN', '0', 'MATCH', pattern, 'COUNT', str(count)])
                lines = result.split('\n')
                if len(lines) >= 2:
                    # Skip cursor, return keys
                    keys_line = lines[1] if len(lines) > 1 else ""
                    return [k.strip() for k in keys_line.split() if k.strip()]
                return []
        except RedisConnectionError:
            return []