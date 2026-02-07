#!/bin/bash

# Push document-upload-service to GitHub
# Run this after creating the repository on GitHub

cd /Users/vin/Documents/code/ai/document-upload-service

echo "Pushing document-upload-service to GitHub..."
echo ""

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✓ Remote 'origin' already configured"
else
    echo "Adding remote 'origin'..."
    git remote add origin https://github.com/vinjanampati/document-upload-service.git
fi

# Rename branch to main if needed
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "Renaming branch to 'main'..."
    git branch -M main
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "Repository: https://github.com/vinjanampati/document-upload-service"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "1. Repository exists on GitHub"
    echo "2. You have authentication configured (SSH key or token)"
    echo "3. Remote URL is correct"
fi
