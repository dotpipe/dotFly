<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

echo json_encode([
    'server_name' => 'chat.chessers.club',
    'version' => '1.0.0',
    'php_version' => PHP_VERSION,
    'server_time' => time(),
    'endpoints' => [
        '/api/status.php' => 'GET - Check server status',
        '/api/message.php' => 'POST - Send a message',
        '/api/messages.php' => 'GET - Retrieve messages',
        '/api/user.php' => 'GET - Get user information',
        '/api/info.php' => 'GET - Get server information'
    ]
]);
