#!/bin/bash
# Complete Fresh 2-Agent Proof of Concept Setup
# This script uses the proper agent workflow scripts

echo "=== Complete Fresh 2-Agent Proof of Concept Setup ==="
echo "This script will clean everything and set up from scratch using proper agent scripts"
echo ""

# Set up environment
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

echo "1. Killing all existing processes..."
pkill -9 -f uvicorn 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

echo "2. Cleaning up old directories..."
rm -rf /Users/chrisrobertson/dev/jamanager-workzone
rm -rf /Users/chrisrobertson/dev/jamanager-agents
rm -rf /Users/chrisrobertson/dev/jamanager-merge
rm -rf /Users/chrisrobertson/dev/jamanager-logs

echo "3. Setting up agent workspaces using proper agent scripts..."
./scripts/agents/phase-2/setup/setup-agents.sh

if [ $? -ne 0 ]; then
    echo "❌ Setup failed!"
    exit 1
fi

echo "4. Running agents using proper agent scripts..."
./scripts/agents/phase-2/execution/start-agents.sh

if [ $? -ne 0 ]; then
    echo "❌ Agent execution failed!"
    exit 1
fi

echo "5. Merging agent results using proper agent scripts..."
./scripts/agents/phase-2/merge/merge-agents.sh

if [ $? -ne 0 ]; then
    echo "❌ Agent merge failed!"
    exit 1
fi

echo "6. Testing agent work..."
./scripts/agents/test-agent-work.sh

if [ $? -ne 0 ]; then
    echo "❌ Agent testing failed!"
    exit 1
fi

echo ""
echo "✅ Complete setup finished using proper agent workflow!"
echo ""
echo "🎯 Next: Start the application"
echo "cd /Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspace"
echo "export PYENV_VERSION=\"jv3.11.11\""
echo "eval \"\$(pyenv init -)\""
echo "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Then visit: http://localhost:8000"
echo ""
echo "📊 Agent Results:"
echo "- Console Logs Agent: Removed console.log statements"
echo "- Accessibility Agent: Added ARIA labels and tabindex elements"
echo "- All changes merged and tested successfully"