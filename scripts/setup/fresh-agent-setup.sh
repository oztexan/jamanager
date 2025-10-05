#!/bin/bash

echo "=== Fresh 2-Agent Proof of Concept Setup ==="
echo ""

# Set up environment
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

echo "1. Cleaning up old workspaces..."
rm -rf /Users/chrisrobertson/dev/jamanager-workzone/workspaces/agent-workspaces/*
rm -rf /Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspace/*
rm -rf /Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspaces

echo "2. Setting up agent workspaces..."

# Create agent workspaces
AGENT_WORKSPACE="/Users/chrisrobertson/dev/jamanager-workzone/workspaces/agent-workspaces"
MERGE_WORKSPACE="/Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspace"

# Clone repositories for each agent
echo "Cloning repositories for agents..."

# Console Logs Agent
echo "Setting up Console Logs Agent..."
git clone . "$AGENT_WORKSPACE/agent-console-logs"
cd "$AGENT_WORKSPACE/agent-console-logs"
git checkout -b feature/agent-console-logs
cd /Users/chrisrobertson/dev/jamanager

# Accessibility Agent
echo "Setting up Accessibility Agent..."
git clone . "$AGENT_WORKSPACE/agent-accessibility"
cd "$AGENT_WORKSPACE/agent-accessibility"
git checkout -b feature/agent-accessibility
cd /Users/chrisrobertson/dev/jamanager

# Merge Workspace
echo "Setting up Merge Workspace..."
git clone . "$MERGE_WORKSPACE"
cd "$MERGE_WORKSPACE"
git checkout -b feature/agent-merge
cd /Users/chrisrobertson/dev/jamanager

echo "3. Creating agent status file..."
echo "Agent Status - $(date)" > "$AGENT_WORKSPACE/agent-status.txt"
echo "Console Logs Agent: Ready" >> "$AGENT_WORKSPACE/agent-status.txt"
echo "Accessibility Agent: Ready" >> "$AGENT_WORKSPACE/agent-status.txt"
echo "Merge Workspace: Ready" >> "$AGENT_WORKSPACE/agent-status.txt"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Agent workspaces created:"
echo "  Console Logs: $AGENT_WORKSPACE/agent-console-logs"
echo "  Accessibility: $AGENT_WORKSPACE/agent-accessibility"
echo "  Merge Workspace: $MERGE_WORKSPACE"
echo ""
echo "Next steps:"
echo "  1. Run agents: ./scripts/agents/phase-2/execution/start-agents.sh"
echo "  2. Merge results: ./scripts/agents/phase-2/merge/merge-agents.sh"
echo "  3. Test application: ./scripts/agents/test-agent-work.sh"




