"""
Remote Filesystem Bridge
Connects local WebView app to remote PHP server for file operations
Treats remote files as if they were local
Uses session state (in-memory) by default, with optional persistence
"""

import requests
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import base64


class RemoteFilesystemBridge:
    """Bridge between local app and remote PHP server for file operations"""
    
    def __init__(self, server_url: str = "http://chat.chessers.club", api_key: str = None, 
                 session_mode: bool = True, persist_enabled: bool = False):
        """
        Initialize the bridge
        
        Args:
            server_url: Base URL of remote PHP server (e.g., http://chat.chessers.club)
            api_key: Optional API key for authentication
            session_mode: If True, use in-memory session state by default (no persistence)
            persist_enabled: If True (and session_mode=True), enable file persistence from manifest settings
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.api_endpoint = f"{self.server_url}/api/fs"
        self.session_mode = session_mode
        self.persist_enabled = persist_enabled
        
        # In-memory session storage (used when session_mode=True)
        self.session_storage: Dict[str, str] = {}
        self.session_directories: Dict[str, List[str]] = {}
        self.persistence_config = {}
        
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to remote server"""
        url = f"{self.api_endpoint}/{endpoint}"
        
        headers = kwargs.pop('headers', {})
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        headers['Content-Type'] = 'application/json'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, **kwargs)
            elif method == 'POST':
                response = requests.post(url, headers=headers, **kwargs)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, **kwargs)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'code': 'request_failed'
            }
    
    def read(self, filepath: str, encoding: str = 'utf-8') -> str:
        """
        Read a file from session state or remote server
        
        Args:
            filepath: Path to file
            encoding: Text encoding (default: utf-8)
        
        Returns:
            File contents as string
        """
        # Check session state first
        if self.session_mode and filepath in self.session_storage:
            return self.session_storage[filepath]
        
        # Fall back to remote server
        result = self._request('POST', 'read', json={
            'path': filepath,
            'encoding': encoding
        })
        
        if result.get('success'):
            content = result.get('content', '')
            if result.get('is_base64'):
                content = base64.b64decode(content).decode(encoding)
            
            # Cache in session
            if self.session_mode:
                self.session_storage[filepath] = content
            
            return content
        
        raise Exception(f"Failed to read {filepath}: {result.get('error')}")
    
    def write(self, filepath: str, content: str, encoding: str = 'utf-8', create_dirs: bool = True, 
              persist: bool = None) -> bool:
        """
        Write content to session state or remote server
        
        Args:
            filepath: Path to file
            content: Content to write
            encoding: Text encoding (default: utf-8)
            create_dirs: Create directories if they don't exist
            persist: Override persistence setting (None=use config)
        
        Returns:
            True if successful
        """
        # Determine if we should persist
        should_persist = persist if persist is not None else self._should_persist(filepath)
        
        # Always write to session
        if self.session_mode:
            self.session_storage[filepath] = content
            # Track directories
            directory = str(Path(filepath).parent)
            if directory not in self.session_directories:
                self.session_directories[directory] = []
            filename = str(Path(filepath).name)
            if filename not in self.session_directories[directory]:
                self.session_directories[directory].append(filename)
        
        # Write to remote server if persistence is enabled
        if should_persist and not self.session_mode:
            result = self._request('POST', 'write', json={
                'path': filepath,
                'content': content,
                'encoding': encoding,
                'create_dirs': create_dirs
            })
            
            if result.get('success'):
                return True
            
            raise Exception(f"Failed to write to {filepath}: {result.get('error')}")
        
        return True
    
    def append(self, filepath: str, content: str, encoding: str = 'utf-8', persist: bool = None) -> bool:
        """
        Append content to session state or remote server
        
        Args:
            filepath: Path to file
            content: Content to append
            encoding: Text encoding (default: utf-8)
            persist: Override persistence setting (None=use config)
        
        Returns:
            True if successful
        """
        should_persist = persist if persist is not None else self._should_persist(filepath)
        
        # Append to session
        if self.session_mode:
            if filepath in self.session_storage:
                self.session_storage[filepath] += content
            else:
                self.session_storage[filepath] = content
        
        # Append to remote server if persistence is enabled
        if should_persist and not self.session_mode:
            result = self._request('POST', 'append', json={
                'path': filepath,
                'content': content,
                'encoding': encoding
            })
            
            if result.get('success'):
                return True
            
            raise Exception(f"Failed to append to {filepath}: {result.get('error')}")
        
        return True
    
    def delete(self, filepath: str, persist: bool = None) -> bool:
        """Delete a file from session state or remote server"""
        should_persist = persist if persist is not None else self._should_persist(filepath)
        
        # Delete from session
        if self.session_mode and filepath in self.session_storage:
            del self.session_storage[filepath]
        
        # Delete from remote server if persistence is enabled
        if should_persist and not self.session_mode:
            result = self._request('DELETE', 'delete', json={'path': filepath})
            
            if result.get('success'):
                return True
            
            raise Exception(f"Failed to delete {filepath}: {result.get('error')}")
        
        return True
    
    def exists(self, filepath: str) -> bool:
        """Check if file exists in session state or remote server"""
        # Check session first
        if self.session_mode and filepath in self.session_storage:
            return True
        
        # Check remote server
        result = self._request('POST', 'exists', json={'path': filepath})
        return result.get('exists', False)
    
    def listdir(self, directory: str) -> List[str]:
        """List files in directory from session state or remote server"""
        # Check session first
        if self.session_mode and directory in self.session_directories:
            return self.session_directories[directory].copy()
        
        # Fall back to remote server
        result = self._request('POST', 'listdir', json={'path': directory})
        
        if result.get('success'):
            files = result.get('files', [])
            # Cache in session
            if self.session_mode:
                self.session_directories[directory] = files
            return files
        
        raise Exception(f"Failed to list {directory}: {result.get('error')}")
    
    def mkdir(self, directory: str, parents: bool = True) -> bool:
        """Create directory on remote server"""
        result = self._request('POST', 'mkdir', json={
            'path': directory,
            'parents': parents
        })
        
        if result.get('success'):
            return True
        
        raise Exception(f"Failed to create {directory}: {result.get('error')}")
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get file metadata (size, modified time, etc.)"""
        result = self._request('POST', 'info', json={'path': filepath})
        
        if result.get('success'):
            return result.get('info', {})
        
        raise Exception(f"Failed to get info for {filepath}: {result.get('error')}")
    
    def execute_php(self, script: str, data: Dict = None) -> Any:
        """
        Execute custom PHP script on remote server
        
        Args:
            script: PHP script to execute (relative to api directory)
            data: Data to send to PHP script
        
        Returns:
            Result from PHP execution
        """
        result = self._request('POST', f'execute/{script}', json=data or {})
        return result
    
    def _should_persist(self, filepath: str) -> bool:
        """
        Determine if a file should be persisted to remote storage
        
        Based on:
        1. persistence_config settings from manifest
        2. Explicit path patterns
        """
        if not self.persist_enabled:
            return False
        
        # Check if path matches persistent paths from manifest
        persistent_paths = self.persistence_config.get('paths', [])
        for pattern in persistent_paths:
            if self._path_matches(filepath, pattern):
                return True
        
        # Check if persistence is globally enabled
        if self.persistence_config.get('global', False):
            return True
        
        return False
    
    def _path_matches(self, filepath: str, pattern: str) -> bool:
        """Check if filepath matches a pattern"""
        import fnmatch
        return fnmatch.fnmatch(filepath, pattern)
    
    def load_manifest_config(self, manifest: Dict[str, Any]):
        """
        Load storage configuration from manifest.json
        
        Manifest should contain:
        {
            "storage": {
                "mode": "session",  # or "persistent"
                "persist": {
                    "enabled": true,
                    "paths": ["/data/*", "/logs/*"],
                    "global": false
                }
            }
        }
        """
        storage_config = manifest.get('storage', {})
        mode = storage_config.get('mode', 'session')
        
        if mode == 'session':
            self.session_mode = True
            self.persist_enabled = False
        elif mode == 'persistent':
            self.session_mode = False
            self.persist_enabled = True
        
        # Load persistence config
        persist_config = storage_config.get('persist', {})
        self.persist_enabled = persist_config.get('enabled', False)
        self.persistence_config = persist_config
    
    def get_session_state(self) -> Dict[str, Any]:
        """Get entire session state (in-memory files)"""
        return {
            'files': self.session_storage.copy(),
            'directories': self.session_directories.copy(),
            'mode': 'session' if self.session_mode else 'persistent',
            'persist_enabled': self.persist_enabled
        }
    
    def clear_session(self):
        """Clear all session state (memory)"""
        self.session_storage.clear()
        self.session_directories.clear()
    
    def export_session(self, filepath: str, encoding: str = 'utf-8'):
        """Export entire session to a single file for backup/transfer"""
        import json
        state = self.get_session_state()
        
        # Don't export directories, just the files
        export_data = {
            'timestamp': time.time(),
            'files': state['files'],
            'mode': state['mode']
        }
        
        if self.session_mode:
            self.session_storage[filepath] = json.dumps(export_data, indent=2)
        else:
            self.write(filepath, json.dumps(export_data, indent=2), persist=True)
    
    def import_session(self, filepath: str, encoding: str = 'utf-8', merge: bool = False):
        """Import session from exported file"""
        import json
        content = self.read(filepath, encoding)
        data = json.loads(content)
        
        if not merge:
            self.session_storage.clear()
        
        # Import files
        for filename, file_content in data.get('files', {}).items():
            self.session_storage[filename] = file_content


class LocalFileProxy:
    """
    Proxy that makes remote files appear as local files
    Use with Python's open() or as a context manager
    """
    
    def __init__(self, bridge: RemoteFilesystemBridge, filepath: str, mode: str = 'r'):
        """
        Initialize file proxy
        
        Args:
            bridge: RemoteFilesystemBridge instance
            filepath: Path to remote file
            mode: File mode ('r', 'w', 'a', 'rb', etc.)
        """
        self.bridge = bridge
        self.filepath = filepath
        self.mode = mode
        self.content = None
        self._position = 0
        
        # Load initial content for read modes
        if 'r' in mode and self.bridge.exists(filepath):
            self.content = self.bridge.read(filepath)
    
    def read(self, size: int = -1) -> str:
        """Read from file"""
        if self.content is None:
            self.content = self.bridge.read(self.filepath)
        
        if size == -1:
            result = self.content[self._position:]
            self._position = len(self.content)
        else:
            result = self.content[self._position:self._position + size]
            self._position += size
        
        return result
    
    def write(self, content: str) -> int:
        """Write to file"""
        if self.content is None:
            self.content = ""
        
        if 'a' in self.mode:
            # Append mode
            self.bridge.append(self.filepath, content)
            self.content += content
        else:
            # Write mode
            self.bridge.write(self.filepath, content)
            self.content = content
        
        return len(content)
    
    def close(self):
        """Close file"""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Example usage
if __name__ == '__main__':
    # Initialize bridge
    bridge = RemoteFilesystemBridge(
        server_url="http://chat.chessers.club",
        api_key="your-api-key"  # Set if needed
    )
    
    print("Remote Filesystem Bridge Initialized")
    print(f"Server: {bridge.server_url}")
    print()
    
    # Example: Check if file exists
    print("Testing file operations...")
    try:
        exists = bridge.exists('/data/test.txt')
        print(f"File exists: {exists}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nBridge ready for WebView integration!")
