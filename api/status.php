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
    'message' => 'Chat server is running',
    'timestamp' => time(),
    'version' => '1.0.0'
]);
