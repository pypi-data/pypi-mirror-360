#!/bin/bash
# publish_to_pypi.sh - Script to publish to PyPI with automatic version increment

set -e  # Exit on any error

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found. Please create it with PYPI_TOKEN=your_token"
    exit 1
fi

# Check if PYPI_TOKEN is set
if [ -z "$PYPI_TOKEN" ]; then
    echo "Error: PYPI_TOKEN not found in .env file"
    exit 1
fi

# Get package name from pyproject.toml
PACKAGE_NAME=$(grep -m 1 'name = ' pyproject.toml | sed 's/name = "\(.*\)"/\1/')
echo "Package name: $PACKAGE_NAME"

# Get current version from package.json
ORIGINAL_VERSION=$(grep -m 1 '"version":' package.json | sed 's/.*"version": "\(.*\)",/\1/')
echo "Current version in package.json: $ORIGINAL_VERSION"

# Create a backup of package.json
cp package.json package.json.bak

# Make the Python script executable
chmod +x get_pypi_version.py

# Get the latest version from PyPI and calculate the new version
echo "Fetching latest version from PyPI..."
if python3 ./get_pypi_version.py "$PACKAGE_NAME" > version_info.txt; then
    # Successfully got version from PyPI
    source version_info.txt
    echo "Latest version on PyPI: $PYPI_VERSION"
    echo "New version to publish: $NEW_VERSION"
else
    # Failed to get version from PyPI, use local version + 1
    echo "Could not get version from PyPI. Using local version + 1."
    # Parse the version components
    MAJOR=$(echo $ORIGINAL_VERSION | cut -d. -f1)
    MINOR=$(echo $ORIGINAL_VERSION | cut -d. -f2)
    PATCH=$(echo $ORIGINAL_VERSION | cut -d. -f3)
    
    # If patch contains non-numeric characters, extract just the number part
    PATCH_NUM=$(echo $PATCH | grep -o '^[0-9]*')
    if [ -z "$PATCH_NUM" ]; then
        PATCH_NUM=0
    fi
    
    # Increment the patch version
    NEW_PATCH=$((PATCH_NUM + 1))
    NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
fi

echo "Will publish as version: $NEW_VERSION"

# Update the version in package.json
sed -i.tmp "s/\"version\": \"$ORIGINAL_VERSION\"/\"version\": \"$NEW_VERSION\"/" package.json
rm package.json.tmp

# Verify the version was updated correctly
UPDATED_VERSION=$(grep -m 1 '"version":' package.json | sed 's/.*"version": "\(.*\)",/\1/')
echo "Updated version in package.json: $UPDATED_VERSION"
if [ "$UPDATED_VERSION" != "$NEW_VERSION" ]; then
    echo "ERROR: Failed to update version in package.json. Aborting."
    mv package.json.bak package.json
    exit 1
fi

# Update version.ts file with the new version
echo "Updating version.ts with version $NEW_VERSION"
echo "// This file is automatically updated by the build process
export const VERSION = '$NEW_VERSION';" > src/version.ts

# Clean up temporary files
rm -f version_info.txt

# Do NOT restore the original version after publishing - keep the new version
RESTORE_VERSION=false

echo "Permanently updating version in package.json to $NEW_VERSION"

# Clean previous builds and dist directory
echo "Cleaning previous builds and dist directory..."
npm run clean:all
rm -rf dist/

# Install dependencies if needed
echo "Installing dependencies..."
npm install

# Build the extension
echo "Building the extension..."
npm run build:prod

# Create a temporary pyproject.toml without README to prevent README upload
echo "Creating temporary pyproject.toml without README..."
cp pyproject.toml pyproject.toml.bak
sed '/^readme = /d' pyproject.toml > pyproject.toml.tmp
mv pyproject.toml.tmp pyproject.toml

# Build the Python package
echo "Building the Python package..."
python -m pip install --upgrade build
python -m build

# Restore original pyproject.toml
echo "Restoring original pyproject.toml..."
mv pyproject.toml.bak pyproject.toml

