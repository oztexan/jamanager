# Jamanger - Comprehensive Test Plan

## Overview
This test plan covers all functionality of the Jamanger application, including anonymous user features, jam manager features, real-time updates, and system integration.

## Test Environment Setup
- **Backend**: FastAPI server running on `http://localhost:8000`
- **Database**: PostgreSQL with test data
- **Browser**: Chrome/Firefox/Safari (test on multiple browsers)
- **Test Data**: Ensure test jams exist with various dates (today, past, future)

---

## 1. ANONYMOUS USER FEATURES

### 1.1 Home Page Access
- [ ] **1.1.1** Navigate to `http://localhost:8000`
- [ ] **1.1.2** Verify page loads without errors
- [ ] **1.1.3** Verify "Welcome to Jamanger!" message is displayed
- [ ] **1.1.4** Verify lock button (🔒) is visible in top-right corner
- [ ] **1.1.5** Verify jam manager features are hidden by default

### 1.2 Jams Happening Today Section
- [ ] **1.2.1** Verify "Jams Happening Today" section is visible
- [ ] **1.2.2** Verify current date is displayed in dd MMM YYYY format (Sydney timezone)
- [ ] **1.2.3** Verify jams scheduled for today are displayed as clickable tiles
- [ ] **1.2.4** Verify jam tiles show name and location
- [ ] **1.2.5** Verify "No jams today" message when no jams are scheduled
- [ ] **1.2.6** Verify jam tiles have hover effects
- [ ] **1.2.7** Click on a jam tile and verify navigation to jam page

### 1.3 Jam Page (Anonymous User)
- [ ] **1.3.1** Navigate to a jam page via jam tile
- [ ] **1.3.2** Verify jam information is displayed (name, location, date)
- [ ] **1.3.3** Verify background image is displayed (if present)
- [ ] **1.3.4** Verify background is blurred appropriately
- [ ] **1.3.5** Verify foreground elements are semi-transparent
- [ ] **1.3.6** Verify QR code is displayed
- [ ] **1.3.7** Verify songs are listed in vote order (highest to lowest)
- [ ] **1.3.8** Verify heart buttons are present for each song
- [ ] **1.3.9** Verify vote counts are displayed
- [ ] **1.3.10** Verify "Perform" buttons are NOT visible (anonymous user)
- [ ] **1.3.11** Verify "Play Song" button is NOT visible (anonymous user)

### 1.4 Anonymous Voting
- [ ] **1.4.1** Click heart button on a song
- [ ] **1.4.2** Verify heart changes to filled state
- [ ] **1.4.3** Verify vote count increases
- [ ] **1.4.4** Click heart button again
- [ ] **1.4.5** Verify heart changes to empty state
- [ ] **1.4.6** Verify vote count decreases
- [ ] **1.4.7** Verify song reordering based on vote count
- [ ] **1.4.8** Refresh page and verify vote persists (session-based)

### 1.5 WebSocket Real-time Updates
- [ ] **1.5.1** Open jam page in two browser windows
- [ ] **1.5.2** Vote on song in first window
- [ ] **1.5.3** Verify vote appears in second window within 1 second
- [ ] **1.5.4** Verify song reordering happens in both windows
- [ ] **1.5.5** Test with multiple songs and votes

---

## 2. JAM MANAGER FEATURES

### 2.1 Access Code System
- [ ] **2.1.1** Click lock button (🔒) on home page
- [ ] **2.1.2** Verify access code dialog appears
- [ ] **2.1.3** Enter incorrect access code
- [ ] **2.1.4** Verify error message is displayed
- [ ] **2.1.5** Enter correct access code (jam2024)
- [ ] **2.1.6** Verify success message is displayed
- [ ] **2.1.7** Verify lock button changes to unlocked (🔓)
- [ ] **2.1.8** Verify jam manager features become visible
- [ ] **2.1.9** Click unlocked lock button
- [ ] **2.1.10** Verify return to anonymous user state

### 2.2 Venue Management
- [ ] **2.2.1** Click "Manage Venues" card
- [ ] **2.2.2** Verify venue management page loads
- [ ] **2.2.3** Click "Add Venue" button
- [ ] **2.2.4** Fill in venue name (required)
- [ ] **2.2.5** Fill in venue address
- [ ] **2.2.6** Fill in venue description
- [ ] **2.2.7** Click "Save Venue" button
- [ ] **2.2.8** Verify venue appears in venues list
- [ ] **2.2.9** Test editing existing venue
- [ ] **2.2.10** Test deleting venue
- [ ] **2.2.11** Verify venue validation (required name)

