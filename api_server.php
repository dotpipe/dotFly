<?php
/**
 * API Server for chat.chessers.club
 * Place this file at the root or configure routing to handle /api/* requests
 */

// Enable CORS for all origins
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json');

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Get the request URI and method
$requestUri = $_SERVER['REQUEST_URI'];
$method = $_SERVER['REQUEST_METHOD'];

// Parse the path
$path = parse_url($requestUri, PHP_URL_PATH);

// Get POST data if available
$postData = null;
if ($method === 'POST') {
    $postData = json_decode(file_get_contents('php://input'), true);
}

// Route handler
switch ($path) {
    case '/api/status':
        handleStatus();
        break;
    
    case '/api/message':
        handleMessage($postData);
        break;
    
    case '/api/messages':
        handleMessages();
        break;
    
    case '/api/user':
        handleUser();
        break;
    
    case '/api/info':
        handleInfo();
        break;
    
    case '/api/fs':
        handleFileSystem($postData);
        break;
    
    default:
        http_response_code(404);
        echo json_encode([
            'error' => 'Endpoint not found',
            'path' => $path,
            'available_endpoints' => [
                '/api/status',
                '/api/message',
                '/api/messages',
                '/api/user',
                '/api/info',
                '/api/fs'
            ]
        ]);
        break;
}

/**
 * GET /api/status - Check server status
 */
function handleStatus() {
    echo json_encode([
        'status' => 'online',
        'message' => 'Server is running',
        'timestamp' => time(),
        'uptime' => getServerUptime(),
        'version' => '1.0.0'
    ]);
}

/**
 * POST /api/message - Send a message
 */
function handleMessage($data) {
    if (!$data || !isset($data['message'])) {
        http_response_code(400);
        echo json_encode([
            'error' => 'Message is required',
            'received' => $data
        ]);
        return;
    }

    // Here you would save the message to database, process it, etc.
    $messageId = uniqid('msg_');
    
    echo json_encode([
        'success' => true,
        'message_id' => $messageId,
        'message' => $data['message'],
        'timestamp' => time(),
        'status' => 'delivered'
    ]);
}

/**
 * GET /api/messages - Retrieve messages
 */
function handleMessages() {
    // This would typically fetch from database
    $messages = [
        [
            'id' => 'msg_001',
            'sender' => 'system',
            'message' => 'Welcome to the chat server!',
            'timestamp' => time() - 3600
        ],
        [
            'id' => 'msg_002',
            'sender' => 'user_123',
            'message' => 'Hello, this is a test message',
            'timestamp' => time() - 1800
        ],
        [
            'id' => 'msg_003',
            'sender' => 'admin',
            'message' => 'Server maintenance scheduled for tonight',
            'timestamp' => time() - 900
        ]
    ];

    echo json_encode([
        'success' => true,
        'count' => count($messages),
        'messages' => $messages
    ]);
}

/**
 * GET /api/user - Get user information
 */
function handleUser() {
    // This would typically fetch from session or database
    echo json_encode([
        'user_id' => 'user_' . rand(1000, 9999),
        'username' => 'guest_user',
        'email' => 'guest@example.com',
        'role' => 'user',
        'joined' => time() - 86400 * 30,
        'last_active' => time()
    ]);
}

/**
 * GET /api/info - Get server information
 */
function handleInfo() {
    echo json_encode([
        'server_name' => 'chat.chessers.club',
        'version' => '1.0.0',
        'api_version' => 'v1',
        'php_version' => PHP_VERSION,
        'server_time' => time(),
        'timezone' => date_default_timezone_get(),
        'endpoints' => [
            '/api/status' => 'GET - Check server status',
            '/api/message' => 'POST - Send a message',
            '/api/messages' => 'GET - Retrieve messages',
            '/api/user' => 'GET - Get user information',
            '/api/info' => 'GET - Get server information'
        ]
    ]);
}

/**
 * POST/GET /api/fs - File system operations
 */
function handleFileSystem($data) {
    // Define allowed operations
    $operation = $_GET['operation'] ?? ($data['operation'] ?? null);
    
    if (!$operation) {
        http_response_code(400);
        echo json_encode([
            'error' => 'Operation parameter required',
            'available_operations' => ['list', 'read', 'write', 'delete', 'info']
        ]);
        return;
    }
    
    switch ($operation) {
        case 'list':
            // List files in a directory
            $dir = $data['path'] ?? './';
            if (!is_dir($dir)) {
                echo json_encode(['error' => 'Directory not found']);
                return;
            }
            $files = array_diff(scandir($dir), ['.', '..']);
            echo json_encode([
                'success' => true,
                'path' => $dir,
                'files' => array_values($files)
            ]);
            break;
            
        case 'read':
            // Read file contents
            $file = $data['file'] ?? null;
            if (!$file || !file_exists($file)) {
                echo json_encode(['error' => 'File not found']);
                return;
            }
            echo json_encode([
                'success' => true,
                'file' => $file,
                'content' => file_get_contents($file),
                'size' => filesize($file)
            ]);
            break;
            
        case 'write':
            // Write file contents
            $file = $data['file'] ?? null;
            $content = $data['content'] ?? '';
            if (!$file) {
                echo json_encode(['error' => 'File path required']);
                return;
            }
            $result = file_put_contents($file, $content);
            echo json_encode([
                'success' => $result !== false,
                'file' => $file,
                'bytes_written' => $result
            ]);
            break;
            
        case 'delete':
            // Delete a file
            $file = $data['file'] ?? null;
            if (!$file || !file_exists($file)) {
                echo json_encode(['error' => 'File not found']);
                return;
            }
            $result = unlink($file);
            echo json_encode([
                'success' => $result,
                'file' => $file
            ]);
            break;
            
        case 'info':
            // Get file information
            $file = $data['file'] ?? null;
            if (!$file || !file_exists($file)) {
                echo json_encode(['error' => 'File not found']);
                return;
            }
            echo json_encode([
                'success' => true,
                'file' => $file,
                'size' => filesize($file),
                'modified' => filemtime($file),
                'is_writable' => is_writable($file),
                'is_readable' => is_readable($file)
            ]);
            break;
            
        default:
            echo json_encode([
                'error' => 'Unknown operation',
                'available_operations' => ['list', 'read', 'write', 'delete', 'info']
            ]);
            break;
    }
}

/**
 * Helper function to get server uptime
 */
function getServerUptime() {
    if (file_exists('/proc/uptime')) {
        $uptime = file_get_contents('/proc/uptime');
        $uptime = explode(' ', $uptime);
        return (int)$uptime[0];
    }
    return 0;
}
