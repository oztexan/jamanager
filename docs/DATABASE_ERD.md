# JaManager Database Entity Relationship Diagram

## Overview

This document contains the complete Entity Relationship Diagram (ERD) for the JaManager database schema, showing all tables, relationships, and constraints.

## ERD Diagram

```mermaid
erDiagram
    VENUES {
        string id PK
        string name UK
        string address
        text description
        datetime created_at
        datetime updated_at
    }
    
    JAMS {
        string id PK
        string name
        string slug UK
        text description
        string venue_id FK
        date jam_date
        string background_image
        string current_song_id FK
        string status
        datetime created_at
        datetime updated_at
    }
    
    SONGS {
        string id PK
        string title
        string artist
        string chord_sheet_url
        boolean chord_sheet_is_valid
        datetime chord_sheet_validated_at
        integer times_played
        datetime last_played
        json play_history
        datetime created_at
        datetime updated_at
    }
    
    JAM_SONGS {
        string id PK
        string jam_id FK
        string song_id FK
        json captains
        boolean played
        datetime played_at
        datetime created_at
        datetime updated_at
    }
    
    ATTENDEES {
        string id PK
        string jam_id FK
        string name
        string session_id
        datetime registered_at
    }
    
    VOTES {
        string id PK
        string jam_id FK
        string song_id FK
        string attendee_id FK
        string session_id
        datetime voted_at
    }
    
    PERFORMANCE_REGISTRATIONS {
        string id PK
        string jam_id FK
        string song_id FK
        string attendee_id FK
        string instrument
        datetime registered_at
    }
    
    JAM_CHORD_SHEETS {
        string id PK
        string jam_id FK
        string song_id FK
        string chord_sheet_url
        boolean chord_sheet_is_valid
        datetime chord_sheet_validated_at
        string title
        string rating
        string created_by FK
        datetime created_at
        datetime updated_at
    }
    
    %% Relationships
    VENUES ||--o{ JAMS : "hosts"
    JAMS ||--o{ JAM_SONGS : "contains"
    SONGS ||--o{ JAM_SONGS : "included_in"
    SONGS ||--o| JAMS : "current_song"
    JAMS ||--o{ ATTENDEES : "has"
    JAMS ||--o{ VOTES : "receives"
    SONGS ||--o{ VOTES : "receives"
    ATTENDEES ||--o{ VOTES : "casts"
    JAMS ||--o{ PERFORMANCE_REGISTRATIONS : "has"
    SONGS ||--o{ PERFORMANCE_REGISTRATIONS : "has"
    ATTENDEES ||--o{ PERFORMANCE_REGISTRATIONS : "registers"
    JAMS ||--o{ JAM_CHORD_SHEETS : "has"
    SONGS ||--o{ JAM_CHORD_SHEETS : "has"
    ATTENDEES ||--o{ JAM_CHORD_SHEETS : "creates"
```

## Table Summary

| Table | Purpose | Key Features |
|-------|---------|--------------|
| **VENUES** | Venue information | Unique names, address/description |
| **JAMS** | Jam session management | Unique slugs, venue links, status tracking |
| **SONGS** | Master song library | Chord sheet URLs, play statistics |
| **JAM_SONGS** | Jam-song relationships | Junction table, play status |
| **ATTENDEES** | User registration | Session tracking, unique names per jam |
| **VOTES** | Voting system | Anonymous + registered voting |
| **PERFORMANCE_REGISTRATIONS** | Performance tracking | Instrument specification |
| **JAM_CHORD_SHEETS** | Chord sheet overrides | Jam-specific chord sheets |

## Key Relationships

### Core Relationships
- **Venues** host multiple **Jams**
- **Jams** contain multiple **Songs** (via JAM_SONGS)
- **Jams** have multiple **Attendees**
- **Attendees** can vote on **Songs** in **Jams**
- **Attendees** can register to perform on **Songs**

### Chord Sheet System
- **Songs** have default chord sheet URLs
- **JAM_CHORD_SHEETS** allows jam-specific chord sheet overrides
- **Attendees** can create chord sheet entries
- Validation status tracked for both default and jam-specific chord sheets

### Voting System
- Supports both anonymous (session-based) and registered (attendee-based) voting
- One vote per user per song per jam
- Real-time vote updates via WebSocket

## Constraints

### Unique Constraints
- `venues.name` - Unique venue names
- `jams.slug` - Unique jam slugs for URLs
- `attendees(jam_id, name)` - Unique attendee names per jam
- `jam_chord_sheets(jam_id, song_id)` - One chord sheet per song per jam

### Foreign Key Relationships
- All foreign keys maintain referential integrity
- Cascade deletes configured for dependent relationships
- Nullable foreign keys where appropriate (anonymous voting, optional current song)

## Data Types

- **IDs**: String (32-character hex tokens)
- **Timestamps**: DateTime with automatic creation/update
- **JSON Fields**: Used for flexible data (captains, play_history)
- **Boolean Fields**: For flags and validation status
- **Text Fields**: For longer descriptions and content

## Indexing Strategy

- Primary keys automatically indexed
- Unique constraints create indexes
- Foreign keys should be indexed for performance
- Consider composite indexes for common query patterns:
  - `(jam_id, song_id)` for votes and performance registrations
  - `(jam_id, attendee_id)` for attendee-specific queries
  - `(song_id, jam_id)` for song-specific queries

---

*This ERD represents the current database schema as of October 2025. For implementation details, see [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md).*
