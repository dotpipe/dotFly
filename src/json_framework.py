"""
JSON Web Framework for dotPipe
================================
Convert JSON structures to HTML and manage databases with CSV storage.
Optimized for maximum performance and minimal dependencies.
"""

import json
import csv
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path


class JSONToHTML:
    """Convert JSON structures to HTML with full attribute support."""
    
    def __init__(self):
        self.void_elements = {'br', 'hr', 'img', 'input', 'link', 'meta', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
    
    def convert(self, json_obj: Dict[str, Any]) -> str:
        """Convert JSON object to HTML string."""
        if not json_obj:
            return ""
        
        # Handle multiple root elements
        if isinstance(json_obj, list):
            return "".join(self.convert(item) for item in json_obj)
        
        return self._element_to_html(json_obj)
    
    def _element_to_html(self, element: Dict[str, Any]) -> str:
        """Convert a single JSON element to HTML."""
        tag = element.get('tag', 'div')
        text = element.get('text', '')
        children = element.get('children', [])
        
        # Build attributes from explicit 'attributes' dict AND from element keys
        attributes = element.get('attributes', {}).copy()
        
        # Add any other keys as attributes (except reserved ones)
        reserved_keys = {'tag', 'text', 'children', 'attributes'}
        for key, value in element.items():
            if key not in reserved_keys and key not in attributes:
                attributes[key] = value
        
        # Build attribute string
        attr_str = self._build_attributes(attributes)
        
        # Build opening tag
        html = f"<{tag}{attr_str}>"
        
        # Add text content
        if text:
            html += self._escape_html(str(text))
        
        # Add children
        if children:
            for child in children:
                if isinstance(child, dict):
                    html += self._element_to_html(child)
                elif isinstance(child, str):
                    html += self._escape_html(child)
        
        # Add closing tag (unless void element)
        if tag not in self.void_elements:
            html += f"</{tag}>"
        
        return html
    
    def _build_attributes(self, attrs: Dict[str, Any]) -> str:
        """Build HTML attribute string from dictionary."""
        if not attrs:
            return ""
        
        parts = []
        for key, value in attrs.items():
            if value is None:
                continue
            elif value is True:
                parts.append(f' {key}')
            elif value is False:
                continue
            else:
                value_str = self._escape_attr(str(value))
                parts.append(f' {key}="{value_str}"')
        
        return "".join(parts)
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
    
    @staticmethod
    def _escape_attr(text: str) -> str:
        """Escape attribute values."""
        return text.replace('"', '&quot;').replace('&', '&amp;')


class OptimizedCSVDatabase:
    """High-performance CSV database with caching and indexing."""
    
    def __init__(self, filepath: str, auto_index: bool = True):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.auto_index = auto_index
        self._cache = None
        self._headers = None
        self._index = {}
        self._load()
    
    def _load(self):
        """Load CSV file into memory with caching."""
        if not self.filepath.exists():
            self._cache = []
            self._headers = []
            return
        
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                self._headers = reader.fieldnames or []
                self._cache = list(reader)
            
            # Build index for faster lookups
            if self.auto_index and self._headers:
                self._rebuild_index()
        except Exception as e:
            print(f"Error loading CSV: {e}")
            self._cache = []
            self._headers = []
    
    def _rebuild_index(self):
        """Rebuild index for primary key lookups."""
        self._index = {}
        if not self._headers or not self._cache:
            return
        
        # Use first column as primary key if exists
        first_key = self._headers[0]
        for idx, row in enumerate(self._cache):
            if first_key in row:
                self._index[row[first_key]] = idx
    
    def _save(self):
        """Write cache back to CSV file."""
        if not self._cache or not self._headers:
            return
        
        try:
            with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self._headers)
                writer.writeheader()
                writer.writerows(self._cache)
        except Exception as e:
            print(f"Error saving CSV: {e}")
    
    def select(self, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Select rows matching conditions."""
        if not where:
            return self._cache.copy()
        
        results = []
        for row in self._cache:
            if all(row.get(k) == str(v) for k, v in where.items()):
                results.append(row)
        return results
    
    def select_by_id(self, id_value: Any) -> Optional[Dict[str, Any]]:
        """Fast lookup by primary key."""
        if not self._headers or id_value not in self._index:
            return None
        idx = self._index[id_value]
        return self._cache[idx] if idx < len(self._cache) else None
    
    def insert(self, row: Dict[str, Any]) -> bool:
        """Insert new row."""
        # Ensure all columns exist
        for key in self._headers:
            if key not in row:
                row[key] = ''
        
        self._cache.append(row)
        self._rebuild_index()
        self._save()
        return True
    
    def update(self, id_or_where: Union[str, Dict[str, Any]], values: Optional[Dict[str, Any]] = None) -> int:
        """Update rows by ID or matching conditions."""
        # If called with just ID string
        if isinstance(id_or_where, str) and values is None:
            return 0
        
        # If called with ID and values dict
        if isinstance(id_or_where, str) and isinstance(values, dict):
            where = {'id': id_or_where}
            count = 0
            for row in self._cache:
                if all(row.get(k) == str(v) for k, v in where.items()):
                    row.update(values)
                    count += 1
            if count > 0:
                self._rebuild_index()
                self._save()
            return count
        
        # Original behavior: where dict
        if isinstance(id_or_where, dict):
            where = id_or_where
            count = 0
            for row in self._cache:
                if all(row.get(k) == str(v) for k, v in where.items()):
                    row.update(values or {})
                    count += 1
            
            if count > 0:
                self._rebuild_index()
                self._save()
            return count
        
        return 0
    
    def delete(self, id_or_where: Union[str, Dict[str, Any]]) -> int:
        """Delete rows by ID or matching conditions."""
        # If called with just ID string
        if isinstance(id_or_where, str):
            where = {'id': id_or_where}
            original_len = len(self._cache)
            self._cache = [row for row in self._cache 
                          if not all(row.get(k) == str(v) for k, v in where.items())]
            count = original_len - len(self._cache)
            
            if count > 0:
                self._rebuild_index()
                self._save()
            return count
        
        # Original behavior: where dict
        if isinstance(id_or_where, dict):
            where = id_or_where
            original_len = len(self._cache)
            self._cache = [row for row in self._cache 
                          if not all(row.get(k) == str(v) for k, v in where.items())]
            count = original_len - len(self._cache)
            
            if count > 0:
                self._rebuild_index()
                self._save()
            return count
        
        return 0
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all rows."""
        return self._cache.copy()
    
    def count(self) -> int:
        """Count total rows."""
        return len(self._cache)
    
    def get_headers(self) -> List[str]:
        """Get column headers."""
        return self._headers.copy()
    
    def create_table(self, headers: List[str]):
        """Create table with specified columns."""
        self._headers = headers
        self._cache = []
        self._save()


class JSONPage:
    """Build complete HTML pages from JSON structure."""
    
    def __init__(self):
        self.converter = JSONToHTML()
    
    def build(self, page_json: Dict[str, Any]) -> str:
        """Build complete HTML page from JSON."""
        html = '<!DOCTYPE html>\n<html'
        
        # Add attributes
        if 'htmlAttributes' in page_json:
            attrs = page_json['htmlAttributes']
            if isinstance(attrs, dict):
                for k, v in attrs.items():
                    html += f' {k}="{v}"'
        
        html += '>\n'
        
        # Head section
        if 'head' in page_json:
            html += self._build_head(page_json['head'])
        else:
            html += '<head><meta charset="UTF-8"></head>\n'
        
        # Body section
        html += '<body>\n'
        if 'body' in page_json:
            if isinstance(page_json['body'], list):
                for element in page_json['body']:
                    html += self.converter.convert(element)
            else:
                html += self.converter.convert(page_json['body'])
        
        # Add DOM watcher script to re-process dotPipe on dynamic content
        html += '''
<script>
(function() {
    // Watch for DOM changes and re-process dotPipe elements
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Re-attach click listeners to elements with IDs using flashClickListener
                        if (node.id && typeof flashClickListener === 'function') {
                            flashClickListener(node);
                        }
                        
                        // Process child elements with IDs
                        if (node.querySelectorAll) {
                            const elementsWithIds = node.querySelectorAll('[id]');
                            elementsWithIds.forEach(function(elem) {
                                if (typeof flashClickListener === 'function') {
                                    flashClickListener(elem);
                                }
                            });
                        }
                        
                        // Check if dotPipe exists and has register method
                        if (typeof dotPipe !== 'undefined' && typeof dotPipe.register === 'function') {
                            setTimeout(function() {
                                dotPipe.register();
                            }, 100);
                        }
                        
                        // Execute any script tags in the new content
                        if (node.tagName === 'SCRIPT' || node.querySelector) {
                            const scripts = node.tagName === 'SCRIPT' ? [node] : node.querySelectorAll('script');
                            scripts.forEach(function(script) {
                                if (script.textContent) {
                                    try {
                                        eval(script.textContent);
                                    } catch(e) {
                                        console.error('Script execution error:', e);
                                    }
                                }
                            });
                        }
                    }
                });
            }
        });
    });
    
    // Start observing
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
})();
</script>
'''
        
        html += '\n</body>\n'
        
        html += '</html>'
        return html
    
    def _build_head(self, head: Dict[str, Any]) -> str:
        """Build head section from JSON."""
        html = '<head>\n'
        
        # Charset
        html += '<meta charset="UTF-8">\n'
        
        # Title
        if 'title' in head:
            html += f'<title>{self.converter._escape_html(str(head["title"]))}</title>\n'
        
        # Meta tags
        if 'meta' in head and isinstance(head['meta'], list):
            for meta in head['meta']:
                if isinstance(meta, dict):
                    html += self.converter.convert(meta)
        
        # Link tags (stylesheets, etc.)
        if 'link' in head:
            if isinstance(head['link'], list):
                for link in head['link']:
                    if isinstance(link, dict):
                        html += self.converter.convert(link)
            elif isinstance(head['link'], dict):
                html += self.converter.convert(head['link'])
        
        # Stylesheets (legacy)
        if 'stylesheets' in head and isinstance(head['stylesheets'], list):
            for css in head['stylesheets']:
                if isinstance(css, str):
                    html += f'<link rel="stylesheet" href="{css}">\n'
                elif isinstance(css, dict):
                    html += self.converter.convert(css)
        
        # Inline styles
        if 'styles' in head:
            html += '<style>\n' + head['styles'] + '\n</style>\n'
        
        # Scripts (head)
        if 'scripts' in head and isinstance(head['scripts'], list):
            for script in head['scripts']:
                if isinstance(script, str):
                    html += f'<script src="{script}"></script>\n'
                elif isinstance(script, dict):
                    html += self.converter.convert(script)
        
        html += '</head>\n'
        return html


class JSONLink:
    """Handle link generation with AJAX vs redirect logic."""
    
    @staticmethod
    def create_internal(href: str, text: str = "", classes: str = "", **attrs) -> Dict[str, Any]:
        """Create internal link (uses AJAX)."""
        element = {
            'tag': 'a',
            'attributes': {
                'href': href,
                'class': f'ajax {classes}'.strip(),
                'data-ajax': href,
                'data-target': attrs.get('target', ''),
                **attrs
            },
            'children': [text] if text else []
        }
        return element
    
    @staticmethod
    def create_external(href: str, text: str = "", classes: str = "", **attrs) -> Dict[str, Any]:
        """Create external link (uses redirect)."""
        element = {
            'tag': 'a',
            'attributes': {
                'href': href,
                'class': f'redirect {classes}'.strip(),
                'target': '_blank',
                **attrs
            },
            'children': [text] if text else []
        }
        return element


class JSONForm:
    """Build forms from JSON structure."""
    
    @staticmethod
    def create_form(form_id: str, method: str = "POST", **fields) -> Dict[str, Any]:
        """Create form with fields."""
        form_element = {
            'tag': 'form',
            'attributes': {
                'id': form_id,
                'method': method,
                'class': 'json-form'
            },
            'children': []
        }
        
        for field_name, field_config in fields.items():
            field_type = field_config.get('type', 'text')
            form_element['children'].append(
                JSONForm._create_field(field_name, field_type, field_config)
            )
        
        # Add submit button
        form_element['children'].append({
            'tag': 'button',
            'attributes': {
                'type': 'submit',
                'class': 'btn btn-primary'
            },
            'text': 'Submit'
        })
        
        return form_element
    
    @staticmethod
    def _create_field(name: str, field_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create form field."""
        wrapper = {
            'tag': 'div',
            'attributes': {'class': 'form-group'},
            'children': []
        }
        
        # Label
        if config.get('label'):
            wrapper['children'].append({
                'tag': 'label',
                'attributes': {'for': name},
                'text': config['label']
            })
        
        # Field
        field = {
            'tag': 'input' if field_type != 'textarea' else 'textarea',
            'attributes': {
                'id': name,
                'name': name,
                'type': field_type if field_type != 'textarea' else None,
                'class': 'form-control',
                **(config.get('attributes', {}))
            }
        }
        
        # Remove None type
        if field['attributes']['type'] is None:
            del field['attributes']['type']
        
        if field_type == 'textarea':
            field['text'] = config.get('value', '')
        
        wrapper['children'].append(field)
        return wrapper


class JSONTable:
    """Generate tables from JSON or CSV data."""
    
    @staticmethod
    def from_list(data: List[Dict[str, Any]], **options) -> Dict[str, Any]:
        """Create table from list of dicts."""
        if not data:
            return {'tag': 'p', 'text': 'No data available'}
        
        # Get headers
        headers = list(data[0].keys())
        
        table = {
            'tag': 'table',
            'attributes': {
                'class': 'data-table ' + options.get('class', ''),
                **options.get('attributes', {})
            },
            'children': []
        }
        
        # Thead
        thead = {
            'tag': 'thead',
            'children': [{
                'tag': 'tr',
                'children': [
                    {'tag': 'th', 'text': h}
                    for h in headers
                ]
            }]
        }
        table['children'].append(thead)
        
        # Tbody
        tbody = {
            'tag': 'tbody',
            'children': [
                {
                    'tag': 'tr',
                    'children': [
                        {'tag': 'td', 'text': str(row.get(h, ''))}
                        for h in headers
                    ]
                }
                for row in data
            ]
        }
        table['children'].append(tbody)
        
        return table
    
    @staticmethod
    def from_csv(csv_path: str, **options) -> Dict[str, Any]:
        """Create table from CSV file."""
        db = OptimizedCSVDatabase(csv_path)
        data = db.get_all()
        return JSONTable.from_list(data, **options)


class JSONWebApp:
    """Main application class for JSON-based web apps."""
    
    def __init__(self, app_name: str = "JSONApp", data_dir: str = "data"):
        self.app_name = app_name
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.databases: Dict[str, OptimizedCSVDatabase] = {}
        self.pages: Dict[str, Dict[str, Any]] = {}
        self.converter = JSONToHTML()
        self.page_builder = JSONPage()
    
    def create_database(self, name: str, columns: Optional[List[str]] = None) -> OptimizedCSVDatabase:
        """Create or load database."""
        db_path = self.data_dir / f"{name}.csv"
        db = OptimizedCSVDatabase(str(db_path))
        
        if columns and not db.get_headers():
            db.create_table(columns)
        
        self.databases[name] = db
        return db
    
    def register_page(self, path: str, page_json: Dict[str, Any]):
        """Register a page."""
        self.pages[path] = page_json
    
    def render_page(self, path: str) -> str:
        """Render page to HTML."""
        if path not in self.pages:
            return "<h1>404 - Page Not Found</h1>"
        
        return self.page_builder.build(self.pages[path])
    
    def query(self, db_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Query database."""
        if db_name not in self.databases:
            return []
        
        if 'where' in kwargs:
            return self.databases[db_name].select(kwargs['where'])
        else:
            return self.databases[db_name].get_all()
    
    def insert(self, db_name: str, data: Dict[str, Any]) -> bool:
        """Insert data."""
        if db_name not in self.databases:
            return False
        return self.databases[db_name].insert(data)
    
    def update(self, db_name: str, where: Dict[str, Any], values: Dict[str, Any]) -> int:
        """Update data."""
        if db_name not in self.databases:
            return 0
        return self.databases[db_name].update(where, values)
    
    def delete(self, db_name: str, where: Dict[str, Any]) -> int:
        """Delete data."""
        if db_name not in self.databases:
            return 0
        return self.databases[db_name].delete(where)


# Example usage functions
def example_json_structure() -> Dict[str, Any]:
    """Example JSON page structure."""
    return {
        "head": {
            "title": "JSON Web Framework Demo",
            "stylesheets": ["styles.css"],
            "styles": "body { font-family: Arial, sans-serif; }"
        },
        "body": [
            {
                "tag": "header",
                "attributes": {"class": "main-header"},
                "children": [
                    {
                        "tag": "h1",
                        "text": "Welcome to JSON Web Framework"
                    }
                ]
            },
            {
                "tag": "nav",
                "attributes": {"class": "navbar"},
                "children": [
                    {
                        "tag": "a",
                        "attributes": {
                            "href": "/",
                            "class": "ajax nav-link"
                        },
                        "text": "Home"
                    },
                    {
                        "tag": "a",
                        "attributes": {
                            "href": "https://example.com",
                            "class": "redirect nav-link",
                            "target": "_blank"
                        },
                        "text": "External Link"
                    }
                ]
            },
            {
                "tag": "main",
                "children": [
                    {
                        "tag": "h2",
                        "text": "Content Section"
                    },
                    {
                        "tag": "p",
                        "text": "This is a paragraph."
                    }
                ]
            }
        ]
    }


if __name__ == "__main__":
    # Demo
    print("JSON Web Framework v1.0")
    print("=" * 50)
    
    # Create app
    app = JSONWebApp("DemoApp")
    
    # Create database
    users_db = app.create_database("users", ["id", "name", "email"])
    
    # Insert data
    users_db.insert({"id": "1", "name": "John", "email": "john@example.com"})
    users_db.insert({"id": "2", "name": "Jane", "email": "jane@example.com"})
    
    # Query data
    all_users = users_db.get_all()
    print(f"Users: {all_users}")
    
    # Convert to table
    table = JSONTable.from_list(all_users, **{"class": "users-table"})
    html = JSONToHTML().convert(table)
    print("\nTable HTML:")
    print(html)
    
    # Build page
    page_json = example_json_structure()
    page_html = app.page_builder.build(page_json)
    print("\nPage HTML (first 500 chars):")
    print(page_html[:500])
