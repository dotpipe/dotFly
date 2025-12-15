"""
Pre-render JSON pages to HTML using modala() in pywebview
"""

import webview
import json
import time
from pathlib import Path
import sys


class HTMLRenderer:
    """Render JSON to HTML using modala() in a hidden webview"""
    
    def __init__(self, dotpipe_path: str):
        self.dotpipe_path = Path(dotpipe_path)
        self.window = None
        self.html_result = None
        
    def render_json_to_html(self, json_data: dict) -> str:
        """Render JSON to HTML using modala()"""
        
        # Create a minimal HTML page that loads dotpipe and runs modala()
        template = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body id="renderTarget">
    <script>
    {self.dotpipe_path.read_text(encoding='utf-8')}
    </script>
    <script>
        const pageData = {json.dumps(json_data)};
        
        // Call modala to render
        modala(pageData, document.body);
        
        // Return the full HTML after rendering
        window.getRenderedHTML = function() {{
            return document.documentElement.outerHTML;
        }};
    </script>
</body>
</html>'''
        
        # Create hidden window
        self.window = webview.create_window('Renderer', html=template, hidden=True)
        
        # Start webview and wait for rendering
        def get_html():
            time.sleep(0.5)  # Wait for modala to finish
            try:
                self.html_result = self.window.evaluate_js('window.getRenderedHTML()')
            except Exception as e:
                print(f"Error getting HTML: {e}")
                self.html_result = None
            finally:
                self.window.destroy()
        
        # Run in separate thread
        import threading
        thread = threading.Thread(target=get_html)
        thread.daemon = True
        thread.start()
        
        webview.start(debug=False)
        thread.join(timeout=5)
        
        return self.html_result or "<h1>Rendering failed</h1>"


def render_page_file(json_path: str, output_path: str, dotpipe_path: str):
    """Render a JSON page file to HTML"""
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Render
    renderer = HTMLRenderer(dotpipe_path)
    html = renderer.render_json_to_html(json_data)
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Rendered: {json_path} -> {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python render_page.py <json_file> <output_html> <dotpipe_js>")
        sys.exit(1)
    
    render_page_file(sys.argv[1], sys.argv[2], sys.argv[3])
