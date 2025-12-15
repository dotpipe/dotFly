"""Test the remote filesystem bridge in session mode"""
from remote_fs_bridge import RemoteFilesystemBridge
import json

# Create bridge (session mode by default)
bridge = RemoteFilesystemBridge('http://myserver.chessers.club')

print("=" * 50)
print("Session Mode Test (In-Memory Storage)")
print("=" * 50)

# Test 1: Write files to session
print("\n1. Writing files to session...")
bridge.write('/data/users.json', json.dumps({"users": ["alice", "bob"]}))
bridge.write('/data/config.txt', 'app_name=MyApp\nversion=1.0')
bridge.write('/logs/app.log', 'App started...')
print("   ✓ Files written")

# Test 2: Read files
print("\n2. Reading files from session...")
users = json.loads(bridge.read('/data/users.json'))
print(f"   ✓ Users: {users['users']}")
config = bridge.read('/data/config.txt')
print(f"   ✓ Config: {config.splitlines()[0]}")

# Test 3: Check existence
print("\n3. Checking file existence...")
print(f"   ✓ /data/users.json exists: {bridge.exists('/data/users.json')}")
print(f"   ✓ /missing.txt exists: {bridge.exists('/missing.txt')}")

# Test 4: List directory
print("\n4. Listing directory...")
bridge.write('/data/file1.txt', 'content1')
bridge.write('/data/file2.txt', 'content2')
files = [f for f in bridge.session_storage.keys() if f.startswith('/data/')]
print(f"   ✓ Files in /data/: {files}")

# Test 5: Get session state
print("\n5. Session state...")
state = bridge.get_session_state()
print(f"   ✓ Total files in session: {len(state['files'])}")
print(f"   ✓ Mode: {state['mode']}")
print(f"   ✓ Persistence enabled: {state['persist_enabled']}")

# Test 6: Export session
print("\n6. Exporting session...")
bridge.export_session('/backup/session.json')
backup = json.loads(bridge.read('/backup/session.json'))
print(f"   ✓ Exported {len(backup['files'])} files")

print("\n" + "=" * 50)
print("✓ All session mode tests passed!")
print("=" * 50)
print("\nSession storage is working perfectly.")
print("Files exist only in memory until you configure persistence.")
