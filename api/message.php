<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

$data = json_decode(file_get_contents('php://input'), true);

if (!$data || !isset($data['message'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Message is required']);
    exit();
}

// Create data directory if it doesn't exist
$dataDir = __DIR__ . '/data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0777, true);
}

// Load existing messages
$messagesFile = $dataDir . '/messages.json';
$messages = [];
if (file_exists($messagesFile)) {
    $messages = json_decode(file_get_contents($messagesFile), true) ?: [];
}

// Create new message
$newMessage = [
    'id' => uniqid('msg_'),
    'sender' => $data['sender'] ?? 'anonymous',
    'message' => $data['message'],
    'timestamp' => time(),
    'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown'
];

// Add to messages array
array_unshift($messages, $newMessage); // Add to beginning

// Keep only last 100 messages
$messages = array_slice($messages, 0, 100);

// Save messages
file_put_contents($messagesFile, json_encode($messages, JSON_PRETTY_PRINT));

echo json_encode([
    'success' => true,
    'message_id' => $newMessage['id'],
    'message' => $newMessage['message'],
    'sender' => $newMessage['sender'],
    'timestamp' => $newMessage['timestamp'],
    'total_messages' => count($messages)
]);
