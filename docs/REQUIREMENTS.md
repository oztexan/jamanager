# Jamanager - User Stories & Requirements

## Overview
Jamanager is a real-time song voting and jam management system with two main user types: **Jam Managers** and **Attendees**.

## User Stories

### Attendee Stories (Priority 1)

#### AT-001: QR Code Access ✅ **COMPLETED**
**As an attendee, I can access a jam instance via QR code**
- **Acceptance Criteria:**
  - ✅ QR code displays jam URL (e.g., `http://localhost:8000/jam/{slug}`)
  - ✅ QR code is prominently displayed on jam page
  - ✅ Mobile-friendly access to jam via QR scan
  - ✅ QR code updates when jam slug changes
- **Implementation**: `/api/jams/{jam_id}/qr` endpoint generates PNG QR codes

#### AT-002: Single Vote Per Song ✅ **COMPLETED**
**As an attendee, I can vote once per song**
- **Acceptance Criteria:**
  - ✅ Each attendee can vote only once per song
  - ✅ Vote count reflects total unique votes
  - ✅ Visual feedback when vote is cast
  - ✅ Cannot vote again on same song
- **Implementation**: Database constraints prevent duplicate votes, attendee-based voting system

#### AT-003: Musician Registration ✅ **COMPLETED**
**As an attendee, I can register as a muso in the jam (enter unique name to track attendee)**
- **Acceptance Criteria:**
  - ✅ Simple name entry form on jam page
  - ✅ Unique name validation (no duplicates in same jam)
  - ✅ Name persists for session duration
  - ✅ Name displayed when voting/registering for songs
- **Implementation**: `/api/jams/{jam_id}/attendees` endpoint with unique name validation

#### AT-004: Song Performance Registration ✅ **COMPLETED**
**As an attendee, I can register to perform on a song selected in the jam instance**
- **Acceptance Criteria:**
  - ✅ Select from songs already in jam queue
  - ✅ Register as performer for specific song
  - ✅ Multiple performers can register for same song
  - ✅ Visual indication of who's registered to perform
  - ✅ Toggle registration (register/unregister) by clicking perform button
  - ✅ Song row highlighting when user is registered to perform
  - ✅ Microphone icon (🎤) with filled/empty states
- **Implementation**: `/api/jams/{jam_id}/songs/{song_id}/register` and `DELETE` endpoints with toggle functionality

#### AT-005: Song Suggestions ✅ **COMPLETED**
**As an attendee, I can suggest existing and new songs for the jam instance (automatically register to perform)**
- **Acceptance Criteria:**
  - ✅ Search existing song library
  - ✅ Add new songs to library if not found
  - ✅ Automatically register as performer when suggesting
  - ✅ Song appears in jam queue after suggestion
  - ✅ Ultimate Guitar chord sheet integration
- **Implementation**: Complete song suggestion system with chord sheet lookup

### Universal User Stories (Priority 1.5)

#### UU-001: Universal Heart Voting ✅ **COMPLETED**
**As any user (anonymous, registered, or jam manager), I can vote for a song in the jam by toggling a love heart button**
- **Acceptance Criteria:**
  - ✅ Heart button shows filled/unfilled state
  - ✅ Click toggles vote on/off
  - ✅ No registration required (anonymous voting)
  - ✅ Visual feedback on toggle
  - ✅ Vote count updates immediately
  - ✅ All user types can vote (anonymous, registered attendees, jam managers)
- **Implementation**: `/api/jams/{jam_id}/songs/{song_id}/heart` endpoint with session-based tracking

#### UU-002: Vote-Based Song Ordering ✅ **COMPLETED**
**As anybody, I see the order of songs in a jam in the order of most to least voted for**
- **Acceptance Criteria:**
  - ✅ Songs automatically sort by vote count (descending)
  - ✅ Real-time reordering as votes change
  - ✅ Clear visual indication of vote counts
  - ✅ Maintains order during live updates
- **Implementation**: Frontend sorting with rank display and real-time updates

#### UU-003: Today's Jams Display ✅ **COMPLETED**
**As an anonymous user, I can see a list of jams happening today on the home page**
- **Acceptance Criteria:**
  - ✅ "Jams Happening Today" section with current date in dd MMM YYYY format
  - ✅ Sydney timezone support for date display
  - ✅ Clickable jam tiles showing name and location
  - ✅ Filtered to show only jams scheduled for today
  - ✅ "No jams today" message when no jams are scheduled
- **Implementation**: Home page section with date filtering and responsive tile layout

#### UU-004: Ultimate Guitar Integration ✅ **COMPLETED**
**As any user, I can look up chord sheets for songs using Ultimate Guitar**
- **Acceptance Criteria:**
  - ✅ Automatic chord sheet lookup when adding songs
  - ✅ Manual chord sheet lookup for existing songs
  - ✅ Results sorted by rating (highest first)
  - ✅ Click to open chord sheet in new window
  - ✅ Visual indicator when chord sheet is linked
