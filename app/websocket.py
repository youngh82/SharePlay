"""WebSocket connection manager for real-time updates"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json


class ConnectionManager:
    """Manages WebSocket connections for rooms"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_code: str):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = []
        self.active_connections[room_code].append(websocket)
        print(f"Client connected to room {room_code}. Total: {len(self.active_connections[room_code])}")
    
    def disconnect(self, websocket: WebSocket, room_code: str):
        """Remove a WebSocket connection"""
        if room_code in self.active_connections:
            if websocket in self.active_connections[room_code]:
                self.active_connections[room_code].remove(websocket)
                print(f"Client disconnected from room {room_code}. Remaining: {len(self.active_connections[room_code])}")
            
            # Clean up empty room lists
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]
    
    async def broadcast(self, room_code: str, message: dict):
        """
        Broadcast a message to all connections in a room.
        
        Args:
            room_code: Room code to broadcast to
            message: Dictionary message to send
        """
        if room_code not in self.active_connections:
            return
        
        dead_connections = []
        for connection in self.active_connections[room_code]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                dead_connections.append(connection)
        
        # Remove dead connections
        for dead in dead_connections:
            self.disconnect(dead, room_code)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    def get_room_connection_count(self, room_code: str) -> int:
        """Get the number of active connections in a room"""
        return len(self.active_connections.get(room_code, []))


# Global connection manager instance
manager = ConnectionManager()


def get_websocket_manager() -> ConnectionManager:
    """Get the WebSocket manager instance"""
    return manager
