"""
Remote Server WebView Application
Uses local WebView + remote PHP server for file operations
The app can read/write files on the remote server as if they were local
"""

import webview
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
from remote_fs_bridge import RemoteFilesystemBridge, LocalFileProxy


class RemoteAppHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for remote server app"""
    
    bridge = None
    
    def do_GET(self):
        """Handle GET requests"""
        path = self.path.lstrip('/')
        
        # Serve app pages
        if path == '' or path == 'index.html':
            self._serve_app_page('index.html')
        elif path.endswith('.html'):
            self._serve_app_page(path)
        elif path.startswith('api/'):
            self._handle_api(path)
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        path = self.path.lstrip('/')
        
        if path.startswith('api/'):
            self._handle_api(path)
        else:
            self.send_response(404)
            self.end_headers()
    
    def _serve_app_page(self, filename: str):
        """Serve app HTML page"""
        pages = {
            'index.html': self._get_index_html(),
            'dashboard.html': self._get_dashboard_html(),
            'files.html': self._get_files_html(),
        }
        
        if filename in pages:
            html = pages[filename]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(html.encode()))
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def _handle_api(self, path: str):
        """Handle API requests that interact with remote server"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode()) if body else {}
        except:
            data = {}
        
        parts = path.split('?')[0].split('/')
        action = parts[1] if len(parts) > 1 else 'unknown'
        
        try:
            result = None
            
            if action == 'read':
                file_path = data.get('path', '')
                content = self.bridge.read(file_path)
                result = {'success': True, 'content': content}
            
            elif action == 'write':
                file_path = data.get('path', '')
                content = data.get('content', '')
                self.bridge.write(file_path, content)
                result = {'success': True, 'message': 'File written'}
            
            elif action == 'listfiles':
                directory = data.get('path', '/')
                files = self.bridge.listdir(directory)
                result = {'success': True, 'files': files}
            
            elif action == 'execute':
                script = data.get('script', '')
                script_data = data.get('data', {})
                result = self.bridge.execute_php(script, script_data)
            
            elif action == 'test':
                # Test connection to remote server
                exists = self.bridge.exists('/test.txt')
                result = {'success': True, 'connected': True, 'message': 'Connected to remote server'}
            
            else:
                result = {'success': False, 'error': f'Unknown action: {action}'}
            
        except Exception as e:
            result = {'success': False, 'error': str(e)}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def _get_index_html(self) -> str:
        """Return main index page"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>Remote Server App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        header h1 { font-size: 2em; margin-bottom: 10px; }
        header p { opacity: 0.9; }
        nav {
            display: flex;
            background: #f5f5f5;
            border-bottom: 1px solid #ddd;
        }
        nav a {
            flex: 1;
            padding: 15px;
            text-align: center;
            text-decoration: none;
            color: #333;
            cursor: pointer;
            border-right: 1px solid #ddd;
            transition: background 0.3s;
        }
        nav a:hover, nav a.active {
            background: #667eea;
            color: white;
        }
        .content {
            padding: 30px;
            display: none;
        }
        .content.active {
            display: block;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
        textarea {
            min-height: 200px;
            resize: vertical;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
        }
        button:hover {
            background: #764ba2;
        }
        .message {
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
            display: none;
        }
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .file-list {
            list-style: none;
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
        }
        .file-list li {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        .file-list li:last-child {
            border-bottom: none;
        }
        .status {
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            padding: 15px;
            border-radius: 4px;
            color: #004085;
        }
        .status.connected {
            background: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 Remote Server App</h1>
            <p>Local WebView + Remote PHP Server Integration</p>
        </header>
        
        <nav>
            <a class="nav-link active" onclick="showContent('dashboard')">Dashboard</a>
            <a class="nav-link" onclick="showContent('files')">File Manager</a>
            <a class="nav-link" onclick="showContent('execute')">Execute PHP</a>
        </nav>
        
        <!-- Dashboard -->
        <div id="dashboard" class="content active">
            <div class="section">
                <h2>📊 Dashboard</h2>
                <div class="status" id="status">
                    Testing connection...
                </div>
            </div>
            
            <div class="section">
                <h2>📝 Quick Info</h2>
                <p>This app connects to your remote PHP server and treats it as if it were local.</p>
                <ul>
                    <li>Read/write files on remote server</li>
                    <li>Execute PHP scripts</li>
                    <li>Manage directories</li>
                    <li>All through a local WebView interface</li>
                </ul>
            </div>
        </div>
        
        <!-- File Manager -->
        <div id="files" class="content">
            <div class="section">
                <h2>📁 File Manager</h2>
                
                <div class="form-group">
                    <label>File Path:</label>
                    <input type="text" id="filePath" placeholder="/data/myfile.txt">
                </div>
                
                <div class="form-group">
                    <label>File Content:</label>
                    <textarea id="fileContent" placeholder="Enter file content..."></textarea>
                </div>
                
                <button onclick="readFile()">Read File</button>
                <button onclick="writeFile()">Write File</button>
                <button onclick="deleteFile()">Delete File</button>
                
                <div class="message" id="fileMessage"></div>
            </div>
        </div>
        
        <!-- Execute PHP -->
        <div id="execute" class="content">
            <div class="section">
                <h2>⚙️ Execute PHP</h2>
                
                <div class="form-group">
                    <label>Script Name:</label>
                    <input type="text" id="scriptName" placeholder="process_data">
                </div>
                
                <div class="form-group">
                    <label>Data (JSON):</label>
                    <textarea id="scriptData" placeholder='{"key": "value"}'>{}</textarea>
                </div>
                
                <button onclick="executePhp()">Execute</button>
                
                <div class="message" id="phpMessage"></div>
                
                <div class="form-group">
                    <label>Result:</label>
                    <textarea id="phpResult" readonly></textarea>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showContent(name) {
            document.querySelectorAll('.content').forEach(el => el.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        async function apiCall(action, data) {
            try {
                const response = await fetch(`api/${action}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (e) {
                return {success: false, error: e.message};
            }
        }
        
        async function readFile() {
            const path = document.getElementById('filePath').value;
            if (!path) {
                showMessage('fileMessage', 'Please enter a file path', 'error');
                return;
            }
            
            const result = await apiCall('read', {path});
            if (result.success) {
                document.getElementById('fileContent').value = result.content;
                showMessage('fileMessage', 'File read successfully', 'success');
            } else {
                showMessage('fileMessage', result.error, 'error');
            }
        }
        
        async function writeFile() {
            const path = document.getElementById('filePath').value;
            const content = document.getElementById('fileContent').value;
            
            if (!path) {
                showMessage('fileMessage', 'Please enter a file path', 'error');
                return;
            }
            
            const result = await apiCall('write', {path, content});
            if (result.success) {
                showMessage('fileMessage', 'File written successfully', 'success');
            } else {
                showMessage('fileMessage', result.error, 'error');
            }
        }
        
        async function deleteFile() {
            const path = document.getElementById('filePath').value;
            if (!path) {
                showMessage('fileMessage', 'Please enter a file path', 'error');
                return;
            }
            
            if (!confirm('Delete this file?')) return;
            
            const result = await apiCall('delete', {path});
            if (result.success) {
                document.getElementById('fileContent').value = '';
                showMessage('fileMessage', 'File deleted successfully', 'success');
            } else {
                showMessage('fileMessage', result.error, 'error');
            }
        }
        
        async function executePhp() {
            const script = document.getElementById('scriptName').value;
            const dataStr = document.getElementById('scriptData').value;
            
            if (!script) {
                showMessage('phpMessage', 'Please enter a script name', 'error');
                return;
            }
            
            let data = {};
            try {
                data = JSON.parse(dataStr);
            } catch (e) {
                showMessage('phpMessage', 'Invalid JSON data', 'error');
                return;
            }
            
            const result = await apiCall('execute', {script, data});
            document.getElementById('phpResult').value = JSON.stringify(result, null, 2);
            
            if (result.success) {
                showMessage('phpMessage', 'Script executed successfully', 'success');
            } else {
                showMessage('phpMessage', result.error, 'error');
            }
        }
        
        function showMessage(elementId, message, type) {
            const el = document.getElementById(elementId);
            el.textContent = message;
            el.className = `message ${type}`;
            el.style.display = 'block';
        }
        
        // Test connection on load
        window.addEventListener('load', async () => {
            const result = await apiCall('test', {});
            const statusEl = document.getElementById('status');
            
            if (result.connected) {
                statusEl.innerHTML = '<strong>✓ Connected to Remote Server</strong><br>Ready to read/write files';
                statusEl.classList.add('connected');
            } else {
                statusEl.innerHTML = '<strong>✗ Connection Failed</strong><br>Check server configuration';
            }
        });
    </script>
</body>
</html>
        '''
    
    def _get_dashboard_html(self) -> str:
        return self._get_index_html()  # Same as index
    
    def _get_files_html(self) -> str:
        return self._get_index_html()  # Same as index
    
    def log_message(self, format, *args):
        """Suppress logging"""
        pass


class RemoteServerApp:
    """WebView app for remote server operations"""
    
    def __init__(self, server_url: str = "http://chat.chessers.club", api_key: str = None, port: int = 8001):
        """
        Initialize app
        
        Args:
            server_url: Remote PHP server URL
            api_key: Optional API key
            port: Local HTTP server port
        """
        self.server_url = server_url
        self.api_key = api_key
        self.port = port
        self.bridge = RemoteFilesystemBridge(server_url, api_key)
        self.server = None
        self.server_thread = None
    
    def start_server(self):
        """Start local HTTP server"""
        RemoteAppHTTPHandler.bridge = self.bridge
        
        self.server = HTTPServer(('localhost', self.port), RemoteAppHTTPHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"HTTP server started on localhost:{self.port}")
    
    def stop_server(self):
        """Stop HTTP server"""
        if self.server:
            self.server.shutdown()
    
    def launch(self):
        """Launch WebView window"""
        self.start_server()
        time.sleep(0.5)
        
        url = f'http://localhost:{self.port}/'
        window = webview.create_window(
            title='Remote Server App',
            url=url,
            width=1200,
            height=800,
            resizable=True,
            background_color='#FFFFFF'
        )
        
        webview.start()
        self.stop_server()


if __name__ == '__main__':
    import sys
    
    server_url = "http://chat.chessers.club"
    api_key = None  # Set if your PHP API requires authentication
    
    print(f"Starting Remote Server App")
    print(f"Server: {server_url}")
    
    app = RemoteServerApp(server_url, api_key)
    app.launch()
