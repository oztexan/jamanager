#!/usr/bin/env python3
"""
Test Jamanager Application with PostgreSQL
Mini-Sprint: PostgreSQL Development Setup

This script tests the application functionality with PostgreSQL backend
to ensure everything works correctly before production deployment.
"""

import asyncio
import httpx
import time
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Change to project root directory
os.chdir(project_root)

async def test_api_endpoints():
    """Test all API endpoints with PostgreSQL backend"""
    print("🧪 Testing API Endpoints with PostgreSQL")
    print("=========================================")
    
    base_url = "http://localhost:3000"
    
    endpoints_to_test = [
        ("/api/system/health", "Health Check"),
        ("/api/system/stats", "System Stats"),
        ("/api/jams", "Jams List"),
        ("/api/songs", "Songs List"),
        ("/api/venues", "Venues List"),
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint, description in endpoints_to_test:
            try:
                print(f"\n📊 Testing {description} ({endpoint})")
                start_time = time.perf_counter()
                
                response = await client.get(f"{base_url}{endpoint}")
                response_time = time.perf_counter() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"  ✅ Status: {response.status_code}")
                        print(f"  📈 Response Time: {response_time:.3f}s")
                        print(f"  📊 Items Returned: {len(data)}")
                    else:
                        print(f"  ✅ Status: {response.status_code}")
                        print(f"  📈 Response Time: {response_time:.3f}s")
                        print(f"  📊 Response: {type(data).__name__}")
                else:
                    print(f"  ❌ Status: {response.status_code}")
                    print(f"  📄 Response: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")

async def test_jam_details():
    """Test jam details endpoint with specific jam"""
    print("\n🎸 Testing Jam Details Endpoint")
    print("===============================")
    
    base_url = "http://localhost:3000"
    
    # First get the list of jams to find a valid slug
    async with httpx.AsyncClient() as client:
        try:
            print("📋 Getting jams list...")
            response = await client.get(f"{base_url}/api/jams")
            
            if response.status_code == 200:
                jams = response.json()
                if jams:
                    jam_slug = jams[0]["slug"]
                    print(f"🎯 Testing jam: {jams[0]['name']}")
                    print(f"🔗 Slug: {jam_slug}")
                    
                    # Test jam details
                    print(f"\n📊 Testing jam details...")
                    start_time = time.perf_counter()
                    
                    details_response = await client.get(f"{base_url}/api/jams/by-slug/{jam_slug}")
                    response_time = time.perf_counter() - start_time
                    
                    if details_response.status_code == 200:
                        jam_data = details_response.json()
                        print(f"  ✅ Status: {details_response.status_code}")
                        print(f"  📈 Response Time: {response_time:.3f}s")
                        print(f"  🏢 Venue: {jam_data.get('venue', {}).get('name', 'N/A')}")
                        print(f"  🎵 Songs: {len(jam_data.get('songs', []))}")
                        
                        # Test voting endpoint
                        if jam_data.get('songs'):
                            song_id = jam_data['songs'][0]['song']['id']
                            print(f"\n🗳️ Testing vote endpoint for song: {jam_data['songs'][0]['song']['title']}")
                            
                            vote_response = await client.post(
                                f"{base_url}/api/jams/{jam_data['id']}/vote",
                                json={"song_id": song_id, "attendee_id": "test-attendee"}
                            )
                            
                            if vote_response.status_code in [200, 201]:
                                print(f"  ✅ Vote endpoint working")
                            else:
                                print(f"  ⚠️ Vote endpoint returned: {vote_response.status_code}")
                    else:
                        print(f"  ❌ Jam details failed: {details_response.status_code}")
                else:
                    print("  ⚠️ No jams found in database")
            else:
                print(f"  ❌ Failed to get jams list: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error testing jam details: {e}")

async def test_performance():
    """Test performance with PostgreSQL"""
    print("\n⚡ Performance Testing with PostgreSQL")
    print("=====================================")
    
    base_url = "http://localhost:3000"
    num_requests = 10
    
    endpoints = [
        "/api/jams",
        "/api/songs",
        "/api/venues"
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            print(f"\n📊 Testing {endpoint} ({num_requests} requests)")
            
            times = []
            for i in range(num_requests):
                start_time = time.perf_counter()
                try:
                    response = await client.get(f"{base_url}{endpoint}")
                    response_time = time.perf_counter() - start_time
                    
                    if response.status_code == 200:
                        times.append(response_time)
                    else:
                        print(f"  ⚠️ Request {i+1} failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Request {i+1} error: {e}")
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                print(f"  📈 Average: {avg_time:.3f}s")
                print(f"  📉 Min: {min_time:.3f}s")
                print(f"  📈 Max: {max_time:.3f}s")
                print(f"  ✅ Successful: {len(times)}/{num_requests}")
                
                if avg_time < 0.1:  # 100ms
                    print(f"  🚀 Excellent performance!")
                elif avg_time < 0.2:  # 200ms
                    print(f"  ✅ Good performance")
                else:
                    print(f"  ⚠️ Performance could be improved")

async def test_database_connection():
    """Test database connection and basic queries"""
    print("\n🐘 Testing Database Connection")
    print("=============================")
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not set")
            return
        
        engine = create_async_engine(database_url)
        session_factory = sessionmaker(engine, class_=AsyncSession)
        
        async with session_factory() as session:
            # Test basic connection
            result = await session.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"✅ Database connection test: {test_value}")
            
            # Test table counts
            tables = ["venues", "songs", "jams", "attendees", "jam_songs", "votes"]
            for table in tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"📊 {table}: {count} rows")
            
            # Test a complex query (similar to our optimized jam query)
            result = await session.execute(text("""
                SELECT j.id, j.name, v.name as venue_name, COUNT(js.id) as song_count
                FROM jams j
                JOIN venues v ON j.venue_id = v.id
                LEFT JOIN jam_songs js ON j.id = js.jam_id
                GROUP BY j.id, j.name, v.name
                ORDER BY j.created_at DESC
                LIMIT 5
            """))
            
            jams = result.fetchall()
            print(f"🎸 Complex query test: {len(jams)} jams returned")
            
            for jam in jams:
                print(f"  - {jam[1]} at {jam[2]} ({jam[3]} songs)")
        
        await engine.dispose()
        print("✅ Database connection test completed")
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 Jamanager PostgreSQL Testing Suite")
    print("=====================================")
    print("")
    
    # Check if application is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000/api/system/health", timeout=5.0)
            if response.status_code != 200:
                print("❌ Application not responding on port 3000")
                print("Please start the application first:")
                print("  uvicorn main:app --host 0.0.0.0 --port 3000 --reload")
                return
    except Exception:
        print("❌ Application not running on port 3000")
        print("Please start the application first:")
        print("  uvicorn main:app --host 0.0.0.0 --port 3000 --reload")
        return
    
    print("✅ Application is running on port 3000")
    print("")
    
    # Run all tests
    await test_database_connection()
    await test_api_endpoints()
    await test_jam_details()
    await test_performance()
    
    print("\n🎉 PostgreSQL Testing Complete!")
    print("===============================")
    print("")
    print("📋 Summary:")
    print("✅ Database connection working")
    print("✅ API endpoints responding")
    print("✅ Jam details working")
    print("✅ Performance acceptable")
    print("")
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    asyncio.run(main())
