# Jamanager User Stories

## Project Overview
Jamanager is a real-time jam session management application that allows musicians to organize, participate in, and manage live music jam sessions. The application supports both plebs and bosses with different levels of functionality.

## User Roles
- **User**: All roles
- **Anonymous User**: Abbreviated "pleb" - can view home page, specific jams, register in a jam as a muso, vote on songs
- **Jam Manager**: Abbreviated "boss" - has all capabilities plus jam management, song management, and administrative features
- **Jam Muso**: Abbreviated "muso" - a pleb or boss who has registered in a jam session as a muso

---

## Epic 1: Jam Discovery and Access

### Story 1.1: Jam Access via Link
**As a** user  
**I want to** access a jam session via a direct link  
**So that** I can join jam sessions shared by others  

**Acceptance Criteria:**
- Given a jam URL (e.g., `/jam/jam-slug-2025-10-04`)
- When I visit the URL
- Then I should see the jam details and be able to participate

### Story 1.2: QR Code Access
**As a** user  
**I want to** access a jam session via QR code  
**So that** I can easily join jam sessions in physical venues  

**Acceptance Criteria:**
- Given a jam session with a QR code
- When I scan the QR code with my phone
- Then I should be taken directly to the jam page

### Story 1.3: Jam Sharing
**As a** user  
**I want to** share a jam session with others  
**So that** more people can join the jam  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When I click the "Share Jam" button
- Then I should see a dialog with:
  - The jam URL that I can copy
  - A QR code that others can scan
- And I should be able to copy the URL to my clipboard

---

## Epic 2: User Registration and Authentication

### Story 2.1: Anonymous User Registration
**As a** pleb  
**I want to** register my name to join a jam session as a muso  
**So that** I can participate in voting and performance registration  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When I enter my name and click "Join Jam"
- Then I should be registered as an attendee
- And I should see my name displayed
- And I should gain access to voting and performance features

### Story 2.2: Jam Manager Authentication
**As a** user  
**I want to** authenticate with an access code  
**So that** I can become a "boss" with boss access

**Acceptance Criteria:**
- Given I have a boss access code
- When I enter the code and authenticate
- Then I should gain boss privileges
- And I should see additional boss features
- And my session should persist across page refreshes

### Story 2.3: User Session Management
**As a** muso  
**I want** my session to persist across jam page refreshes  
**So that** I don't have to re-register to a specific jam every time  

**Acceptance Criteria:**
- Given I'm registered in a jam session
- When I refresh the page
- Then I should remain registered
- And I should see my previous registration status
- Note, I must register again in a different jam

### Story 2.4: Browser Session Isolation
**As a** muso  
**I want** each browser window/tab to be treated as a separate session  
**So that** I can have different registrations in different browser instances  

**Acceptance Criteria:**
- Given I'm registered in a jam session in one browser
- When I open the same jam in a different browser window/tab
- Then I should start as an anonymous "pleb" (not auto-logged in)
- And I should need to register separately in the new browser
- And each browser should maintain its own independent session

### Story 2.5: Session Security
**As a** muso  
**I want** my session to be secure and not easily hijacked  
**So that** my votes and registrations can't be manipulated by others  

**Acceptance Criteria:**
- Given I'm registered in a jam session
- When my session is active
- Then my session ID should be unique and unpredictable
- And my session should only be valid for the specific jam I registered for
- And my session should not be accessible from other browser instances

---

## Epic 3: Song Management

### Story 3.1: View Jam Song Queue
**As a** user  
**I want to** see all songs currently in the jam queue  
**So that** I can see what's planned for the session  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When the page loads
- Then I should see a list of all songs in the jam
- And each song should show:
  - Title and artist
  - Current vote count
  - Performance registration status

### Story 3.2: Song Sorting Options
**As a** user  
**I want to** sort the song list by different criteria  
**So that** I can organize the songs in a way that makes sense to me  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When I look at the song list
- Then I should see sorting options for:
  - Song Name (A-Z or Z-A)
  - Song Artist (A-Z or Z-A)
  - Vote Count (highest to lowest or lowest to highest)
