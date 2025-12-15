# Session State vs Persistent Storage

## Overview

The Remote Filesystem Bridge now supports two modes of operation:

1. **Session State (Default)** - In-memory storage that exists only during the app session
2. **Persistent Storage** - Files saved to remote server disk for permanent storage

By default, all file operations use **session state** (in-memory). Files are only persisted to the remote server if explicitly enabled via `manifest.json`.

## Architecture

```
Request to Read/Write File
        ↓
┌───────────────────────┐
│ Session State Check   │
│ (In-Memory)           │
├───────────────────────┤
│ ✓ Found?              │
│ Return immediately    │
└───────────────────────┘
        ↓ No
┌───────────────────────┐
│ Remote Server Check   │
│ (Only if enabled)     │
├───────────────────────┤
│ ✓ Found?              │
│ Cache in session      │
│ Return                │
└───────────────────────┘
```

## Configuration in manifest.json

### Session Mode (Default)

```json
{
  "storage": {
    "mode": "session",
    "persist": {
      "enabled": false,
      "paths": [],
      "global": false
    }
  }
}
```

**Behavior:**
- All files stored in app memory
- Fast access
- Data lost when app closes
- No server disk space used
- Perfect for temporary data, caching, session variables

### Selective Persistence

```json
{
  "storage": {
    "mode": "session",
    "persist": {
      "enabled": true,
      "paths": ["/data/*", "/logs/*", "/exports/*.json"],
      "global": false
    }
  }
}
```

**Behavior:**
- Most files in session memory
- Specific paths saved to server
- Selective persistence for important files
- Example: Keep logs but lose temp files

### Full Persistence

```json
{
  "storage": {
    "mode": "persistent",
    "persist": {
      "enabled": true,
      "paths": [],
      "global": true
    }
  }
}
```

**Behavior:**
- All files saved to remote server disk
- Survives app restarts
- All data persistent
- Full server filesystem interaction

## Usage Examples

### Initialize with Session State (Default)

```python
from remote_fs_bridge import RemoteFilesystemBridge

# Creates bridge in session mode by default
bridge = RemoteFilesystemBridge(
    server_url="http://chat.chessers.club"
)

# This stores in memory only
bridge.write('/data/temp.txt', 'Session data')

# File exists in memory
print(bridge.exists('/data/temp.txt'))  # True

# App closes, file is gone
```

### Load Configuration from Manifest

```python
import json
from remote_fs_bridge import RemoteFilesystemBridge

# Read manifest
with open('manifest.json') as f:
    manifest = json.load(f)

# Create bridge and load config
bridge = RemoteFilesystemBridge(
    server_url="http://chat.chessers.club"
)
bridge.load_manifest_config(manifest)

# Now behavior depends on manifest storage config
bridge.write('/data/users.json', '{}')
# ✓ Saved to session memory
# ✓ Also saved to server if path matches or global=true
```

### Selective Persistence by Path

```python
bridge = RemoteFilesystemBridge(
    server_url="http://chat.chessers.club",
    session_mode=True,
    persist_enabled=True
)

bridge.persistence_config = {
    'enabled': True,
    'paths': ['/data/*', '/config/*'],
    'global': False
}

# This goes to memory + server (matches /data/*)
bridge.write('/data/users.json', '{}')

# This goes to memory only (doesn't match patterns)
bridge.write('/temp/cache.txt', 'temp data')

# Explicit persistence override
bridge.write('/other/file.txt', 'content', persist=True)
```

### Override Persistence Per Operation

```python
# Always save to server for this operation
bridge.write('/critical.json', data, persist=True)

# Never save to server (keep in memory)
bridge.write('/temp.txt', data, persist=False)

# Use config setting (default)
bridge.write('/normal.txt', data, persist=None)
```

## Session State Operations

### Get All Session Data

```python
session = bridge.get_session_state()
# {
#   'files': {'/data/user1.txt': 'content', ...},
#   'directories': {'/data': ['user1.txt', 'user2.txt'], ...},
#   'mode': 'session',
#   'persist_enabled': True
# }
```

### Clear Session

```python
# Removes all in-memory files
bridge.clear_session()

# Files on server remain untouched (if persisted)
```

### Export Session to File

