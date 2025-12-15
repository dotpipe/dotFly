# dotFly App Manifest Specification

## Overview

The `manifest.json` file is the heart of a dotFly application. It describes the app structure, pages, databases, assets, and configuration. Think of it as a package.json for desktop applications, but specifically designed for JSON-based UIs.

## File Structure

A complete dotFly app package looks like:

```
MyApp/
├── manifest.json          (required - app metadata & structure)
├── pages/                 (required - JSON page files)
│   ├── index.json
│   ├── products.json
│   └── about.json
├── data/                  (optional - CSV database files)
│   ├── products.csv
│   └── users.csv
└── assets/                (optional - images, CSS, etc.)
    ├── logo.png
    ├── background.jpg
    └── style.css
```

## manifest.json Specification

### Root Properties

```json
{
  "name": "string",                    // App name (required)
  "version": "string",                 // Version (semver format)
  "description": "string",             // App description
  "main": "string",                    // Main page ID (default: "index")
  "pages": {},                         // Page definitions
  "databases": [],                     // Database configurations
  "assets": [],                        // Asset file list
  "theme": {},                         // Theme settings
  "settings": {}                       // App settings
}
```

### Properties Detail

#### `name` (required)
- Type: `string`
- The application name displayed in the window title
- Example: `"My Awesome App"`

#### `version` (optional)
- Type: `string` (semver format)
- Application version
- Default: `"1.0.0"`
- Example: `"2.3.1"`

#### `description` (optional)
- Type: `string`
- Brief description of the app
- Example: `"A product management system"`

#### `main` (optional)
- Type: `string`
- The page ID to load on startup
- Must match a key in `pages`
- Default: `"index"`
- Example: `"main"` → loads `pages/main.json`

#### `pages` (required)
- Type: `object` (key-value pairs)
- Maps page IDs to file paths
- Keys: Page identifiers (used in routing)
- Values: Relative paths to JSON files in `pages/` directory
- Example:
```json
{
  "pages": {
    "index": "index.json",
    "products": "products.json",
    "about": "about.json",
    "settings": "admin/settings.json"
  }
}
```
- Usage: Navigate to pages with links:
  ```json
  {"tag": "a", "href": "/products", "text": "View Products"}
  ```

#### `databases` (optional)
- Type: `array of objects`
- Defines CSV databases used by the app
- Each database object:
  ```json
  {
    "id": "string",              // Database ID (used in code)
    "file": "string",            // CSV filename in data/
    "columns": ["string"]        // Column names
  }
  ```
- Example:
```json
{
  "databases": [
    {
      "id": "products_db",
      "file": "products.csv",
      "columns": ["id", "name", "price", "category"]
    },
    {
      "id": "users_db",
      "file": "users.csv",
      "columns": ["id", "username", "email", "role"]
    }
  ]
}
```

#### `assets` (optional)
- Type: `array of strings`
- List of asset files in the `assets/` directory
- Can include images, CSS, JavaScript, fonts, etc.
- Files are served at `/assets/filename`
- Example:
```json
{
  "assets": [
    "logo.png",
    "background.jpg",
    "style.css",
    "script.js",
    "fonts/roboto.ttf"
  ]
}
```

#### `theme` (optional)
- Type: `object`
- CSS theme configuration
- Custom properties for styling
- Example:
```json
{
  "theme": {
    "color_primary": "#007bff",
    "color_secondary": "#6c757d",
    "color_success": "#28a745",
    "color_danger": "#dc3545",
    "font_family": "Segoe UI, Arial, sans-serif",
    "font_size_base": "14px",
    "border_radius": "4px"
  }
}
```

#### `settings` (optional)
- Type: `object`
- Application runtime settings
- Example:
```json
{
  "settings": {
    "window_width": 1200,
    "window_height": 800,
    "resizable": true,
    "dev_tools": false,
    "always_on_top": false,
    "debug_mode": false
  }
}
```
- Properties:
  - `window_width`: Initial window width in pixels (default: 1024)
  - `window_height`: Initial window height in pixels (default: 768)
  - `resizable`: Allow window resizing (default: true)
  - `dev_tools`: Show developer tools (default: false)
  - `always_on_top`: Keep window on top (default: false)
  - `debug_mode`: Enable debug logging (default: false)

## Complete Example

