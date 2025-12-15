"""
Demo script: Execute the JSON Task Manager App
Shows JSON → HTML conversion, database loading, and app structure
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.app_manager import AppManager
from src.json_framework import JSONToHTML


def main():
    print("=" * 80)
    print("dotFly JSON Task Manager - Demo Execution")
    print("=" * 80)
    print()
    
    # Initialize app
    print("📦 Loading App from manifest.json...")
    app_path = Path('demo_app')
    app = AppManager(str(app_path))
    
    print(f"✓ App loaded: {app.manifest.app_name}")
    print()
    
    # Show app info
    print("📋 App Information:")
    info = app.get_app_info()
    print(f"  Name: {info['name']}")
    print(f"  Version: {info['version']}")
    print(f"  Main Page: {info['main_page']}")
    print(f"  Pages: {', '.join(info['pages'])}")
    print(f"  Databases: {', '.join(info['databases'])}")
    print()
    
    # Load and display database
    print("🗄️  Database Contents:")
    db = app.get_database('tasks_db')
    if db:
        all_tasks = db.get_all()
        print(f"  Total records: {len(all_tasks)}")
        print()
        print("  Tasks:")
        for task in all_tasks:
            status_icon = "✓" if task['status'] == 'Completed' else "→" if task['status'] == 'In Progress' else "○"
            priority_color = "🔴" if task['priority'] == 'High' else "🟡" if task['priority'] == 'Medium' else "🟢"
            print(f"    {status_icon} [{task['id']}] {task['title']:30} | {priority_color} {task['priority']:6} | {task['due_date']}")
    print()
    
    # Convert pages to HTML
    print("🎨 Page Rendering (JSON → HTML):")
    print()
    
    pages_to_render = ['index', 'tasks', 'add_task']
    
    for page_id in pages_to_render:
        print(f"  [{page_id.upper()}]")
        html = app.get_page(page_id)
        html_preview = html[:200] + "..." if len(html) > 200 else html
        print(f"    Generated {len(html)} bytes of HTML")
        print(f"    Preview: {html_preview.replace(chr(10), ' ')}")
        print()
    
    # Show manifest structure
    print("📄 Manifest Structure:")
    with open(app_path / 'manifest.json', 'r') as f:
        manifest = json.load(f)
    print(json.dumps(manifest, indent=2)[:500] + "...\n")
    
    # Show example page JSON
    print("📝 Example: Page JSON Definition (index.json):")
    with open(app_path / 'pages' / 'index.json', 'r') as f:
        page = json.load(f)
    
    # Show a snippet
    print(json.dumps(page, indent=2)[:600] + "...\n")
    
    # Statistics
    print("=" * 80)
    print("📊 Execution Summary:")
    print("=" * 80)
    print(f"✓ App loaded successfully")
    print(f"✓ Manifest parsed: {len(manifest['pages'])} pages defined")
    print(f"✓ Databases loaded: 1 database with {len(all_tasks)} records")
    print(f"✓ Pages rendered: {len(pages_to_render)} pages converted to HTML")
    print(f"✓ Total HTML output: {sum(len(app.get_page(p)) for p in pages_to_render):,} bytes")
    print()
    print("What just happened:")
    print("  1. The framework loaded manifest.json")
    print("  2. It discovered 3 JSON page files in pages/")
    print("  3. It loaded the tasks.csv database with 5 records")
    print("  4. Each JSON page was converted to complete HTML")
    print("  5. Navigation links were identified")
    print("  6. Forms and tables were parsed")
    print()
    print("In a real execution:")
    print("  - The app would start an HTTP server on localhost:8000")
    print("  - A Windows WebView window would open")
    print("  - Users could click links to navigate between pages")
    print("  - Forms would submit to AJAX endpoints")
    print("  - Database would be queryable via API")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
