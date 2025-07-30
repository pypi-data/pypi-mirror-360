#!/bin/bash

# Default to patch if no argument provided
BUMP_TYPE=${1:-patch}

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "Error: Invalid bump type '$BUMP_TYPE'. Must be one of: patch, minor, major"
    exit 1
fi

echo "Building with bump type: $BUMP_TYPE"

# Remove old distribution files
echo "Removing old distribution files..."
rm -rf dist/ *.egg-info/

# Bump version
echo "Bumping $BUMP_TYPE version..."
bumpver update --$BUMP_TYPE

# Build the package
echo "Building package..."
python -m build


echo "Build completed successfully!"