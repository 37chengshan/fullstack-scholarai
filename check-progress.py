#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ScholarAI Progress Checker
Usage: python check-progress.py
"""

import json
import sys
import os
from datetime import datetime

def read_tasks():
    """Read tasks.json file"""
    try:
        with open('tasks.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['tasks']
    except FileNotFoundError:
        print("Error: tasks.json not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Cannot parse tasks.json - {e}")
        sys.exit(1)

def display_progress():
    """Display project progress"""
    tasks = read_tasks()

    # Count tasks by status
    completed = [t for t in tasks if t['status'] == 'completed']
    in_progress = [t for t in tasks if t['status'] == 'in_progress']
    pending = [t for t in tasks if t['status'] == 'pending']

    total = len(tasks)
    completed_count = len(completed)
    in_progress_count = len(in_progress)
    pending_count = len(pending)
    percentage = int(completed_count / total * 100) if total > 0 else 0

    # Display header
    print()
    print("=" * 60)
    print("  ScholarAI Project Progress")
    print("=" * 60)
    print()

    # Display overall progress
    print("Overall Progress:")
    print(f"  Total tasks:     {total}")
    print(f"  Completed:       {completed_count}")
    print(f"  In progress:     {in_progress_count}")
    print(f"  Pending:         {pending_count}")
    print()

    # Progress bar
    progress_width = 50
    filled = int(completed_count / total * progress_width) if total > 0 else 0
    empty = progress_width - filled
    progress_bar = "#" * filled + "-" * empty
    print(f"  Progress:        [{progress_bar}] {percentage}%")
    print()

    # Next pending tasks (by priority)
    if pending:
        pending_sorted = sorted(pending, key=lambda x: (x['priority'], x['id']))[:5]
        print("Next Pending Tasks (by priority):")
        for task in pending_sorted:
            print(f"  {task['id']} | {task['title']}")
            print(f"    Category: {task['category']}, Priority: {task['priority']}")
        print()

    # Recent completed tasks (last 5)
    if completed:
        completed_sorted = sorted(completed,
                               key=lambda x: x.get('completed_at', ''),
                               reverse=True)[:5]
        print("Recently Completed (last 5):")
        for task in completed_sorted:
            completed_at = task.get('completed_at', 'Unknown')
            if completed_at and completed_at != 'Unknown':
                try:
                    dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    completed_at = dt.strftime('%m-%d %H:%M')
                except:
                    pass
            print(f"  {task['id']} | {task['title']}")
            print(f"    Completed: {completed_at}")
        print()

    # Display footer
    print("=" * 60)
    print(f"  Completion: {percentage}%")
    print("=" * 60)
    print()

if __name__ == '__main__':
    display_progress()
