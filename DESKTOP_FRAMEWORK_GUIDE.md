# dotFly Complete Desktop App Framework

## Overview

**dotFly** is a complete framework for building Windows desktop applications using pure JSON. No HTML, CSS, or JavaScript needed.

```
┌─────────────────────────────────────────┐
│     Your Application (JSON Files)       │
│  ├── manifest.json (app config)         │
│  ├── pages/*.json (UI definitions)      │
│  ├── data/*.csv (database files)        │
│  └── assets/* (images, etc.)            │
└──────────────┬──────────────────────────┘
               │
         dotFly Framework
               │
    ┌──────────┴──────────┐
    │                     │
┌────────────┐    ┌──────────────┐
│   App      │    │  HTTP Server │
│  Manager   │    │  (localhost) │
└────────────┘    └──────────────┘
    │                     │
    └──────────┬──────────┘
               │
        ┌──────────────┐
        │  WebView     │
        │  (Windows)   │
        └──────────────┘
```

## Architecture

### Components

#### 1. **AppManager** (`src/app_manager.py`)
- Parses `manifest.json` files
- Loads JSON page definitions
- Manages CSV databases
- Serves asset files
- Handles page routing

#### 2. **AppRuntime** (`src/app_runtime.py`)
- Starts HTTP server on localhost
- Creates native Windows WebView window
- Handles page requests
- Manages AJAX API calls
- Serves static assets

#### 3. **Launcher** (`launcher.py`)
- Command-line interface
- Creates new apps
- Launches existing apps
- Manages app lifecycle

#### 4. **JSON Framework** (`src/json_framework.py`)
- Converts JSON to HTML
- Manages pages
- Handles database operations
- Generates HTML5 output

## Complete Workflow

### 1. Create New App
```bash
python launcher.py create MyStore
```
Creates:
```
MyStore/
├── manifest.json          ← App metadata
├── pages/
│   └── index.json        ← Home page (JSON)
├── data/                 ← CSV files go here
└── assets/               ← Images, CSS, etc.
```

### 2. Define Pages (JSON)
Edit `pages/index.json`:
```json
{
  "tag": "html",
  "head": {"title": "My Store"},
  "body": {
    "tag": "div",
    "class": "container",
    "children": [
      {"tag": "h1", "text": "Welcome"},
      {"tag": "a", "href": "/products", "text": "Shop Now"}
    ]
  }
}
```

### 3. Configure App (manifest.json)
```json
{
  "name": "My Store",
  "version": "1.0.0",
  "main": "index",
  "pages": {
    "index": "index.json",
    "products": "products.json"
  },
  "databases": [
    {
      "id": "products_db",
      "file": "products.csv",
      "columns": ["id", "name", "price"]
    }
  ],
  "settings": {
    "window_width": 1200,
    "window_height": 800
  }
}
```

### 4. Add Data (CSV)
Create `data/products.csv`:
```
id,name,price
1,Laptop,999.99
2,Mouse,29.99
3,Keyboard,79.99
```

### 5. Launch App
```bash
python launcher.py run MyStore
```

A native Windows window opens with your app!

## File Structure

### manifest.json Format

```json
{
  // App Identity
  "name": "Application Name",
  "version": "1.0.0",
  "description": "What this app does",
  
  // Navigation
  "main": "index",                    // Main page ID
  "pages": {                          // Page definitions
    "page_id": "pages/file.json"
  },
  
  // Data
  "databases": [                      // CSV databases
    {
      "id": "db_id",
      "file": "data/file.csv",
      "columns": ["col1", "col2"]
    }
  ],
  
  // Resources
  "assets": ["logo.png", "bg.jpg"],   // Static files
  "theme": {                          // CSS variables
    "color_primary": "#007bff"
  },
  
  // Runtime
  "settings": {
    "window_width": 1200,
    "window_height": 800,
    "resizable": true,
    "dev_tools": false
  }
}
```

### JSON Page Format

```json
{
  "tag": "html",
  "head": {
    "title": "Page Title",
    "meta": [
      {"charset": "UTF-8"},
      {"viewport": "width=device-width, initial-scale=1.0"}
    ]
  },
  "body": {
    "tag": "div",
    "class": "container",
    "children": [
      {"tag": "h1", "text": "Heading"},
      {"tag": "p", "text": "Content"},
      {
        "tag": "a",
        "href": "/other-page",
        "text": "Link"
      }
    ]
  }
}
```

## Usage Examples

### Example 1: Simple Page

**pages/home.json:**
```json
{
  "tag": "html",
  "body": {
    "tag": "div",
    "children": [
      {"tag": "h1", "text": "Hello World"},
      {"tag": "p", "text": "This is a dotFly app"}
    ]
  }
}
```

### Example 2: Navigation

