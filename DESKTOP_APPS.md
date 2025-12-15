# dotFly Desktop Apps - Quick Start

## What is dotFly Desktop Apps?

Instead of writing HTML/CSS/JavaScript, **define your entire desktop application in JSON**.

```json
{
  "tag": "div",
  "class": "container",
  "children": [
    {"tag": "h1", "text": "My App"},
    {"tag": "p", "text": "Built entirely with JSON"}
  ]
}
```

The framework automatically:
- ✅ Converts JSON to beautiful HTML
- ✅ Serves pages in a native Windows WebView
- ✅ Manages CSV databases
- ✅ Packages everything as a single app
- ✅ Handles routing and AJAX calls

## Installation

```bash
# Install pywebview for Windows WebView support
pip install pywebview

# Or install from requirements.txt
pip install -r requirements.txt
```

## 5-Minute Quick Start

### 1. Create Your First App

```bash
python launcher.py create MyApp
```

This creates:
```
MyApp/
├── manifest.json        ← App configuration
├── pages/
│   └── index.json       ← Your first page (pure JSON)
├── data/                ← CSV databases go here
└── assets/              ← Images and static files
```

### 2. Edit Your First Page

Open `MyApp/pages/index.json`:

```json
{
  "tag": "html",
  "head": {"title": "My First App"},
  "body": {
    "tag": "div",
    "class": "container",
    "children": [
      {"tag": "h1", "text": "Welcome to dotFly!"},
      {"tag": "p", "text": "This is your first page"},
      {
        "tag": "button",
        "class": "btn btn-primary",
        "text": "Click Me"
      }
    ]
  }
}
```

### 3. Launch Your App

```bash
python launcher.py run MyApp
```

A Windows WebView window opens with your app. That's it!

## Understanding the Structure

### manifest.json - The Blueprint

The manifest defines your entire app:

```json
{
  "name": "My Store",
  "version": "1.0.0",
  "main": "index",
  "pages": {
    "index": "index.json",
    "products": "products.json",
    "about": "about.json"
  },
  "databases": [
    {
      "id": "products_db",
      "file": "products.csv",
      "columns": ["id", "name", "price", "stock"]
    }
  ],
  "assets": ["logo.png", "background.jpg"],
  "settings": {
    "window_width": 1200,
    "window_height": 800
  }
}
```

### Pages - JSON That Becomes HTML

Instead of HTML:
```html
<div class="product">
  <h2>Laptop</h2>
  <p>$999.99</p>
</div>
```

Write JSON:
```json
{
  "tag": "div",
  "class": "product",
  "children": [
    {"tag": "h2", "text": "Laptop"},
    {"tag": "p", "text": "$999.99"}
  ]
}
```

### Databases - CSV with Indexing

Create `data/products.csv`:
```
id,name,price,stock
1,Laptop,999.99,10
2,Mouse,29.99,50
3,Keyboard,79.99,30
```

Reference in manifest:
```json
{
  "id": "products_db",
  "file": "products.csv",
  "columns": ["id", "name", "price", "stock"]
}
```

Then access from your pages automatically!

## Page JSON Syntax

### Basic Element
```json
{"tag": "div", "text": "Hello"}
```
→ `<div>Hello</div>`

### With Attributes
```json
{
  "tag": "input",
  "type": "text",
  "placeholder": "Enter name",
  "class": "form-input"
}
```
→ `<input type="text" placeholder="Enter name" class="form-input">`

### Children
```json
{
  "tag": "ul",
  "children": [
    {"tag": "li", "text": "Item 1"},
    {"tag": "li", "text": "Item 2"}
  ]
}
```

### Navigation Links
```json
{"tag": "a", "href": "/products", "text": "View Products"}
```
→ Links to another page

## Complete Example App

### 1. Create the app
```bash
python launcher.py example
```

This creates a complete example with:
- Multiple pages
- Navigation
- CSV database
- Working examples

### 2. Files created

