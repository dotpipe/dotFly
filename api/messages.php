<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

echo json_encode([
    'success' => true,
    'messages' => [
        ['id' => 'msg_001', 'sender' => 'system', 'message' => 'Welcome!', 'timestamp' => time() - 3600],
        ['id' => 'msg_002', 'sender' => 'user_123', 'message' => 'Hello', 'timestamp' => time() - 1800]
    ]
]);
