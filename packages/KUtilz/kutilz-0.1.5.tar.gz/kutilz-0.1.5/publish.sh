#!/bin/bash

# Exit on error
set -e

# Function to increment version
increment_version() {
    local version=$1
    local position=$2
    IFS='.' read -ra ADDR <<< "$version"
    ADDR[$position]=$((ADDR[$position] + 1))
    # Reset all lower positions to 0
    for ((i=position+1; i<${#ADDR[@]}; i++)); do
        ADDR[$i]=0
    done
    echo "${ADDR[0]}.${ADDR[1]}.${ADDR[2]}"
}

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
echo "Current version: $CURRENT_VERSION"

# Handle version argument
if [ -z "$1" ]; then
    # Auto-increment patch version if no version provided
    NEW_VERSION=$(increment_version "$CURRENT_VERSION" 2)
    echo "No version specified. Auto-incrementing to $NEW_VERSION"
else
    NEW_VERSION=$1
    echo "Using specified version: $NEW_VERSION"
fi

# Update version in pyproject.toml
sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package
echo "Building package..."
proxychains4 python -m build || {
    echo "Build failed!"
    exit 1
}

# Check the build
echo "Checking build..."
proxychains4 python -m twine check dist/* || {
    echo "Build check failed!"
    exit 1
}

# Upload to PyPI
echo "Uploading to PyPI..."
proxychains4 python -m twine upload dist/* || {
    echo "Upload failed!"
    # Revert version change
    sed -i "s/version = \"$NEW_VERSION\"/version = \"$CURRENT_VERSION\"/" pyproject.toml
    exit 1
}

echo "Successfully published version $NEW_VERSION"

# Create and push git tag
git add pyproject.toml
git commit -m "Release version $NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
proxychains4 git push && proxychains4 git push --tags

echo "Done! Version $NEW_VERSION has been published and tagged." 