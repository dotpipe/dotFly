# dotPipe.js Interactive Tutorial

## 🎉 Complete Documentation & Demo System

This is a fully interactive tutorial and documentation system for **dotPipe.js** - a Dynamic Web Components & Attribute Framework. The tutorial demonstrates every major feature with live, working examples.

## 📂 Files Created

### Main Tutorial Page
- **`demo_app/dotpipe_tutorial.html`** - The main tutorial interface with tabbed navigation

### Tutorial Content (JSON Files)
Located in `demo_app/pages/tutorial/`:

1. **`overview.json`** - Introduction and quick start
2. **`inline_macros.json`** - Variable storage, DOM manipulation, pipelines
3. **`ajax_pipes.json`** - AJAX loading, POST requests, callbacks
4. **`tabs_demo.json`** - Tab component documentation
5. **`csv_demo.json`** - CSV data display and tables
6. **`carousel_demo.json`** - Image carousels and sliders
7. **`modala_demo.json`** - JSON templating system
8. **`advanced.json`** - Advanced patterns and techniques

### Supporting Tab Content
Located in `demo_app/pages/tutorial/tabs/`:
- `home.json`, `features.json`, `contact.json`
- `form.json`, `actions.json`, `data.json`

## 🚀 How to Use

### Option 1: Simple HTTP Server (Recommended)
```bash
cd "c:\Users\g0d77\New folder\dotFly"
python -m http.server 8080
```

Then open in your browser:
```
http://localhost:8080/demo_app/dotpipe_tutorial.html
```

### Option 2: Direct File Access
Simply open `demo_app/dotpipe_tutorial.html` in your web browser. Note that some AJAX features may require a server.

### Option 3: Using dotFly Launcher
```bash
python launcher.py run demo_app
```

## 📚 What's Covered

### ⚡ Inline Macros
- Variable storage and retrieval with `&varName:value` and `!varName`
- DOM manipulation with `$id.property:value`
- Reading element values with `#varName:id.property`
- Function calls with `%funcName:[args]`
- Pipeline chaining with `|` operator
- **5 interactive demos** with live code examples

### 🔗 AJAX & Pipes
- Basic AJAX loading with `<pipe>` elements
- POST requests with data
- Dynamic endpoint switching
- Response formatting (JSON, plain-text, HTML)
- Callbacks and event handling
- **5 working examples** with real API calls

### 📑 Tabs Component
- Creating tabbed interfaces
- Loading content from JSON files
- Nested content and forms
- Dynamic tab creation
- **3 live demos** with working tabs

### 📊 CSV Component
- Loading and displaying CSV data as tables
- Sortable columns
- Pagination
- Lazy loading for performance
- Search and filter integration
- **Working demo** with sample data

### 🎠 Carousel Component
- Image sliders
- Auto-rotating carousels
- Multi-item display
- Navigation controls
- Content carousels with JSON
- **Interactive demonstrations**

### 🎨 Modala Templates
- JSON-to-HTML rendering
- Building complex UIs with JSON
- Special keys (br, js, css, modala)
- Three loading methods
- **Complete examples** including this tutorial itself

#### Modala Rendering Rules
- **`children` arrays:** When a JSON object contains a `children` array, each item is rendered as nested content under the current element. Use objects for elements and primitives for text nodes. Example:

```json
{
  "div": {
    "class": "panel",
    "children": [
      { "h2": "Title" },
      { "p": "A paragraph inside the panel." }
    ]
  }
}
```

- **Key-as-tag fallback:** If an object key is a recognized HTML or dotPipe tag (for example `div`, `carousel`, `button`, `select`) and the nested object does not provide a `tagname`, the parser will use the key as the element tag. This enables the compact form:

```json
{
  "carousel": {
    "id": "c1",
    "type": "img",
    "sources": "img1.jpg;img2.jpg",
    "boxes": "1"
  }
}
```

- **`tagname` fallback:** If neither a key-as-tag nor a `tagname` is present, the renderer will create a `div` element by default.

- **Carousel / Card `sources`:** For carousel and card elements the raw `sources` string is preserved as an attribute on the created element so rotation helpers (e.g. `shiftFilesLeft` / `shiftFilesRight`) can read and split the value.

- **Recursion & attachment:** Nested objects are rendered into their immediate parent element so `children` and nested-key forms produce proper DOM trees without leaking nodes to the global document root.


### 🛠️ Advanced Techniques
- Shell variables (scoped pipelines)
- The `|call` operator for custom functions
- Chaining AJAX requests
- Event-driven architecture
- Form handling with class grouping
- Dynamic styling and class toggling
- Authentication flows
- Timed updates
- E-commerce components
- Multi-column layouts
- **Full application example**

## 🎯 Features

### Interactive Demos
Every section includes:
- ✅ Live, working code examples
- ✅ Syntax-highlighted code blocks
- ✅ Click-to-run demonstrations
- ✅ Real-time output displays
- ✅ Best practices and tips

