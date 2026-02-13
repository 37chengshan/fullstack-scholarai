import json
import sys
from datetime import datetime, timezone

try:
    with open('tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data['tasks'])
    completed = sum(1 for t in data['tasks'] if t['status'] == 'completed')
    pending = sum(1 for t in data['tasks'] if t['status'] == 'pending')
    in_progress = sum(1 for t in data['tasks'] if t['status'] == 'in_progress')
    percentage = int(completed / total * 100) if total > 0 else 0

    print(f'{total}|{completed}|{pending}|{percentage}')

except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
