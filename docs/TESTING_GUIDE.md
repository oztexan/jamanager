# Jamanager Testing Guide

## Overview
This guide provides comprehensive testing instructions for the Jamanager application, including both manual and automated testing approaches.

## Test Plan Files

### 1. Manual Testing
- **File**: `TEST_PLAN.md`
- **Purpose**: Comprehensive checklist for manual testing
- **Coverage**: All features, user roles, and edge cases
- **Usage**: Execute each test case manually and document results

### 2. Automated Testing
- **File**: `automated_test_runner.py`
- **Purpose**: Automated test execution for core functionality
- **Coverage**: API endpoints, basic functionality, integration tests
- **Usage**: Run via Python script or shell script

### 3. Test Execution Script
- **File**: `run_tests.sh`
- **Purpose**: Convenient shell script to run automated tests
- **Usage**: `./run_tests.sh` (requires server to be running)

## Quick Start Testing

### Prerequisites
1. **Server Running**: Ensure FastAPI server is running on `http://localhost:8000`
2. **Database**: SQLite database with test data
3. **Dependencies**: Python with `requests` library installed

### Running Automated Tests
```bash
# Option 1: Using the shell script
./run_tests.sh

# Option 2: Direct Python execution
python3 automated_test_runner.py

# Option 3: With custom server URL
python3 automated_test_runner.py http://localhost:8000
```

### Running Manual Tests
1. Open `TEST_PLAN.md`
2. Execute each test case systematically
3. Document results using the provided template
4. Report any failures with screenshots and details

## Test Categories

### 1. Core Functionality Tests
- ✅ Home page accessibility
- ✅ API endpoint availability
- ✅ Jam creation and management
- ✅ Song creation and management
- ✅ Access code system
- ✅ WebSocket connectivity

### 2. User Role Tests
- **Anonymous Users**: Voting, jam discovery, basic features
- **Jam Managers**: Full feature access, jam creation, management
- **Registered Attendees**: Performance registration, enhanced features

### 3. Real-time Features
- WebSocket connections
- Live vote updates
- Song play status
- Performance registrations

### 4. Integration Tests
- Database persistence
- API integration
- Frontend-backend communication
- Cross-browser compatibility

## Test Results

### Current Status (Automated Tests)
- **Total Tests**: 9
- **Passing**: 8
- **Failing**: 1 (anonymous voting - needs session handling fix)
- **Success Rate**: 88.9%

### Manual Test Coverage
- **Anonymous User Features**: 15 test cases
- **Jam Manager Features**: 20 test cases
- **Real-time Functionality**: 8 test cases
- **Cross-browser Testing**: 5 test cases
- **Security Testing**: 8 test cases
- **Performance Testing**: 8 test cases

## Test Execution Options

### Option 1: Manual Testing Only
- **Best for**: Thorough validation, edge case testing
- **Time**: 2-4 hours for complete test suite
- **Coverage**: 100% of features
- **Requirements**: Human tester, multiple browsers

### Option 2: Automated Testing Only
- **Best for**: Quick validation, CI/CD integration
- **Time**: 2-5 minutes
- **Coverage**: Core functionality (~70%)
- **Requirements**: Python environment, server running

### Option 3: Hybrid Approach (Recommended)
- **Best for**: Production deployment
- **Time**: 30 minutes automated + 1 hour manual
- **Coverage**: 95% of features
- **Requirements**: Both automated and manual testing

## Creating a Testing Agent

### For Automated Testing
The `automated_test_runner.py` can be easily adapted for use by testing agents:

```python
# Example agent integration
from automated_test_runner import JamanagerTestRunner

def run_agent_tests():
    runner = JamanagerTestRunner("http://your-server.com")
    results = runner.run_core_tests()
    
    # Process results
    if all(results.values()):
        return "PASS"
    else:
        return "FAIL"
```

### For Manual Testing
The `TEST_PLAN.md` provides a structured checklist that can be:
- Converted to test management tools (Jira, TestRail, etc.)
- Used with browser automation tools (Selenium, Playwright)
- Integrated with CI/CD pipelines

## Test Data Requirements

### Required Test Data
1. **Jams**: At least 3 jams with different dates (today, past, future)
2. **Songs**: At least 5 songs with various attributes
3. **Attendees**: Test attendee registrations
4. **Votes**: Sample vote data for testing

### Test Data Setup
```bash
# Run database initialization
python3 init_db.py

# Create additional test data
python3 -c "
import requests
# Create test jams, songs, etc.
"
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Jamanager Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start server
        run: uvicorn main:app --port 8000 &
      - name: Run tests
        run: python3 automated_test_runner.py
```

## Troubleshooting

### Common Issues
1. **Server not running**: Ensure FastAPI server is started
2. **Database connection**: Check SQLite database file exists
3. **Port conflicts**: Verify port 8000 is available
4. **Dependencies**: Install required Python packages

### Debug Mode
```bash
# Run with verbose output
python3 automated_test_runner.py --verbose

# Test specific functionality
python3 -c "
from automated_test_runner import JamanagerTestRunner
runner = JamanagerTestRunner()
runner.test_home_page()
"
```

## Test Reporting

### Automated Reports
- **File**: `test_report.md` (generated after each run)
- **Content**: Test results, timestamps, error details
- **Format**: Markdown for easy reading and sharing

### Manual Test Reports
- **Template**: Provided in `TEST_PLAN.md`
- **Format**: Structured checklist with pass/fail status
- **Documentation**: Screenshots, error messages, browser details

## Best Practices

### For Manual Testing
1. Test on multiple browsers and devices
2. Test with different user roles
3. Document all failures with details
4. Test edge cases and error conditions
5. Verify real-time functionality

### For Automated Testing
1. Run tests frequently during development
2. Integrate with CI/CD pipeline
3. Monitor test execution time
4. Update tests when features change
5. Maintain test data consistency

## Conclusion

The Jamanager testing framework provides comprehensive coverage of all application features through both manual and automated approaches. Choose the appropriate testing method based on your needs:

- **Development**: Use automated tests for quick validation
- **Staging**: Use hybrid approach for thorough testing
- **Production**: Use manual testing for final validation

For questions or issues with testing, refer to the individual test files or contact the development team.
