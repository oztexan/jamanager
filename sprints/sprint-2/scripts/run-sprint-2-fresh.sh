#!/bin/bash

# Sprint 2 Fresh Run Script
# This script cleans up and then runs Sprint 2 from scratch

echo "🚀 Sprint 2 Fresh Run Script"
echo "============================"
echo ""

# Step 1: Cleanup
echo "Step 1: Cleaning up previous Sprint 2 workspaces..."
echo "---------------------------------------------------"
./cleanup-sprint-2.sh

echo ""
echo "Step 2: Running Sprint 2 with improved agents..."
echo "================================================"

# Step 2: Run Sprint 2
./run-sprint-2.sh

echo ""
echo "🎉 Sprint 2 fresh run completed!"
echo ""
echo "📋 What happened:"
echo "  1. ✅ Cleaned up all previous Sprint 2 workspaces"
echo "  2. ✅ Set up fresh Sprint 2 agent workspaces"
echo "  3. ✅ Executed Type Hints and Error Handling agents"
echo "  4. ✅ Merged agent changes"
echo "  5. ✅ Deployed Sprint 2 application on port 3000"
echo ""
echo "🌐 Access your Sprint 2 application at: http://localhost:3000"
echo ""
echo "📊 Check the Sprint 2 acceptance criteria:"
echo "  - Type hints improvements"
echo "  - Error handling improvements"
echo "  - Application running on port 3000"
echo "  - Sprint 2 dev indicator visible"
