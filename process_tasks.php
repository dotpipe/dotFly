<?php
/**
 * Process Tasks - PHP Script
 * Receives task data, processes it, and returns analytics
 * 
 * Place on server: /api/scripts/process_tasks.php
 */

// Get incoming data
$tasks = $data['tasks'] ?? [];

// Process tasks
$analytics = [
    'total' => count($tasks),
    'completed' => 0,
    'pending' => 0,
    'in_progress' => 0,
    'high_priority' => 0,
    'overdue' => 0,
    'by_status' => [],
    'by_priority' => [],
    'upcoming' => []
];

$today = date('Y-m-d');

foreach ($tasks as $task) {
    $status = $task['status'] ?? 'Unknown';
    $priority = $task['priority'] ?? 'Unknown';
    $due_date = $task['due_date'] ?? '';
    
    // Count by status
    if ($status === 'Completed') {
        $analytics['completed']++;
    } elseif ($status === 'Pending') {
        $analytics['pending']++;
    } elseif ($status === 'In Progress') {
        $analytics['in_progress']++;
    }
    
    // Count by priority
    if ($priority === 'High') {
        $analytics['high_priority']++;
    }
    
    // Check overdue
    if ($due_date && $due_date < $today && $status !== 'Completed') {
        $analytics['overdue']++;
    }
    
    // Group by status
    if (!isset($analytics['by_status'][$status])) {
        $analytics['by_status'][$status] = [];
    }
    $analytics['by_status'][$status][] = $task;
    
    // Group by priority
    if (!isset($analytics['by_priority'][$priority])) {
        $analytics['by_priority'][$priority] = [];
    }
    $analytics['by_priority'][$priority][] = $task;
    
    // Upcoming tasks (within 7 days)
    if ($due_date && $due_date >= $today && $due_date <= date('Y-m-d', strtotime('+7 days'))) {
        $analytics['upcoming'][] = $task;
    }
}

// Generate HTML report
$html_report = "<div class='analytics-report'>";
$html_report .= "<h3>📊 Task Analytics</h3>";
$html_report .= "<div class='stats-grid'>";
$html_report .= "<div class='stat'><strong>Total:</strong> {$analytics['total']}</div>";
$html_report .= "<div class='stat success'><strong>Completed:</strong> {$analytics['completed']}</div>";
$html_report .= "<div class='stat warning'><strong>Pending:</strong> {$analytics['pending']}</div>";
$html_report .= "<div class='stat info'><strong>In Progress:</strong> {$analytics['in_progress']}</div>";
$html_report .= "<div class='stat danger'><strong>High Priority:</strong> {$analytics['high_priority']}</div>";
$html_report .= "<div class='stat danger'><strong>Overdue:</strong> {$analytics['overdue']}</div>";
$html_report .= "</div>";

// Upcoming tasks
if (!empty($analytics['upcoming'])) {
    $html_report .= "<h4>📅 Upcoming Tasks (Next 7 Days)</h4>";
    $html_report .= "<ul class='upcoming-list'>";
    foreach ($analytics['upcoming'] as $task) {
        $html_report .= "<li><strong>{$task['title']}</strong> - Due: {$task['due_date']} ({$task['priority']})</li>";
    }
    $html_report .= "</ul>";
}

$html_report .= "</div>";

// Return results
return [
    'success' => true,
    'analytics' => $analytics,
    'html_report' => $html_report,
    'processed_at' => date('Y-m-d H:i:s'),
    'message' => "Processed {$analytics['total']} tasks successfully"
];
?>
