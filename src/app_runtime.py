"""
dotFly App Runtime - Windows WebView application loader
Loads JSON-based apps and serves them in a native Windows WebView
Uses pywebview for cross-platform WebView support
"""

import webview
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import urllib.parse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .app_manager import AppManager


class AppHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves JSON pages and assets"""
    
    app_manager = None
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Handle favicon
        if path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
            return
        
        # Handle dotpipe.js from project root
        if path == '/dotpipe.js':
            self._serve_dotpipe()
            return
        
        # Handle .json file requests (for tabs/AJAX loading)
        if path.endswith('.json'):
            self._serve_json_file(path)
            return
                # Handle static HTML files
        if path.endswith('.html') or path == '/console':
            html_path = path if path.endswith('.html') else '/console.html'
            self._serve_static_html(html_path)
            return
                # Handle asset files
        if path.startswith('/assets/'):
            self._serve_asset(path[8:])
            return
        
        # Handle API endpoints
        if path.startswith('/api/'):
            self._handle_api(path)
            return
        
        # Handle page requests
        if path == '/':
            path = '/' + self.app_manager.manifest.main_page
        
        self._serve_page(path)
    
    def do_POST(self):
        """Handle POST requests (forms, API calls)"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Handle API endpoints
        if path.startswith('/api/'):
            self._handle_api_post(path)
            return
        
        # Default 404
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def _serve_page(self, page_path: str):
        """Serve pre-rendered HTML or generate from JSON"""
        # Remove leading slash
        page_id = page_path.lstrip('/')
        
        try:
            # Check if pre-rendered HTML exists
            pages_dir = Path(self.app_manager.app_dir) / 'pages'
            json_file = pages_dir / f"{page_id}.json"
            html_file = pages_dir / f"{page_id}.html"
            
            if html_file.exists():
                # Serve pre-rendered HTML
                html = html_file.read_text(encoding='utf-8')
            else:
                # Generate HTML from JSON using modala()
                page_json = self.app_manager.get_page_json(page_id)
                
                html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'unsafe-hashes'; style-src 'self' 'unsafe-inline' 'unsafe-hashes'; img-src 'self' data: https: http:;">
    <title>Server Console</title>
</head>
<body id="pageBody">
    <h1 id="status">Loading JavaScript...</h1>
    <script src="/dotpipe.js"></script>
    <script>
        console.log('Script started');
        console.log('pageData:', {json.dumps(page_json)});
        
        const pageData = {json.dumps(page_json)};
        
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', init);
        }} else {{
            init();
        }}
        
        function init() {{
            console.log('Init called');
            console.log('modala type:', typeof modala);
            
            const statusEl = document.getElementById('status');
            
            if (typeof modala === 'function') {{
                statusEl.textContent = 'Calling modala()...';
                try {{
                    console.log('pageData structure:', JSON.stringify(pageData, null, 2));
                    modala(pageData, document.body);
                    console.log('modala() finished rendering');
                    console.log('document.body.innerHTML:', document.body.innerHTML.substring(0, 500));
                    
                    // Check if tabs element exists
                    const tabsElements = document.getElementsByTagName('tabs');
                    console.log('Found tabs elements:', tabsElements.length);
                    if (tabsElements.length > 0) {{
                        console.log('Tabs element:', tabsElements[0]);
                        console.log('Tab attribute:', tabsElements[0].getAttribute('tab'));
                    }}
                    
                    // Call dotPipe initialization functions to register tabs
                    if (typeof domContentLoad === 'function') {{
                        domContentLoad();
                        console.log('domContentLoad() called');
                    }}
                    if (typeof addPipe === 'function') {{
                        addPipe(document.body);
                        console.log('addPipe() called');
                    }}
                    
                    // Call flashClickListener on all elements with IDs
                    if (typeof flashClickListener === 'function') {{
                        document.querySelectorAll('[id]').forEach(elem => {{
                            flashClickListener(elem);
                        }});
                        console.log('flashClickListener() called on all ID elements');
                    }}
                    
                    // Remove status message
                    if (statusEl && statusEl.parentNode) {{
                        statusEl.parentNode.removeChild(statusEl);
                    }}
                    
                    console.log('modala() executed successfully - tabs initialized');
                }} catch(e) {{
                    statusEl.textContent = 'Error: ' + e.message;
                    console.error('modala() error:', e);
                }}
            }} else {{
                statusEl.textContent = 'modala() function not found!';
                console.error('modala() not found. dotpipe.js may not be loaded.');
                console.log('Available functions:', Object.keys(window).filter(k => typeof window[k] === 'function').slice(0, 20));
            }}
        }}
    </script>