```json
{
  "name": "E-Commerce Store",
  "version": "1.2.0",
  "description": "A simple product catalog and shopping system",
  "main": "index",
  "pages": {
    "index": "index.json",
    "products": "products.json",
    "cart": "cart.json",
    "checkout": "checkout.json",
    "about": "about.json"
  },
  "databases": [
    {
      "id": "products_db",
      "file": "products.csv",
      "columns": ["id", "name", "price", "description", "stock"]
    },
    {
      "id": "orders_db",
      "file": "orders.csv",
      "columns": ["id", "date", "customer", "total", "status"]
    },
    {
      "id": "users_db",
      "file": "users.csv",
      "columns": ["id", "email", "name", "phone"]
    }
  ],
  "assets": [
    "logo.png",
    "banner.jpg",
    "product1.jpg",
    "product2.jpg",
    "favicon.ico",
    "style.css"
  ],
  "theme": {
    "color_primary": "#FF6B6B",
    "color_secondary": "#4ECDC4",
    "color_background": "#F7F7F7",
    "font_family": "Segoe UI, Tahoma, Geneva, Verdana, sans-serif",
    "font_size_base": "16px",
    "border_radius": "8px"
  },
  "settings": {
    "window_width": 1400,
    "window_height": 900,
    "resizable": true,
    "dev_tools": false,
    "debug_mode": false
  }
}
```

## CSV Database Format

CSV files in the `data/` directory must have headers matching the `columns` array in the manifest.

Example `products.csv`:
```
id,name,price,category
1,Laptop,999.99,Electronics
2,Mouse,29.99,Accessories
3,Keyboard,79.99,Accessories
4,Monitor,299.99,Electronics
```

The first row is always treated as headers and must match the `columns` definition.

## JSON Page Format

Pages are standard JSON objects that get converted to HTML. They use the same JSON structure as the core dotFly framework.

Example `pages/index.json`:
```json
{
  "tag": "html",
  "head": {
    "title": "Home Page",
    "meta": [
      {"charset": "UTF-8"},
      {"viewport": "width=device-width, initial-scale=1.0"}
    ]
  },
  "body": {
    "tag": "div",
    "class": "container",
    "children": [
      {"tag": "h1", "text": "Welcome"},
      {
        "tag": "nav",
        "children": [
          {"tag": "a", "href": "/products", "text": "Products", "class": "nav-link"},
          {"tag": "a", "href": "/about", "text": "About", "class": "nav-link"}
        ]
      },
      {"tag": "p", "text": "Browse our catalog"}
    ]
  }
}
```

## File Path Considerations

All paths in the manifest are relative to the app directory:
- `pages/index.json` → `<app_dir>/pages/index.json`
- `data/products.csv` → `<app_dir>/data/products.csv`
- `assets/logo.png` → `<app_dir>/assets/logo.png`

## Validation Rules

When creating or modifying a manifest:

1. **Required fields:**
   - `name` must be a non-empty string
   - `pages` must be an object with at least one page
   - Each page path must exist as a file

2. **Page references:**
   - `main` must reference a valid page ID
   - Page files must be valid JSON

3. **Database references:**
   - Each database `id` must be unique
   - Database `file` must exist in `data/`
   - Column count must match the CSV file

4. **Asset references:**
   - Asset files should exist in `assets/`
   - Asset paths are served as `/assets/<path>`

## Advanced Features

### Nested Pages
You can organize pages in subdirectories:
```json
{
  "pages": {
    "admin_settings": "admin/settings.json",
    "admin_users": "admin/users.json"
  }
}
```
- Navigate with: `{"tag": "a", "href": "/admin_settings", ...}`

### Multiple Databases
Different sections can use different databases:
```json
{
  "databases": [
    {"id": "products", "file": "products.csv", "columns": [...]},
    {"id": "orders", "file": "orders.csv", "columns": [...]},
    {"id": "analytics", "file": "analytics.csv", "columns": [...]}
  ]
}
```

### Asset Organization
```
assets/
├── images/
│   ├── logo.png
│   └── icons/
│       ├── home.png
│       └── settings.png
├── css/
│   ├── main.css
│   └── theme.css
└── fonts/
    └── roboto.ttf
```
Reference as: `/assets/images/logo.png` or `/assets/css/main.css`

## Migration from HTML

If converting from HTML, the manifest.json replaces:
- HTML structure → JSON `pages/`
- CSS files → Theme in `theme` section
- Image assets → `assets/` directory
- Database tables → CSV files in `data/`
- Configuration → `settings` section

This makes applications more modular, easier to version control, and simpler to deploy.