- And I should be able to select any sorting option
- And the song list should update immediately when I change the sort order
- And my sorting preference should be remembered during my session

### Story 3.3: Performance Filter (Muso Only)
**As a** muso  
**I want to** filter the song list to show only songs I'm performing on  
**So that** I can focus on my performance commitments  

**Acceptance Criteria:**
- Given I'm registered as a muso in a jam session
- When I look at the song list
- Then I should see a filter option to "Show only my performances"
- And when I enable this filter
- Then I should only see songs where I'm registered to perform
- And I should be able to toggle this filter on/off
- And the filter should work in combination with sorting options

### Story 3.4: Performance Order Display
**As a** user  
**I want to** see performance order numbers on each song  
**So that** I can understand the planned sequence of performances  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When I look at the song list
- Then each song should display a performance order number
- And the order should be determined by:
  - Vote count (highest to lowest)
  - Then song name (A to Z) for songs with equal votes
- And the order numbers should be visually distinct and easy to read
- And the order should update automatically when votes change

### Story 3.5: Add Songs to Jam 
**As a** boss or muso  
**I want to** add songs from the song library to the jam  
**So that** I can help build the song queue for the session  

**Acceptance Criteria:**
- Given I'm a muso or boss viewing a jam
- When I click "Add Song"
- Then I should see a modal with available songs
- And I should be able to select a song from the dropdown
- And when I click "Add Song", the song should be added to the jam
- And the song list should update immediately

### Story 3.6: Song Library Management
**As a** boss  
**I want to** manage the song library  
**So that** I can add new songs and maintain the database  

**Acceptance Criteria:**
- Given I'm a boss
- When I access the song management interface
- Then I should be able to:
  - Add new songs with title, artist, and chord sheet URL
  - Have the chord sheet finder service available as an option for choosing a URL
  - Edit existing songs
  - Delete songs
  - Search and filter songs
---

## Epic 4: Voting System

### Story 4.1: Vote on Songs
**As a** muso  
**I want to** vote on songs in the jam queue  
**So that** I can influence which songs get played  

**Acceptance Criteria:**
- Given I'm registered in a jam session
- When I click the vote button on a song
- Then my vote should be recorded
- And the vote count should update immediately
- And the vote on the song shall only apply to this jam
- And I should be able to remove my vote by clicking again

### Story 4.2: View Vote Counts
**As a** user  
**I want to** see how many votes each song has received  
**So that** I can see which songs are most popular  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When I look at the song list
- Then each song should display its current vote count
- And the songs should be ordered by vote count (highest first)

### Story 4.3: Heart Toggle Voting
**As a** user  
**I want to** use a heart icon to vote on songs  
**So that** I have a more intuitive and visually appealing way to vote  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When I look at the song list
- Then I should see an unfilled heart icon/image next to each song's vote count (where thumbs up used to be)
- And when I click the heart icon/image:
  - If I haven't voted, the heart/icon should fill red and my vote should be recorded
  - If I have voted, the heart should become unfill and my vote should be removed
- And the vote count should update immediately

### Story 4.4: Real-time Vote Updates
**As a** user  
**I want** to see vote updates from other users in real-time  
**So that** I can see the current state of the jam without refreshing  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When another user votes on a song
- Then I should see the vote count update immediately
- And I should see the heart visual state change only for the user who voted
- And I should not need to refresh the page to see updates

### Story 4.5: Vote State Persistence
**As a** muso  
**I want** my vote state to be preserved across page refreshes  
**So that** I can see which songs I've voted on when I return  

**Acceptance Criteria:**
- Given I'm registered in a jam session and have voted on songs
- When I refresh the page
- Then I should see my previous votes reflected in the heart states
- And the vote counts should be accurate
- And I should be able to toggle my votes as expected

---

## Epic 5: Performance Registration

### Story 5.1: Register to Perform
**As a** muso  
**I want to** register to perform on specific songs  
**So that** I can participate in the musical performance  

