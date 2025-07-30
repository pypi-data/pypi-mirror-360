#!/usr/bin/env python3
"""
Build and Upload Script for Financial MCP Package

This script provides an interactive way to build and upload the financial-mcp package to PyPI.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"\n{'='*50}")
    if description:
        print(f"🔄 {description}")
    print(f"Running: {command}")
    print('='*50)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ Command failed with return code {result.returncode}")
        return False
    else:
        print("✅ Command completed successfully")
        return True

def clean_build_directories():
    """Clean previous build artifacts"""
    directories_to_clean = ['build', 'dist', 'financial_mcp.egg-info']
    
    for dir_name in directories_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Removing {dir_name}/")
            shutil.rmtree(dir_name)
    
    print("✅ Build directories cleaned")

def check_requirements():
    """Check if required tools are installed"""
    required_tools = ['build', 'twine']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([sys.executable, '-c', f'import {tool}'], 
                          check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        print("Installing missing tools...")
        install_cmd = f"{sys.executable} -m pip install {' '.join(missing_tools)}"
        if not run_command(install_cmd, "Installing build tools"):
            return False
    
    print("✅ All required tools are available")
    return True

def build_package():
    """Build the package"""
    if not run_command(f"{sys.executable} -m build", "Building package"):
        return False
    
    # Check if dist files were created
    dist_files = list(Path('dist').glob('*'))
    if not dist_files:
        print("❌ No distribution files were created")
        return False
    
    print(f"✅ Built {len(dist_files)} distribution files:")
    for file in dist_files:
        print(f"  📦 {file.name}")
    
    return True

def check_package():
    """Check the built package"""
    return run_command("twine check dist/*", "Checking package")

def upload_to_test_pypi():
    """Upload to Test PyPI"""
    print("\n🚀 Uploading to Test PyPI...")
    print("Note: You'll need your Test PyPI API token")
    
    return run_command(
        "twine upload --repository testpypi dist/*",
        "Uploading to Test PyPI"
    )

def upload_to_pypi():
    """Upload to production PyPI"""
    print("\n🚀 Uploading to PyPI...")
    print("Note: You'll need your PyPI API token")
    print("⚠️  This will make the package publicly available!")
    
    confirm = input("Are you sure you want to upload to production PyPI? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Upload cancelled")
        return False
    
    return run_command(
        "twine upload dist/*",
        "Uploading to PyPI"
    )

def test_installation():
    """Test installation from PyPI"""
    print("\n🧪 Testing installation...")
    
    # Create a temporary virtual environment for testing
    test_env = "test_install_env"
    
    commands = [
        f"{sys.executable} -m venv {test_env}",
        f"{test_env}/bin/pip install --upgrade pip",
        f"{test_env}/bin/pip install financial-mcp",
        f"{test_env}/bin/financial-mcp --version",
        f"rm -rf {test_env}"
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    
    return True

def main():
    """Main function"""
    print("🔧 Financial MCP - Build and Upload Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('pyproject.toml').exists():
        print("❌ pyproject.toml not found. Are you in the project root directory?")
        sys.exit(1)
    
    # Menu
    while True:
        print("\n📋 What would you like to do?")
        print("1. Clean build directories")
        print("2. Build package")
        print("3. Check package")
        print("4. Upload to Test PyPI")
        print("5. Upload to PyPI (production)")
        print("6. Complete build and upload process")
        print("7. Test installation")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            clean_build_directories()
        elif choice == '2':
            if check_requirements():
                build_package()
        elif choice == '3':
            if Path('dist').exists() and list(Path('dist').glob('*')):
                check_package()
            else:
                print("❌ No dist files found. Build the package first.")
        elif choice == '4':
            if Path('dist').exists() and list(Path('dist').glob('*')):
                upload_to_test_pypi()
            else:
                print("❌ No dist files found. Build the package first.")
        elif choice == '5':
            if Path('dist').exists() and list(Path('dist').glob('*')):
                upload_to_pypi()
            else:
                print("❌ No dist files found. Build the package first.")
        elif choice == '6':
            print("\n🚀 Running complete build and upload process...")
            
            # Ask destination
            dest = input("Upload to (1) Test PyPI or (2) Production PyPI? Enter 1 or 2: ").strip()
            
            if dest not in ['1', '2']:
                print("❌ Invalid choice")
                continue
            
            # Complete process
            success = True
            success &= check_requirements()
            if success:
                clean_build_directories()
                success &= build_package()
            if success:
                success &= check_package()
            if success:
                if dest == '1':
                    success &= upload_to_test_pypi()
                else:
                    success &= upload_to_pypi()
            
            if success:
                print("\n🎉 Process completed successfully!")
            else:
                print("\n❌ Process failed at some step")
        elif choice == '7':
            test_installation()
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