# Check the built package
echo "Checking the built package..."
python -m pip install --upgrade twine
python -m twine check dist/*

# Manual PyPI history cleanup instructions
echo ""
echo "============================================================"
echo "MANUAL PYPI CLEANUP REQUIRED"
echo "============================================================"
echo "PyPI does not allow automated version deletion via API."
echo "To clean up previous versions manually:"
echo ""
echo "1. Visit: https://pypi.org/manage/project/$PACKAGE_NAME/"
echo "2. Log in with your PyPI account"
echo "3. Go to 'Manage' -> 'Releases'"
echo "4. Delete old versions one by one using the web interface"
echo "5. Or contact PyPI support for bulk deletion assistance"
echo ""
echo "Current version to be uploaded: $NEW_VERSION"
echo "============================================================"
echo ""

# Check if the version already exists and increment if needed
echo "Checking if version $NEW_VERSION already exists on PyPI..."
python -m pip install --upgrade requests

cat > check_version_exists.py << 'EOF'
import requests
import sys

def version_exists(package_name, version):
    """Check if a specific version exists on PyPI"""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        if response.status_code == 404:
            return False
        elif response.status_code != 200:
            return False
            
        data = response.json()
        versions = list(data['releases'].keys())
        return version in versions
        
    except Exception as e:
        print(f"Error checking version: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python check_version_exists.py <package_name> <version>")
        sys.exit(1)
        
    package_name = sys.argv[1]
    version = sys.argv[2]
    
    exists = version_exists(package_name, version)
    print("EXISTS" if exists else "NOT_EXISTS")
    sys.exit(0)
EOF

VERSION_CHECK=$(python check_version_exists.py "$PACKAGE_NAME" "$NEW_VERSION")
rm -f check_version_exists.py

if [ "$VERSION_CHECK" = "EXISTS" ]; then
    echo "Version $NEW_VERSION already exists on PyPI. Auto-incrementing..."
    
    # Parse version and increment patch
    MAJOR=$(echo $NEW_VERSION | cut -d. -f1)
    MINOR=$(echo $NEW_VERSION | cut -d. -f2)
    PATCH=$(echo $NEW_VERSION | cut -d. -f3)
    PATCH_NUM=$(echo $PATCH | grep -o '^[0-9]*')
    
    # Keep incrementing until we find a version that doesn't exist
    while [ "$VERSION_CHECK" = "EXISTS" ]; do
        PATCH_NUM=$((PATCH_NUM + 1))
        NEW_VERSION="$MAJOR.$MINOR.$PATCH_NUM"
        echo "Trying version: $NEW_VERSION"
        
        cat > check_version_exists.py << 'EOF'
import requests
import sys

def version_exists(package_name, version):
    """Check if a specific version exists on PyPI"""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        if response.status_code == 404:
            return False
        elif response.status_code != 200:
            return False
            
        data = response.json()
        versions = list(data['releases'].keys())
        return version in versions
        
    except Exception as e:
        print(f"Error checking version: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python check_version_exists.py <package_name> <version>")
        sys.exit(1)
        
    package_name = sys.argv[1]
    version = sys.argv[2]
    
    exists = version_exists(package_name, version)
    print("EXISTS" if exists else "NOT_EXISTS")
    sys.exit(0)
EOF
        
        VERSION_CHECK=$(python check_version_exists.py "$PACKAGE_NAME" "$NEW_VERSION")
        rm -f check_version_exists.py
    done
    
    echo "Found available version: $NEW_VERSION"
    
    # Update package.json with the new incremented version
    sed -i.tmp "s/\"version\": \"$UPDATED_VERSION\"/\"version\": \"$NEW_VERSION\"/" package.json
    rm package.json.tmp
    
    # Update version.ts file with the new version
    echo "// This file is automatically updated by the build process
export const VERSION = '$NEW_VERSION';" > src/version.ts
    
    # Rebuild with new version
    echo "Rebuilding with new version $NEW_VERSION..."
    npm run build:prod
    
    # Rebuild Python package
    rm -rf dist/
    python -m build
fi

# Upload to PyPI (only the current version)
echo "Uploading to PyPI (version $NEW_VERSION only)..."
python -m twine upload dist/*$NEW_VERSION* -u __token__ -p "$PYPI_TOKEN"

# Restore the original version in package.json if needed
if [ "$RESTORE_VERSION" = true ]; then
    echo "Restoring original version in package.json..."
    mv package.json.bak package.json
else
    echo "Keeping new version $NEW_VERSION in package.json"
    rm -f package.json.bak
fi

echo "Process completed!"
echo "If successful, your package should now be available at: https://pypi.org/project/$PACKAGE_NAME/"
echo "Users can install it with: pip install $PACKAGE_NAME"
echo "Published version: $NEW_VERSION"
