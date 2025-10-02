from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# SQLAlchemy Models
class Song(Base):
    __tablename__ = "songs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, default="rock")
    chord_chart = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True, default=list)  # Store as JSON array
    vote_count = Column(Integer, default=0)
    times_played = Column(Integer, default=0)
    last_played = Column(DateTime, nullable=True)
    play_history = Column(JSONB, nullable=True, default=list)  # Store as JSON array
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Jam(Base):
    __tablename__ = "jams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False)
    jam_date = Column(Date, nullable=False)
    background_image = Column(String(500), nullable=True)  # Path to uploaded image
    current_song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=True)
    status = Column(String(50), default="waiting")  # waiting, playing, paused, ended
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    venue = relationship("Venue", back_populates="jams")
    current_song = relationship("Song", foreign_keys=[current_song_id])
    jam_songs = relationship("JamSong", back_populates="jam", cascade="all, delete-orphan")

class JamSong(Base):
    __tablename__ = "jam_songs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jam_id = Column(UUID(as_uuid=True), ForeignKey("jams.id"), nullable=False)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False)
    captains = Column(JSONB, nullable=True, default=list)  # Store captain IDs as JSON array
    played = Column(Boolean, default=False)
    played_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    jam = relationship("Jam", back_populates="jam_songs")
    song = relationship("Song")

class Attendee(Base):
    __tablename__ = "attendees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jam_id = Column(UUID(as_uuid=True), ForeignKey("jams.id"), nullable=False)
    name = Column(String(255), nullable=False)
    session_id = Column(String(255), nullable=True)  # For tracking browser sessions
    registered_at = Column(DateTime, default=func.now())
    
    # Relationships
    jam = relationship("Jam")
    
    # Unique constraint on jam_id + name
    __table_args__ = (
        UniqueConstraint('jam_id', 'name', name='unique_attendee_name_per_jam'),
        {'extend_existing': True}
    )

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jam_id = Column(UUID(as_uuid=True), ForeignKey("jams.id"), nullable=False)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False)
    attendee_id = Column(UUID(as_uuid=True), ForeignKey("attendees.id"), nullable=True)
    session_id = Column(String(255), nullable=True)  # For anonymous voting
    voted_at = Column(DateTime, default=func.now())
    
    # Relationships
    jam = relationship("Jam")
    song = relationship("Song")
    attendee = relationship("Attendee")
    
    # Unique constraint on jam_id + song_id + attendee_id (one vote per attendee per song)
    # and jam_id + song_id + session_id (one vote per session per song)
    __table_args__ = (
        {'extend_existing': True}
    )

class PerformanceRegistration(Base):
    __tablename__ = "performance_registrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jam_id = Column(UUID(as_uuid=True), ForeignKey("jams.id"), nullable=False)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False)
    attendee_id = Column(UUID(as_uuid=True), ForeignKey("attendees.id"), nullable=False)
    instrument = Column(String(100), nullable=True)  # Optional instrument specification
    registered_at = Column(DateTime, default=func.now())
    
    # Relationships
    jam = relationship("Jam")
    song = relationship("Song")
    attendee = relationship("Attendee")
    
    # Unique constraint on jam_id + song_id + attendee_id (one registration per attendee per song)
    __table_args__ = (
        {'extend_existing': True}
    )

class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    address = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    jams = relationship("Jam", back_populates="venue")

# Pydantic Models for API
class SongBase(BaseModel):
    title: str
    artist: str
    type: str = "rock"
    chord_chart: Optional[str] = None
    tags: Optional[List[str]] = []
    vote_count: Optional[int] = 0
    times_played: Optional[int] = 0
    last_played: Optional[datetime] = None
    play_history: Optional[List[Dict[str, Any]]] = []

class SongCreate(SongBase):
    pass

class SongUpdate(SongBase):
    title: Optional[str] = None
    artist: Optional[str] = None
    type: Optional[str] = None

class SongInDB(SongBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JamSongBase(BaseModel):
    captains: Optional[List[str]] = []
    played: Optional[bool] = False
    played_at: Optional[datetime] = None

class JamSongCreate(JamSongBase):
    song_id: uuid.UUID

class JamSongUpdate(JamSongBase):
    pass

class JamSongInDB(JamSongBase):
    id: uuid.UUID
    jam_id: uuid.UUID
    song_id: uuid.UUID
    song: SongInDB
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JamBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    venue_id: uuid.UUID  # Made mandatory
    jam_date: datetime  # Made mandatory
    background_image: Optional[str] = None
    current_song_id: Optional[uuid.UUID] = None
    status: Optional[str] = "waiting"

class JamCreate(JamBase):
    pass

class JamUpdate(JamBase):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    current_song_id: Optional[uuid.UUID] = None
    status: Optional[str] = None

class JamInDB(JamBase):
    id: uuid.UUID
    songs: Optional[List[JamSongInDB]] = []
    current_song: Optional[SongInDB] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Venue Pydantic Models
class VenueBase(BaseModel):
    name: str
    address: Optional[str] = None
    description: Optional[str] = None

class VenueCreate(VenueBase):
    pass

class VenueUpdate(VenueBase):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None

class VenueInDB(VenueBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Recreate JamInDB with venue field after VenueInDB is defined
class JamInDBWithVenue(JamBase):
    id: uuid.UUID
    venue: Optional[VenueInDB] = None
    songs: Optional[List[JamSongInDB]] = []
    current_song: Optional[SongInDB] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True