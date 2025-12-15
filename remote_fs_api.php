<?php
/**
 * Remote Filesystem API
 * Handles file operations for remote clients via HTTP
 * 
 * Place in: http://chat.chessers.club/api/fs.php
 * 
 * Operations:
 *   POST /api/fs/read     - Read file
 *   POST /api/fs/write    - Write file
 *   POST /api/fs/append   - Append to file
 *   POST /api/fs/delete   - Delete file
 *   POST /api/fs/exists   - Check if file exists
 *   POST /api/fs/listdir  - List directory
 *   POST /api/fs/mkdir    - Create directory
 *   POST /api/fs/info     - Get file info
 *   POST /api/fs/execute/* - Execute PHP script
 */

header('Content-Type: application/json');

// Configuration
$CONFIG = [
    'root_directory' => __DIR__ . '/../data',  // Base directory for file operations
    'allowed_paths' => [],  // Empty = all paths under root, or specify allowed paths
    'api_key' => getenv('REMOTE_FS_API_KEY') ?: null,  // Set via environment variable
    'max_file_size' => 100 * 1024 * 1024,  // 100MB
    'allowed_extensions' => [],  // Empty = all allowed, or specify whitelist
];

// Verify API key if configured
function verify_api_key() {
    global $CONFIG;
    
    if (!$CONFIG['api_key']) {
        return true;  // No key required
    }
    
    $provided_key = $_SERVER['HTTP_X_API_KEY'] ?? null;
    if (!$provided_key || $provided_key !== $CONFIG['api_key']) {
        http_response_code(401);
        die(json_encode(['success' => false, 'error' => 'Unauthorized', 'code' => 'auth_failed']));
    }
    
    return true;
}

// Sanitize path to prevent directory traversal
function sanitize_path($path) {
    global $CONFIG;
    
    // Remove leading/trailing slashes
    $path = trim($path, '/');
    
    // Prevent directory traversal
    if (strpos($path, '..') !== false) {
        throw new Exception('Invalid path: directory traversal detected');
    }
    
    $full_path = realpath($CONFIG['root_directory'] . '/' . $path);
    $root = realpath($CONFIG['root_directory']);
    
    if ($full_path === false || strpos($full_path, $root) !== 0) {
        throw new Exception('Invalid path: outside root directory');
    }
    
    // Check extension whitelist
    if (!empty($CONFIG['allowed_extensions'])) {
        $ext = strtolower(pathinfo($full_path, PATHINFO_EXTENSION));
        if (!in_array($ext, $CONFIG['allowed_extensions'])) {
            throw new Exception('File type not allowed');
        }
    }
    
    return $full_path;
}

// Helper to send JSON response
function respond($success, $data = [], $error = null) {
    $response = ['success' => $success] + $data;
    if ($error) {
        $response['error'] = $error;
    }
    echo json_encode($response);
    exit;
}

// Get request data
$request = json_decode(file_get_contents('php://input'), true) ?? [];
$method = strtolower($_SERVER['REQUEST_METHOD']);

// Route to appropriate handler
$path_parts = explode('/', trim($_SERVER['PATH_INFO'] ?? '', '/'));
$action = $path_parts[0] ?? 'unknown';
$script_name = $path_parts[1] ?? null;

verify_api_key();

try {
    switch ($action) {
        case 'read':
            handle_read($request);
            break;
        
        case 'write':
            handle_write($request);
            break;
        
        case 'append':
            handle_append($request);
            break;
        
        case 'delete':
            handle_delete($request);
            break;
        
        case 'exists':
            handle_exists($request);
            break;
        
        case 'listdir':
            handle_listdir($request);
            break;
        
        case 'mkdir':
            handle_mkdir($request);
            break;
        
        case 'info':
            handle_info($request);
            break;
        
        case 'execute':
            handle_execute($request, $script_name);
            break;
        
        default:
            http_response_code(400);
            respond(false, [], "Unknown action: $action");
    }
} catch (Exception $e) {
    http_response_code(400);
    respond(false, [], $e->getMessage());
}

// Handler functions
function handle_read($request) {
    global $CONFIG;
    
    $path = $request['path'] ?? null;
    if (!$path) {
        respond(false, [], 'Path required');
    }
    
    $full_path = sanitize_path($path);
    
    if (!file_exists($full_path)) {
        respond(false, [], 'File not found');
    }
    
    if (!is_readable($full_path)) {
        respond(false, [], 'Permission denied');
    }
    
    $content = file_get_contents($full_path);
    
    respond(true, [
        'content' => $content,
        'size' => strlen($content),
        'is_base64' => false
    ]);
}

