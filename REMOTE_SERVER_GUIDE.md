# Remote Server WebView Application

A complete system that allows a local WebView app to seamlessly interact with your remote PHP server, making remote files appear as local.

## Architecture

```
Local Machine (WebView)
    ↓
Local HTTP Server (port 8001)
    ↓
Remote Filesystem Bridge (Python)
    ↓
HTTP/HTTPS to Remote Server
    ↓
Remote PHP Server (chat.chessers.club)
    ↓
Filesystem Operations
```

## Components

### 1. **remote_fs_bridge.py** (Python Client)
Bridges local Python app to remote PHP server via HTTP

**Key Classes:**
- `RemoteFilesystemBridge` - Main interface for file operations
- `LocalFileProxy` - Makes remote files appear as local file objects

**Methods:**
- `read(filepath)` - Read remote file
- `write(filepath, content)` - Write to remote file
- `append(filepath, content)` - Append to remote file
- `delete(filepath)` - Delete remote file
- `exists(filepath)` - Check if file exists
- `listdir(path)` - List directory contents
- `mkdir(path)` - Create directory
- `get_file_info(path)` - Get file metadata
- `execute_php(script, data)` - Execute PHP script on server

### 2. **remote_fs_api.php** (PHP Backend)
Place this on your remote server at: `http://chat.chessers.club/api/fs.php`

**Endpoints:**
- `POST /api/fs/read` - Read file
- `POST /api/fs/write` - Write file
- `POST /api/fs/append` - Append to file
- `POST /api/fs/delete` - Delete file
- `POST /api/fs/exists` - Check existence
- `POST /api/fs/listdir` - List directory
- `POST /api/fs/mkdir` - Create directory
- `POST /api/fs/info` - Get file info
- `POST /api/fs/execute/[script]` - Execute PHP script

**Configuration:**
```php
$CONFIG = [
    'root_directory' => __DIR__ . '/../data',
    'api_key' => getenv('REMOTE_FS_API_KEY'),
    'max_file_size' => 100 * 1024 * 1024,
];
```

### 3. **remote_server_app.py** (WebView App)
Complete WebView application with UI for remote file management

**Features:**
- Dashboard with server connection status
- File Manager - read/write/delete files
- PHP Executor - run PHP scripts with data
- Real-time status indicators

## Setup Instructions

### Step 1: Upload PHP API to Remote Server

```bash
# 1. Copy remote_fs_api.php to your server
scp remote_fs_api.php user@chat.chessers.club:/path/to/public_html/api/

# 2. Create data directory
ssh user@chat.chessers.club
mkdir -p /path/to/public_html/data
chmod 755 /path/to/public_html/data

# 3. Optional: Set API key (if you want authentication)
export REMOTE_FS_API_KEY="your-secret-key"
```

### Step 2: Configure Local App

```python
from remote_server_app import RemoteServerApp

app = RemoteServerApp(
    server_url="http://chat.chessers.club",
    api_key="your-secret-key"  # Optional
)
app.launch()
```

### Step 3: Run the App

```bash
python remote_server_app.py
```

This opens a WebView window at `http://localhost:8001/`

## Usage Examples

### Python Script - Read/Write Files

```python
from remote_fs_bridge import RemoteFilesystemBridge

bridge = RemoteFilesystemBridge("http://chat.chessers.club")

# Read a file
content = bridge.read('/data/config.txt')
print(content)

# Write a file
bridge.write('/data/log.txt', 'New log entry\n')

# Append to file
bridge.append('/data/log.txt', 'Another entry\n')

# Check if file exists
if bridge.exists('/data/backup.zip'):
    print("Backup exists")

# List files in directory
files = bridge.listdir('/data')
print(f"Files: {files}")

# Delete a file
bridge.delete('/data/temp.txt')

# Get file information
info = bridge.get_file_info('/data/archive.zip')
print(f"Size: {info['size']} bytes")
print(f"Modified: {info['modified']}")
```

### Using LocalFileProxy

```python
from remote_fs_bridge import RemoteFilesystemBridge, LocalFileProxy

bridge = RemoteFilesystemBridge("http://chat.chessers.club")

# Use as file object
with LocalFileProxy(bridge, '/data/data.json', 'r') as f:
    content = f.read()
    print(content)

# Write through proxy
with LocalFileProxy(bridge, '/data/output.txt', 'w') as f:
    f.write("Hello from remote server!")
```

### Execute Custom PHP

Create a PHP script at `http://chat.chessers.club/api/scripts/process_data.php`:

```php
<?php
// $data contains input from JavaScript
$name = $data['name'] ?? 'Unknown';
$age = $data['age'] ?? 0;

return [
    'success' => true,
    'message' => "Hello $name, you are $age years old",
    'processed_at' => date('Y-m-d H:i:s')
];
?>
```

