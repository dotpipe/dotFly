<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

// Simple session tracking using IP
$userId = 'user_' . md5($_SERVER['REMOTE_ADDR'] ?? 'unknown');
$username = 'Guest_' . substr($userId, -4);

// Track active users
$dataDir = __DIR__ . '/data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0777, true);
}

$usersFile = $dataDir . '/users.json';
$users = [];
if (file_exists($usersFile)) {
    $users = json_decode(file_get_contents($usersFile), true) ?: [];
}

// Update or add user
$users[$userId] = [
    'user_id' => $userId,
    'username' => $username,
    'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
    'last_active' => time(),
    'first_seen' => $users[$userId]['first_seen'] ?? time()
];

// Remove inactive users (>1 hour)
$users = array_filter($users, function($user) {
    return ($user['last_active'] > time() - 3600);
});

file_put_contents($usersFile, json_encode($users, JSON_PRETTY_PRINT));

echo json_encode([
    'user_id' => $userId,
    'username' => $username,
    'role' => 'user',
    'last_active' => time(),
    'active_users' => count($users),
    'session_age' => time() - $users[$userId]['first_seen']
]);
