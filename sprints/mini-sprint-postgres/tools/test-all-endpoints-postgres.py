#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script for Jamanager with PostgreSQL
Tests all API endpoints to ensure they work correctly with PostgreSQL backend
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:3000"

# Test data
JAM_ID = "e810f23f-74a8-4339-83ed-21cc1b54ba3b"
JAM_SLUG = "country-folk-gathering-2025-10-09"
SONG_ID = "ab0324b91d6f9bf6720656e75abeba70"
ATTENDEE_ID = "test-attendee"  # This will fail as expected

async def test_endpoint(session, method, url, data=None, expected_status=200):
    """Test a single endpoint"""
    try:
        if method.upper() == "GET":
            async with session.get(url) as response:
                status = response.status
                if status == expected_status:
                    print(f"✅ {method} {url} - {status}")
                    return True
                else:
                    print(f"❌ {method} {url} - Expected {expected_status}, got {status}")
                    return False
        elif method.upper() == "POST":
            async with session.post(url, json=data) as response:
                status = response.status
                if status == expected_status:
                    print(f"✅ {method} {url} - {status}")
                    return True
                else:
                    print(f"❌ {method} {url} - Expected {expected_status}, got {status}")
                    return False
    except Exception as e:
        print(f"❌ {method} {url} - Error: {e}")
        return False

async def run_comprehensive_tests():
    """Run comprehensive endpoint tests"""
    
    print("🧪 PostgreSQL Endpoint Testing Suite")
    print("====================================")
    
    async with aiohttp.ClientSession() as session:
        tests = []
        
        # System endpoints
        print("\n📊 System Endpoints:")
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/system/health"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/system/stats"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/system/config"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/dev-info"))
        
        # Core data endpoints
        print("\n🎵 Core Data Endpoints:")
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/songs"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/venues"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/jams"))
        
        # Jam-specific endpoints
        print("\n🎤 Jam-Specific Endpoints:")
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/jams/by-slug/{JAM_SLUG}"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/jams/{JAM_ID}/songs"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/jams/{JAM_ID}/attendees"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/jams/{JAM_ID}/votes"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/jams/{JAM_ID}/performers"))
        
        # Jam chord sheets
        print("\n📄 Jam Chord Sheets:")
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/jams/{JAM_ID}/chord-sheets"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/jams/{JAM_ID}/chord-sheets/{SONG_ID}"))
        
        # Vote endpoint (expected to fail with test attendee)
        print("\n🗳️ Vote Endpoint (Expected Failure):")
        vote_data = {
            "attendee_id": ATTENDEE_ID,
            "song_id": SONG_ID
        }
        tests.append(await test_endpoint(session, "POST", f"{BASE_URL}/api/jams/{JAM_ID}/vote", vote_data, expected_status=404))
        
        # Access code endpoints
        print("\n🔐 Access Code Endpoints:")
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/api/access-code/status"))
        
        # Static file serving
        print("\n📁 Static File Serving:")
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/"))
        tests.append(await test_endpoint(session, "GET", f"{BASE_URL}/static/css/base.css"))
        
        # Calculate results
        passed = sum(tests)
        total = len(tests)
        success_rate = (passed / total) * 100
        
        print(f"\n📊 Test Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 Excellent! PostgreSQL integration is working well!")
        elif success_rate >= 80:
            print("👍 Good! Most endpoints are working with PostgreSQL.")
        else:
            print("⚠️ Some issues detected with PostgreSQL integration.")
        
        return success_rate >= 80

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)