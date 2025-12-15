# dotFly Desktop Application Framework

A lightweight desktop application framework combining Python with dotPipe.js to create web-based desktop apps using JSON-driven UI templates.

## What We Built

A complete desktop application featuring:
- **Native Desktop Window**: Python + pywebview for cross-platform desktop apps
- **JSON Template System**: Define UI using simple JSON structures
- **API Testing Console**: Full-featured REST API client with tabbed interface
- **Live Development**: Auto-reload when JSON templates change
- **Remote API Integration**: Connect to external servers with CORS support

## Architecture

```
Python Desktop App (pywebview)
    ↓
HTTP Server (localhost:8000)
    ↓
Static HTML Page (console.html)
    ↓
dotPipe.js Framework (renders JSON)
    ↓
<tabs> Component (loads JSON via AJAX)
    ↓
API Tester (fetches from chat.chessers.club)
```

## Project Structure

```
dotFly/
├── launcher.py              # Start the app
├── dotpipe.js              # 6624-line rendering framework
├── demo_app/
│   ├── console.html        # Main console page
│   ├── pages/
│   │   ├── console_api.json     # API testing interface
│   │   ├── console_docs.json    # Documentation tab
│   │   └── console_history.json # History tab
│   └── assets/
│       └── style.css       # Styling with tabs CSS
├── api/                    # Upload to your server
│   ├── status.php
│   ├── message.php
│   ├── messages.php
│   ├── user.php
│   └── info.php
└── src/
    └── app_runtime.py      # Server & file watcher
```

## Run It

```bash
python launcher.py run demo_app
```

Opens a desktop window with the console at `http://localhost:8000/console`

## Console Features

### Tabs
- **🚀 API Tester**: Test REST APIs interactively
- **📚 Docs**: View API documentation  
- **📜 History**: See request history

### API Tester
- Select endpoint from dropdown
- Choose GET or POST method
- Edit JSON request body
- Click "Send Request" to call API
- View formatted response in terminal-style display
- "Load Example" populates sample data
- "Clear" resets the form

### Connected Endpoints
- `GET /api/status.php` - Server status
- `POST /api/message.php` - Send message
- `GET /api/messages.php` - Get messages
- `GET /api/user.php` - User info
- `GET /api/info.php` - Server info

All connect to: `http://chat.chessers.club/api/`

## JSON Template Format

```json
{
  "tagname": "div",
  "id": "myDiv",
  "class": "container",
  "children": [
    {
      "tagname": "h1",
      "textContent": "Title"
    },
    {
      "tagname": "button",
      "id": "btn",
      "textContent": "Click Me",
      "onclick": "alert('Hi!')"
    }
  ]
}
```

### Tabs Component
```json
{
  "tagname": "tabs",
  "id": "myTabs",
  "tab": "Tab1:target1:/path/to/tab1.json;Tab2:target2:/path/to/tab2.json"
}
```

### Select Dropdown
```json
{
  "tagname": "select",
  "id": "mySelect",
  "options": "Label1:Value1;Label2:Value2"
}
```

### Form Elements
Add `class="formClassName"` to inputs, and `form-class="formClassName"` to submit button

## Backend API (PHP)

Upload `api/` folder to your server. Each file has CORS headers enabled:

```php
<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

echo json_encode([
    'status' => 'online',
    'timestamp' => time()
]);
```

## How It Works

### 1. Python Server
`src/app_runtime.py` runs HTTP server on port 8000:
- Serves static HTML (`console.html`)
- Serves dotPipe.js framework
- Serves JSON templates
- Watches for file changes → auto-reload

### 2. Static HTML Page
`demo_app/console.html`:
- No CSP restrictions
- Loads dotPipe.js
- Contains `<tabs>` element
- Calls `domContentLoad()` to initialize dotPipe

### 3. dotPipe.js Framework
`dotpipe.js` (6624 lines):
- Processes `<tabs>` element
- Parses `tab` attribute
- Fetches JSON files via AJAX
- Renders with `modala()` function
- Sets up click handlers
- Manages tab switching

### 4. Tab Content
`console_api.json`:
- Table structure with form elements
- Select dropdowns with `options` attribute
- Buttons with `onclick` handlers
- Script tag with `sendRequest()` function
- Fetches from remote API using `fetch()`

### 5. Remote API
`chat.chessers.club/api/*.php`:
- Responds with JSON
- CORS headers allow cross-origin requests
- Handles GET/POST methods

## Key Decisions

### Why Static HTML Instead of JSON?
- **CSP Issues**: modala() injected restrictive CSP that blocked inline styles
- **Solution**: Use plain HTML page, let dotPipe process `<tabs>` component
- **Benefit**: No CSP conflicts, full browser API access

### Why .php Extensions?
- **URL Rewriting Failed**: .htaccess routing didn't work on server
- **Solution**: Direct PHP file access (`status.php` instead of `status`)
- **Benefit**: Works on any PHP host without special configuration

### Why No Form Submission?
- **API Design**: Using `fetch()` for AJAX calls instead of HTML forms
- **Benefit**: Better control, JSON payloads, async responses

## Development

### Add New Page
1. Create `demo_app/pages/my-page.json`
2. Access at `http://localhost:8000/my-page`

### Add New Tab
Edit `console.html`:
```html
<tabs id="myTabs" tab="New Tab:tabId:/demo_app/pages/new-content.json"></tabs>
```

### Style Changes
Edit `demo_app/assets/style.css` - changes apply immediately

### API Changes
Edit PHP files, upload to server, test in console

## Requirements

```txt
pywebview>=5.0
watchdog>=3.0
```

Install: `pip install -r requirements.txt`

## Troubleshooting

### Tabs Not Showing
- Check browser console (F12) for errors
- Verify `domContentLoad()` is called
- Ensure JSON files exist

### API Not Connecting
- Check CORS headers on server
- Verify endpoint URLs
- Test endpoint directly in browser
- Check browser console for network errors

### Styles Not Applying
- Remove any CSP meta tags
- Check CSS file is being served
- Inspect element to verify CSS loaded

## Tech Stack

- **Python 3.13**: Application runtime
- **pywebview**: Native window (uses Chromium on Windows)
- **watchdog**: File monitoring for auto-reload
- **dotPipe.js**: Client-side rendering framework
- **PHP**: Backend API (any language works with CORS)

## What Makes This Special

1. **No Build Process**: JSON → UI instantly
2. **Live Reload**: Edit JSON, see changes immediately
3. **Desktop Native**: Runs as real Windows app, not browser
4. **API Testing**: Built-in REST client for development
5. **Simple Deployment**: Just Python + JSON files

## Future Enhancements

- [ ] Add authentication to API
- [ ] Implement request history storage
- [ ] Add more API endpoints
- [ ] Create visual JSON editor
- [ ] Package as standalone executable
- [ ] Add database integration
- [ ] Create component library

## Credits

**dotPipe.js**: Custom web components framework  
**Built**: December 15, 2025  
**Stack**: Python + JavaScript + PHP

---

For the dotPipe language documentation, see `README_dotpipe_language.md`