Then call from app:

```python
result = bridge.execute_php('process_data', {
    'name': 'John',
    'age': 30
})
print(result)  # {'success': True, 'message': '...', 'processed_at': '...'}
```

## WebView Interface

The included WebView app provides a GUI with three tabs:

### 1. Dashboard
- Server connection status
- Quick info about capabilities

### 2. File Manager
- Read files from server
- Write files to server
- Delete files
- Real-time editing

### 3. Execute PHP
- Run custom PHP scripts
- Send JSON data
- View results in real-time

## Security Considerations

1. **API Key**: Use the optional API key for authentication
   ```php
   if (!$CONFIG['api_key']) { return true; }
   $provided_key = $_SERVER['HTTP_X_API_KEY'] ?? null;
   ```

2. **Path Validation**: All paths are validated to prevent directory traversal
   ```php
   if (strpos($path, '..') !== false) {
       throw new Exception('Directory traversal detected');
   }
   ```

3. **File Size Limits**: Configure max file size in PHP config
   ```php
   'max_file_size' => 100 * 1024 * 1024,  // 100MB
   ```

4. **Extension Whitelist**: Optional file type restrictions
   ```php
   'allowed_extensions' => ['txt', 'json', 'csv', 'php'],
   ```

5. **HTTPS**: Use HTTPS in production
   ```python
   bridge = RemoteFilesystemBridge("https://chat.chessers.club")
   ```

## Advanced: Custom PHP Scripts

Create reusable PHP scripts in `/api/scripts/` directory:

```php
<?php
// /api/scripts/generate_report.php
$report_data = $data['report_data'] ?? [];

// Generate report
$report = [
    'title' => 'Generated Report',
    'items' => count($report_data),
    'generated' => date('Y-m-d H:i:s'),
    'data' => $report_data
];

// Save to file
file_put_contents('/data/reports/' . time() . '.json', json_encode($report));

return [
    'success' => true,
    'report' => $report,
    'saved_to' => '/data/reports/'
];
?>
```

Call from Python:

```python
result = bridge.execute_php('generate_report', {
    'report_data': [1, 2, 3, 4, 5]
})
print(result)
```

## Troubleshooting

### Connection Failed
- Check server URL is correct
- Verify API endpoint is accessible: `http://chat.chessers.club/api/fs.php`
- Check firewall/network access

### Permission Denied
- Ensure PHP has write permissions to data directory
- Check directory ownership: `chown www-data:www-data /path/to/data`
- Verify permissions: `chmod 755 /path/to/data`

### File Not Found
- Verify file path (relative to configured root_directory)
- Use `exists()` to check before reading
- Check file permissions with `get_file_info()`

### API Key Issues
- Set environment variable on server: `export REMOTE_FS_API_KEY="key"`
- Pass API key to bridge: `RemoteFilesystemBridge(..., api_key="key")`
- Verify header is sent: `X-API-Key: your-key`

## Performance Tips

1. **Batch Operations**: Group multiple reads/writes
2. **Caching**: Cache frequently accessed files locally
3. **File Size**: Use appropriate chunk sizes for large files
4. **Network**: Use HTTPS with keep-alive connections

## Integration with Existing Apps

Use the bridge in your dotFly demo app:

```python
from remote_fs_bridge import RemoteFilesystemBridge

bridge = RemoteFilesystemBridge("http://chat.chessers.club")

# In API handler
def serve_page(page_id):
    content = bridge.read(f'/pages/{page_id}.json')
    return convert_to_html(json.loads(content))
```

This allows your demo app to serve pages from the remote server!

## Complete Workflow Example

```python
from remote_fs_bridge import RemoteFilesystemBridge

# Initialize bridge
bridge = RemoteFilesystemBridge(
    server_url="http://chat.chessers.club",
    api_key="optional-secret"
)

# Create data structure
bridge.mkdir('/data/projects')

# Write project file
project = {
    'name': 'My Project',
    'status': 'Active',
    'tasks': ['Design', 'Develop', 'Test']
}
bridge.write('/data/projects/current.json', json.dumps(project, indent=2))

# Read it back
content = bridge.read('/data/projects/current.json')
project = json.loads(content)
print(project)

# List all projects
projects = bridge.listdir('/data/projects')
print(f"Found {len(projects)} projects")

# Execute PHP to generate report
report = bridge.execute_php('generate_report', {
    'project': 'current.json'
})
print(report)
```

## Conclusion

This system gives you the power of a web server combined with the simplicity of local file operations. Your WebView app can access all server capabilities while maintaining a clean, Pythonic interface.

Key benefits:
- ✅ Local WebView with server-side logic
- ✅ Clean Python API for file operations
- ✅ Execute custom PHP scripts
- ✅ Web UI for manual operations
- ✅ Full security controls
- ✅ Scalable architecture