</body>
</html>''';
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error_html = f"<h1>Error</h1><p>{str(e)}</p>"
            self.wfile.write(error_html.encode('utf-8'))
    
    def _serve_asset(self, asset_name: str):
        """Serve static asset files (images, CSS, etc.)"""
        asset_path = self.app_manager.get_asset_path(asset_name)
        
        if not asset_path:
            self.send_response(404)
            self.end_headers()
            return
        
        try:
            mime_type, _ = mimetypes.guess_type(str(asset_path))
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            with open(asset_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
    
    def _serve_static_html(self, path: str):
        """Serve static HTML files from app directory"""
        # Remove leading slash and get file from app directory
        filename = path.lstrip('/')
        html_path = Path(self.app_manager.app_dir) / filename
        
        if not html_path.exists():
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"HTML file not found: {filename}".encode('utf-8'))
            return
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            print(f"Served static HTML: {filename}")
        except Exception as e:
            print(f"Error serving HTML {filename}: {e}")
            self.send_response(500)
            self.end_headers()
    
    def _serve_dotpipe(self):
        """Serve dotpipe.js from project root"""
        # dotpipe.js is in the project root, not in app directory
        dotpipe_path = Path(__file__).parent.parent / 'dotpipe.js'
        
        if not dotpipe_path.exists():
            print(f"ERROR: dotpipe.js not found at {dotpipe_path}")
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"dotpipe.js not found at {dotpipe_path}".encode('utf-8'))
            return
        
        try:
            with open(dotpipe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript; charset=utf-8')
            self.send_header('Content-Length', len(content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            print(f"Served dotpipe.js ({len(content)} chars)")
        except Exception as e:
            print(f"ERROR serving dotpipe.js: {e}")
            self.send_response(500)
            self.end_headers()
    
    def _serve_json_file(self, path: str):
        """Serve raw JSON files for AJAX/tab loading"""
        # Remove leading slash and /demo_app/ prefix if present
        file_path = path.lstrip('/')
        if file_path.startswith('demo_app/'):
            file_path = file_path[9:]  # Remove 'demo_app/' prefix
        
        # Look for file in app pages directory
        json_path = Path(self.app_manager.app_dir) / file_path
        
        if not json_path.exists():
            print(f"ERROR: JSON file not found at {json_path}")
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'File not found'}).encode('utf-8'))
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            print(f"Served JSON file: {json_path.name}")
        except Exception as e:
            print(f"ERROR serving JSON file: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
    
    def _handle_api(self, path: str):
        """Handle API endpoints"""
        # Format: /api/database_id/action?params
        parts = path[5:].split('?')[0].split('/')  # Remove /api/ and query string
        
        if len(parts) < 2:
            self.send_error(400)
            return
        
        db_id = parts[0]
        action = parts[1]
        
        db = self.app_manager.get_database(db_id)
        if not db:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Database not found'}).encode())
            return
        
        try:
            if action == 'all':
                result = db.get_all()
                response = {'success': True, 'data': result}
            elif action == 'count':
                result = db.count()
                response = {'success': True, 'count': result}
            else:
                response = {'error': 'Unknown action'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def _handle_api_post(self, path: str):
        """Handle POST API requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
        except:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
            return
        
        # Handle PHP script execution: /api/execute/script_name
        if path.startswith('/api/execute/'):
            script_name = path[13:]  # Remove '/api/execute/'
            self._execute_php_script(script_name, data)
            return
        
        # Format: /api/database_id/action
        parts = path[5:].split('/')
        
        if len(parts) < 2:
            self.send_error(400)
            return
        
        db_id = parts[0]
        action = parts[1]
        
        db = self.app_manager.get_database(db_id)
        if not db:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Database not found'}).encode())
            return
        
        try:
            if action == 'insert':
                result = db.insert(data)
                response = {'success': True, 'result': result}
            elif action == 'update':
                id_val = data.get('id')
                result = db.update(id_val, data)
                response = {'success': True, 'updated': result}
            elif action == 'delete':
                id_val = data.get('id')
                result = db.delete(id_val)
                response = {'success': True, 'deleted': result}
            else:
                response = {'error': 'Unknown action'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def _execute_php_script(self, script_name: str, data: Dict[str, Any]):
        """Execute a local Python script that simulates PHP processing"""
        # For local testing, we'll execute Python equivalents of PHP scripts
        # Look for script in app directory
        script_path = self.app_manager.app_dir / f"{script_name}.py"
        
        if not script_path.exists():
            # Try .php extension
            script_path = self.app_manager.app_dir.parent / f"{script_name}.php"
            if not script_path.exists():
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': f'Script not found: {script_name}'
                }).encode())
                return
        
        try:
            # If it's a Python file, execute it
            if script_path.suffix == '.py':
                # Execute Python script
                namespace = {'data': data}
                with open(script_path, 'r') as f:
                    code = f.read()
                exec(code, namespace)
                result = namespace.get('result', {'success': True})
            else:
                # For PHP files, parse and simulate execution
                result = self._simulate_php_execution(script_path, data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())
    
    def _simulate_php_execution(self, php_file: Path, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate PHP execution by parsing and running the logic in Python"""
        # Read PHP file
        with open(php_file, 'r', encoding='utf-8') as f:
            php_code = f.read()
        
        # For process_tasks.php specifically
        if 'process_tasks' in php_file.name:
            tasks = data.get('tasks', [])
            
            # Process tasks (Python version of the PHP logic)
            analytics = {
                'total': len(tasks),
                'completed': 0,
                'pending': 0,
                'in_progress': 0,
                'high_priority': 0,
                'overdue': 0,
                'by_status': {},
                'by_priority': {},
                'upcoming': []
            }
            
            from datetime import datetime, timedelta
            today = datetime.now().strftime('%Y-%m-%d')
            week_later = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            for task in tasks:
                status = task.get('status', 'Unknown')
                priority = task.get('priority', 'Unknown')
                due_date = task.get('due_date', '')
                
                # Count by status
                if status == 'Completed':
                    analytics['completed'] += 1
                elif status == 'Pending':
                    analytics['pending'] += 1
                elif status == 'In Progress':
                    analytics['in_progress'] += 1
                
                # Count high priority
                if priority == 'High':
                    analytics['high_priority'] += 1
                
                # Check overdue
                if due_date and due_date < today and status != 'Completed':
                    analytics['overdue'] += 1
                
                # Group by status
                if status not in analytics['by_status']:
                    analytics['by_status'][status] = []
                analytics['by_status'][status].append(task)
                
                # Group by priority
                if priority not in analytics['by_priority']:
                    analytics['by_priority'][priority] = []
                analytics['by_priority'][priority].append(task)
                
                # Upcoming tasks
                if due_date and today <= due_date <= week_later:
                    analytics['upcoming'].append(task)
            
            # Generate HTML report
            html_report = "<div class='analytics-report'>"
            html_report += "<h3>📊 Task Analytics</h3>"
            html_report += "<div class='stats-grid'>"
            html_report += f"<div class='stat'><strong>Total:</strong> {analytics['total']}</div>"
            html_report += f"<div class='stat success'><strong>Completed:</strong> {analytics['completed']}</div>"
            html_report += f"<div class='stat warning'><strong>Pending:</strong> {analytics['pending']}</div>"
            html_report += f"<div class='stat info'><strong>In Progress:</strong> {analytics['in_progress']}</div>"
            html_report += f"<div class='stat danger'><strong>High Priority:</strong> {analytics['high_priority']}</div>"
            html_report += f"<div class='stat danger'><strong>Overdue:</strong> {analytics['overdue']}</div>"
            html_report += "</div>"
            
            # Upcoming tasks
            if analytics['upcoming']:
                html_report += "<h4>📅 Upcoming Tasks (Next 7 Days)</h4>"
                html_report += "<ul class='upcoming-list'>"
                for task in analytics['upcoming']:
                    html_report += f"<li><strong>{task['title']}</strong> - Due: {task['due_date']} ({task['priority']})</li>"
                html_report += "</ul>"
            
            html_report += "</div>"
            
            return {
                'success': True,
                'analytics': analytics,
                'html_report': html_report,
                'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'message': f"Processed {analytics['total']} tasks successfully"
            }
        
        # Default response for unknown scripts
        return {
            'success': True,
            'message': 'Script executed',
            'data': data
        }
    
    def log_message(self, format, *args):
        """Suppress HTTP server logging"""
        pass

class FileChangeHandler(FileSystemEventHandler):
    """Watch for file changes, render HTML, and reload the page"""
    
    def __init__(self, window, app_dir, dotpipe_path):
        self.window = window
        self.app_dir = Path(app_dir)
        self.dotpipe_path = Path(dotpipe_path)
        self.last_reload = 0
        self.rendering = False
        
    def render_json_to_html(self, json_path: Path):
        """Render JSON file to HTML using modala()"""
        if self.rendering:
            return
        
        self.rendering = True
        try:
            # Determine output path (same name but .html)
            output_path = json_path.with_suffix('.html')
            
            # Load JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Create temporary render page with script link (don't embed dotpipe.js)
            template = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Server Console</title>
</head>
<body>
<script src="/dotpipe.js"></script>
<script>
const pageData = {json.dumps(json_data)};
if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', function() {{
        modala(pageData, document.body);
    }});
}} else {{
    modala(pageData, document.body);
}}
</script>
</body>
</html>'''
            
            # Save rendered HTML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template)
            
            print(f"Rendered: {json_path.name} -> {output_path.name}")
            
        except Exception as e:
            print(f"Render error: {e}")
        finally:
            self.rendering = False
        
    def on_modified(self, event):
        """Reload when files are modified"""
        if event.is_directory:
            return
        
        # Only process .json files in pages directory
        if not event.src_path.endswith('.json'):
            return
        
        json_path = Path(event.src_path)
        if 'pages' not in json_path.parts:
            return
        
        # Render JSON to HTML
        self.render_json_to_html(json_path)
        
        # Debounce reloads (max once per second)
        current_time = time.time()
        if current_time - self.last_reload < 1:
            return
        
        self.last_reload = current_time
        print(f"File changed: {event.src_path} - Reloading...")
        
        # Reload the page
        if self.window:
            self.window.evaluate_js('location.reload()')


