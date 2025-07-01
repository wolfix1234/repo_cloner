#!/bin/bash
set -e  # Exit on any error

echo "Cloning repository: $REPO_URL"
repo_name=$(basename -s .git "$REPO_URL")
git clone "$REPO_URL" "$repo_name"
cd "$repo_name"

if [ -f package.json ]; then
    echo "Installing Node.js dependencies..."
    npm install

    echo "Starting JSON update server and Next.js app..."
    
    PORT=${PORT:-3000}  # Default to 3000 if not set
    
    # Start the Node.js app
    node index.js -p "$PORT"  -H 0.0.0.0
else
    echo "No package.json found; exiting."
    exit 1
fi
