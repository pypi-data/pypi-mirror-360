"""
WebSocket connection management.
"""
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from essencia.models import User


@dataclass
class Connection:
    """WebSocket connection info."""
    id: str
    websocket: WebSocket
    user_id: Optional[str]
    user_role: Optional[str]
    client_info: Dict[str, Any]
    connected_at: datetime
    rooms: Set[str]
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid4())
        if not self.rooms:
            self.rooms = set()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        # Active connections by connection ID
        self.connections: Dict[str, Connection] = {}
        
        # Room memberships (room -> set of connection IDs)
        self.rooms: Dict[str, Set[str]] = {}
        
        # User connections (user_id -> set of connection IDs)
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Connection stats
        self.stats = {
            "total_connections": 0,
            "messages_sent": 0,
            "messages_received": 0
        }
    
    async def connect(
        self,
        websocket: WebSocket,
        user: Optional[User] = None,
        client_info: Optional[Dict[str, Any]] = None
    ) -> Connection:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        # Create connection
        connection = Connection(
            id=str(uuid4()),
            websocket=websocket,
            user_id=str(user.id) if user else None,
            user_role=user.role if user else None,
            client_info=client_info or {},
            connected_at=datetime.now(),
            rooms=set()
        )
        
        # Store connection
        self.connections[connection.id] = connection
        
        # Track user connection
        if connection.user_id:
            if connection.user_id not in self.user_connections:
                self.user_connections[connection.user_id] = set()
            self.user_connections[connection.user_id].add(connection.id)
            
            # Auto-join user's personal room
            await self.join_room(connection.id, f"user:{connection.user_id}")
        
        # Update stats
        self.stats["total_connections"] += 1
        
        # Send welcome message
        await self.send_to_connection(connection.id, {
            "type": "welcome",
            "connection_id": connection.id,
            "timestamp": datetime.now().isoformat()
        })
        
        return connection
    
    async def disconnect(self, connection_id: str):
        """Disconnect and cleanup a connection."""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Leave all rooms
        for room in list(connection.rooms):
            await self.leave_room(connection_id, room)
        
        # Remove from user connections
        if connection.user_id and connection.user_id in self.user_connections:
            self.user_connections[connection.user_id].discard(connection_id)
            if not self.user_connections[connection.user_id]:
                del self.user_connections[connection.user_id]
        
        # Remove connection
        del self.connections[connection_id]
        
        # Close WebSocket
        try:
            await connection.websocket.close()
        except:
            pass
    
    async def join_room(self, connection_id: str, room: str):
        """Join a connection to a room."""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        
        # Add to room
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(connection_id)
        
        # Update connection
        connection.rooms.add(room)
        
        # Notify room members
        await self.send_to_room(room, {
            "type": "user_joined",
            "room": room,
            "user_id": connection.user_id,
            "timestamp": datetime.now().isoformat()
        }, exclude=[connection_id])
        
        return True
    
    async def leave_room(self, connection_id: str, room: str):
        """Remove a connection from a room."""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        
        # Remove from room
        if room in self.rooms:
            self.rooms[room].discard(connection_id)
            if not self.rooms[room]:
                del self.rooms[room]
        
        # Update connection
        connection.rooms.discard(room)
        
        # Notify room members
        await self.send_to_room(room, {
            "type": "user_left",
            "room": room,
            "user_id": connection.user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to a specific connection."""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        
        try:
            await connection.websocket.send_json(message)
            self.stats["messages_sent"] += 1
            return True
        except:
            # Connection is broken, disconnect it
            await self.disconnect(connection_id)
            return False
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections of a user."""
        if user_id not in self.user_connections:
            return 0
        
        sent_count = 0
        for connection_id in list(self.user_connections[user_id]):
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def send_to_room(
        self,
        room: str,
        message: Dict[str, Any],
        exclude: Optional[List[str]] = None
    ):
        """Send message to all connections in a room."""
        if room not in self.rooms:
            return 0
        
        exclude = exclude or []
        sent_count = 0
        
        for connection_id in list(self.rooms[room]):
            if connection_id not in exclude:
                if await self.send_to_connection(connection_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def broadcast(
        self,
        message: Dict[str, Any],
        role: Optional[str] = None,
        exclude: Optional[List[str]] = None
    ):
        """Broadcast message to all connections or specific role."""
        exclude = exclude or []
        sent_count = 0
        
        for connection_id, connection in list(self.connections.items()):
            if connection_id in exclude:
                continue
            
            if role and connection.user_role != role:
                continue
            
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def handle_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle incoming message from a connection."""
        self.stats["messages_received"] += 1
        
        # Basic message handling
        message_type = message.get("type")
        
        if message_type == "ping":
            await self.send_to_connection(connection_id, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
        
        elif message_type == "join":
            room = message.get("room")
            if room:
                await self.join_room(connection_id, room)
        
        elif message_type == "leave":
            room = message.get("room")
            if room:
                await self.leave_room(connection_id, room)
        
        # Other message types handled by specific handlers
        return message
    
    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get connection by ID."""
        return self.connections.get(connection_id)
    
    def get_user_connections(self, user_id: str) -> List[Connection]:
        """Get all connections for a user."""
        if user_id not in self.user_connections:
            return []
        
        return [
            self.connections[conn_id]
            for conn_id in self.user_connections[user_id]
            if conn_id in self.connections
        ]
    
    def get_room_connections(self, room: str) -> List[Connection]:
        """Get all connections in a room."""
        if room not in self.rooms:
            return []
        
        return [
            self.connections[conn_id]
            for conn_id in self.rooms[room]
            if conn_id in self.connections
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            **self.stats,
            "active_connections": len(self.connections),
            "active_rooms": len(self.rooms),
            "active_users": len(self.user_connections)
        }


class WebSocketManager:
    """High-level WebSocket manager with handlers."""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.handlers: Dict[str, Any] = {}
        self.middleware: List[Any] = []
    
    def add_handler(self, message_type: str, handler: Any):
        """Register a message handler."""
        self.handlers[message_type] = handler
    
    def add_middleware(self, middleware: Any):
        """Add middleware for message processing."""
        self.middleware.append(middleware)
    
    async def handle_connection(
        self,
        websocket: WebSocket,
        user: Optional[User] = None,
        client_info: Optional[Dict[str, Any]] = None
    ):
        """Handle a WebSocket connection lifecycle."""
        # Connect
        connection = await self.connection_manager.connect(
            websocket, user, client_info
        )
        
        try:
            # Message loop
            while True:
                # Receive message
                try:
                    data = await websocket.receive_json()
                except json.JSONDecodeError:
                    await self.connection_manager.send_to_connection(
                        connection.id,
                        {
                            "type": "error",
                            "error": "Invalid JSON"
                        }
                    )
                    continue
                
                # Apply middleware
                for mw in self.middleware:
                    data = await mw.process_incoming(connection, data)
                    if data is None:
                        break
                
                if data is None:
                    continue
                
                # Handle message
                await self.handle_message(connection, data)
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            # Disconnect
            await self.connection_manager.disconnect(connection.id)
    
    async def handle_message(self, connection: Connection, message: Dict[str, Any]):
        """Route message to appropriate handler."""
        message_type = message.get("type")
        
        # Let connection manager handle basic messages
        message = await self.connection_manager.handle_message(
            connection.id, message
        )
        
        # Route to specific handler
        if message_type in self.handlers:
            handler = self.handlers[message_type]
            try:
                response = await handler.handle(connection, message)
                
                # Send response if any
                if response:
                    await self.connection_manager.send_to_connection(
                        connection.id, response
                    )
                    
            except Exception as e:
                await self.connection_manager.send_to_connection(
                    connection.id,
                    {
                        "type": "error",
                        "error": str(e),
                        "request_id": message.get("id")
                    }
                )
    
    async def send_notification(
        self,
        user_id: str,
        notification: Dict[str, Any]
    ):
        """Send notification to a user."""
        message = {
            "type": "notification",
            "notification": notification,
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.connection_manager.send_to_user(user_id, message)
    
    async def broadcast_update(
        self,
        update_type: str,
        data: Dict[str, Any],
        room: Optional[str] = None,
        role: Optional[str] = None
    ):
        """Broadcast an update."""
        message = {
            "type": "update",
            "update_type": update_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        if room:
            return await self.connection_manager.send_to_room(room, message)
        else:
            return await self.connection_manager.broadcast(message, role=role)


# Global instance
websocket_manager = WebSocketManager()