### 2.3 Enhanced Jam Creation
- [ ] **2.3.1** Click "Create Jam" card
- [ ] **2.3.2** Verify create jam modal appears
- [ ] **2.3.3** Fill in jam name (required field)
- [ ] **2.3.4** Select venue from dropdown (required)
- [ ] **2.3.5** Select jam date (today's date)
- [ ] **2.3.6** Fill in description
- [ ] **2.3.7** Upload background image (PNG/JPG)
- [ ] **2.3.8** Click "Create Jam" button
- [ ] **2.3.9** Verify success message
- [ ] **2.3.10** Verify navigation to new jam page
- [ ] **2.3.11** Verify jam appears in "Jams Happening Today" section

### 2.4 Jam Creation Validation
- [ ] **2.4.1** Try to create jam without name
- [ ] **2.4.2** Verify error message for required name
- [ ] **2.4.3** Try to create jam without selecting venue
- [ ] **2.4.4** Verify error message for required venue
- [ ] **2.4.5** Try to upload invalid file type (e.g., .txt)
- [ ] **2.4.6** Verify error message for invalid file type
- [ ] **2.4.7** Try to upload file larger than 5MB
- [ ] **2.4.8** Verify error message for file size

### 2.5 Song Management
- [ ] **2.5.1** Click "Add Song" card
- [ ] **2.5.2** Verify add song modal appears
- [ ] **2.5.3** Fill in song title
- [ ] **2.5.4** Fill in artist name
- [ ] **2.5.5** Fill in song key
- [ ] **2.5.6** Fill in tempo
- [ ] **2.5.7** Fill in tags
- [ ] **2.5.8** Click "Add Song" button
- [ ] **2.5.9** Verify success message
- [ ] **2.5.10** Verify song appears in song library

### 2.6 Jam Management
- [ ] **2.6.1** Click "Manage Jams" card
- [ ] **2.6.2** Verify jam manager panel loads
- [ ] **2.6.3** Verify list of jams is displayed
- [ ] **2.6.4** Verify jam details are shown (name, venue, date, song count)
- [ ] **2.6.5** Click on a jam to view details
- [ ] **2.6.6** Verify jam details page loads

---

## 3. JAM PAGE FEATURES (JAM MANAGER)

### 3.1 Jam Manager Controls
- [ ] **3.1.1** Access jam page as jam manager
- [ ] **3.1.2** Verify "Perform" buttons are visible
- [ ] **3.1.3** Verify "Play Song" button is visible
- [ ] **3.1.4** Verify "Add Song to Jam" section is visible
- [ ] **3.1.5** Verify attendee registration section is visible

### 3.2 Song Performance Registration
- [ ] **3.2.1** Click "Register to Perform" on a song
- [ ] **3.2.2** Verify registration modal appears
- [ ] **3.2.3** Enter attendee name
- [ ] **3.2.4** Click "Register" button
- [ ] **3.2.5** Verify success message
- [ ] **3.2.6** Verify "Perform" button changes to "Registered"
- [ ] **3.2.7** Verify attendee appears in performers list

### 3.3 Song Playback
- [ ] **3.3.1** Click "Play Song" button
- [ ] **3.3.2** Verify song starts playing
- [ ] **3.3.3** Verify play status updates in real-time
- [ ] **3.3.4** Verify other users see the song is playing

### 3.4 Add Songs to Jam
- [ ] **3.4.1** Use "Add Song to Jam" section
- [ ] **3.4.2** Search for existing song
- [ ] **3.4.3** Select song from search results
- [ ] **3.4.4** Click "Add to Jam" button
- [ ] **3.4.5** Verify song appears in jam song list
- [ ] **3.4.6** Verify song appears in correct vote order

---

## 4. FEATURE FLAGS SYSTEM

### 4.1 Role-Based Access Control
- [ ] **4.1.1** Verify anonymous users see only voting features
- [ ] **4.1.2** Verify registered attendees see performance registration
- [ ] **4.1.3** Verify jam managers see all features
- [ ] **4.1.4** Test feature flag changes in real-time

### 4.2 Permission Checking
- [ ] **4.2.1** Verify API endpoints respect user permissions
- [ ] **4.2.2** Verify frontend UI updates based on permissions
- [ ] **4.2.3** Test permission changes without page refresh

---

## 5. REAL-TIME FUNCTIONALITY

### 5.1 WebSocket Connections
- [ ] **5.1.1** Verify WebSocket connects on jam page load
- [ ] **5.1.2** Verify WebSocket reconnects after disconnection
- [ ] **5.1.3** Verify multiple users can connect simultaneously
- [ ] **5.1.4** Verify WebSocket closes on page unload

### 5.2 Real-time Updates
- [ ] **5.2.1** Test vote updates across multiple users
- [ ] **5.2.2** Test song play status updates
- [ ] **5.2.3** Test performance registration updates
- [ ] **5.2.4** Test song addition updates
- [ ] **5.2.5** Verify updates happen within 1 second

---

## 6. DATABASE INTEGRITY

### 6.1 Data Persistence
- [ ] **6.1.1** Create jam and verify it persists after server restart
- [ ] **6.1.2** Add song and verify it persists
- [ ] **6.1.3** Cast vote and verify it persists
- [ ] **6.1.4** Register attendee and verify it persists

### 6.2 Data Relationships
- [ ] **6.2.1** Verify jam-song relationships are maintained
- [ ] **6.2.2** Verify vote-jam-song relationships are maintained
- [ ] **6.2.3** Verify attendee-jam relationships are maintained
- [ ] **6.2.4** Verify performance registration relationships are maintained

---

## 7. ERROR HANDLING

### 7.1 Network Errors
- [ ] **7.1.1** Test with server offline
- [ ] **7.1.2** Verify graceful error messages
- [ ] **7.1.3** Test with slow network connection
- [ ] **7.1.4** Verify retry mechanisms work

### 7.2 Input Validation
- [ ] **7.2.1** Test with invalid jam data
- [ ] **7.2.2** Test with invalid song data
- [ ] **7.2.3** Test with invalid access codes
- [ ] **7.2.4** Test with malformed requests

---

## 8. PERFORMANCE TESTING

### 8.1 Load Testing
- [ ] **8.1.1** Test with 10+ concurrent users
- [ ] **8.1.2** Test with 100+ songs in a jam
- [ ] **8.1.3** Test with multiple jams running simultaneously
- [ ] **8.1.4** Verify response times remain under 2 seconds

### 8.2 Memory Usage
- [ ] **8.2.1** Monitor memory usage during extended use
- [ ] **8.2.2** Verify no memory leaks in WebSocket connections
- [ ] **8.2.3** Test with large background images

---

## 9. CROSS-BROWSER TESTING

### 9.1 Browser Compatibility
- [ ] **9.1.1** Test on Chrome (latest)
- [ ] **9.1.2** Test on Firefox (latest)
- [ ] **9.1.3** Test on Safari (latest)
- [ ] **9.1.4** Test on Edge (latest)
- [ ] **9.1.5** Test on mobile browsers

### 9.2 Responsive Design
- [ ] **9.2.1** Test on desktop (1920x1080)
- [ ] **9.2.2** Test on tablet (768x1024)
- [ ] **9.2.3** Test on mobile (375x667)
- [ ] **9.2.4** Verify all features work on all screen sizes

---

## 10. SECURITY TESTING

### 10.1 Access Control
- [ ] **10.1.1** Verify anonymous users cannot access jam manager features
- [ ] **10.1.2** Verify access code is required for jam manager access
- [ ] **10.1.3** Test with invalid access codes
- [ ] **10.1.4** Verify session management works correctly

### 10.2 Input Sanitization
- [ ] **10.2.1** Test with XSS attempts in jam names
- [ ] **10.2.2** Test with SQL injection attempts
- [ ] **10.2.3** Test with malicious file uploads
- [ ] **10.2.4** Verify all inputs are properly sanitized

---

## 11. INTEGRATION TESTING

### 11.1 API Integration
- [ ] **11.1.1** Test all API endpoints with valid data
- [ ] **11.1.2** Test all API endpoints with invalid data
- [ ] **11.1.3** Verify API responses match expected format
- [ ] **11.1.4** Test API rate limiting
- [ ] **11.1.5** Test venue management API endpoints
- [ ] **11.1.6** Test jam creation with venue selection
- [ ] **11.1.7** Test venue validation and error handling

### 11.2 Database Integration
- [ ] **11.2.1** Test database connection stability
- [ ] **11.2.2** Test database transaction handling
- [ ] **11.2.3** Test database constraint enforcement
- [ ] **11.2.4** Test database backup and restore

---

## 12. USABILITY TESTING

### 12.1 User Experience
- [ ] **12.1.1** Test complete user journey from home to voting
- [ ] **12.1.2** Test jam manager workflow from creation to management
- [ ] **12.1.3** Verify intuitive navigation and controls
- [ ] **12.1.4** Test error message clarity and helpfulness

### 12.2 Accessibility
- [ ] **12.2.1** Test keyboard navigation
- [ ] **12.2.2** Test screen reader compatibility
- [ ] **12.2.3** Test color contrast ratios
- [ ] **12.2.4** Test with accessibility tools

---

## Test Execution Notes

### Manual Testing
- Each test case should be executed manually
- Document any failures with screenshots and error messages
- Test on multiple browsers and devices
- Test with different user roles and permissions

### Automated Testing
- This test plan can be adapted for automated testing
- Focus on API endpoints and core functionality first
- Use tools like Selenium for UI testing
- Use tools like Postman for API testing

### Test Data Requirements
- Create test jams with various dates (today, past, future)
- Create test songs with different attributes
- Create test attendees with different names
- Test with various file types and sizes

### Success Criteria
- All critical functionality must pass
- Performance must meet requirements
- Security vulnerabilities must be addressed
- User experience must be intuitive and smooth

---

## Test Results Template

```
Test Case ID: [ID]
Test Date: [DATE]
Tester: [NAME]
Browser: [BROWSER]
Status: [PASS/FAIL]
Notes: [DETAILS]
Screenshots: [IF FAILED]
```

---

*This test plan should be executed before any production deployment to ensure the Jamanger application meets all requirements and provides a reliable user experience.*