**pages/index.json:**
```json
{
  "tag": "html",
  "body": {
    "tag": "div",
    "children": [
      {
        "tag": "nav",
        "children": [
          {"tag": "a", "href": "/products", "text": "Products"},
          {"tag": "a", "href": "/about", "text": "About"}
        ]
      },
      {"tag": "h1", "text": "Welcome"}
    ]
  }
}
```

### Example 3: With Database

**manifest.json:**
```json
{
  "pages": {"products": "products.json"},
  "databases": [
    {
      "id": "products_db",
      "file": "products.csv",
      "columns": ["id", "name", "price", "stock"]
    }
  ]
}
```

**pages/products.json:**
```json
{
  "tag": "html",
  "body": {
    "tag": "div",
    "children": [
      {"tag": "h1", "text": "Our Products"},
      {"tag": "table", "id": "products-table"}
    ]
  }
}
```

**data/products.csv:**
```
id,name,price,stock
1,Laptop,999.99,5
2,Mouse,29.99,50
```

## Command Reference

```bash
# Create a new app
python launcher.py create AppName

# Launch an existing app
python launcher.py run path/to/AppName

# Create and launch example app
python launcher.py example
```

## JSON Element Syntax

### Basic Element
```json
{"tag": "div", "text": "Content"}
```

### With Class and ID
```json
{
  "tag": "div",
  "id": "my-div",
  "class": "container",
  "text": "Content"
}
```

### With Children
```json
{
  "tag": "div",
  "class": "list",
  "children": [
    {"tag": "p", "text": "Item 1"},
    {"tag": "p", "text": "Item 2"}
  ]
}
```

### With Attributes
```json
{
  "tag": "input",
  "type": "text",
  "placeholder": "Enter name",
  "class": "form-input"
}
```

### Links
```json
{"tag": "a", "href": "/page-id", "text": "Click Here"}
```

### Images
```json
{"tag": "img", "src": "/assets/logo.png", "alt": "Logo"}
```

## Advanced Features

### Multi-Page Apps

Add multiple pages to manifest:
```json
{
  "pages": {
    "index": "index.json",
    "products": "products.json",
    "contact": "contact.json",
    "admin": "admin/dashboard.json"
  }
}
```

Link between pages:
```json
{"tag": "a", "href": "/products", "text": "Products"}
```

### Multiple Databases

```json
{
  "databases": [
    {"id": "products", "file": "products.csv", "columns": [...]},
    {"id": "users", "file": "users.csv", "columns": [...]},
    {"id": "orders", "file": "orders.csv", "columns": [...]}
  ]
}
```

### Asset Organization

```
assets/
├── images/
│   ├── logo.png
│   └── icons/
├── css/
│   └── custom.css
└── fonts/
    └── roboto.ttf
```

Reference: `{"tag": "img", "src": "/assets/images/logo.png"}`

### Window Customization

```json
{
  "settings": {
    "window_width": 1400,
    "window_height": 900,
    "resizable": true,
    "dev_tools": false,
    "always_on_top": false
  }
}
```

## Performance

- **JSON Parsing:** < 1ms
- **HTML Generation:** < 10ms for complex pages
- **Database Lookups:** O(1) with indexing
- **Page Loading:** < 100ms (local HTTP)
- **Asset Serving:** Direct filesystem access

## Limitations and Notes

- Requires Python 3.13+
- Requires pywebview library
- WebView must be available on Windows
- CSV is suitable for up to 100,000 records
- Pages load over HTTP (localhost:8000)

## Deployment

### Standalone Executable

Use PyInstaller to create a standalone .exe:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed launcher.py
```

Then distribute with your app folder.

### Sharing Apps

Just share the app folder. Users can:
```bash
python launcher.py run YourAppName
```

## File Reference

| File | Purpose |
|------|---------|
| `src/app_manager.py` | Manifest parsing, app loading, database management |
| `src/app_runtime.py` | WebView window, HTTP server, request handling |
| `src/json_framework.py` | JSON to HTML conversion (from core framework) |
| `launcher.py` | CLI for creating and launching apps |
| `requirements.txt` | Dependencies (pywebview) |
| `docs/APP_MANIFEST_SPEC.md` | Complete manifest.json specification |
| `docs/JSON_FRAMEWORK.md` | JSON syntax reference |

## Getting Started

### Quick 5-Minute Start

```bash
# 1. Create app
python launcher.py create MyApp

# 2. Edit MyApp/pages/index.json

# 3. Launch
python launcher.py run MyApp
```

### Next Steps

1. Read [DESKTOP_APPS.md](DESKTOP_APPS.md) - Quick start guide
2. Read [APP_MANIFEST_SPEC.md](docs/APP_MANIFEST_SPEC.md) - Manifest reference
3. Build your first complete app
4. Add databases and multiple pages
5. Deploy as executable or folder

## Support

- Check documentation files
- Review example apps
- Test with `python launcher.py example`

---

**dotFly:** *Define once, run everywhere* - Just JSON, no code needed.