class AppWindow:
    """Manages the WebView window for a dotFly app"""
    
    def __init__(self, app_dir: str, port: int = 8000):
        self.app_dir = Path(app_dir)
        self.port = port
        self.app_manager = None
        self.server = None
        self.server_thread = None
        self.window = None
        self.observer = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the app manager"""
        self.app_manager = AppManager(str(self.app_dir))
        AppHTTPHandler.app_manager = self.app_manager
    
    def start_server(self):
        """Start the HTTP server in background thread"""
        self.server = HTTPServer(('localhost', self.port), AppHTTPHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def stop_server(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def start_file_watcher(self):
        """Start watching for file changes"""
        # Get path to dotpipe.js
        dotpipe_path = Path(__file__).parent.parent / 'dotpipe.js'
        
        event_handler = FileChangeHandler(self.window, self.app_dir, dotpipe_path)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.app_dir), recursive=True)
        self.observer.start()
        print(f"Watching for file changes in {self.app_dir}")
    
    def stop_file_watcher(self):
        """Stop watching for file changes"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def launch(self):
        """Launch the WebView window"""
        # Get settings from manifest
        settings = self.app_manager.manifest.settings
        width = settings.get('window_width', 1024)
        height = settings.get('window_height', 768)
        resizable = settings.get('resizable', True)
        
        # Start HTTP server
        self.start_server()
        
        # Wait for server to start
        time.sleep(0.5)
        
        # Create WebView window with JS enabled
        url = f'http://localhost:{self.port}/'
        self.window = webview.create_window(
            title=self.app_manager.manifest.app_name,
            url=url,
            width=width,
            height=height,
            resizable=resizable,
            background_color='#FFFFFF',
            js_api=None  # Enable JavaScript
        )
        
        # Start file watcher after window is created
        def on_shown():
            self.start_file_watcher()
        
        self.window.events.shown += on_shown
        
        # Start the window with debug mode to see console errors
        webview.start(debug=True)
        
        # Cleanup after window closes
        self.stop_file_watcher()
        self.stop_server()
    

    def get_app_info(self) -> Dict[str, Any]:
        """Get app information"""
        return self.app_manager.get_app_info()


def launch_app(app_dir: str, port: int = 8000):
    """
    Launch a dotFly app in a WebView window
    
    Args:
        app_dir: Path to the app directory (must contain manifest.json)
        port: HTTP server port (default 8000)
    """
    app_window = AppWindow(app_dir, port)
    app_window.launch()


def launch_app_from_manifest(manifest_path: str, port: int = 8000):
    """
    Launch a dotFly app from a manifest file path
    
    Args:
        manifest_path: Path to manifest.json file
        port: HTTP server port (default 8000)
    """
    app_dir = Path(manifest_path).parent
    launch_app(str(app_dir), port)
