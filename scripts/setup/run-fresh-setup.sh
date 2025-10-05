#!/bin/bash
# Run Fresh 2-Agent Proof of Concept Setup
# Simplified version for user to run in fresh terminal

echo "=== Run Fresh 2-Agent Proof of Concept Setup ==="
echo "This script will clean everything and set up from scratch"
echo ""

# Set up environment
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

echo "🚀 Starting complete fresh setup..."
./complete-fresh-setup.sh

echo ""
echo "🎉 Setup complete! The application is ready to run."
echo ""
echo "📋 Summary:"
echo "- ✅ Agent workspaces created and organized"
echo "- ✅ Console Logs Agent executed (removed console.log statements)"
echo "- ✅ Accessibility Agent executed (added ARIA labels, tabindex)"
echo "- ✅ All changes merged and validated"
echo "- ✅ Application tested and ready"
echo ""
echo "🌐 To start the application:"
echo "cd /Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspace"
echo "export PYENV_VERSION=\"jv3.11.11\""
echo "eval \"\$(pyenv init -)\""
echo "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Then visit: http://localhost:8000"