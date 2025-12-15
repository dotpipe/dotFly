"""
dotFly App Launcher and Examples
Run standalone dotFly applications with manifest.json
"""

import sys
from pathlib import Path
from src.app_manager import AppBuilder, create_example_app
from src.app_runtime import launch_app, AppWindow
import json


def create_and_launch_example_app():
    """Create and launch the example app"""
    print("=" * 60)
    print("dotFly - Desktop Application Framework")
    print("=" * 60)
    print()
    
    # Create example app
    print("Creating example app structure...")
    app_path = create_example_app('.')
    print(f"✓ App created at: {app_path}")
    print()
    
    # Show manifest
    manifest_path = app_path / 'manifest.json'
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print("App Manifest:")
    print(f"  Name: {manifest['name']}")
    print(f"  Version: {manifest['version']}")
    print(f"  Main Page: {manifest['main']}")
    print(f"  Pages: {', '.join(manifest['pages'].keys())}")
    print(f"  Databases: {', '.join([db['id'] for db in manifest['databases']])}")
    print()
    
    # Launch app
    print("Launching app in WebView...")
    print("(Window will open in a moment)")
    print()
    
    try:
        launch_app(str(app_path), port=8000)
    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Make sure you have pywebview installed:")
        print("  pip install pywebview")


def launch_from_path(app_path: str):
    """Launch app from a given path"""
    app_path = Path(app_path)
    
    if not (app_path / 'manifest.json').exists():
        print(f"Error: No manifest.json found in {app_path}")
        sys.exit(1)
    
    try:
        print(f"Launching {app_path.name}...")
        launch_app(str(app_path), port=8000)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def create_blank_app(name: str, path: str = '.'):
    """Create a blank app with basic structure"""
    print(f"Creating blank app: {name}")
    app_path = AppBuilder.create_app(name, path, create_example=True)
    print(f"✓ App created at: {app_path}")
    print()
    print("App structure:")
    print(f"  {app_path}/")
    print(f"    manifest.json")
    print(f"    pages/")
    print(f"      index.json")
    print(f"    data/")
    print(f"    assets/")
    return app_path


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'example':
            create_and_launch_example_app()
        elif command == 'create':
            if len(sys.argv) > 2:
                app_name = sys.argv[2]
                app_path = create_blank_app(app_name)
                print()
                print("To launch your app:")
                print(f"  python launcher.py run {app_path}")
            else:
                print("Usage: python launcher.py create <app_name>")
        elif command == 'run':
            if len(sys.argv) > 2:
                app_path = sys.argv[2]
                launch_from_path(app_path)
            else:
                print("Usage: python launcher.py run <path_to_app>")
        else:
            print(f"Unknown command: {command}")
            print()
            print("Usage:")
            print("  python launcher.py example          - Create and launch example app")
            print("  python launcher.py create <name>    - Create blank app")
            print("  python launcher.py run <path>       - Launch existing app")
    else:
        print("=" * 60)
        print("dotFly Application Launcher")
        print("=" * 60)
        print()
        print("Usage:")
        print("  python launcher.py example          - Create and launch example app")
        print("  python launcher.py create <name>    - Create blank app")
        print("  python launcher.py run <path>       - Launch existing app")
        print()
        print("Examples:")
        print("  python launcher.py example")
        print("  python launcher.py create MyApp")
        print("  python launcher.py run MyApp")
        print()