**manifest.json:**
```json
{
  "name": "Example App",
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
  ]
}
```

**pages/index.json:**
```json
{
  "tag": "html",
  "head": {"title": "Home"},
  "body": {
    "tag": "div",
    "children": [
      {"tag": "h1", "text": "Welcome"},
      {"tag": "a", "href": "/products", "text": "Browse Products"}
    ]
  }
}
```

**pages/products.json:**
```json
{
  "tag": "html",
  "head": {"title": "Products"},
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
id,name,price
1,Laptop,999.99
2,Mouse,29.99
3,Keyboard,79.99
```

### 3. Launch and see it in action!

```bash
python launcher.py run ExampleApp
```

## Key Features

### 🎨 JSON Instead of HTML
- No HTML/CSS/JavaScript knowledge needed
- Simple JSON syntax
- Automatically generates clean HTML

### 🗄️ Built-in Database
- Use CSV files as databases
- Automatic indexing and caching
- O(1) lookups by ID
- No need for SQL

### 📦 Complete Packaging
- App + Pages + Database + Assets = One folder
- Easy to backup, share, or deploy
- Everything is text-based (easy version control)

### 🖥️ Native Windows App
- Real WebView (not Electron)
- Fast and lightweight
- Looks like a real Windows application

### 🔄 Instant Updates
- Change JSON files
- Refresh browser
- See changes immediately

### 🌐 AJAX-Ready
- Forms auto-submit
- Links can be internal or external
- Real-time updates possible

## Next Steps

### Learn More
- Read [APP_MANIFEST_SPEC.md](docs/APP_MANIFEST_SPEC.md) for complete manifest reference
- Read [JSON_FRAMEWORK.md](docs/JSON_FRAMEWORK.md) for JSON syntax details

### Build Your App

```bash
# Create a new blank app
python launcher.py create MyInventoryApp

# Edit the manifest to add pages
# Create JSON page files in pages/
# Add CSV data files in data/

# Launch and test
python launcher.py run MyInventoryApp
```

### Deploy

Share the entire `MyInventoryApp/` folder. Others can launch it with:
```bash
python launcher.py run MyInventoryApp
```

Or create a standalone .exe with PyInstaller for full distribution.

## Common Tasks

### Add a New Page

1. Create `pages/new_page.json`
2. Add to manifest:
```json
{
  "pages": {
    "new_page": "new_page.json"
  }
}
```
3. Link to it: `{"tag": "a", "href": "/new_page", "text": "New Page"}`

### Add a Database

1. Create `data/mydata.csv` with headers
2. Add to manifest:
```json
{
  "databases": [
    {
      "id": "my_db",
      "file": "mydata.csv",
      "columns": ["id", "name", "value"]
    }
  ]
}
```

### Add Images

1. Put images in `assets/`
2. Reference with `<img>` tag:
```json
{"tag": "img", "src": "/assets/logo.png"}
```

### Customize Window

Edit manifest `settings`:
```json
{
  "settings": {
    "window_width": 1400,
    "window_height": 900,
    "resizable": true
  }
}
```

## Troubleshooting

**Q: "pywebview not found" error**
```bash
pip install pywebview
```

**Q: App doesn't show**
- Make sure manifest.json is valid JSON
- Check that page files exist in pages/ directory
- Look at console for error messages

**Q: Changes don't appear**
- Refresh the browser (F5)
- Check that JSON is valid

**Q: Database not loading**
- Verify CSV file exists in data/
- Check columns match manifest
- Ensure first row is header

## The Vision

dotFly desktop apps represent a new way to think about UI development:

- **Before:** HTML + CSS + JavaScript + database setup
- **Now:** JSON files + CSV database

That's it. No frameworks. No build tools. Just JSON.

Perfect for:
- ✅ Business applications
- ✅ Data management tools
- ✅ Internal utilities
- ✅ Simple CRM/ERP systems
- ✅ Educational projects
- ✅ Quick prototypes

**Start building:** `python launcher.py example`
