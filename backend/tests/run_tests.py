#!/usr/bin/env python3
"""
Test Runner for Epic 7 Sprint 2 Testing Suite
Epic 7 Sprint 3 - Comprehensive Testing

Runs all tests with proper configuration and reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_test_environment():
    """Set up test environment variables"""
    test_env = os.environ.copy()
    test_env.update({
        'FLASK_ENV': 'testing',
        'TESTING': 'true',
        'API_VERSION': '1.0.0',
        'LOG_LEVEL': 'DEBUG',
        'DATABASE_URL': 'sqlite:///:memory:',
        'ENABLE_RATE_LIMITING': 'false',  # Disable for most tests
        'CORS_ORIGINS': 'http://localhost:3000',
        'PYTHONPATH': str(Path(__file__).parent.parent)
    })
    return test_env


def run_test_suite(test_type='all', verbose=False, coverage=False):
    """Run test suite with specified options"""
    
    # Set up environment
    env = setup_test_environment()
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test directory
    test_dir = Path(__file__).parent
    cmd.append(str(test_dir))
    
    # Configure output
    if verbose:
        cmd.extend(['-v', '-s'])
    else:
        cmd.append('-v')
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            '--cov=backend/api',
            '--cov-report=term-missing',
            '--cov-report=html:backend/tests/coverage_html',
            '--cov-fail-under=70'
        ])
    
    # Filter by test type
    if test_type == 'unit':
        cmd.extend(['-m', 'unit or not (integration or performance or security)'])
    elif test_type == 'integration':
        cmd.extend(['-m', 'integration'])
    elif test_type == 'performance':
        cmd.extend(['-m', 'performance'])
    elif test_type == 'security':
        cmd.extend(['-m', 'security'])
    elif test_type == 'smoke':
        cmd.extend(['-m', 'smoke'])
    elif test_type == 'quick':
        cmd.extend(['-m', 'not (slow or performance)'])
    
    # Additional pytest options
    cmd.extend([
        '--tb=short',
        '--strict-markers',
        '--maxfail=10',
        '--durations=10'
    ])
    
    print(f"🧪 Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 80)
    
    # Run tests
    try:
        result = subprocess.run(cmd, env=env, cwd=test_dir.parent.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def run_specific_test_file(test_file, verbose=False):
    """Run a specific test file"""
    
    env = setup_test_environment()
    test_dir = Path(__file__).parent
    test_path = test_dir / test_file
    
    if not test_path.exists():
        print(f"❌ Test file not found: {test_file}")
        return 1
    
    cmd = ['python', '-m', 'pytest', str(test_path)]
    
    if verbose:
        cmd.extend(['-v', '-s'])
    
    cmd.extend(['--tb=short'])
    
    print(f"🧪 Running test file: {test_file}")
    print("=" * 80)
    
    try:
        result = subprocess.run(cmd, env=env, cwd=test_dir.parent.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1


def install_test_dependencies():
    """Install required test dependencies"""
    dependencies = [
        'pytest>=6.0.0',
        'pytest-cov>=2.10.0',
        'pytest-mock>=3.3.0',
        'pytest-xdist>=2.0.0',
        'pytest-timeout>=1.4.0',
        'flask[testing]>=2.0.0',
        'coverage>=5.0.0'
    ]
    
    print("📦 Installing test dependencies...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True)
            print(f"  ✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"  ❌ Failed to install {dep}")
    
    print("✅ Test dependencies installation complete")


def generate_test_report():
    """Generate comprehensive test report"""
    print("📊 Generating test report...")
    
    # Run all tests with coverage
    env = setup_test_environment()
    cmd = [
        'python', '-m', 'pytest',
        '--cov=backend/api',
        '--cov-report=html:backend/tests/coverage_html',
        '--cov-report=term-missing',
        '--cov-report=json:backend/tests/coverage.json',
        '--junit-xml=backend/tests/test_results.xml',
        '--tb=short',
        '-v'
    ]
    
    test_dir = Path(__file__).parent
    cmd.append(str(test_dir))
    
    try:
        result = subprocess.run(cmd, env=env, cwd=test_dir.parent.parent)
        
        if result.returncode == 0:
            print("✅ Test report generated successfully")
            print("📄 Reports available at:")
            print("  - HTML Coverage: backend/tests/coverage_html/index.html")
            print("  - JSON Coverage: backend/tests/coverage.json")
            print("  - JUnit XML: backend/tests/test_results.xml")
        else:
            print("⚠️  Test report generated with failures")
        
        return result.returncode
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return 1


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Epic 7 Sprint 2 Test Runner')
    
    parser.add_argument(
        'command',
        choices=['run', 'file', 'install', 'report'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--type',
        choices=['all', 'unit', 'integration', 'performance', 'security', 'smoke', 'quick'],
        default='all',
        help='Type of tests to run'
    )
    
    parser.add_argument(
        '--file',
        help='Specific test file to run (for file command)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run with coverage reporting'
    )
    
    args = parser.parse_args()
    
    if args.command == 'install':
        return install_test_dependencies()
    
    elif args.command == 'run':
        return run_test_suite(args.type, args.verbose, args.coverage)
    
    elif args.command == 'file':
        if not args.file:
            print("❌ --file argument required for 'file' command")
            return 1
        return run_specific_test_file(args.file, args.verbose)
    
    elif args.command == 'report':
        return generate_test_report()
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    exit_code = main()
    
    # Print summary
    if exit_code == 0:
        print("\n🎉 All tests completed successfully!")
    else:
        print(f"\n❌ Tests completed with exit code: {exit_code}")
    
    sys.exit(exit_code)