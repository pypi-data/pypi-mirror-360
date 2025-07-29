"""
WebSocket support for real-time features.
"""

import json
import logging
from typing import Dict, Set, List, Optional, Any, Callable
from datetime import datetime
import asyncio

from fastapi import WebSocket, WebSocketDisconnect, status
from fastapi.websockets import WebSocketState

from ..security.auth import AuthService


logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for a specific channel/room.
    """
    
    def __init__(self, channel: str):
        self.channel = channel
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(
        self,
        websocket: WebSocket,
        user_id: Optional[str] = None
    ) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: Optional user identifier
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
            
        logger.info(f"WebSocket connected to channel {self.channel}: {user_id or 'anonymous'}")
        
    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None) -> None:
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
            user_id: Optional user identifier
        """
        self.active_connections.discard(websocket)
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                
        logger.info(f"WebSocket disconnected from channel {self.channel}: {user_id or 'anonymous'}")
        
    async def send_personal_message(
        self,
        message: Any,
        websocket: WebSocket
    ) -> None:
        """
        Send message to specific WebSocket connection.
        
        Args:
            message: Message to send (will be JSON encoded)
            websocket: Target WebSocket connection
        """
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                if isinstance(message, dict):
                    await websocket.send_json(message)
                else:
                    await websocket.send_text(str(message))
            except Exception as e:
                logger.error(f"Error sending personal message: {e}")
                
    async def send_user_message(
        self,
        message: Any,
        user_id: str
    ) -> None:
        """
        Send message to all connections of a specific user.
        
        Args:
            message: Message to send
            user_id: Target user ID
        """
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    await self.send_personal_message(message, connection)
                except Exception:
                    disconnected.append(connection)
                    
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)
                
    async def broadcast(
        self,
        message: Any,
        exclude: Optional[WebSocket] = None
    ) -> None:
        """
        Broadcast message to all connections in the channel.
        
        Args:
            message: Message to broadcast
            exclude: Optional connection to exclude
        """
        disconnected = []
        for connection in self.active_connections:
            if connection != exclude:
                try:
                    await self.send_personal_message(message, connection)
                except Exception:
                    disconnected.append(connection)
                    
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
            
    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)
        
    def get_user_count(self) -> int:
        """Get number of connected users."""
        return len(self.user_connections)


class WebSocketManager:
    """
    Manages multiple WebSocket channels/rooms.
    """
    
    def __init__(self):
        self.channels: Dict[str, ConnectionManager] = {}
        self.websocket_handlers: Dict[str, List[Callable]] = {}
        
    def get_channel(self, channel: str) -> ConnectionManager:
        """
        Get or create a channel manager.
        
        Args:
            channel: Channel name
            
        Returns:
            ConnectionManager for the channel
        """
        if channel not in self.channels:
            self.channels[channel] = ConnectionManager(channel)
        return self.channels[channel]
        
    async def connect(
        self,
        websocket: WebSocket,
        channel: str = "default",
        user_id: Optional[str] = None
    ) -> None:
        """
        Connect to a specific channel.
        
        Args:
            websocket: WebSocket connection
            channel: Channel name
            user_id: Optional user identifier
        """
        manager = self.get_channel(channel)
        await manager.connect(websocket, user_id)
        
        # Notify about new connection
        await self.broadcast(
            channel,
            {
                "type": "connection",
                "action": "joined",
                "user_id": user_id or "anonymous",
                "timestamp": datetime.utcnow().isoformat(),
                "connections": manager.get_connection_count()
            },
            exclude=websocket
        )
        
    def disconnect(
        self,
        websocket: WebSocket,
        channel: str = "default",
        user_id: Optional[str] = None
    ) -> None:
        """
        Disconnect from a specific channel.
        
        Args:
            websocket: WebSocket connection
            channel: Channel name
            user_id: Optional user identifier
        """
        if channel in self.channels:
            manager = self.channels[channel]
            manager.disconnect(websocket, user_id)
            
            # Clean up empty channels
            if manager.get_connection_count() == 0:
                del self.channels[channel]
            else:
                # Notify about disconnection
                asyncio.create_task(
                    self.broadcast(
                        channel,
                        {
                            "type": "connection",
                            "action": "left",
                            "user_id": user_id or "anonymous",
                            "timestamp": datetime.utcnow().isoformat(),
                            "connections": manager.get_connection_count()
                        }
                    )
                )
                
    async def send_personal_message(
        self,
        message: Any,
        websocket: WebSocket,
        channel: str = "default"
    ) -> None:
        """Send message to specific connection."""
        if channel in self.channels:
            await self.channels[channel].send_personal_message(message, websocket)
            
    async def send_user_message(
        self,
        message: Any,
        user_id: str,
        channel: str = "default"
    ) -> None:
        """Send message to all connections of a user."""
        if channel in self.channels:
            await self.channels[channel].send_user_message(message, user_id)
            
    async def broadcast(
        self,
        channel: str,
        message: Any,
        exclude: Optional[WebSocket] = None
    ) -> None:
        """Broadcast message to all connections in a channel."""
        if channel in self.channels:
            await self.channels[channel].broadcast(message, exclude)
            
    def register_handler(
        self,
        message_type: str,
        handler: Callable
    ) -> None:
        """
        Register a message handler for specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        if message_type not in self.websocket_handlers:
            self.websocket_handlers[message_type] = []
        self.websocket_handlers[message_type].append(handler)
        
    async def handle_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        channel: str = "default",
        user_id: Optional[str] = None
    ) -> None:
        """
        Handle incoming WebSocket message.
        
        Args:
            websocket: WebSocket connection
            message: Parsed message data
            channel: Channel name
            user_id: Optional user identifier
        """
        message_type = message.get("type", "unknown")
        
        # Call registered handlers
        if message_type in self.websocket_handlers:
            for handler in self.websocket_handlers[message_type]:
                try:
                    await handler(websocket, message, channel, user_id)
                except Exception as e:
                    logger.error(f"Error in WebSocket handler: {e}")
                    await self.send_personal_message(
                        {
                            "type": "error",
                            "message": f"Error processing message: {str(e)}"
                        },
                        websocket,
                        channel
                    )
        else:
            # Echo message to all connections in channel by default
            await self.broadcast(
                channel,
                {
                    **message,
                    "from": user_id or "anonymous",
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude=websocket
            )
            
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics."""
        return {
            "channels": {
                channel: {
                    "connections": manager.get_connection_count(),
                    "users": manager.get_user_count()
                }
                for channel, manager in self.channels.items()
            },
            "total_connections": sum(
                m.get_connection_count() for m in self.channels.values()
            ),
            "total_channels": len(self.channels)
        }


# Example WebSocket endpoint
async def websocket_endpoint(
    websocket: WebSocket,
    manager: WebSocketManager,
    channel: str = "default",
    token: Optional[str] = None
):
    """
    Example WebSocket endpoint with authentication.
    
    Args:
        websocket: WebSocket connection
        manager: WebSocketManager instance
        channel: Channel to join
        token: Optional authentication token
    """
    user_id = None
    
    # Authenticate if token provided
    if token:
        try:
            # Verify token and get user
            auth_service = AuthService()
            user = await auth_service.get_user_from_token(token)
            if user:
                user_id = str(user.id)
        except Exception as e:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
    # Connect to channel
    await manager.connect(websocket, channel, user_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle message
            await manager.handle_message(websocket, data, channel, user_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, channel, user_id)