- **Implementation**: Ultimate Guitar API integration with web scraping

### Feature Flags System (Priority 1.5)

#### FF-001: Role-Based Access Control ✅ **COMPLETED**
**As a jam manager, I can control what features are available to different user types**
- **Acceptance Criteria:**
  - ✅ Three user roles: Anonymous, Registered Attendee (Muso), Jam Manager
  - ✅ Feature flags control access to specific functionality
  - ✅ Backend API endpoints protected by role-based decorators
  - ✅ Frontend UI elements show/hide based on user permissions
  - ✅ Easy to add new roles and features in the future
  - ✅ All user types can vote (including jam managers)
- **Implementation**: Complete feature flags system with decorators and frontend integration

#### FF-002: Dynamic Permission Checking ✅ **COMPLETED**
**As a user, I only see features I have permission to use**
- **Acceptance Criteria:**
  - ✅ Anonymous users see only voting and viewing features
  - ✅ Registered attendees see performance registration and song suggestions
  - ✅ Jam managers see all management and jam manager features
  - ✅ Real-time permission updates when user role changes
  - ✅ All user types can vote (universal voting permission)
- **Implementation**: Frontend feature gates with dynamic UI updates

### Jam Manager Stories (Priority 2)

#### JM-002: Enhanced Jam Creation ✅ **COMPLETED**
**As a jam manager, I can create a jam with detailed information and custom background**
- **Acceptance Criteria:**
  - ✅ Create jam with name (required), location, date, and description
  - ✅ Upload background image (PNG, JPG, GIF, WebP) with validation
  - ✅ User-friendly slug generation in format: name-location-date
  - ✅ Background image renders blurred with configurable intensity
  - ✅ Foreground elements are semi-transparent to show background
  - ✅ Default background color when no image is provided
- **Implementation**: Complete enhanced jam creation with image upload and styling

#### JM-003: Venue Management ✅ **COMPLETED**
**As a jam manager, I can manage venues and select from a dropdown when creating jams**
- **Acceptance Criteria:**
  - ✅ Admin page for managing venues
  - ✅ Add, edit, and delete venues
  - ✅ Venue dropdown in jam creation form
  - ✅ Venue selection required for jam creation
  - ✅ Venue information displayed on jam pages
  - ✅ Venue management link on home page for jam managers
- **Status**: Complete venue management system implemented

#### JM-004: Breadcrumb Navigation ✅ **COMPLETED**
**As a jam manager, I can navigate the site using breadcrumb navigation**
- **Acceptance Criteria:**
  - ✅ Breadcrumb navigation shows current page location
  - ✅ Clickable breadcrumbs for easy navigation back to previous levels
  - ✅ Consistent breadcrumb styling across all pages
  - ✅ Home > Jam Manager > [Current Page] hierarchy
  - ✅ Jam details show: Home > Jam Manager > [Jam Name]
  - ✅ Breadcrumbs only visible to jam managers with access code
  - ✅ Breadcrumbs hide/show based on access status
- **Status**: Complete breadcrumb navigation system implemented

#### JM-005: Custom Jam Styling ✅ **COMPLETED**
**As a jam manager, I can customize the visual appearance of jam pages**
- **Acceptance Criteria:**
  - ✅ Background images are automatically blurred (configurable intensity)
  - ✅ Foreground elements have semi-transparent backgrounds
  - ✅ Configurable transparency levels for foreground elements
  - ✅ Backdrop blur effects for modern glass-morphism look
  - ✅ Graceful fallback to default background when no image provided
- **Implementation**: CSS styling with configurable blur and transparency settings

#### JM-001: Access Code Authentication ✅ **COMPLETED**
**As an anonymous user, I can gain jam manager privileges by entering an access code**
- **Acceptance Criteria:**
  - ✅ Lock button visible in top navigation bar
  - ✅ Clicking lock shows access code dialog
  - ✅ Entering correct access code grants jam manager role
  - ✅ Lock button changes to unlocked state
  - ✅ Clicking unlocked lock button logs out and returns to anonymous
  - ✅ Access code is configurable via environment variable
- **Implementation**: Complete access code system with session management

#### JM-002: Jam Creation & Management
**As a jam manager, I can create and manage jam sessions**
- **Acceptance Criteria:**
  - Create new jam with name and description
  - Set jam status (waiting, active, ended)
  - Manage jam settings and permissions
  - Archive or delete jam sessions

#### JM-002: Song Queue Management
**As a jam manager, I can manage the song queue**
- **Acceptance Criteria:**
  - Reorder songs in queue
  - Remove songs from queue
  - Set current playing song
  - Mark songs as played/skipped

#### JM-003: Attendee Management
**As a jam manager, I can view and manage attendees**
- **Acceptance Criteria:**
  - View list of registered attendees
  - See who's registered to perform on each song
  - Manage performer assignments
  - Remove problematic attendees if needed