```python
# Save entire session to a file (useful for backup/transfer)
bridge.export_session('/backup/session_export.json')

# Creates a JSON file with all session data
# Can be imported into another session
```

### Import Session

```python
# Import previously exported session
bridge.import_session('/backup/session_export.json', merge=False)

# merge=False: Replace session
# merge=True: Merge with existing files (new files added, existing kept)
```

## Practical Examples

### Ephemeral Session App

```json
{
  "storage": {
    "mode": "session",
    "persist": {
      "enabled": false,
      "global": false
    }
  }
}
```

```python
bridge = RemoteFilesystemBridge()
bridge.load_manifest_config(manifest)

# App data is purely in-memory
users = {'active': []}
bridge.write('/session/users.txt', json.dumps(users))

# When user closes app → data gone
# Perfect for: Temporary editors, sandboxes, demo apps
```

### Log Persistent App

```json
{
  "storage": {
    "mode": "session",
    "persist": {
      "enabled": true,
      "paths": ["/logs/*"],
      "global": false
    }
  }
}
```

```python
bridge = RemoteFilesystemBridge()
bridge.load_manifest_config(manifest)

# Session state: fast access
bridge.write('/cache/query.json', '{}')  # Memory only

# Persistent: saved to server
bridge.write('/logs/app.log', 'Entry...')  # Memory + server

# Log survives app restart, cache is discarded
```

### Full Persistence App

```json
{
  "storage": {
    "mode": "persistent",
    "persist": {
      "enabled": true,
      "global": true
    }
  }
}
```

```python
bridge = RemoteFilesystemBridge()
bridge.load_manifest_config(manifest)

# Everything is persistent
bridge.write('/data/users.json', '{}')  # Server disk
bridge.write('/config/app.json', '{}')  # Server disk

# All data survives app restart
# Perfect for: Real applications, data storage, user files
```

## Performance Considerations

| Mode | Speed | Memory | Disk | Restart |
|------|-------|--------|------|---------|
| **Session Only** | ⚡ Very Fast | Medium | None | Lost |
| **Session + Selective** | ⚡ Very Fast | Medium | Some | Partial |
| **Full Persistent** | 🚀 Fast | Low | Full | Preserved |

## Use Cases

### ✅ Session State Only
- Chat applications
- Real-time editors
- Demo/sandbox apps
- Temporary calculations
- Load testing
- Prototype apps

### ✅ Session + Log Persistence
- User applications with audit trails
- Apps that need logging but discard temp data
- Services with session-based access
- Development/testing with persistent logs

### ✅ Full Persistence
- Production applications
- Data management systems
- User file storage
- Real databases
- Configuration management
- Long-term projects

## Migration Between Modes

### From Session to Persistent

```python
# Export current session
bridge.export_session('/data/session_backup.json')

# Create new bridge in persistent mode
new_bridge = RemoteFilesystemBridge(session_mode=False)

# Import session data
new_bridge.import_session('/data/session_backup.json')
```

### From Persistent to Session

```python
# All server data stays on server
# Just create session bridge
session_bridge = RemoteFilesystemBridge(session_mode=True)

# To migrate specific files:
users = old_bridge.read('/data/users.json')
session_bridge.write('/data/users.json', users)
```

## Security & Privacy

**Session State Benefits:**
- ✅ No unintended disk writes
- ✅ No persistent user data on server
- ✅ Privacy: Data not stored
- ✅ Compliance: GDPR-friendly

**Persistence Benefits:**
- ✅ Explicit storage via manifest
- ✅ Controlled via configuration
- ✅ Audit trail: What gets saved
- ✅ Opt-in for each app

## Default Behavior Summary

| Setting | Default | Description |
|---------|---------|-------------|
| `mode` | `"session"` | Uses in-memory storage |
| `persist.enabled` | `false` | No persistence to server |
| `persist.paths` | `[]` | No selective paths |
| `persist.global` | `false` | No global persistence |

**Result:** All files stored in memory, disappear when app closes.

## Conclusion

This design provides:

1. **Safety First** - Session state by default
2. **Flexibility** - Enable persistence only when needed
3. **Control** - Selective persistence per path
4. **Performance** - In-memory speed when possible
5. **Simplicity** - Works out of the box without configuration

Combine with `manifest.json` for powerful, declarative app behavior! 🚀