### Beautiful Design
- 🎨 Modern gradient design
- 🎨 Responsive layout
- 🎨 Clear visual hierarchy
- 🎨 Intuitive navigation
- 🎨 Professional styling

### Comprehensive Coverage
- 📖 8 major topic sections
- 📖 30+ interactive demos
- 📖 100+ code examples
- 📖 Complete attribute reference tables
- 📖 Real-world application examples

## 🏗️ Architecture

The tutorial is built using dotPipe itself, demonstrating the framework's power:

```
dotpipe_tutorial.html (Main page)
  ├── Uses <tabs> for navigation
  ├── Loads JSON content via modala
  └── Each tab is a separate JSON file
      ├── overview.json
      ├── inline_macros.json
      ├── ajax_pipes.json
      ├── tabs_demo.json
      ├── csv_demo.json
      ├── carousel_demo.json
      ├── modala_demo.json
      └── advanced.json
```

Each JSON file contains:
- Formatted documentation
- Live code examples
- Interactive demonstrations
- Reference tables
- Best practices

## 💡 Key Concepts Demonstrated

### Pipeline Operators
```
|               Chain operations
&varName:value  Store variable
!varName        Retrieve variable
$id.prop:value  Set DOM property
#var:id.prop    Read DOM property
%func:[args]    Call function
|+id:shell      Open shell (scope)
|-shell         Close shell
```

### Custom Tags
```html
<pipe>      AJAX loader
<tabs>      Tabbed navigation
<csv>       CSV data tables
<carousel>  Image/content slider
<cart>      Shopping cart
<login>     Auth forms
<checkout>  Checkout flow
<search>    Content filtering
<columns>   Multi-column layout
<timed>     Auto-refresh
```

### Modala JSON Structure
```json
{
  "elementName": {
    "attribute": "value",
    "text": "safe text content",
    "html": "<b>HTML content</b>",
    "children": [
      {"childElement": "..."}
    ]
  }
}
```

## 🎓 Learning Path

1. **Start with Overview** - Understand the basics
2. **Master Inline Macros** - Learn the pipeline syntax
3. **Explore AJAX/Pipes** - Load dynamic content
4. **Try Components** - Tabs, CSV, Carousel
5. **Learn Modala** - JSON templating
6. **Apply Advanced** - Complex patterns

## 🔧 Customization

The tutorial is fully customizable:

### Modify Styling
Edit the `<style>` section in `dotpipe_tutorial.html`:
```css
body { /* Change colors, fonts, etc */ }
.section { /* Modify section appearance */ }
.demo-box { /* Customize demo containers */ }
```

### Add New Sections
1. Create a new JSON file in `demo_app/pages/tutorial/`
2. Add it to the tabs definition in `dotpipe_tutorial.html`:
```html
<tabs id="mainTabs" tab="...;
    New Section:newTab:/demo_app/pages/tutorial/newsection.json
"></tabs>
```

### Update Examples
Edit any JSON file to modify:
- Demo descriptions
- Code examples
- Interactive elements
- Styling

## 📦 Dependencies

- **dotpipe.js** - The core framework (included)
- **Modern web browser** - Chrome, Firefox, Safari, Edge
- **HTTP server** (optional) - For AJAX features

## 🐛 Troubleshooting

### Tabs Not Loading
- Ensure the HTTP server is running
- Check that JSON file paths are correct
- Verify JSON syntax (use a validator)

### Inline Macros Not Working
- Make sure dotPipe.js is loaded
- Check browser console for errors
- Verify element IDs are unique

### API Calls Failing
- Check CORS settings if using external APIs
- Verify API endpoints are accessible
- Check network tab in browser DevTools

## 📝 Notes

- This tutorial is fully self-contained
- All examples are production-ready
- JSON structure can be reused in your projects
- The tutorial itself is a dotPipe application

## 🎯 Next Steps

After completing this tutorial:
1. Build your own dotPipe application
2. Create custom components
3. Integrate with your backend APIs
4. Explore the dotPipe.js source code
5. Join the dotPipe community

## 📄 License

This tutorial is part of the dotFly/dotPipe project.

## 🤝 Contributing

To improve this tutorial:
1. Edit the JSON files for content changes
2. Modify `dotpipe_tutorial.html` for structure changes
3. Test all interactive examples
4. Submit improvements

## 🌟 Highlights

- **8 comprehensive sections** covering all dotPipe features
- **30+ interactive demos** you can click and run
- **100+ code examples** with syntax highlighting
- **Self-documenting** - the tutorial explains itself
- **Production-ready** - use patterns in real projects
- **Beautiful design** - modern, responsive, accessible

---

**Built with ❤️ using dotPipe.js**

This tutorial demonstrates that dotPipe can build complex, interactive applications using declarative HTML attributes and JSON templates, with minimal JavaScript required.
