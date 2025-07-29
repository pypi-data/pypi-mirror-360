#!/bin/bash
# VeriDoc PyPI Build and Publish Script

echo "🚀 VeriDoc PyPI Build Script"
echo "============================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Please run from project root.${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info/

# Install/upgrade build tools
echo -e "${YELLOW}Installing/upgrading build tools...${NC}"
pip install --upgrade pip setuptools wheel build twine

# Build the package
echo -e "${YELLOW}Building package...${NC}"
python -m build

# Check the built package
echo -e "${YELLOW}Checking package with twine...${NC}"
twine check dist/*

# Display package contents
echo -e "${GREEN}Package contents:${NC}"
ls -la dist/

echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "To upload to PyPI Test:"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "To upload to PyPI (production):"
echo "  twine upload dist/*"
echo ""
echo "Make sure you have configured your PyPI credentials in ~/.pypirc"