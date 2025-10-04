"""
WebSocket endpoints for real-time communication in the Jamanager application.
"""
import json
import logging
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from core.database import get_database
from core.feature_flag_config import set_global_feature_flag, set_user_feature_flag, set_jam_feature_flag, set_role_feature_flag
from core.feature_flags import UserRole
from models.database import Song, Jam, JamSong, Attendee, Vote, PerformanceRegistration

logger = logging.getLogger(__name__)

router = APIRouter()

# Connection manager will be imported from the main app
connection_manager = None

def set_connection_manager(cm):
    """Set the connection manager instance"""
    global connection_manager
    connection_manager = cm

@router.websocket("/ws/{jam_id}")
async def websocket_endpoint(websocket: WebSocket, jam_id: str):
    if not connection_manager:
        logger.error("Connection manager not initialized")
        return
        
    await connection_manager.connect(websocket, jam_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "register_attendee":
                attendee_name = message.get("attendee_name")
                session_id = message.get("session_id")
                if attendee_name and session_id:
                    async with get_database() as db:
                        # Check if attendee already exists for this jam and session
                        existing_attendee = await db.execute(
                            select(Attendee).where(
                                (Attendee.jam_id == jam_id) & 
                                (Attendee.session_id == session_id)
                            )
                        )
                        existing_attendee = existing_attendee.scalars().first()

                        if existing_attendee:
                            # Update existing attendee's name if it changed
                            if existing_attendee.name != attendee_name:
                                existing_attendee.name = attendee_name
                                existing_attendee.updated_at = func.now()
                                await db.commit()
                                await db.refresh(existing_attendee)
                                logger.info(f"Updated attendee {attendee_name} in jam {jam_id}")
                            attendee = existing_attendee
                        else:
                            # Create new attendee
                            attendee = Attendee(
                                id=str(uuid.uuid4()),
                                jam_id=jam_id,
                                name=attendee_name,
                                session_id=session_id,
                                registered_at=func.now()
                            )
                            db.add(attendee)
                            await db.commit()
                            await db.refresh(attendee)
                            logger.info(f"Registered new attendee {attendee_name} in jam {jam_id}")
                        
                        # Send updated attendee list to all connected clients
                        await connection_manager.broadcast(jam_id, {"type": "attendee_update", "attendee": attendee.dict()})
                        await connection_manager.send_personal_message({"type": "registration_success", "attendee_id": attendee.id}, websocket)
                else:
                    await connection_manager.send_personal_message({"type": "error", "message": "Attendee name and session ID are required."}, websocket)

            elif message_type == "vote_song":
                song_id = message.get("song_id")
                attendee_id = message.get("attendee_id")
                session_id = message.get("session_id")
                if song_id and (attendee_id or session_id):
                    async with get_database() as db:
                        # Check if the song exists
                        song_result = await db.execute(select(Song).where(Song.id == song_id))
                        song = song_result.scalars().first()
                        if not song:
                            await connection_manager.send_personal_message({"type": "error", "message": "Song not found."}, websocket)
                            continue

                        # Check if attendee exists or create a dummy one for session_id if needed
                        attendee = None
                        if attendee_id:
                            attendee_result = await db.execute(select(Attendee).where(Attendee.id == attendee_id))
                            attendee = attendee_result.scalars().first()
                        elif session_id:
                            attendee_result = await db.execute(select(Attendee).where(Attendee.session_id == session_id))
                            attendee = attendee_result.scalars().first()
                            # If no attendee found for session_id, create a temporary one for voting purposes
                            if not attendee:
                                attendee = Attendee(
                                    id=str(uuid.uuid4()),
                                    jam_id=jam_id,
                                    name=f"Guest-{session_id[:4]}", # Simple guest name
                                    session_id=session_id,
                                    registered_at=func.now()
                                )
                                db.add(attendee)
                                await db.commit()
                                await db.refresh(attendee)
                                logger.info(f"Created temporary attendee {attendee.name} for voting in jam {jam_id}")

                        if not attendee:
                            await connection_manager.send_personal_message({"type": "error", "message": "Attendee not found or could not be created."}, websocket)
                            continue

                        # Check if the attendee/session has already voted for this song in this jam
                        existing_vote_query = select(Vote).where(
                            (Vote.jam_id == jam_id) &
                            (Vote.song_id == song_id) &
                            (
                                (Vote.attendee_id == attendee.id) |
                                (Vote.session_id == session_id)
                            )
                        )
                        existing_vote = await db.execute(existing_vote_query)
                        existing_vote = existing_vote.scalars().first()

                        if existing_vote:
                            await connection_manager.send_personal_message({"type": "error", "message": "You have already voted for this song."}, websocket)
                            continue

                        # Create new vote
                        vote = Vote(
                            id=str(uuid.uuid4()),
                            jam_id=jam_id,
                            song_id=song_id,
                            attendee_id=attendee.id,
                            session_id=session_id,
                            voted_at=func.now()
                        )
                        db.add(vote)
                        
                        # Increment vote count for the song in the JamSong table
                        # Find the JamSong entry
                        jam_song_query = select(JamSong).where(
                            (JamSong.jam_id == jam_id) & (JamSong.song_id == song_id)
                        )
                        jam_song_result = await db.execute(jam_song_query)
                        jam_song = jam_song_result.scalars().first()

                        if not jam_song:
                            # If JamSong entry doesn't exist, create it
                            new_jam_song = JamSong(
                                id=str(uuid.uuid4()),
                                jam_id=jam_id,
                                song_id=song_id,
                                created_at=func.now(),
                                updated_at=func.now()
                            )
                            db.add(new_jam_song)
                            await db.commit()
                            await db.refresh(new_jam_song)
                            logger.info(f"Created new JamSong entry for song {song_id} in jam {jam_id} with vote count 1.")

                        await db.commit()
                        await db.refresh(vote)
                        
                        # Broadcast updated song list with new vote counts
                        updated_songs = await get_songs_for_jam(jam_id, db)
                        await connection_manager.broadcast(jam_id, {"type": "song_list_update", "songs": [s.dict() for s in updated_songs]})
                        await connection_manager.send_personal_message({"type": "vote_success", "song_id": song_id}, websocket)
                else:
                    await connection_manager.send_personal_message({"type": "error", "message": "Song ID and attendee ID/session ID are required."}, websocket)

            elif message_type == "suggest_song":
                title = message.get("title")
                artist = message.get("artist")
                if title and artist:
                    async with get_database() as db:
                        # Check if song already exists
                        existing_song_query = select(Song).where(
                            (func.lower(Song.title) == func.lower(title)) &
                            (func.lower(Song.artist) == func.lower(artist))
                        )
                        existing_song_result = await db.execute(existing_song_query)
                        existing_song = existing_song_result.scalars().first()

                        if existing_song:
                            song = existing_song
                            logger.info(f"Song '{title}' by '{artist}' already exists. Using existing song.")
                        else:
                            # Create new song
                            song = Song(
                                id=str(uuid.uuid4()),
                                title=title,
                                artist=artist,
                                times_played=0,
                                created_at=func.now(),
                                updated_at=func.now()
                            )
                            db.add(song)
                            await db.commit()
                            await db.refresh(song)
                            logger.info(f"Suggested new song: {title} by {artist}")

                        # Add song to jam_songs if not already present
                        jam_song_query = select(JamSong).where(
                            (JamSong.jam_id == jam_id) & (JamSong.song_id == song.id)
                        )
                        jam_song_result = await db.execute(jam_song_query)
                        jam_song = jam_song_result.scalars().first()

                        if not jam_song:
                            new_jam_song = JamSong(
                                id=str(uuid.uuid4()),
                                jam_id=jam_id,
                                song_id=song.id,
                                created_at=func.now(),
                                updated_at=func.now()
                            )
                            db.add(new_jam_song)
                            await db.commit()
                            await db.refresh(new_jam_song)
                            logger.info(f"Added suggested song '{title}' to jam {jam_id}'s song list.")
                        
                        # Broadcast updated song list
                        updated_songs = await get_songs_for_jam(jam_id, db)
                        await connection_manager.broadcast(jam_id, {"type": "song_list_update", "songs": [s.dict() for s in updated_songs]})
                        await connection_manager.send_personal_message({"type": "suggestion_success", "song": song.dict()}, websocket)
                else:
                    await connection_manager.send_personal_message({"type": "error", "message": "Song title and artist are required."}, websocket)

            elif message_type == "register_to_perform":
                song_id = message.get("song_id")
                attendee_id = message.get("attendee_id")
                instrument = message.get("instrument")
                if song_id and attendee_id and instrument:
                    async with get_database() as db:
                        # Check if already registered for this song
                        existing_registration_query = select(PerformanceRegistration).where(
                            (PerformanceRegistration.jam_id == jam_id) &
                            (PerformanceRegistration.song_id == song_id) &
                            (PerformanceRegistration.attendee_id == attendee_id)
                        )
                        existing_registration = await db.execute(existing_registration_query)
                        if existing_registration.scalars().first():
                            await connection_manager.send_personal_message({"type": "error", "message": "You are already registered to perform this song."}, websocket)
                            continue

                        registration = PerformanceRegistration(
                            id=str(uuid.uuid4()),
                            jam_id=jam_id,
                            song_id=song_id,
                            attendee_id=attendee_id,
                            instrument=instrument,
                            registered_at=func.now()
                        )
                        db.add(registration)
                        await db.commit()
                        await db.refresh(registration)
                        logger.info(f"Attendee {attendee_id} registered to perform song {song_id} with {instrument} in jam {jam_id}")
                        
                        # Broadcast updated performers list for the song
                        performers = await get_performers_for_song(jam_id, song_id, db)
                        await connection_manager.broadcast(jam_id, {"type": "performers_update", "song_id": song_id, "performers": [p.dict() for p in performers]})
                        await connection_manager.send_personal_message({"type": "registration_success", "song_id": song_id}, websocket)
                else:
                    await connection_manager.send_personal_message({"type": "error", "message": "Song ID, attendee ID, and instrument are required."}, websocket)

            elif message_type == "play_song":
                song_id = message.get("song_id")
                if song_id:
                    async with get_database() as db:
                        # Update current_song_id for the jam
                        await db.execute(
                            update(Jam).where(Jam.id == jam_id).values(current_song_id=song_id, updated_at=func.now())
                        )
                        # Update times_played and last_played for the song
                        song_update_stmt = (
                            update(Song)
                            .where(Song.id == song_id)
                            .values(
                                times_played=Song.times_played + 1,
                                last_played=func.now(),
                                updated_at=func.now()
                            )
                        )
                        await db.execute(song_update_stmt)

                        # Update played status and played_at for the jam_song entry
                        jam_song_update_stmt = (
                            update(JamSong)
                            .where((JamSong.jam_id == jam_id) & (JamSong.song_id == song_id))
                            .values(played=True, played_at=func.now(), updated_at=func.now())
                        )
                        await db.execute(jam_song_update_stmt)

                        await db.commit()
                        
                        # Fetch updated jam and song details
                        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
                        updated_jam = jam_result.scalars().first()
                        song_result = await db.execute(select(Song).where(Song.id == song_id))
                        played_song = song_result.scalars().first()

                        if updated_jam and played_song:
                            await connection_manager.broadcast(jam_id, {"type": "song_played", "current_song": played_song.dict(), "jam_status": updated_jam.status})
                            await connection_manager.send_personal_message({"type": "play_success", "song_id": song_id}, websocket)
                        else:
                            await connection_manager.send_personal_message({"type": "error", "message": "Failed to update jam or song status."}, websocket)
                else:
                    await connection_manager.send_personal_message({"type": "error", "message": "Song ID is required."}, websocket)

            elif message_type == "update_feature_flag":
                feature_name = message.get("feature_name")
                scope = message.get("scope")
                scope_id = message.get("scope_id")
                value = message.get("value")
                if feature_name and scope and value is not None:
                    async with get_database() as db:
                        try:
                            if scope == "global":
                                await set_global_feature_flag(db, feature_name, value)
                            elif scope == "user" and scope_id:
                                await set_user_feature_flag(db, scope_id, feature_name, value)
                            elif scope == "jam" and scope_id:
                                await set_jam_feature_flag(db, scope_id, feature_name, value)
                            elif scope == "role" and scope_id:
                                await set_role_feature_flag(db, UserRole[scope_id.upper()], feature_name, value)
                            else:
                                raise ValueError("Invalid scope or missing scope_id for non-global scope.")
                            
                            await connection_manager.broadcast(jam_id, {"type": "feature_flag_updated", "feature_name": feature_name, "scope": scope, "scope_id": scope_id, "value": value})
                            await connection_manager.send_personal_message({"type": "feature_flag_update_success", "feature_name": feature_name}, websocket)
                        except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
                            logger.error(f"Error updating feature flag: {e}")
                            await connection_manager.send_personal_message({"type": "error", "message": f"Failed to update feature flag: {e}"}, websocket)
                else:
                    await connection_manager.send_personal_message({"type": "error", "message": "Feature name, scope, and value are required."}, websocket)

            else:
                await connection_manager.send_personal_message({"type": "error", "message": "Unknown message type."}, websocket)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, jam_id)
        logger.info(f"Client disconnected from jam {jam_id}")
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"WebSocket error in jam {jam_id}: {e}")
        await connection_manager.send_personal_message({"type": "error", "message": f"An unexpected error occurred: {e}"}, websocket)

async def get_songs_for_jam(jam_id: str, db: AsyncSession):
    """Helper to fetch songs for a given jam, ordered by vote count."""
    result = await db.execute(
        select(Song)
        .join(JamSong, Song.id == JamSong.song_id)
        .where(JamSong.jam_id == jam_id)
        .order_by(JamSong.created_at)
    )
    songs = result.scalars().all()
    return [SongInDB.from_orm(song) for song in songs]

async def get_performers_for_song(jam_id: str, song_id: str, db: AsyncSession):
    """Helper to fetch performers for a specific song in a jam."""
    result = await db.execute(
        select(Attendee)
        .join(PerformanceRegistration, Attendee.id == PerformanceRegistration.attendee_id)
        .where(
            (PerformanceRegistration.jam_id == jam_id) &
            (PerformanceRegistration.song_id == song_id)
        )
        .order_by(PerformanceRegistration.registered_at)
    )
    performers = result.scalars().all()
    return [Attendee.from_orm(p) for p in performers]
