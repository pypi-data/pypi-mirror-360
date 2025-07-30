#!/bin/bash

set -e

# Function to extract version from pyproject.toml
get_version_from_file() {
    local file="$1"
    local version=$(grep -E '^version = ' "$file" 2>/dev/null | sed 's/.*"\(.*\)".*/\1/')
    if [ -z "$version" ]; then
        echo "ERROR: Could not find version in $file" >&2
        return 1
    fi
    echo "$version"
}

# Get current version from pyproject.toml
if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: pyproject.toml not found in current directory" >&2
    exit 1
fi

CURRENT_VERSION=$(get_version_from_file pyproject.toml)
if [ $? -ne 0 ]; then
    echo "ERROR: Could not get version from pyproject.toml" >&2
    exit 1
fi

echo "Current version: $CURRENT_VERSION"

# Check if there's a previous commit
if ! git rev-parse HEAD~1 >/dev/null 2>&1; then
    echo "No previous commit found - treating as version change (initial commit)"
    exit 0  # Version changed (or initial commit)
fi

# Try to get previous version from git
if git show HEAD~1:pyproject.toml > previous_pyproject.toml 2>/dev/null; then
    PREVIOUS_VERSION=$(get_version_from_file previous_pyproject.toml 2>/dev/null)
    rm -f previous_pyproject.toml
    
    if [ -z "$PREVIOUS_VERSION" ]; then
        echo "Previous commit had no version in pyproject.toml - treating as version change"
        exit 0  # Version changed
    fi
    
    echo "Previous version: $PREVIOUS_VERSION"
else
    echo "Previous commit had no pyproject.toml - treating as version change"
    exit 0  # Version changed
fi

# Compare versions
if [ "$CURRENT_VERSION" != "$PREVIOUS_VERSION" ]; then
    echo "Version changed from $PREVIOUS_VERSION to $CURRENT_VERSION"
    exit 0  # Version changed
else
    echo "Version unchanged: $CURRENT_VERSION"
    exit 1  # Version not changed
fi 