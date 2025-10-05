#!/usr/bin/env python3
"""
Performance Testing Script for Sprint 3
Tests the optimized API endpoints and compares performance.
"""

import asyncio
import time
import aiohttp
import json
from typing import List, Dict, Any

class PerformanceTester:
    """Performance testing for Sprint 3 optimizations."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
    
    async def test_endpoint(self, endpoint: str, iterations: int = 10) -> Dict[str, Any]:
        """Test a single endpoint multiple times and return performance metrics."""
        times = []
        errors = 0
        
        async with aiohttp.ClientSession() as session:
            for i in range(iterations):
                start_time = time.time()
                try:
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        if response.status == 200:
                            await response.json()  # Consume response
                        else:
                            errors += 1
                except Exception as e:
                    errors += 1
                    print(f"Error testing {endpoint}: {e}")
                
                end_time = time.time()
                times.append(end_time - start_time)
        
        return {
            "endpoint": endpoint,
            "iterations": iterations,
            "errors": errors,
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times)
        }
    
    async def test_cache_performance(self, endpoint: str) -> Dict[str, Any]:
        """Test cache performance by making multiple requests."""
        times = []
        
        async with aiohttp.ClientSession() as session:
            # First request (cache miss)
            start_time = time.time()
            async with session.get(f"{self.base_url}{endpoint}") as response:
                await response.json()
            first_request_time = time.time() - start_time
            
            # Second request (cache hit)
            start_time = time.time()
            async with session.get(f"{self.base_url}{endpoint}") as response:
                await response.json()
            second_request_time = time.time() - start_time
            
            # Third request (cache hit)
            start_time = time.time()
            async with session.get(f"{self.base_url}{endpoint}") as response:
                await response.json()
            third_request_time = time.time() - start_time
        
        return {
            "endpoint": endpoint,
            "first_request": first_request_time,
            "second_request": second_request_time,
            "third_request": third_request_time,
            "cache_improvement": (first_request_time - second_request_time) / first_request_time * 100
        }
    
    async def run_performance_tests(self):
        """Run comprehensive performance tests."""
        print("🚀 Sprint 3: Performance Testing")
        print("=" * 50)
        
        # Test endpoints
        endpoints = [
            "/api/jams",
            "/api/songs", 
            "/api/venues",
            "/api/jams/by-slug/today's-acoustic-session-401efc7985f38d97b1bc609a7ca8e119-2025-10-05"
        ]
        
        print("\n📊 API Endpoint Performance Tests")
        print("-" * 40)
        
        for endpoint in endpoints:
            print(f"\nTesting {endpoint}...")
            result = await self.test_endpoint(endpoint, iterations=5)
            self.results.append(result)
            
            print(f"   Average: {result['avg_time']:.3f}s")
            print(f"   Min: {result['min_time']:.3f}s")
            print(f"   Max: {result['max_time']:.3f}s")
            print(f"   Errors: {result['errors']}")
        
        # Test cache performance
        print("\n📊 Cache Performance Tests")
        print("-" * 40)
        
        cache_endpoints = [
            "/api/jams",
            "/api/jams/by-slug/today's-acoustic-session-401efc7985f38d97b1bc609a7ca8e119-2025-10-05"
        ]
        
        for endpoint in cache_endpoints:
            print(f"\nTesting cache for {endpoint}...")
            cache_result = await self.test_cache_performance(endpoint)
            
            print(f"   First request: {cache_result['first_request']:.3f}s")
            print(f"   Second request: {cache_result['second_request']:.3f}s")
            print(f"   Third request: {cache_result['third_request']:.3f}s")
            print(f"   Cache improvement: {cache_result['cache_improvement']:.1f}%")
    
    def print_summary(self):
        """Print performance test summary."""
        print("\n📋 Performance Test Summary")
        print("=" * 50)
        
        if not self.results:
            print("No test results available.")
            return
        
        # Calculate overall metrics
        total_requests = sum(r['iterations'] for r in self.results)
        total_errors = sum(r['errors'] for r in self.results)
        avg_response_time = sum(r['avg_time'] for r in self.results) / len(self.results)
        
        print(f"Total requests: {total_requests}")
        print(f"Total errors: {total_errors}")
        print(f"Error rate: {(total_errors / total_requests * 100):.1f}%")
        print(f"Average response time: {avg_response_time:.3f}s")
        
        # Performance targets
        print(f"\n🎯 Sprint 3 Performance Targets:")
        print(f"   Target: < 200ms average response time")
        print(f"   Actual: {avg_response_time * 1000:.0f}ms average response time")
        
        if avg_response_time < 0.2:
            print("   ✅ TARGET ACHIEVED!")
        else:
            print("   ⚠️  Target not met - further optimization needed")
        
        # Best and worst performers
        best = min(self.results, key=lambda x: x['avg_time'])
        worst = max(self.results, key=lambda x: x['avg_time'])
        
        print(f"\n🏆 Best performer: {best['endpoint']} ({best['avg_time']:.3f}s)")
        print(f"🐌 Worst performer: {worst['endpoint']} ({worst['avg_time']:.3f}s)")

async def main():
    """Main function to run performance tests."""
    tester = PerformanceTester()
    
    try:
        await tester.run_performance_tests()
        tester.print_summary()
        print("\n✅ Performance testing complete!")
        
    except Exception as e:
        print(f"❌ Error during performance testing: {e}")

if __name__ == "__main__":
    asyncio.run(main())
