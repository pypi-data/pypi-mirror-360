#!/bin/bash
# check_pypi_name.sh - Script to check if a package name is available on PyPI

# Get package name from command line argument or from pyproject.toml
if [ -n "$1" ]; then
    PACKAGE_NAME="$1"
else
    # Get package name from pyproject.toml
    PACKAGE_NAME=$(grep -m 1 'name = ' pyproject.toml | sed 's/name = "\(.*\)"/\1/')
    echo "Using package name from pyproject.toml: $PACKAGE_NAME"
fi

echo "Checking availability for package name: $PACKAGE_NAME"

# Check if package name is available on PyPI
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/pypi/$PACKAGE_NAME/json")

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "Warning: Package name '$PACKAGE_NAME' is already taken on PyPI."
    echo "Consider choosing a different name in pyproject.toml."
else
    echo "Good news! Package name '$PACKAGE_NAME' appears to be available on PyPI."
fi

echo "You can also check manually by visiting: https://pypi.org/project/$PACKAGE_NAME/"
