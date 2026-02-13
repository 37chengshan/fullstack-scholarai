#!/usr/bin/env python3
"""
ScholarAI Backend - Test Runner

Run all tests with coverage reporting.
Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --coverage   # Generate coverage report
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(args):
    """Run pytest with appropriate arguments."""
    base_args = ['pytest', '-v']

    if args.unit:
        base_args.extend(['-m', 'unit'])
    elif args.integration:
        base_args.extend(['-m', 'integration'])

    if args.coverage or not (args.unit or args.integration):
        # Add coverage flags
        base_args.extend([
            '--cov=.',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-report=json:coverage.json',
            '--cov-fail-under=80'
        ])

    # Add test path if specified
    if args.path:
        base_args.append(args.path)

    print(f"\n{'='*60}")
    print("Running ScholarAI Backend Test Suite")
    print(f"{'='*60}\n")
    print(f"Command: {' '.join(base_args)}\n")

    result = subprocess.run(base_args)

    if result.returncode == 0:
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60)
        print("\nCoverage reports:")
        print("  - Terminal: (shown above)")
        print("  - HTML:     htmlcov/index.html")
        print("  - JSON:     coverage.json")
    else:
        print("\n" + "="*60)
        print("❌ Some tests failed!")
        print("="*60)

    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run ScholarAI backend tests'
    )
    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run only unit tests'
    )
    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run only integration tests'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '--path',
        type=str,
        help='Run tests at specific path'
    )

    args = parser.parse_args()

    sys.exit(run_tests(args))


if __name__ == '__main__':
    main()
