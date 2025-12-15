"""
dotFly App Manager - Handles JSON-based Windows desktop applications
Manages app structure, manifest parsing, asset bundling, and deployment
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import csv
from .json_framework import JSONWebApp, OptimizedCSVDatabase


class AppManifest:
    """Parses and validates a manifest.json file for a dotFly app"""
    
    def __init__(self, manifest_path: str):
        self.manifest_path = Path(manifest_path)
        self.manifest_dir = self.manifest_path.parent
        self.data = self._load_manifest()
        self.app_dir = self.manifest_dir
        
    def _load_manifest(self) -> Dict[str, Any]:
        """Load and parse manifest.json"""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"manifest.json not found at {self.manifest_path}")
        
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    @property
    def app_name(self) -> str:
        return self.data.get('name', 'dotFly App')
    
    @property
    def version(self) -> str:
        return self.data.get('version', '1.0.0')
    
    @property
    def description(self) -> str:
        return self.data.get('description', '')
    
    @property
    def main_page(self) -> str:
        return self.data.get('main', 'index')
    
    @property
    def pages(self) -> Dict[str, str]:
        """Returns dict of page_id -> page_path"""
        return self.data.get('pages', {})
    
    @property
    def databases(self) -> List[Dict[str, Any]]:
        """Returns list of database configurations"""
        return self.data.get('databases', [])
    
    @property
    def assets(self) -> List[str]:
        """Returns list of asset files to include"""
        return self.data.get('assets', [])
    
    @property
    def theme(self) -> Dict[str, str]:
        """Returns theme configuration"""
        return self.data.get('theme', {})
    
    @property
    def settings(self) -> Dict[str, Any]:
        """Returns app-specific settings"""
        return self.data.get('settings', {})


class AppManager:
    """
    Manages dotFly applications:
    - Load JSON pages from files
    - Manage CSV databases
    - Handle assets (images, CSS, etc.)
    - Serve pages with proper routing
    """
    
    def __init__(self, app_dir: str):
        self.app_dir = Path(app_dir)
        self.manifest_path = self.app_dir / 'manifest.json'
        self.manifest = AppManifest(str(self.manifest_path))
        
        self.web_app = JSONWebApp(self.manifest.app_name)
        self.databases: Dict[str, OptimizedCSVDatabase] = {}
        
        self._initialize_pages()
        self._initialize_databases()
    
    def _initialize_pages(self):
        """Load all JSON page files defined in manifest"""
        pages_dir = self.app_dir / 'pages'
        
        for page_id, page_path in self.manifest.pages.items():
            full_path = pages_dir / page_path
            
            if not full_path.exists():
                print(f"Warning: Page file not found: {full_path}")
                continue
            
            with open(full_path, 'r', encoding='utf-8') as f:
                page_json = json.load(f)
            
            # Register with app
            self.web_app.register_page(f"/{page_id}", page_json)
    
    def _initialize_databases(self):
        """Load all CSV database files defined in manifest"""
        data_dir = self.app_dir / 'data'
        
        for db_config in self.manifest.databases:
            db_id = db_config.get('id')
            db_file = db_config.get('file')
            
            if not db_id or not db_file:
                print(f"Warning: Invalid database config: {db_config}")
                continue
            
            db_path = data_dir / db_file
            
            if not db_path.exists():
                print(f"Warning: Database file not found: {db_path}")
                continue
            
            # Load CSV file and create database
            columns = db_config.get('columns', [])
            db = OptimizedCSVDatabase(str(db_path), columns)
            self.databases[db_id] = db
    
    def get_database(self, db_id: str) -> Optional[OptimizedCSVDatabase]:
        """Get a database by ID"""
        return self.databases.get(db_id)
    
    def get_page(self, page_id: str) -> str:
        """Get rendered HTML for a page"""
        route = f"/{page_id}"
        if route not in self.web_app.pages:
            return f"<h1>Page not found: {page_id}</h1>"
        
        page_json = self.web_app.pages[route]
        return self.web_app.render_page(route)
    
    def get_page_json(self, page_id: str) -> Dict[str, Any]:
        """Get raw JSON for a page"""
        route = f"/{page_id}"
        if route not in self.web_app.pages:
            return {"tagname": "h1", "textContent": f"Page not found: {page_id}"}
        
        return self.web_app.pages[route]
    
    def get_main_page(self) -> str:
        """Get the main landing page"""
        return self.get_page(self.manifest.main_page)
    
    def get_asset_path(self, asset_name: str) -> Optional[Path]:
        """Get full path to an asset file"""
        assets_dir = self.app_dir / 'assets'
        asset_path = assets_dir / asset_name
        
        if asset_path.exists():
            return asset_path
        return None
    
    def list_pages(self) -> List[str]:
        """List all available pages"""
        return list(self.manifest.pages.keys())
    
    def list_databases(self) -> List[str]:
        """List all available databases"""
        return list(self.databases.keys())
    
    def get_app_info(self) -> Dict[str, Any]:
        """Get app metadata"""
        return {
            'name': self.manifest.app_name,
            'version': self.manifest.version,
            'description': self.manifest.description,
            'pages': self.list_pages(),
            'databases': self.list_databases(),
            'main_page': self.manifest.main_page
        }


class AppBuilder:
    """
    Creates a new dotFly app with proper structure
    """
    
    @staticmethod
    def create_app(app_name: str, app_dir: str, create_example: bool = True) -> Path:
        """
        Create a new dotFly app structure
        
        Structure:
        app_name/
            manifest.json
            pages/
                index.json
            data/
                (CSV files)
            assets/
                (images, CSS, etc.)
        """
        app_path = Path(app_dir) / app_name
        
        # Create directories
        app_path.mkdir(parents=True, exist_ok=True)
        (app_path / 'pages').mkdir(exist_ok=True)
        (app_path / 'data').mkdir(exist_ok=True)
        (app_path / 'assets').mkdir(exist_ok=True)
        
        # Create manifest
        manifest = {
            'name': app_name,
            'version': '1.0.0',
            'description': f'{app_name} - Built with dotFly',
            'main': 'index',
            'pages': {},
            'databases': [],
            'assets': [],
            'theme': {
                'color_primary': '#007bff',
                'color_secondary': '#6c757d',
                'font_family': 'Arial, sans-serif'
            },
            'settings': {
                'window_width': 1200,
                'window_height': 800,
                'resizable': True,
                'dev_tools': False
            }
        }
        
        if create_example:
            # Create index page
            index_page = {
                'tag': 'html',
                'head': {
                    'title': app_name,
                    'meta': [
                        {'charset': 'UTF-8'},
                        {'viewport': 'width=device-width, initial-scale=1.0'}
                    ]
                },
                'body': {
                    'tag': 'div',
                    'class': 'container',
                    'children': [
                        {'tag': 'h1', 'text': f'Welcome to {app_name}'},
                        {'tag': 'p', 'text': 'This is a dotFly application built with JSON'},
                        {
                            'tag': 'div',
                            'class': 'info',
                            'children': [
                                {'tag': 'h2', 'text': 'Getting Started'},
                                {'tag': 'p', 'text': 'Edit pages/index.json to customize this page'},
                                {'tag': 'p', 'text': 'Add more pages in the pages/ directory'},
                                {'tag': 'p', 'text': 'Add CSV data files in the data/ directory'},
                            ]
                        }
                    ]
                }
            }
            
            # Save index page
            with open(app_path / 'pages' / 'index.json', 'w', encoding='utf-8') as f:
                json.dump(index_page, f, indent=2)
            
            manifest['pages']['index'] = 'index.json'
        
        # Save manifest
        with open(app_path / 'manifest.json', 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        return app_path


def create_example_app(app_dir: str):
    """Create a complete example app with sample pages and data"""
    app_path = AppBuilder.create_app('ExampleApp', app_dir, create_example=False)
    
    # Create manifest
    manifest = {
        'name': 'Example dotFly App',
        'version': '1.0.0',
        'description': 'Example application showcasing dotFly features',
        'main': 'index',
        'pages': {
            'index': 'index.json',
            'products': 'products.json',
            'about': 'about.json'
        },
        'databases': [
            {
                'id': 'products_db',
                'file': 'products.csv',
                'columns': ['id', 'name', 'price', 'category']
            }
        ],
        'assets': ['products_bg.jpg'],
        'theme': {
            'color_primary': '#FF6B6B',
            'color_secondary': '#4ECDC4',
            'font_family': 'Segoe UI, Arial, sans-serif'
        },
        'settings': {
            'window_width': 1024,
            'window_height': 768,
            'resizable': True,
            'dev_tools': False
        }
    }
    
    # Create index page
    index_page = {
        'tag': 'html',
        'head': {'title': 'Example dotFly App'},
        'body': {
            'tag': 'div',
            'children': [
                {'tag': 'h1', 'text': 'Example dotFly Application'},
                {
                    'tag': 'nav',
                    'children': [
                        {'tag': 'a', 'href': '/products', 'text': 'Products', 'class': 'nav-link'},
                        {'tag': 'a', 'href': '/about', 'text': 'About', 'class': 'nav-link'}
                    ]
                },
                {'tag': 'p', 'text': 'Welcome! This example shows what dotFly apps can do.'}
            ]
        }
    }
    
    # Create products page
    products_page = {
        'tag': 'html',
        'head': {'title': 'Products'},
        'body': {
            'tag': 'div',
            'children': [
                {'tag': 'h1', 'text': 'Our Products'},
                {'tag': 'p', 'text': 'Browse our product catalog'},
                {
                    'tag': 'div',
                    'id': 'products-table',
                    'class': 'table-container'
                }
            ]
        }
    }
    
    # Create about page
    about_page = {
        'tag': 'html',
        'head': {'title': 'About'},
        'body': {
            'tag': 'div',
            'children': [
                {'tag': 'h1', 'text': 'About dotFly'},
                {'tag': 'p', 'text': 'dotFly is a JSON-based desktop application framework'},
                {'tag': 'p', 'text': 'Define your UI entirely in JSON'},
                {'tag': 'p', 'text': 'Serve it in a native Windows WebView'},
                {'tag': 'p', 'text': 'Package everything including databases and assets'}
            ]
        }
    }
    
    # Create sample CSV data
    products_csv = [
        ['id', 'name', 'price', 'category'],
        ['1', 'Laptop', '999.99', 'Electronics'],
        ['2', 'Mouse', '29.99', 'Accessories'],
        ['3', 'Keyboard', '79.99', 'Accessories'],
        ['4', 'Monitor', '299.99', 'Electronics']
    ]
    
    # Save files
    with open(app_path / 'pages' / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(index_page, f, indent=2)
    
    with open(app_path / 'pages' / 'products.json', 'w', encoding='utf-8') as f:
        json.dump(products_page, f, indent=2)
    
    with open(app_path / 'pages' / 'about.json', 'w', encoding='utf-8') as f:
        json.dump(about_page, f, indent=2)
    
    with open(app_path / 'data' / 'products.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(products_csv)
    
    with open(app_path / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    return app_path
