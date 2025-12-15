"""Test CSV database read/write operations"""
from src.json_framework import OptimizedCSVDatabase
import json

# Test CSV database operations
print("Testing CSV Database Read/Write Operations")
print("=" * 50)

# 1. Test Read
print("\n1. Testing READ (get_all):")
db = OptimizedCSVDatabase('demo_app/data/tasks.csv')
tasks = db.get_all()
print(f"   Total tasks: {len(tasks)}")
for i, task in enumerate(tasks[:2], 1):
    print(f"   Task {i}: {task}")

# 2. Test Write (Insert)
print("\n2. Testing WRITE (insert):")
new_task = {
    'id': '999',
    'title': 'Test Task from API',
    'status': 'Pending',
    'priority': 'Low',
    'due_date': '2025-12-20'
}
result = db.insert(new_task)
print(f"   Insert result: {result}")

# 3. Verify write by reading again
print("\n3. Verifying WRITE (re-reading):")
tasks_after = db.get_all()
print(f"   Total tasks after insert: {len(tasks_after)}")
last_task = tasks_after[-1]
print(f"   Last task: {last_task}")

# 4. Check actual CSV file
print("\n4. Checking actual CSV file:")
with open('demo_app/data/tasks.csv', 'r') as f:
    lines = f.readlines()
    print(f"   File lines: {len(lines)}")
    print(f"   Last line: {lines[-1].strip()}")

print("\n✓ Test complete!")
