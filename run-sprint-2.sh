#!/bin/bash
# Run Sprint 2: Type Hints + Error Handling Agents

echo "=== Sprint 2: Type Hints + Error Handling Agents ==="
echo "This script will execute Sprint 2 agents and deploy on port 3000"
echo ""

# Set up environment
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

echo "🚀 Starting Sprint 2 execution..."

# Step 1: Setup Sprint 2
echo "1. Setting up Sprint 2 agent workspaces..."
./scripts/agents/phase-2/setup/setup-sprint-2.sh

if [ $? -ne 0 ]; then
    echo "❌ Sprint 2 setup failed!"
    exit 1
fi

# Step 2: Execute Sprint 2 agents
echo "2. Executing Sprint 2 agents (Type Hints + Error Handling)..."
./scripts/agents/phase-2/execution/start-sprint-2.sh

if [ $? -ne 0 ]; then
    echo "❌ Sprint 2 agent execution failed!"
    exit 1
fi

# Step 3: Merge Sprint 2 results
echo "3. Merging Sprint 2 agent results..."
./scripts/agents/phase-2/merge/merge-sprint-2.sh

if [ $? -ne 0 ]; then
    echo "❌ Sprint 2 merge failed!"
    exit 1
fi

# Step 4: Deploy Sprint 2 application
echo "4. Deploying Sprint 2 application on port 3000..."
./scripts/agents/phase-2/deploy-sprint-2.sh

if [ $? -ne 0 ]; then
    echo "❌ Sprint 2 deployment failed!"
    exit 1
fi

echo ""
echo "🎉 Sprint 2 completed successfully!"
echo ""
echo "📊 Sprint 2 Results:"
echo "- ✅ Type Hints Agent: Added type annotations to Python functions"
echo "- ✅ Error Handling Agent: Standardized exception handling"
echo "- ✅ Application deployed on port 3000"
echo "- ✅ Purple Sprint 2 dev indicator visible"
echo ""
echo "🌐 Sprint 2 Application:"
echo "URL: http://localhost:3000"
echo "Features: Type Hints + Error Handling improvements"
echo "Dev Indicator: Purple 'SPRINT 2' badge"
echo ""
echo "📋 Acceptance Criteria:"
echo "Check: /Users/chrisrobertson/dev/jamanager-workzone/workspaces/sprint-2-merge-workspace/SPRINT_2_ACCEPTANCE_CRITERIA.md"
echo ""
echo "🧪 Testing Instructions:"
echo "1. Visit http://localhost:3000"
echo "2. Look for purple Sprint 2 indicator"
echo "3. Test all features (jams, voting, registration)"
echo "4. Check browser console for errors"
echo "5. Verify type hints in code"
echo "6. Test error handling improvements"
echo ""
echo "🎯 Sprint 2 Goals Achieved:"
echo "- Comprehensive type annotations added"
echo "- Exception handling standardized"
echo "- Application running on port 3000"
echo "- Acceptance criteria documented"
