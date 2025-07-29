#!/bin/bash
# Create GitHub Release for VeriDoc v1.0.1

echo "📦 Creating GitHub Release for VeriDoc v1.0.1"
echo "============================================"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if we're authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub."
    echo "Run: gh auth login"
    exit 1
fi

# Create the release
echo "Creating release v1.0.1..."
gh release create v1.0.1 \
    --title "VeriDoc v1.0.1 - First Official Release" \
    --notes-file RELEASE_NOTES_v1.0.1.md \
    --verify-tag

echo "✅ GitHub release created successfully!"
echo ""
echo "View the release at:"
echo "https://github.com/benny-bc-huang/veridoc/releases/tag/v1.0.1"