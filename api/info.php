<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

// Get statistics
$dataDir = __DIR__ . '/data';
$messagesFile = $dataDir . '/messages.json';
$usersFile = $dataDir . '/users.json';

$messageCount = 0;
if (file_exists($messagesFile)) {
    $messages = json_decode(file_get_contents($messagesFile), true) ?: [];
    $messageCount = count($messages);
}

$activeUsers = 0;
if (file_exists($usersFile)) {
    $users = json_decode(file_get_contents($usersFile), true) ?: [];
    $activeUsers = count($users);
}

// Disk usage
$diskFree = disk_free_space('.');
$diskTotal = disk_total_space('.');
$diskUsed = $diskTotal - $diskFree;

echo json_encode([
    'server_name' => 'chat.chessers.club',
    'version' => '1.0.0',
    'php_version' => PHP_VERSION,
    'server_time' => time(),
    'server_date' => date('Y-m-d H:i:s'),
    'statistics' => [
        'total_messages' => $messageCount,
        'active_users' => $activeUsers,
        'disk_used' => round($diskUsed / 1024 / 1024, 2) . ' MB',
        'disk_free' => round($diskFree / 1024 / 1024, 2) . ' MB'
    ],
    'endpoints' => [
        '/api/status.php' => 'GET - Check server status',
        '/api/message.php' => 'POST - Send a message (stores in data/messages.json)',
        '/api/messages.php' => 'GET - Retrieve messages (reads from data/messages.json)',
        '/api/user.php' => 'GET - Get user information (tracks active users)',
        '/api/info.php' => 'GET - Get server information with statistics'
    ]
]);