function handle_write($request) {
    global $CONFIG;
    
    $path = $request['path'] ?? null;
    $content = $request['content'] ?? '';
    $create_dirs = $request['create_dirs'] ?? true;
    
    if (!$path) {
        respond(false, [], 'Path required');
    }
    
    $full_path = sanitize_path($path);
    $dir = dirname($full_path);
    
    if ($create_dirs && !is_dir($dir)) {
        if (!mkdir($dir, 0755, true)) {
            respond(false, [], 'Failed to create directories');
        }
    }
    
    if (strlen($content) > $CONFIG['max_file_size']) {
        respond(false, [], 'File too large');
    }
    
    if (!file_put_contents($full_path, $content, LOCK_EX)) {
        respond(false, [], 'Failed to write file');
    }
    
    respond(true, [
        'path' => $path,
        'bytes_written' => strlen($content)
    ]);
}

function handle_append($request) {
    global $CONFIG;
    
    $path = $request['path'] ?? null;
    $content = $request['content'] ?? '';
    
    if (!$path) {
        respond(false, [], 'Path required');
    }
    
    $full_path = sanitize_path($path);
    
    if (!file_exists($full_path)) {
        respond(false, [], 'File not found');
    }
    
    $current_size = filesize($full_path);
    if ($current_size + strlen($content) > $CONFIG['max_file_size']) {
        respond(false, [], 'File too large');
    }
    
    if (!file_put_contents($full_path, $content, FILE_APPEND | LOCK_EX)) {
        respond(false, [], 'Failed to append to file');
    }
    
    respond(true, [
        'path' => $path,
        'bytes_appended' => strlen($content)
    ]);
}

function handle_delete($request) {
    $path = $request['path'] ?? null;
    if (!$path) {
        respond(false, [], 'Path required');
    }
    
    $full_path = sanitize_path($path);
    
    if (!file_exists($full_path)) {
        respond(false, [], 'File not found');
    }
    
    if (!unlink($full_path)) {
        respond(false, [], 'Failed to delete file');
    }
    
    respond(true, ['path' => $path]);
}

function handle_exists($request) {
    $path = $request['path'] ?? null;
    if (!$path) {
        respond(false, [], 'Path required');
    }
    
    try {
        $full_path = sanitize_path($path);
        respond(true, ['exists' => file_exists($full_path)]);
    } catch (Exception $e) {
        respond(true, ['exists' => false]);
    }
}

function handle_listdir($request) {
    $path = $request['path'] ?? '/';
    
    $full_path = sanitize_path($path);
    
    if (!is_dir($full_path)) {
        respond(false, [], 'Not a directory');
    }
    
    $files = scandir($full_path);
    $files = array_filter($files, fn($f) => $f !== '.' && $f !== '..');
    
    respond(true, [
        'path' => $path,
        'files' => array_values($files),
        'count' => count($files)
    ]);
}

function handle_mkdir($request) {
    global $CONFIG;
    
    $path = $request['path'] ?? null;
    $parents = $request['parents'] ?? true;
    
    if (!$path) {
        respond(false, [], 'Path required');
    }
    
    $full_path = sanitize_path($path);
    
    if (is_dir($full_path)) {
        respond(true, ['path' => $path, 'created' => false]);
    }
    
    if (!mkdir($full_path, 0755, $parents)) {
        respond(false, [], 'Failed to create directory');
    }
    
    respond(true, ['path' => $path, 'created' => true]);
}

function handle_info($request) {
    $path = $request['path'] ?? null;
    if (!$path) {
        respond(false, [], 'Path required');
    }
    
    $full_path = sanitize_path($path);
    
    if (!file_exists($full_path)) {
        respond(false, [], 'File not found');
    }
    
    $info = [
        'path' => $path,
        'exists' => true,
        'is_file' => is_file($full_path),
        'is_dir' => is_dir($full_path),
        'size' => filesize($full_path),
        'modified' => filemtime($full_path),
        'created' => filectime($full_path),
        'permissions' => substr(sprintf('%o', fileperms($full_path)), -4),
    ];
    
    respond(true, ['info' => $info]);
}

function handle_execute($request, $script_name) {
    if (!$script_name) {
        respond(false, [], 'Script name required');
    }
    
    // Scripts must be in scripts/ subdirectory
    $script_path = __DIR__ . '/../scripts/' . basename($script_name) . '.php';
    
    if (!file_exists($script_path)) {
        respond(false, [], 'Script not found');
    }
    
    // Execute script with data
    $data = $request;
    ob_start();
    $result = include $script_path;
    $output = ob_get_clean();
    
    // Script should return result or echo JSON
    if (is_array($result)) {
        respond(true, $result);
    } else if ($output) {
        echo $output;
    } else {
        respond(true, ['executed' => true]);
    }
}
?>
