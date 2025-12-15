<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

// Load messages from file
$dataDir = __DIR__ . '/data';
$messagesFile = $dataDir . '/messages.json';

$messages = [];
if (file_exists($messagesFile)) {
    $messages = json_decode(file_get_contents($messagesFile), true) ?: [];
}

// Get query parameters
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 50;
$offset = isset($_GET['offset']) ? (int)$_GET['offset'] : 0;

// Paginate
$totalMessages = count($messages);
$paginatedMessages = array_slice($messages, $offset, $limit);

echo json_encode([
    'success' => true,
    'count' => count($paginatedMessages),
    'total' => $totalMessages,
    'limit' => $limit,
    'offset' => $offset,
    'messages' => $paginatedMessages
]);