**Acceptance Criteria:**
- Given I'm registered in a jam session
- When I click "Perform" on a song
- Then I should see a modal asking for my instrument
- And when I enter my instrument and confirm
- Then I should be registered to perform that song
- And I should see confirmation of my registration

### Story 5.2: Performance Limits
**As a** muso  
**I want to** be limited to performing on a maximum number of songs  
**So that** everyone gets a fair chance to participate  

**Acceptance Criteria:**
- Given I'm registered in a jam session
- When I try to register for more than 3 songs (default limit)
- Then I should see a message indicating I've reached the limit
- And I should not be able to register for additional songs
- And the boss should be able to adjust this limit

### Story 5.3: View Performance Registrations
**As a** user  
**I want to** see who is registered to perform on each song  
**So that** I can see the lineup for each song  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When I look at the song list
- Then I should see who is registered to perform on each song
- And I should see what instruments they're playing

### Story 5.4: Unregister from Performance
**As a** muso  
**I want to** unregister from performing on a song I've previously registered for  
**So that** I can change my mind about performing  

**Acceptance Criteria:**
- Given I'm registered to perform on a song
- When I click the "Unregister" button on that song
- Then I should be unregistered from performing
- And the button should change back to "Register to Perform"
- And I should see confirmation of my unregistration

### Story 5.5: Real-time Performance Registration Updates
**As a** user  
**I want** to see performance registrations and unregistrations in real-time  
**So that** I can see the current lineup for each song as it changes  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When another user registers to perform on a song
- Then I should see their name and instrument appear immediately in the performers list
- And when another user unregisters from performing
- Then I should see their name and instrument disappear immediately
- And I should not need to refresh the page to see these updates
- And the updates should appear for all users viewing the jam simultaneously

---

## Epic 6: Jam Management (Jam Managers Only)

### Story 6.1: Create Jam Sessions
**As a** boss  
**I want to** create new jam sessions  
**So that** I can organize musical events  

**Acceptance Criteria:**
- Given I'm a boss
- When I access the jam creation interface
- Then I should be able to:
  - Enter jam name and description
  - Select a venue
  - Set the jam date
  - Upload a background image
  - Create the jam session
- And the jam should be immediately available via its URL

### Story 6.2: Manage Jam Details
**As a** boss  
**I want to** edit jam details  
**So that** I can update information as needed  

**Acceptance Criteria:**
- Given I'm managing a jam session
- When I want to update jam details
- Then I should be able to:
  - Change the jam name and description
  - Update the venue
  - Modify the date
  - Change the background image

### Story 6.3: Venue Management
**As a** boss  
**I want to** manage venues  
**So that** I can create and maintain venue information  

**Acceptance Criteria:**
- Given I'm a boss
- When I access venue management
- Then I should be able to:
  - Add new venues with name, address, and description
  - Edit existing venues
  - Delete venues
  - View all venues

---

## Epic 7: Real-time Updates

### Story 7.1: Live Updates
**As a** user  
**I want to** see real-time updates when others vote or register  
**So that** I can see the current state of the jam  

**Acceptance Criteria:**
- Given I'm viewing a jam session
- When other users vote or register to perform
- Then I should see the updates immediately
- And I shouldn't need to refresh the page

### Story 7.2: WebSocket Connection
**As a** user  
**I want** the application to maintain a real-time connection  
**So that** updates are delivered instantly  

**Acceptance Criteria:**
- Given I'm using the jam session interface
- When the page loads
- Then a WebSocket connection should be established
- And the connection should remain active throughout my session
- And if the connection drops, it should attempt to reconnect

---

## Epic 8: Chord Sheet Integration

### Story 8.1: Chord Sheet Discovery
**As a** boss or muso
**I want to** see the top 5 (configurable number, sorted by highest votes) chord sheets from Ultimate Guitar to choose as the chord sheet for a song in a particular jam. This can be different from the song database chord sheet URL, though the song database chord sheet will be the default.
**So that** musicians have the music they need  

