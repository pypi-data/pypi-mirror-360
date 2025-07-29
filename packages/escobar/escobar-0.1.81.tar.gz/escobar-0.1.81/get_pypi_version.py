#!/usr/bin/env python3
"""
Simple script to get the latest version of a package from PyPI
"""
import sys
import json
import urllib.request
import urllib.error

def get_latest_version(package_name):
    """Get the latest version of a package from PyPI"""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.getcode() == 200:
                data = json.loads(response.read())
                return data['info']['version']
            else:
                print(f"Error: HTTP {response.getcode()}", file=sys.stderr)
                return None
    except urllib.error.URLError as e:
        print(f"Error accessing PyPI: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return None

def increment_version(version):
    """Increment the patch version"""
    parts = version.split('.')
    # Ensure we have at least 3 parts
    while len(parts) < 3:
        parts.append('0')
    
    # Handle non-numeric parts in the patch version
    patch = parts[2]
    # Extract the numeric part before any suffix
    for i, char in enumerate(patch):
        if not char.isdigit():
            patch = patch[:i]
            break
    
    # Convert to int, increment, and convert back to string
    try:
        new_patch = int(patch) + 1
    except ValueError:
        new_patch = 1  # Default if conversion fails
    
    parts[2] = str(new_patch)
    return '.'.join(parts)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} PACKAGE_NAME", file=sys.stderr)
        sys.exit(1)
    
    package_name = sys.argv[1]
    version = get_latest_version(package_name)
    
    if version:
        print(f"PYPI_VERSION={version}")
        new_version = increment_version(version)
        print(f"NEW_VERSION={new_version}")
        sys.exit(0)
    else:
        # If we can't get the version, exit with an error
        sys.exit(1)
