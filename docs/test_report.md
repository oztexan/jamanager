
# Jamanger Test Report
Generated: 2025-10-02T14:29:58.313222

## Summary
- Total Tests: 10
- Passed: 9
- Failed: 1
- Success Rate: 90.0%

## Test Results
✅ HOME_PAGE: Home page loads with required elements
✅ API_GET_/api/jams: Status 200
✅ API_GET_/api/songs: Status 200
✅ ACCESS_CODE_CORRECT: Correct access code accepted
✅ ACCESS_STATUS: Access status correctly reported
✅ CREATE_JAM: Created jam: Test Jam 1759379398
✅ CREATE_SONG: Created song: Test Song 1759379398
✅ API_POST_/api/jams/c3e16acb-5094-4e35-81c2-7aa14411456d/songs: Status 200
❌ API_POST_/api/jams/c3e16acb-5094-4e35-81c2-7aa14411456d/songs/be5aa028-276b-441d-8d65-9b6180561fa1/heart: Expected 200, got 422
✅ WEBSOCKET_ENDPOINT: WebSocket endpoint accessible
