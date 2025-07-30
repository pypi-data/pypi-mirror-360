#!/usr/bin/env python3
"""
Build and publish script for grasp_sdk package.

Usage:
    python build_and_publish.py --build-only    # Only build the package
    python build_and_publish.py --test          # Upload to TestPyPI
    python build_and_publish.py --prod          # Upload to PyPI
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    
    return result


def clean_build_dirs():
    """Clean previous build artifacts."""
    print("Cleaning build directories...")
    dirs_to_clean = ['build', 'dist', 'grasp_sdk.egg-info']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            run_command(f"rm -rf {dir_name}")


def build_package():
    """Build the package."""
    print("Building package...")
    
    # Install build dependencies
    run_command("pip install --upgrade build twine")
    
    # Build the package
    run_command("python -m build")
    
    print("Package built successfully!")
    print("Built files:")
    if os.path.exists('dist'):
        for file in os.listdir('dist'):
            print(f"  - dist/{file}")


def upload_to_testpypi():
    """Upload package to TestPyPI."""
    print("Uploading to TestPyPI...")
    run_command("python -m twine upload --repository testpypi dist/*")
    print("Package uploaded to TestPyPI successfully!")
    print("Install with: pip install --index-url https://test.pypi.org/simple/ grasp_sdk")


def upload_to_pypi():
    """Upload package to PyPI."""
    print("Uploading to PyPI...")
    
    # Confirm before uploading to production
    response = input("Are you sure you want to upload to PyPI? (yes/no): ")
    if response.lower() != 'yes':
        print("Upload cancelled.")
        return
    
    run_command("python -m twine upload dist/*")
    print("Package uploaded to PyPI successfully!")
    print("Install with: pip install grasp_sdk")


def check_package():
    """Run package checks."""
    print("Running package checks...")
    
    # Check if required files exist
    required_files = ['README.md', 'pyproject.toml', 'setup.py', '__init__.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Warning: {file} not found")
    
    # Check package with twine
    if os.path.exists('dist'):
        run_command("python -m twine check dist/*")
    
    print("Package checks completed.")


def main():
    parser = argparse.ArgumentParser(description='Build and publish grasp_sdk package')
    parser.add_argument('--build-only', action='store_true', help='Only build the package')
    parser.add_argument('--test', action='store_true', help='Upload to TestPyPI')
    parser.add_argument('--prod', action='store_true', help='Upload to PyPI')
    parser.add_argument('--check', action='store_true', help='Run package checks only')
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    if args.check:
        check_package()
        return
    
    # Clean and build
    clean_build_dirs()
    build_package()
    check_package()
    
    if args.build_only:
        print("Build completed. Use --test or --prod to upload.")
    elif args.test:
        upload_to_testpypi()
    elif args.prod:
        upload_to_pypi()
    else:
        print("Package built successfully!")
        print("Next steps:")
        print("  - Test upload: python build_and_publish.py --test")
        print("  - Production upload: python build_and_publish.py --prod")


if __name__ == '__main__':
    main()