# Session State Architecture Summary

## What Changed

The Remote Filesystem Bridge now defaults to **session state (in-memory)** storage instead of persistent server storage.

## Key Features

### 🔵 Default Behavior: Session State
```python
bridge = RemoteFilesystemBridge("http://chat.chessers.club")

# All files stored in memory
bridge.write('/data/file.txt', 'content')

# When app closes → data is gone
# No server disk space used
# Lightning fast access
```

### 🟢 Opt-In Persistence: Via manifest.json
```json
{
  "storage": {
    "mode": "session",
    "persist": {
      "enabled": true,
      "paths": ["/logs/*", "/config/*"],
      "global": false
    }
  }
}
```

Only specified paths are saved to server disk.

### 🔴 Full Persistence: When Needed
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

All files persist to server.

## How It Works

1. **First Check**: Look in session memory (in-app storage)
2. **Second Check**: If not found and persistence enabled, check remote server
3. **Cache**: Remote files are cached in session for next access
4. **Save**: New writes go to memory, optionally to server based on config

## Session State Methods

```python
bridge = RemoteFilesystemBridge()

# Get all in-memory files
state = bridge.get_session_state()
# {'files': {...}, 'directories': {...}, 'mode': 'session'}

# Clear memory (keep server files intact)
bridge.clear_session()

# Export session for backup/transfer
bridge.export_session('/backup.json')

# Import saved session
bridge.import_session('/backup.json', merge=False)

# Load config from manifest
bridge.load_manifest_config(manifest)
```

## Configuration in manifest.json

### Session-Only (Default)
```json
{
  "storage": {
    "mode": "session",
    "persist": {"enabled": false}
  }
}
```
- All data in memory
- Lost on app close
- Zero server disk usage

### Session + Selective Persistence
```json
{
  "storage": {
    "mode": "session",
    "persist": {
      "enabled": true,
      "paths": ["/data/*", "/logs/*", "/exports/*.json"]
    }
  }
}
```
- Most data in memory
- Matching paths saved to server
- Control what persists

### Full Persistence
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
- All data saved to server
- Survives app restarts
- Traditional filesystem behavior

## Manifest.json Additions

Add to any app's manifest:

```json
{
  "name": "My App",
  ...
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

**Fields:**
- `mode`: `"session"` or `"persistent"`
- `persist.enabled`: Enable persistence
- `persist.paths`: Patterns to persist (glob patterns)
- `persist.global`: Persist everything

## Comparison

| Feature | Session | Session+Selective | Persistent |
|---------|---------|-------------------|------------|
| Speed | ⚡ Very Fast | ⚡ Very Fast | 🚀 Fast |
| Memory | Medium | Medium | Low |
| Disk Usage | None | Some | Full |
| App Restart | Lost | Partial | Preserved |
| Default | ✅ Yes | No | No |
| Config | None | manifest.json | manifest.json |

## Use Cases

**Session Only:**
- Demo apps
- Sandboxes
- Prototypes
- Testing
- Chat apps
- Real-time editors

**Session + Logs:**
- User apps with audit trails
- Services with logging
- Development environments

**Full Persistent:**
- Production apps
- Data management
- User storage
- Real databases

## Implementation Details

### Files Modified
- ✅ `remote_fs_bridge.py` - Added session state support
- ✅ `demo_app/manifest.json` - Added storage configuration
- ✅ `SESSION_STATE_GUIDE.md` - Complete documentation

### New Methods
```python
# Session management
get_session_state()      # Get all in-memory data
clear_session()          # Clear memory
export_session(path)     # Backup session
import_session(path)     # Restore session
load_manifest_config()   # Load storage settings
```

### New Parameters
```python
RemoteFilesystemBridge(
    session_mode=True,       # Use in-memory (default)
    persist_enabled=False    # Enable persistence
)

# Per-operation override
bridge.write(path, content, persist=True)   # Force persist
bridge.write(path, content, persist=False)  # Force memory
bridge.write(path, content, persist=None)   # Use config
```

## Benefits

✅ **Secure by Default** - Nothing saved unless explicitly enabled
✅ **Fast** - In-memory access is instant
✅ **Flexible** - Configure per app via manifest
✅ **Privacy-Friendly** - No unintended persistence
✅ **Backward Compatible** - Existing code still works
✅ **Declarative** - Storage behavior defined in manifest
✅ **GDPR-Friendly** - Opt-in persistence model

## Quick Start

```python
from remote_fs_bridge import RemoteFilesystemBridge
import json

# 1. Create bridge (session mode by default)
bridge = RemoteFilesystemBridge("http://chat.chessers.club")

# 2. Load app config
with open('manifest.json') as f:
    manifest = json.load(f)
bridge.load_manifest_config(manifest)

# 3. Use like normal (respects manifest settings)
bridge.write('/data/file.txt', 'content')

# Files are stored according to manifest.json storage config
```

That's it! Your app now automatically respects the storage configuration declared in manifest.json. 🎉
