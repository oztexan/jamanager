#!/bin/bash

echo "🚀 Sprint 3: Simple Performance Test"
echo "====================================="

# Test endpoints
endpoints=(
    "/api/jams"
    "/api/songs"
    "/api/venues"
    "/api/jams/by-slug/today's-acoustic-session-401efc7985f38d97b1bc609a7ca8e119-2025-10-05"
)

echo ""
echo "📊 Testing API Endpoints (5 iterations each)"
echo "--------------------------------------------"

for endpoint in "${endpoints[@]}"; do
    echo ""
    echo "Testing: $endpoint"
    
    times=()
    for i in {1..5}; do
        start_time=$(date +%s.%N)
        curl -s "http://localhost:3000$endpoint" > /dev/null
        end_time=$(date +%s.%N)
        
        duration=$(echo "$end_time - $start_time" | bc)
        times+=($duration)
        
        echo "  Request $i: ${duration}s"
    done
    
    # Calculate average
    sum=0
    for time in "${times[@]}"; do
        sum=$(echo "$sum + $time" | bc)
    done
    avg=$(echo "scale=3; $sum / ${#times[@]}" | bc)
    
    echo "  Average: ${avg}s"
    
    # Check if under 200ms target
    target=0.2
    if (( $(echo "$avg < $target" | bc -l) )); then
        echo "  ✅ Under 200ms target"
    else
        echo "  ⚠️  Above 200ms target"
    fi
done

echo ""
echo "📊 Cache Performance Test"
echo "-------------------------"

# Test cache performance for /api/jams
echo ""
echo "Testing cache for /api/jams:"

# First request (cache miss)
start_time=$(date +%s.%N)
curl -s "http://localhost:3000/api/jams" > /dev/null
end_time=$(date +%s.%N)
first_request=$(echo "$end_time - $start_time" | bc)
echo "  First request: ${first_request}s"

# Second request (cache hit)
start_time=$(date +%s.%N)
curl -s "http://localhost:3000/api/jams" > /dev/null
end_time=$(date +%s.%N)
second_request=$(echo "$end_time - $start_time" | bc)
echo "  Second request: ${second_request}s"

# Calculate improvement
if (( $(echo "$first_request > 0" | bc -l) )); then
    improvement=$(echo "scale=1; ($first_request - $second_request) / $first_request * 100" | bc)
    echo "  Cache improvement: ${improvement}%"
fi

echo ""
echo "✅ Performance testing complete!"
