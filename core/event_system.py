"""
Event System for Sprint 3 Architecture Improvements
Provides a centralized event system for real-time updates and decoupled communication.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Represents an event in the system."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    target: Optional[str] = None  # Optional target for directed events

class EventHandler:
    """Handles event subscriptions and notifications."""
    
    def __init__(self):
        self._handlers: Dict[str, Set[Callable]] = {}
        self._middleware: List[Callable] = []
        self._event_history: List[Event] = []
        self._max_history = 1000  # Keep last 1000 events
    
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = set()
        self._handlers[event_type].add(handler)
        logger.debug(f"Subscribed handler to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Unsubscribe from events of a specific type."""
        if event_type in self._handlers:
            self._handlers[event_type].discard(handler)
            if not self._handlers[event_type]:
                del self._handlers[event_type]
            logger.debug(f"Unsubscribed handler from event type: {event_type}")
    
    def add_middleware(self, middleware: Callable[[Event], Event]) -> None:
        """Add middleware to process events before handlers."""
        self._middleware.append(middleware)
        logger.debug("Added event middleware")
    
    async def emit(self, event_type: str, data: Dict[str, Any], source: str = "system", target: Optional[str] = None) -> None:
        """Emit an event to all subscribed handlers."""
        event = Event(
            type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source,
            target=target
        )
        
        # Apply middleware
        for middleware in self._middleware:
            try:
                event = middleware(event)
            except Exception as e:
                logger.error(f"Error in event middleware: {e}")
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Notify handlers
        if event_type in self._handlers:
            handlers = list(self._handlers[event_type])  # Copy to avoid modification during iteration
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
        
        logger.debug(f"Emitted event: {event_type} from {source}")
    
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        """Get recent event history, optionally filtered by type."""
        events = self._event_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        return len(self._handlers.get(event_type, set()))
    
    def get_all_event_types(self) -> List[str]:
        """Get all registered event types."""
        return list(self._handlers.keys())

# Global event handler instance
event_handler = EventHandler()

# Event types for the application
class EventTypes:
    """Constants for event types."""
    
    # Jam events
    JAM_CREATED = "jam.created"
    JAM_UPDATED = "jam.updated"
    JAM_DELETED = "jam.deleted"
    
    # Song events
    SONG_ADDED_TO_JAM = "song.added_to_jam"
    SONG_REMOVED_FROM_JAM = "song.removed_from_jam"
    SONG_PLAYED = "song.played"
    
    # Vote events
    VOTE_ADDED = "vote.added"
    VOTE_REMOVED = "vote.removed"
    
    # Performance events
    PERFORMANCE_REGISTERED = "performance.registered"
    PERFORMANCE_UNREGISTERED = "performance.unregistered"
    
    # Attendee events
    ATTENDEE_REGISTERED = "attendee.registered"
    ATTENDEE_LEFT = "attendee.left"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    ERROR_OCCURRED = "error.occurred"

# Event data builders
class EventDataBuilder:
    """Helper class to build event data."""
    
    @staticmethod
    def jam_event(jam_id: str, jam_name: str, **kwargs) -> Dict[str, Any]:
        """Build jam event data."""
        return {
            "jam_id": jam_id,
            "jam_name": jam_name,
            **kwargs
        }
    
    @staticmethod
    def song_event(song_id: str, song_title: str, jam_id: str, **kwargs) -> Dict[str, Any]:
        """Build song event data."""
        return {
            "song_id": song_id,
            "song_title": song_title,
            "jam_id": jam_id,
            **kwargs
        }
    
    @staticmethod
    def vote_event(song_id: str, jam_id: str, attendee_id: str, **kwargs) -> Dict[str, Any]:
        """Build vote event data."""
        return {
            "song_id": song_id,
            "jam_id": jam_id,
            "attendee_id": attendee_id,
            **kwargs
        }
    
    @staticmethod
    def performance_event(song_id: str, jam_id: str, attendee_id: str, **kwargs) -> Dict[str, Any]:
        """Build performance event data."""
        return {
            "song_id": song_id,
            "jam_id": jam_id,
            "attendee_id": attendee_id,
            **kwargs
        }
    
    @staticmethod
    def attendee_event(attendee_id: str, jam_id: str, **kwargs) -> Dict[str, Any]:
        """Build attendee event data."""
        return {
            "attendee_id": attendee_id,
            "jam_id": jam_id,
            **kwargs
        }

# Event middleware for logging and monitoring
async def logging_middleware(event: Event) -> Event:
    """Middleware to log all events."""
    logger.info(f"Event: {event.type} from {event.source} at {event.timestamp}")
    return event

async def monitoring_middleware(event: Event) -> Event:
    """Middleware to collect metrics."""
    # This could integrate with monitoring systems like Prometheus
    # For now, just log metrics
    logger.debug(f"Event metrics: {event.type} - {len(event.data)} data fields")
    return event

# Initialize middleware
event_handler.add_middleware(logging_middleware)
event_handler.add_middleware(monitoring_middleware)