**Acceptance Criteria:**
- Given I'm viewing a jam session song
- When I access the jam song chord sheet editor (part of song actions)
- Then I should see the current chord sheet for the song
- And I should be able to use the chord sheet lookup service to choose another chord sheet
- And I should be able to save this for the song in this specific jam
- And if a chord sheet is defined for this song in this jam, clicking on the song should open a new window to the chord sheet URL

### Story 8.2: Manual Chord Sheet Input
**As a** boss or muso  
**I want to** manually add or edit chord sheet URLs  
**So that** I can provide music when automatic discovery doesn't work  

**Acceptance Criteria:**
- Given I'm viewing song details or a jam song chord sheet editor
- When I want to add a chord sheet URL
- Then I should be able to:
  - Enter a custom chord sheet URL
  - Edit existing chord sheet URLs
  - Save the changes
- And the URL should be validated for accessibility

---

## Epic 9: User Experience

### Story 9.1: Responsive Design
**As a** user  
**I want** the application to work on my mobile device  
**So that** I can participate from anywhere  

**Acceptance Criteria:**
- Given I'm using a mobile device
- When I access the jam session
- Then the interface should be optimized for mobile
- And all features should be accessible via touch
- And the layout should adapt to different screen sizes

### Story 9.2: Consistent Look & Feel
**As a** user  
**I want** the application to have the same look & feel across all pages  
**So that** I have a joyful user experience  

**Acceptance Criteria:**
- Given I'm accessing the site
- When I see pages and the elements on them
- Then they have a harmonious look and feel
- And they use a standard colour palette
- And foreground elements have a configurable transparency
- And they contrast well against jam specific backgrounds
- And the jam specific backgrounds are probably blurred

### Story 9.3: Error Handling
**As a** user  
**I want** clear error messages when something goes wrong  
**So that** I understand what happened and how to fix it  

**Acceptance Criteria:**
- Given an error occurs in the application
- When I encounter the error
- Then I should see a clear, user-friendly error message
- And I should be given guidance on how to resolve the issue
- And the application should remain functional for other features

### Story 9.4: Loading States
**As a** user  
**I want** to see loading indicators when the app is processing  
**So that** I know the app is working and not frozen  

**Acceptance Criteria:**
- Given I'm performing an action that takes time
- When the action is processing
- Then I should see a loading indicator
- And I should be prevented from performing duplicate actions
- And the loading state should clear when the action completes

### Story 9.5: Modern App-Style Notifications
**As a** user  
**I want** to see modern app-style notifications
**So that** I know when actions succeed or fail  

**Acceptance Criteria:**
- Given I'm performing an action
- When the action deserves a notification
- Then I should see a modern notification popup in the upper right corner
- And the notification should have:
  - A close button (×)
  - An appropriate icon (✓ for success, ✕ for error, ! for warning, i for info)
  - A title and message
  - A progress bar showing auto-dismiss countdown
- And the notification should auto-disappear after a short time
- And I should be able to close it manually
- And multiple notifications should stack vertically
- And the notifications should be responsive and work on mobile devices

### Story 9.6: Feature Removal
**As a** user  
**I want** the interface to only show features that are actually required  
**So that** I'm not confused by unnecessary functionality  

**Acceptance Criteria:**
- Given I'm viewing the jam session interface
- When I look at the available actions
- Then I should only see features that are part of the user requirements
- And I should not see "Change Name" or "Test Notifications" buttons
- And the interface should be clean and focused on core functionality

---

## Epic 10: Administrative Features

### Story 10.1: Feature Flags
**As a** boss  
**I want to** control which features are available  
**So that** I can customize the experience for different events  

**Acceptance Criteria:**
- Given I'm a boss
- When I access the feature flags interface
- Then I should be able to:
  - Enable/disable specific features
  - Set feature availability by user role
  - Apply changes immediately
  - View current feature status

### Story 10.2: Analytics and Reporting
**As a** boss  
**I want to** see statistics about jam sessions  
**So that** I can understand participation and improve future events  

