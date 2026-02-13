#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ScholarAI Auto-Dev Loop - Python Version for Reliability"""

import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

PROJECT_DIR = r"D:\ai\fullstack-merged"

def get_task_stats():
    """Get task statistics from get-task-stats.py"""
    try:
        result = subprocess.run(
            ["python", f"{PROJECT_DIR}\\get-task-stats.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split("|")
            return {
                "total": int(parts[0]),
                "completed": int(parts[1]),
                "pending": int(parts[2]),
                "percentage": int(parts[3])
            }
    except Exception as e:
        print(f"ERROR: Failed to get stats: {e}")
    return None

def run_claude(session_id):
    """Run Claude Code with the automation prompt"""
    prompt = f"""You are now a development assistant for ScholarAI project.

IMPORTANT: Work on ONE task at a time. Follow this workflow:

1. Read tasks.json from {PROJECT_DIR}
2. Select ONE PENDING task (priority=1 first)
3. Update task status to in_progress
4. Implement according to verification_steps
5. Use TDD: write tests first
6. Test your implementation
7. Commit to git with conventional format
8. Update task status to completed
9. Add completed_at timestamp
10. Write session summary to Progress-Logs folder

Project directory: {PROJECT_DIR}
Session ID: {session_id}

Start working now!"""

    # Write prompt to temp file
    temp_prompt = Path(PROJECT_DIR) / "auto-prompt-temp.txt"
    temp_prompt.write_text(prompt, encoding='utf-8')

    # Set environment variable
    env = {
        "CLAUDE_PROJECT_DIR": PROJECT_DIR,
    }

    # Run claude with prompt from stdin
    print("Starting Claude Code...")

    try:
        with open(temp_prompt, 'r', encoding='utf-8') as f:
            result = subprocess.run(
                ["claude", "--print", "--dangerously-skip-permissions"],
                env=env,
                stdin=f,
                timeout=600  # 10 minutes max per iteration
            )
        return result.returncode
    finally:
        # Clean up temp file
        if temp_prompt.exists():
            temp_prompt.unlink()

def main():
    if len(sys.argv) < 2:
        print("Usage: python run-auto.py <max_iterations>")
        print("Example: python run-auto.py 19")
        sys.exit(1)

    max_iterations = int(sys.argv[1])

    print("=" * 60)
    print(f"  ScholarAI Automation - {max_iterations} Tasks")
    print("=" * 60)
    print("")
    print(f"  Mode: Unattended (Auto-Yes)")
    print(f"  Project: {PROJECT_DIR}")
    print("")
    print("========================================")

    current_iteration = 0

    while current_iteration < max_iterations:
        current_iteration += 1
        iteration_start = time.time()
        session_id = f"session-{datetime.now().strftime('%Y-%m-%d')}-{current_iteration:03d}"

        print(f"  Iteration: {current_iteration} / {max_iterations}")
        print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
        print("")

        # Get stats
        stats = get_task_stats()
        if not stats:
            print("  ERROR: Failed to get stats")
            break

        print(f"  Total: {stats['total']} | Completed: {stats['completed']} | Pending: {stats['pending']} ({stats['percentage']}%)")

        if stats['pending'] == 0:
            print("  All tasks completed!")
            print("")
            break

        # Run Claude
        exit_code = run_claude(session_id)

        iteration_end = time.time()
        duration = iteration_end - iteration_start
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        if exit_code == 0:
            print(f"  SUCCESS ({minutes}m {seconds}s)")
        else:
            print(f"  FAILED (Exit code: {exit_code})")

        print("")
        time.sleep(1)

    print("")
    print("=" * 60)
    print("  Automation Complete")
    print("=" * 60)
    print("")
    print(f"  Total iterations: {current_iteration}")
    print("")

if __name__ == "__main__":
    main()
