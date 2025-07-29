#!/bin/bash
# Development script to run the MCP server locally

# Change to script directory
cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install in editable mode
pip install -e .

# Run the server
echo "Starting metool-mcp server..."
python -m metool_mcp.server