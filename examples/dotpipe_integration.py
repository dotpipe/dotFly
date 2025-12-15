"""
Integration Guide: JSON Web Framework + dotPipe.js
===================================================

How to use the JSON Web Framework with the dotPipe.js client-side framework
for complete full-stack JSON-based applications.
"""

# ============================================================================
# PART 1: SERVER SIDE (Python JSON Web Framework)
# ============================================================================

from json_framework import JSONWebApp, JSONTable, JSONLink, JSONForm, OptimizedCSVDatabase
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class JSONWebHandler(BaseHTTPRequestHandler):
    """HTTP request handler that serves JSON-based pages."""
    
    app = JSONWebApp("DotFlyApp")
    
    def do_GET(self):
        """Handle GET requests - return JSON or HTML."""
        path = self.path.split('?')[0]
        
        # AJAX requests return JSON data
        if path.startswith('/api/'):
            self.handle_api_request(path)
        # Regular requests return complete HTML
        else:
            self.handle_page_request(path)
    
    def do_POST(self):
        """Handle POST requests - save data and return updated JSON."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        # Parse JSON body
        try:
            data = json.loads(body)
            self.handle_form_submission(data)
        except:
            self.send_json_response({"error": "Invalid JSON"}, 400)
    
    def handle_api_request(self, path):
        """Return JSON data for AJAX requests."""
        # Examples:
        # /api/products -> all products
        # /api/products/1 -> product 1
        # /api/users?status=active -> filtered users
        
        parts = path.split('/')
        table_name = parts[2] if len(parts) > 2 else None
        
        if not table_name:
            self.send_json_response({"error": "Unknown table"}, 404)
            return
        
        # Get query parameters
        query = urllib.parse.parse_qs(self.path.split('?')[1] if '?' in self.path else '')
        
        # Query database
        if len(parts) > 3:
            # Get specific record
            record = self.app.databases[table_name].select_by_id(parts[3])
            response = record if record else {"error": "Not found"}
        else:
            # Get all or filtered
            where = {k: v[0] for k, v in query.items()}
            response = self.app.databases[table_name].select(where) if where else self.app.databases[table_name].get_all()
        
        self.send_json_response(response, 200)
    
    def handle_page_request(self, path):
        """Return HTML for page requests."""
        if path == '/':
            path = '/home'
        
        if path in self.app.pages:
            html = self.app.render_page(path)
        else:
            html = "<h1>404 - Page Not Found</h1>"
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_form_submission(self, data):
        """Handle form submissions - save to database and return confirmation."""
        table_name = data.get('_table')
        action = data.get('_action', 'insert')
        
        if not table_name:
            self.send_json_response({"error": "No table specified"}, 400)
            return
        
        db = self.app.databases.get(table_name)
        if not db:
            self.send_json_response({"error": "Table not found"}, 404)
            return
        
        # Remove metadata
        clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
        
        if action == 'insert':
            db.insert(clean_data)
            response = {"success": True, "action": "inserted"}
        elif action == 'update':
            db.update({"id": clean_data['id']}, clean_data)
            response = {"success": True, "action": "updated"}
        elif action == 'delete':
            db.delete({"id": clean_data['id']})
            response = {"success": True, "action": "deleted"}
        else:
            response = {"error": "Unknown action"}
        
        self.send_json_response(response, 200)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


# ============================================================================
# PART 2: SETUP APPLICATION
# ============================================================================

def setup_app():
    """Initialize the application with pages and data."""
    app = JSONWebHandler.app
    
    # Create databases
    products_db = app.create_database("products", ["id", "name", "price", "stock"])
    users_db = app.create_database("users", ["id", "name", "email", "status"])
    
    # Seed products
    products_db.insert({"id": "1", "name": "Laptop", "price": "999", "stock": "10"})
    products_db.insert({"id": "2", "name": "Mouse", "price": "29", "stock": "50"})
    products_db.insert({"id": "3", "name": "Keyboard", "price": "79", "stock": "25"})
    
    # Seed users
    users_db.insert({"id": "1", "name": "Alice", "email": "alice@example.com", "status": "active"})
    users_db.insert({"id": "2", "name": "Bob", "email": "bob@example.com", "status": "active"})
    
    # Build pages
    build_pages(app)


def build_pages(app):
    """Build all pages."""
    
    # ========================================
    # HOME PAGE
    # ========================================
    
    home_page = {
        "head": {
            "title": "DotFly - JSON Web Framework",
            "styles": """
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: Arial, sans-serif; background: #f5f5f5; }
                header { background: #333; color: white; padding: 20px; }
                nav { background: #666; display: flex; }
                nav a { color: white; padding: 10px 20px; text-decoration: none; flex: 1; text-align: center; }
                nav a:hover { background: #999; }
                main { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; }
                .data-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .data-table th, .data-table td { border: 1px solid #ddd; padding: 10px; text-align: left; }
                .data-table th { background: #f0f0f0; font-weight: bold; }
                form { max-width: 500px; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #0056b3; }
                footer { background: #333; color: white; text-align: center; padding: 20px; margin-top: 40px; }
            """
        },
        "body": [
            {
                "tag": "header",
                "children": [
                    {"tag": "h1", "text": "🚀 DotFly - JSON Web Framework"}
                ]
            },
            {
                "tag": "nav",
                "children": [
                    JSONLink.create_internal("/", "Home", target="main"),
                    JSONLink.create_internal("/products", "Products", target="main"),
                    JSONLink.create_internal("/users", "Users", target="main"),
                    JSONLink.create_internal("/admin", "Admin", target="main")
                ]
            },
            {
                "tag": "main",
                "attributes": {"id": "main"},
                "children": [
                    {"tag": "h2", "text": "Welcome to DotFly"},
                    {
                        "tag": "p",
                        "text": "A complete JSON-based web framework. Build entire applications using only JSON and Python."
                    },
                    {"tag": "h3", "text": "Features"},
                    {
                        "tag": "ul",
                        "children": [
                            {"tag": "li", "text": "100% JSON for structure"},
                            {"tag": "li", "text": "Built-in CSV database"},
                            {"tag": "li", "text": "Zero external dependencies"},
                            {"tag": "li", "text": "AJAX integration with dotPipe.js"},
                            {"tag": "li", "text": "Complete form handling"}
                        ]
                    }
                ]
            },
            {
                "tag": "footer",
                "text": "© 2024 DotFly Framework. Built with ❤️ for developers."
            }
        ]
    }
    
    # ========================================
    # PRODUCTS PAGE
    # ========================================
    
    products_page = {
        "head": {"title": "Products"},
        "body": [
            {"tag": "header", "children": [{"tag": "h1", "text": "Products"}]},
            {"tag": "nav", "children": [
                JSONLink.create_internal("/", "Home", target="main"),
                JSONLink.create_internal("/products", "Products", target="main")
            ]},
            {
                "tag": "main",
                "attributes": {"id": "main"},
                "children": [
                    {"tag": "h2", "text": "Our Products"},
                    {
                        "tag": "div",
                        "attributes": {"id": "products-container"},
                        "children": [
                            {"tag": "p", "text": "Loading products..."}
                        ]
                    },
                    {
                        "tag": "script",
                        "text": """
// Fetch products via AJAX
fetch('/api/products')
  .then(response => response.json())
  .then(products => {
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `
      <thead><tr><th>ID</th><th>Product</th><th>Price</th><th>Stock</th></tr></thead>
      <tbody>
        ${products.map(p => `
          <tr>
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>$${p.price}</td>
            <td>${p.stock}</td>
          </tr>
        `).join('')}
      </tbody>
    `;
    document.getElementById('products-container').innerHTML = '';
    document.getElementById('products-container').appendChild(table);
  });
                        """
                    }
                ]
            }
        ]
    }
    
    # ========================================
    # USERS PAGE
    # ========================================
    
    users_page = {
        "head": {"title": "Users"},
        "body": [
            {"tag": "header", "children": [{"tag": "h1", "text": "Users"}]},
            {"tag": "nav", "children": [
                JSONLink.create_internal("/", "Home", target="main"),
                JSONLink.create_internal("/users", "Users", target="main")
            ]},
            {
                "tag": "main",
                "attributes": {"id": "main"},
                "children": [
                    {"tag": "h2", "text": "User Management"},
                    {
                        "tag": "div",
                        "attributes": {"id": "users-container"},
                        "children": [
                            {"tag": "p", "text": "Loading users..."}
                        ]
                    },
                    {
                        "tag": "script",
                        "text": """
// Fetch users via AJAX
fetch('/api/users')
  .then(response => response.json())
  .then(users => {
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `
      <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr></thead>
      <tbody>
        ${users.map(u => `
          <tr>
            <td>${u.id}</td>
            <td>${u.name}</td>
            <td>${u.email}</td>
            <td>${u.status}</td>
          </tr>
        `).join('')}
      </tbody>
    `;
    document.getElementById('users-container').innerHTML = '';
    document.getElementById('users-container').appendChild(table);
  });
                        """
                    }
                ]
            }
        ]
    }
    
    # Register pages
    app.register_page("/", home_page)
    app.register_page("/products", products_page)
    app.register_page("/users", users_page)


# ============================================================================
# PART 3: RUN SERVER
# ============================================================================

def run_server(port=8000):
    """Start the HTTP server."""
    setup_app()
    
    server = HTTPServer(('localhost', port), JSONWebHandler)
    print(f"🚀 DotFly Server running at http://localhost:{port}")
    print("\nRoutes:")
    print("  GET  /              -> Home page")
    print("  GET  /products      -> Products page")
    print("  GET  /users         -> Users page")
    print("  GET  /api/products  -> Products JSON")
    print("  GET  /api/users     -> Users JSON")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")


if __name__ == "__main__":
    run_server(port=8000)