**Acceptance Criteria:**
- Given I'm a boss
- When I view jam analytics
- Then I should see:
  - Number of attendees
  - Most popular songs
  - Performance registrations
  - Session duration and activity

---

## Epic 11: Technical Implementation Requirements

### Story 11.1: Code Quality and Structure
**As a** developer  
**I want** the codebase to follow best practices and be well-structured  
**So that** the application is maintainable and scalable  

**Acceptance Criteria:**
- Given I'm working on the codebase
- When I review the code
- Then it should follow Python/FastAPI best practices
- And it should have proper separation of concerns (routers, services, models)
- And it should pass linting checks (flake8, black, isort)
- And it should have minimal code duplication
- And it should be well-documented

### Story 11.2: Real-time Communication Architecture
**As a** developer  
**I want** the real-time communication to be properly architected  
**So that** updates work reliably across all connected clients  

**Acceptance Criteria:**
- Given I'm implementing real-time features
- When users perform actions that affect others
- Then WebSocket messages should be broadcast to all relevant clients
- And the message format should be consistent and well-defined
- And the frontend should handle messages correctly
- And only the appropriate users should see visual updates (e.g., only the voter sees heart changes)

### Story 11.3: Session Management Architecture
**As a** developer  
**I want** session management to be robust and secure  
**So that** users have a consistent and secure experience  

**Acceptance Criteria:**
- Given I'm implementing session management
- When users interact with the application
- Then each browser instance should have a unique session ID
- And sessions should be tied to specific jam instances
- And session state should persist across page refreshes
- And sessions should not leak between different browser instances
- And session IDs should be cryptographically secure

---

## Technical Requirements

### Performance
- Page load time should be under 2 seconds
- Real-time updates should appear within 1 second
- Application should support 100+ concurrent users per jam

### Security
- User sessions should be secure and not easily hijacked
- Access codes should be properly validated
- User input should be sanitized to prevent XSS
- Session IDs should be unique and unpredictable
- Each browser instance should have its own independent session
- Sessions should be tied to specific jam instances

### Reliability
- Application should handle network interruptions gracefully
- Database should maintain data integrity
- WebSocket connections should auto-reconnect
- Real-time updates should work correctly across multiple browser instances
- Vote state should be preserved across page refreshes
- Session state should be maintained across page refreshes within the same browser

### Browser Support
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)
- iOS & Android device browsers

---

## Definition of Done

For each user story to be considered complete:

1. **Functionality**: All acceptance criteria are met
2. **Testing**: Manual testing has been performed
3. **Code Quality**: Code follows project standards and is well-documented
4. **Performance**: Feature performs within acceptable limits
5. **Security**: No security vulnerabilities introduced
6. **User Experience**: Interface is intuitive and responsive
7. **Error Handling**: Appropriate error messages and recovery mechanisms
8. **Documentation**: Any new features are documented

---

## Priority Levels

- **P0 (Critical)**: Core functionality required for basic operation
  - Epic 1: Jam Discovery and Access
  - Epic 2: User Registration and Authentication (including session management)
  - Epic 3: Song Management (basic viewing and adding)
  - Epic 4: Voting System (including real-time updates and state persistence)
  - Epic 5: Performance Registration (basic functionality)
  - Epic 11: Technical Implementation Requirements (code quality, architecture)

- **P1 (High)**: Important features that significantly improve user experience
  - Epic 6: Jam Management (boss features)
  - Epic 7: Real-time Updates
  - Epic 8: Chord Sheet Integration
  - Epic 9: User Experience (responsive design, error handling, notifications)

- **P2 (Medium)**: Nice-to-have features that enhance functionality
  - Epic 10: Administrative Features
  - Advanced performance limits and analytics

- **P3 (Low)**: Future enhancements and optimizations
  - Advanced analytics and reporting
  - Additional integrations

---

*This document should be updated as requirements change or new features are requested. Each story should be reviewed and refined before development begins.*
