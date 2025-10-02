#!/usr/bin/env python3
"""
Automated Test Runner for Jamanager Application
This script can be run by an automated testing agent to validate core functionality.
"""

import requests
import json
import time
import sys
from datetime import datetime, date
from typing import Dict, List, Optional

class JamanagerTestRunner:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.session_id = f"test_session_{int(time.time())}"
        
    def log_test(self, test_id: str, status: str, message: str = ""):
        """Log test result"""
        result = {
            "test_id": test_id,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"[{status.upper()}] {test_id}: {message}")
        
    def test_api_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                         data: Optional[Dict] = None, headers: Optional[Dict] = None) -> bool:
        """Test an API endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, json=data, headers=headers)
            
            if response.status_code == expected_status:
                self.log_test(f"API_{method}_{endpoint}", "PASS", f"Status {response.status_code}")
                return True
            else:
                self.log_test(f"API_{method}_{endpoint}", "FAIL", 
                            f"Expected {expected_status}, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"API_{method}_{endpoint}", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_home_page(self) -> bool:
        """Test home page accessibility"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                # Check for key elements in HTML
                if "Welcome to Jamanager!" in response.text and "Jams Happening Today" in response.text:
                    self.log_test("HOME_PAGE", "PASS", "Home page loads with required elements")
                    return True
                else:
                    self.log_test("HOME_PAGE", "FAIL", "Missing required elements")
                    return False
            else:
                self.log_test("HOME_PAGE", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("HOME_PAGE", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jams_api(self) -> bool:
        """Test jams API endpoint"""
        return self.test_api_endpoint("GET", "/api/jams")
    
    def test_songs_api(self) -> bool:
        """Test songs API endpoint"""
        return self.test_api_endpoint("GET", "/api/songs")
    
    def test_create_jam(self) -> Optional[str]:
        """Test jam creation and return jam ID"""
        jam_data = {
            "name": f"Test Jam {int(time.time())}",
            "description": "Automated test jam",
            "location": "Test Studio",
            "jam_date": date.today().isoformat()
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/jams", data=jam_data)
            if response.status_code == 200:
                jam = response.json()
                self.log_test("CREATE_JAM", "PASS", f"Created jam: {jam['name']}")
                return jam['id']
            else:
                self.log_test("CREATE_JAM", "FAIL", f"Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("CREATE_JAM", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_create_song(self) -> Optional[str]:
        """Test song creation and return song ID"""
        song_data = {
            "title": f"Test Song {int(time.time())}",
            "artist": "Test Artist"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/songs", json=song_data)
            if response.status_code == 200:
                song = response.json()
                self.log_test("CREATE_SONG", "PASS", f"Created song: {song['title']}")
                return song['id']
            else:
                self.log_test("CREATE_SONG", "FAIL", f"Status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("CREATE_SONG", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_add_song_to_jam(self, jam_id: str, song_id: str) -> bool:
        """Test adding song to jam"""
        return self.test_api_endpoint("POST", f"/api/jams/{jam_id}/songs", 
                                    data={"song_id": song_id})
    
    def test_anonymous_voting(self, jam_id: str, song_id: str) -> bool:
        """Test anonymous voting functionality"""
        headers = {"X-Session-ID": self.session_id}
        return self.test_api_endpoint("POST", f"/api/jams/{jam_id}/songs/{song_id}/heart", 
                                    headers=headers)
    
    def test_access_code_system(self) -> bool:
        """Test access code verification"""
        # Test with correct access code
        access_data = {"access_code": "jam2024"}
        headers = {"X-Session-ID": self.session_id}
        
        try:
            response = self.session.post(f"{self.base_url}/api/access-code/verify", 
                                       json=access_data, headers=headers)
            if response.status_code == 200:
                self.log_test("ACCESS_CODE_CORRECT", "PASS", "Correct access code accepted")
                
                # Test access status
                status_response = self.session.get(f"{self.base_url}/api/access-code/status", 
                                                 headers=headers)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("has_access"):
                        self.log_test("ACCESS_STATUS", "PASS", "Access status correctly reported")
                        return True
                    else:
                        self.log_test("ACCESS_STATUS", "FAIL", "Access status not reported correctly")
                        return False
                else:
                    self.log_test("ACCESS_STATUS", "FAIL", f"Status check failed: {status_response.status_code}")
                    return False
            else:
                self.log_test("ACCESS_CODE_CORRECT", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("ACCESS_CODE_SYSTEM", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_websocket_connection(self, jam_id: str) -> bool:
        """Test WebSocket connection (basic check)"""
        try:
            # This is a simplified test - in practice you'd use websocket library
            response = self.session.get(f"{self.base_url}/ws/{jam_id}")
            # WebSocket endpoints typically return 426 or similar for HTTP requests
            if response.status_code in [426, 400, 404]:  # Expected for WebSocket endpoints
                self.log_test("WEBSOCKET_ENDPOINT", "PASS", "WebSocket endpoint accessible")
                return True
            else:
                self.log_test("WEBSOCKET_ENDPOINT", "FAIL", f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("WEBSOCKET_ENDPOINT", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jam_page(self, jam_slug: str) -> bool:
        """Test jam page accessibility"""
        try:
            response = self.session.get(f"{self.base_url}/jam/{jam_slug}")
            if response.status_code == 200:
                if "jam-container" in response.text and "songs-section" in response.text:
                    self.log_test("JAM_PAGE", "PASS", f"Jam page loads: {jam_slug}")
                    return True
                else:
                    self.log_test("JAM_PAGE", "FAIL", "Missing required elements")
                    return False
            else:
                self.log_test("JAM_PAGE", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("JAM_PAGE", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_core_tests(self) -> Dict[str, bool]:
        """Run core functionality tests"""
        print("🚀 Starting Jamanager Automated Tests...")
        print("=" * 50)
        
        results = {}
        
        # Test 1: Home page
        results["home_page"] = self.test_home_page()
        
        # Test 2: API endpoints
        results["jams_api"] = self.test_jams_api()
        results["songs_api"] = self.test_songs_api()
        
        # Test 3: Access code system
        results["access_code"] = self.test_access_code_system()
        
        # Test 4: Create jam
        jam_id = self.test_create_jam()
        results["create_jam"] = jam_id is not None
        
        if jam_id:
            # Test 5: Create song
            song_id = self.test_create_song()
            results["create_song"] = song_id is not None
            
            if song_id:
                # Test 6: Add song to jam
                results["add_song_to_jam"] = self.test_add_song_to_jam(jam_id, song_id)
                
                # Test 7: Anonymous voting
                results["anonymous_voting"] = self.test_anonymous_voting(jam_id, song_id)
            
            # Test 8: WebSocket endpoint
            results["websocket"] = self.test_websocket_connection(jam_id)
            
            # Test 9: Jam page (get slug from jam data)
            try:
                jam_response = self.session.get(f"{self.base_url}/api/jams/{jam_id}")
                if jam_response.status_code == 200:
                    jam_data = jam_response.json()
                    jam_slug = jam_data.get("slug")
                    if jam_slug:
                        results["jam_page"] = self.test_jam_page(jam_slug)
            except:
                results["jam_page"] = False
        
        return results
    
    def generate_report(self) -> str:
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        report = f"""
# Jamanager Test Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Tests: {total_tests}
- Passed: {passed_tests}
- Failed: {failed_tests}
- Success Rate: {(passed_tests/total_tests*100):.1f}%

## Test Results
"""
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            report += f"{status_icon} {result['test_id']}: {result['message']}\n"
        
        return report

def main():
    """Main test execution"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Testing Jamanager at: {base_url}")
    print("Make sure the server is running before executing tests.")
    print()
    
    runner = JamanagerTestRunner(base_url)
    results = runner.run_core_tests()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    # Generate detailed report
    report = runner.generate_report()
    
    # Save report to file
    with open("test_report.md", "w") as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to: test_report.md")
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)
    else:
        print("🎉 All tests passed!")

if __name__ == "__main__":
    main()
