#!/bin/bash

echo "=== Clean Agent Setup ==="
echo "Setting up 2-agent proof of concept from scratch"
echo ""

# Set up environment
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

# Run the setup
echo "Running agent setup..."
./scripts/agents/phase-2/setup/setup-agents.sh

echo ""
echo "Setup complete!"




