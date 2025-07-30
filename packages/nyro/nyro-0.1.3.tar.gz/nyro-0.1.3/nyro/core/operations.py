"""
Advanced Redis Operations Module
🧵 Synth: Consolidating all advanced Redis patterns from bash scripts

Unifies functionality from:
- stream-add.sh, stream-read.sh (Redis Streams)
- push-list.sh, read-list.sh (List operations)  
- scan-garden.sh (Pattern scanning)
- create-walk.sh, create-full-payload.sh (Massive data handling)
- redis-mobile.sh, redis-rest.sh (Interactive operations)
"""

import json
import base64
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from pathlib import Path
import tempfile

from .client import RedisClient


class RedisOperations:
    """Advanced Redis operations consolidating all bash script functionality."""
    
    def __init__(self, client: RedisClient):
        """Initialize with Redis client."""
        self.client = client
    
    # List Operations (push-list.sh, read-list.sh)
    def push_list(self, list_name: str, element: str, direction: str = "left") -> bool:
        """Push element to Redis list (LPUSH/RPUSH)."""
        config = self.client._get_current_config()
        
        try:
            if self.client._is_rest_url(config.url):
                command = "lpush" if direction == "left" else "rpush"
                result = self.client._execute_rest_api(command, {
                    'key': list_name, 
                    'element': element
                })
                return result.get('result', 0) > 0
            else:
                redis_cmd = ['LPUSH' if direction == "left" else 'RPUSH', list_name, element]
                result = self.client._execute_redis_cli(redis_cmd)
                return int(result) > 0
        except Exception as e:
            print(f"🐛 Debug - Push error: {e}")
            return False
    
    def read_list(self, list_name: str, start: int = 0, stop: int = -1) -> List[str]:
        """Read from Redis list (LRANGE)."""
        config = self.client._get_current_config()
        
        try:
            if self.client._is_rest_url(config.url):
                result = self.client._execute_rest_api('lrange', {
                    'key': list_name,
                    'start': start,
                    'stop': stop
                })
                return result.get('result', [])
            else:
                result = self.client._execute_redis_cli(['LRANGE', list_name, str(start), str(stop)])
                if result:
                    return [line.strip() for line in result.split('\\n') if line.strip()]
                return []
        except Exception as e:
            print(f"🐛 Debug - Read list error: {e}")
            return []
    
    def get_list_length(self, list_name: str) -> int:
        """Get length of Redis list."""
        config = self.client._get_current_config()
        
        try:
            if self.client._is_rest_url(config.url):
                result = self.client._execute_rest_api('llen', {'key': list_name})
                return result.get('result', 0)
            else:
                result = self.client._execute_redis_cli(['LLEN', list_name])
                return int(result) if result else 0
        except Exception as e:
            print(f"🐛 Debug - List length error: {e}")
            return 0
    
    # Stream Operations (stream-add.sh, stream-read.sh)
    def stream_add(self, stream_name: str, fields: Dict[str, str], stream_id: str = "*") -> Optional[str]:
        """Add entry to Redis stream (XADD)."""
        config = self.client._get_current_config()
        
        # Add timestamp if not provided
        if 'timestamp' not in fields:
            fields['timestamp'] = datetime.now().isoformat()
        
        try:
            if self.client._is_rest_url(config.url):
                result = self.client._execute_rest_api('xadd', {
                    'key': stream_name,
                    'id': stream_id,
                    'fields': fields
                })
                return result.get('result')
            else:
                # Build Redis CLI command: XADD stream_name id field1 value1 field2 value2...
                cmd = ['XADD', stream_name, stream_id]
                for field, value in fields.items():
                    cmd.extend([field, str(value)])
                
                result = self.client._execute_redis_cli(cmd)
                return result if result else None
        except Exception as e:
            print(f"🐛 Debug - Stream add error: {e}")
            return None
    
    def stream_read(self, stream_name: str, count: int = 10, start_id: str = "-") -> List[Dict[str, Any]]:
        """Read from Redis stream (XRANGE)."""
        config = self.client._get_current_config()
        
        try:
            if self.client._is_rest_url(config.url):
                result = self.client._execute_rest_api('xrange', {
                    'key': stream_name,
                    'start': start_id,
                    'end': '+',
                    'count': count
                })
                return result.get('result', [])
            else:
                result = self.client._execute_redis_cli([
                    'XRANGE', stream_name, start_id, '+', 'COUNT', str(count)
                ])
                
                # Parse Redis CLI stream output
                entries = []
                if result:
                    lines = result.split('\\n')
                    for i in range(0, len(lines), 2):
                        if i + 1 < len(lines):
                            stream_id = lines[i].strip()
                            fields_line = lines[i + 1].strip()
                            
                            # Parse field-value pairs
                            fields = {}
                            if fields_line:
                                parts = fields_line.split()
                                for j in range(0, len(parts), 2):
                                    if j + 1 < len(parts):
                                        fields[parts[j]] = parts[j + 1]
                            
                            entries.append({
                                'id': stream_id,
                                'fields': fields
                            })
                
                return entries
        except Exception as e:
            print(f"🐛 Debug - Stream read error: {e}")
            return []
    
    def add_diary_entry(self, diary_name: str = "garden.diary", event: str = "", **kwargs) -> Optional[str]:
        """Add diary entry to stream (garden diary pattern from scripts)."""
        fields = {
            'event': event,
            'location': kwargs.get('location', 'terminal'),
            'mood': kwargs.get('mood', ''),
            'details': kwargs.get('details', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Remove empty fields
        fields = {k: v for k, v in fields.items() if v}
        
        return self.stream_add(diary_name, fields)
    
    def read_diary(self, diary_name: str = "garden.diary", count: int = 10) -> List[Dict[str, Any]]:
        """Read diary entries from stream."""
        return self.stream_read(diary_name, count)
    
    # Advanced Scanning (scan-garden.sh patterns)
    def scan_garden(self, pattern: str = "*", count: int = 100) -> Dict[str, Any]:
        """Enhanced key scanning with garden metaphor."""
        keys = self.client.scan_keys(pattern, count)
        
        # Group keys by patterns
        categories = {
            'flowers': [],    # Simple string keys
            'trees': [],      # Complex/nested keys  
            'streams': [],    # Stream keys
            'lists': [],      # List keys
            'other': []
        }
        
        for key in keys:
            if ':' in key:
                if 'stream' in key.lower() or 'diary' in key.lower():
                    categories['streams'].append(key)
                elif 'list' in key.lower():
                    categories['lists'].append(key)
                else:
                    categories['trees'].append(key)
            else:
                categories['flowers'].append(key)
        
        return {
            'pattern': pattern,
            'total_keys': len(keys),
            'categories': categories,
            'keys': keys
        }
    
    # Massive Data Handling (create-walk.sh, create-full-payload.sh patterns)
    def create_walking_payload(self, directory_path: str, max_size_mb: int = 10) -> Dict[str, Any]:
        """Create walking payload from directory (consolidated from create-walk.sh)."""
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        payload = {
            'type': 'walking_payload',
            'directory': str(directory.absolute()),
            'timestamp': datetime.now().isoformat(),
            'files': [],
            'structure': {},
            'metadata': {
                'total_files': 0,
                'total_size': 0,
                'max_size_mb': max_size_mb
            }
        }
        
        max_size_bytes = max_size_mb * 1024 * 1024
        current_size = 0
        
        # Walk directory tree
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)
            relative_root = root_path.relative_to(directory)
            
            for file in files:
                file_path = root_path / file
                relative_file = relative_root / file
                
                try:
                    file_size = file_path.stat().st_size
                    
                    # Check size limits
                    if current_size + file_size > max_size_bytes:
                        payload['metadata']['truncated'] = True
                        break
                    
                    # Read file content (text files only)
                    file_info = {
                        'path': str(relative_file),
                        'size': file_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    
                    if file_path.suffix in ['.py', '.js', '.ts', '.json', '.md', '.txt', '.yml', '.yaml']:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                file_info['content'] = content
                                current_size += len(content.encode('utf-8'))
                        except (UnicodeDecodeError, PermissionError):
                            file_info['content'] = '[Binary or unreadable file]'
                    else:
                        file_info['content'] = '[Binary file]'
                    
                    payload['files'].append(file_info)
                    payload['metadata']['total_files'] += 1
                    payload['metadata']['total_size'] += file_size
                    
                except (OSError, PermissionError):
                    continue
        
        return payload
    
    def store_massive_payload(self, key: str, payload: Dict[str, Any], chunk_size: int = 1024*1024) -> bool:
        """Store massive payload with chunking (from redis-mobile.sh patterns)."""
        try:
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode('utf-8')
            
            # If payload is small enough, store directly
            if len(payload_bytes) <= chunk_size:
                return self.client.set_key(key, payload_json)
            
            # Store in chunks
            chunks = []
            for i in range(0, len(payload_bytes), chunk_size):
                chunk = payload_bytes[i:i + chunk_size]
                chunk_encoded = base64.b64encode(chunk).decode('utf-8')
                chunks.append(chunk_encoded)
            
            # Store chunk metadata
            metadata = {
                'type': 'chunked_payload',
                'total_chunks': len(chunks),
                'chunk_size': chunk_size,
                'total_size': len(payload_bytes),
                'timestamp': datetime.now().isoformat()
            }
            
            # Store metadata
            if not self.client.set_key(f"{key}:metadata", json.dumps(metadata)):
                return False
            
            # Store chunks
            for i, chunk in enumerate(chunks):
                chunk_key = f"{key}:chunk:{i}"
                if not self.client.set_key(chunk_key, chunk):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def load_massive_payload(self, key: str) -> Optional[Dict[str, Any]]:
        """Load massive payload with chunking support."""
        try:
            # Try direct load first
            direct_data = self.client.get_key(key)
            if direct_data:
                return json.loads(direct_data)
            
            # Try chunked load
            metadata_key = f"{key}:metadata"
            metadata_json = self.client.get_key(metadata_key)
            if not metadata_json:
                return None
            
            metadata = json.loads(metadata_json)
            if metadata.get('type') != 'chunked_payload':
                return None
            
            # Reconstruct from chunks
            chunks = []
            for i in range(metadata['total_chunks']):
                chunk_key = f"{key}:chunk:{i}"
                chunk_data = self.client.get_key(chunk_key)
                if not chunk_data:
                    return None
                chunks.append(chunk_data)
            
            # Decode chunks
            payload_bytes = b''
            for chunk_encoded in chunks:
                chunk_bytes = base64.b64decode(chunk_encoded.encode('utf-8'))
                payload_bytes += chunk_bytes
            
            payload_json = payload_bytes.decode('utf-8')
            return json.loads(payload_json)
            
        except Exception:
            return None
    
    def export_to_clipboard(self, data: Any) -> bool:
        """Export data to clipboard (from mobile script patterns)."""
        try:
            import subprocess
            import platform
            
            if isinstance(data, dict):
                text = json.dumps(data, indent=2)
            else:
                text = str(data)
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(['pbcopy'], input=text.encode('utf-8'))
            elif system == "Linux":
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'))
            elif system == "Windows":
                subprocess.run(['clip'], input=text.encode('utf-8'))
            else:
                return False
            
            return True
        except Exception:
            return False