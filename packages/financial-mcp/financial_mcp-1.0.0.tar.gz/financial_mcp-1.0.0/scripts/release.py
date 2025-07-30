#!/usr/bin/env python3
"""
Release script for financial-mcp package
Handles version bumping, tagging, and release preparation
"""

import subprocess
import sys
import os
import re
from pathlib import Path
from datetime import datetime

def get_current_version():
    """Get current version from __init__.py"""
    init_file = Path('financial_mcp/__init__.py')
    if not init_file.exists():
        raise FileNotFoundError("Cannot find financial_mcp/__init__.py")
    
    content = init_file.read_text()
    version_match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if not version_match:
        raise ValueError("Cannot find version in __init__.py")
    
    return version_match.group(1)

def update_version(new_version):
    """Update version in __init__.py and setup.py"""
    files_to_update = [
        'financial_mcp/__init__.py',
        'setup.py',
        'pyproject.toml'
    ]
    
    for file_path in files_to_update:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"Warning: {file_path} not found, skipping")
            continue
        
        content = file_path.read_text()
        
        # Update version patterns
        if file_path.name == '__init__.py':
            content = re.sub(r'__version__ = ["\'][^"\']+["\']', 
                           f'__version__ = "{new_version}"', content)
        elif file_path.name == 'setup.py':
            content = re.sub(r'version="[^"]+"', f'version="{new_version}"', content)
        elif file_path.name == 'pyproject.toml':
            content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
        
        file_path.write_text(content)
        print(f"Updated version in {file_path}")

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\nRunning: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def bump_version(current_version, bump_type):
    """Bump version based on type (major, minor, patch)"""
    parts = current_version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current_version}")
    
    major, minor, patch = map(int, parts)
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"

def main():
    """Main release process"""
    print("Financial MCP - Release Tool")
    print("============================")
    
    # Change to repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    os.chdir(repo_root)
    
    # Check if we're in a git repository
    if not Path('.git').exists():
        print("ERROR: Not in a git repository")
        sys.exit(1)
    
    # Check git status
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        print("ERROR: Working directory is not clean. Please commit or stash changes.")
        print("Uncommitted changes:")
        print(result.stdout)
        sys.exit(1)
    
    # Get current version
    try:
        current_version = get_current_version()
        print(f"Current version: {current_version}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Ask for version bump type
    print("\nVersion bump options:")
    print("1. Patch (bug fixes)")
    print("2. Minor (new features)")
    print("3. Major (breaking changes)")
    print("4. Custom version")
    
    choice = input("\nChoose bump type (1-4): ").strip()
    
    if choice == '1':
        new_version = bump_version(current_version, 'patch')
    elif choice == '2':
        new_version = bump_version(current_version, 'minor')
    elif choice == '3':
        new_version = bump_version(current_version, 'major')
    elif choice == '4':
        new_version = input("Enter custom version: ").strip()
        # Validate version format
        if not re.match(r'^\d+\.\d+\.\d+$', new_version):
            print("ERROR: Invalid version format. Use x.y.z")
            sys.exit(1)
    else:
        print("Invalid choice")
        sys.exit(1)
    
    print(f"\nNew version will be: {new_version}")
    confirm = input("Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("Release cancelled")
        sys.exit(0)
    
    # Update version in files
    try:
        update_version(new_version)
    except Exception as e:
        print(f"ERROR updating version: {e}")
        sys.exit(1)
    
    # Run tests
    print("\nRunning tests...")
    if not run_command("python -m pytest tests/ -v", "Running tests"):
        print("Tests failed. Please fix before releasing.")
        sys.exit(1)
    
    # Commit version changes
    if not run_command("git add .", "Staging changes"):
        sys.exit(1)
    
    commit_msg = f"Bump version to {new_version}"
    if not run_command(f'git commit -m "{commit_msg}"', "Committing version bump"):
        sys.exit(1)
    
    # Create git tag
    tag_name = f"v{new_version}"
    tag_msg = f"Release version {new_version}"
    if not run_command(f'git tag -a {tag_name} -m "{tag_msg}"', f"Creating tag {tag_name}"):
        sys.exit(1)
    
    # Ask about pushing
    print(f"\nVersion {new_version} prepared successfully!")
    print(f"Created tag: {tag_name}")
    
    push_choice = input("\nPush changes and tag to remote? (y/N): ")
    if push_choice.lower() == 'y':
        if run_command("git push", "Pushing commits"):
            if run_command(f"git push origin {tag_name}", "Pushing tag"):
                print(f"\n✓ Successfully released version {new_version}!")
                print(f"\nNext steps:")
                print(f"1. Check GitHub Actions for automated PyPI upload")
                print(f"2. Monitor: https://github.com/Tatsuru-Kikuchi/MCP/actions")
                print(f"3. Verify package on PyPI: https://pypi.org/project/financial-mcp/")
            else:
                print("Failed to push tag")
        else:
            print("Failed to push commits")
    else:
        print(f"\nChanges prepared but not pushed.")
        print(f"To push manually:")
        print(f"  git push")
        print(f"  git push origin {tag_name}")
    
    print("\nRelease process completed!")

if __name__ == "__main__":
    main()
