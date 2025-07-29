#!/bin/bash
# filepath: t8386/publish.sh

echo "Building t8386 package..."

# Install build tools
pip install build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python3 -m build

echo "Build complete!"
echo "To upload to PyPI, run:"
echo "python3 -m twine upload dist/*"

# Optional: Upload to TestPyPI first
echo "Uploading to TestPyPI first..."
python3 -m twine upload --repository pypi dist/*