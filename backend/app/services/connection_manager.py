from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Simple WebSocket connection manager"""
    
    def __init__(self):
        # Dictionary to store connections by jam_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, jam_id: str):
        """Accept a WebSocket connection and add it to the jam room"""
        await websocket.accept()
        
        if jam_id not in self.active_connections:
            self.active_connections[jam_id] = []
        
        self.active_connections[jam_id].append(websocket)
        
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        logger.info(f"🔌 Client connected to jam: {jam_id}")
        logger.info(f"📊 Total connections: {total_connections}")
    
    def disconnect(self, websocket: WebSocket, jam_id: str):
        """Remove a WebSocket connection from the jam room"""
        if jam_id in self.active_connections:
            if websocket in self.active_connections[jam_id]:
                self.active_connections[jam_id].remove(websocket)
                
                # Clean up empty jam rooms
                if not self.active_connections[jam_id]:
                    del self.active_connections[jam_id]
        
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        logger.info(f"🔌 Client disconnected from jam: {jam_id}")
        logger.info(f"📊 Total connections: {total_connections}")
    
    async def broadcast_to_jam(self, jam_id: str, event: str, data: dict):
        """Broadcast a message to all connections in a specific jam"""
        if jam_id not in self.active_connections:
            logger.info(f"📡 No connections for jam: {jam_id}")
            return
        
        connections = self.active_connections[jam_id]
        if not connections:
            logger.info(f"📡 No connections for jam: {jam_id}")
            return
        
        message = json.dumps({
            "event": event,
            "data": data
        })
        
        logger.info(f"📡 Broadcasting {event} to {len(connections)} clients in jam {jam_id}")
        
        # Send to all connections, removing dead ones
        dead_connections = []
        for websocket in connections:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"❌ Error broadcasting to client: {e}")
                dead_connections.append(websocket)
        
        # Clean up dead connections
        for websocket in dead_connections:
            self.disconnect(websocket, jam_id)