#### JM-004: Real-time Monitoring
**As a jam manager, I can monitor jam activity in real-time**
- **Acceptance Criteria:**
  - Live vote counts and updates
  - Real-time attendee registrations
  - WebSocket notifications for all activities
  - Dashboard with jam statistics

## Technical Requirements

### Feature Flags System ✅ **COMPLETED**
- **User Roles**: Anonymous, Registered Attendee (Muso), Jam Manager
- **Feature Gates**: Backend and frontend permission checking
- **API Protection**: Decorators for endpoint access control
- **Dynamic UI**: Frontend elements show/hide based on permissions
- **Extensible**: Easy to add new roles and features

### Database Schema Updates ✅ **COMPLETED**
- ✅ **Attendees Table**: Store attendee names and jam associations
- ✅ **Votes Table**: Track individual votes (attendee + song + jam)
- ✅ **Performance Registrations Table**: Track who's registered to perform on songs
- ✅ **Venues Table**: Store venue information (name, address, description)
- ✅ **SQLite Database**: Uses SQLite for zero-configuration setup
- ✅ **String IDs**: Converted from UUID to string-based IDs for better compatibility

### API Endpoints ✅ **COMPLETED**
- ✅ `POST /api/jams/{jam_id}/attendees` - Register attendee
- ✅ `GET /api/jams/{jam_id}/attendees` - List attendees
- ✅ `POST /api/jams/{jam_id}/songs/{song_id}/heart` - Vote (with session tracking)
- ✅ `POST /api/jams/{jam_id}/songs/{song_id}/register` - Register to perform
- ✅ `DELETE /api/jams/{jam_id}/songs/{song_id}/register` - Unregister from performing
- ✅ `GET /api/jams/{jam_id}/songs/{song_id}/performers` - List performers
- ✅ `GET /api/jams/{jam_id}/songs/{song_id}/vote-status` - Check vote status
- ✅ `GET /api/jams/{jam_id}/qr` - Generate QR code
- ✅ `GET /api/venues` - List all venues
- ✅ `POST /api/venues` - Create venue
- ✅ `GET /api/venues/{venue_id}` - Get venue details
- ✅ `PUT /api/venues/{venue_id}` - Update venue
- ✅ `DELETE /api/venues/{venue_id}` - Delete venue
- ✅ `POST /api/jams/{jam_id}/songs` - Add song to jam
- ✅ `GET /api/chord-sheets/search` - Search Ultimate Guitar for chord sheets
- ✅ `PUT /api/jams/{jam_id}/songs/{song_id}/chord-sheet` - Update chord sheet URL

### Frontend Features ✅ **COMPLETED**
- ✅ QR code generation and display
- ✅ Attendee registration modal
- ✅ Song suggestion interface with Ultimate Guitar integration
- ✅ Performance registration buttons
- ✅ Vote tracking and display
- ✅ Real-time updates via WebSocket
- ✅ Mobile-responsive design
- ✅ Chord sheet lookup and linking

## Implementation Priority
1. **Phase 1**: Attendee registration and basic voting
2. **Phase 2**: QR code access and song suggestions
3. **Phase 3**: Performance registration and advanced features
4. **Phase 4**: Jam manager features and analytics

## Status
- ✅ Basic jam creation and management
- ✅ Song library and basic voting
- ✅ WebSocket real-time updates
- ✅ **COMPLETED**: Attendee registration and voting (AT-001 to AT-005)
- ✅ **COMPLETED**: Jam manager features (JM-001 to JM-005)
- ✅ **COMPLETED**: Universal features (UU-001 to UU-004)
- ✅ **COMPLETED**: Feature flags system (FF-001 to FF-002)
- ✅ **COMPLETED**: Database migration to SQLite with string IDs
- ✅ **COMPLETED**: Ultimate Guitar integration

## Progress Summary
**Attendee Features: 5/5 Complete (100%)**
- ✅ QR Code Access
- ✅ Single Vote Per Song  
- ✅ Musician Registration
- ✅ Song Performance Registration
- ✅ Song Suggestions with Ultimate Guitar Integration

**Universal Features: 4/4 Complete (100%)**
- ✅ Universal Heart Voting (all user types)
- ✅ Vote-Based Song Ordering
- ✅ Today's Jams Display
- ✅ Ultimate Guitar Integration

**Feature Flags System: 2/2 Complete (100%)**
- ✅ Role-Based Access Control
- ✅ Dynamic Permission Checking

**Jam Manager Features: 5/5 Complete (100%)**
- ✅ Access Code Authentication
- ✅ Enhanced Jam Creation
- ✅ Custom Jam Styling
- ✅ Venue Management
- ✅ Breadcrumb Navigation

**Technical Infrastructure: 100% Complete**
- ✅ SQLite Database Migration
- ✅ String ID Conversion (UUID → String)
- ✅ WebSocket Real-time Updates
- ✅ Mobile Responsive Design
- ✅ API Documentation
