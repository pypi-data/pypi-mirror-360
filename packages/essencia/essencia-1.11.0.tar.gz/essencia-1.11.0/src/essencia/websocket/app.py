"""
WebSocket endpoint setup for FastAPI.
"""
from typing import Optional, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from essencia.models import User
from .manager import websocket_manager
from .handlers import (
    VitalSignsHandler,
    NotificationHandler,
    ChatHandler,
    MonitoringHandler
)


def setup_websocket_endpoints(app: FastAPI, settings: Any = None) -> FastAPI:
    """
    Add WebSocket endpoints to FastAPI app.
    
    Args:
        app: FastAPI application
        settings: Application settings
        
    Returns:
        FastAPI app with WebSocket endpoints
    """
    if not settings:
        settings = app.state.settings
    
    # Initialize handlers
    db = app.state.db.db
    cache = getattr(app.state, "cache", None)
    
    websocket_manager.add_handler("vital_signs", VitalSignsHandler(db, cache))
    websocket_manager.add_handler("notification", NotificationHandler(db, cache))
    websocket_manager.add_handler("chat", ChatHandler(db, cache))
    websocket_manager.add_handler("monitoring", MonitoringHandler(db, cache))
    
    # Authentication dependency for WebSocket
    async def get_current_user_ws(
        token: Optional[str] = Query(None),
        db=None
    ) -> Optional[User]:
        """Get current user from WebSocket token."""
        if not token:
            return None
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"]
            )
            
            # Get user
            user_id = payload.get("sub")
            if user_id:
                User.set_db(db or app.state.db.db)
                user = await User.find_by_id(user_id)
                return user
                
        except JWTError:
            pass
        
        return None
    
    @app.websocket("/ws")
    async def websocket_endpoint(
        websocket: WebSocket,
        token: Optional[str] = Query(None)
    ):
        """
        Main WebSocket endpoint.
        
        Connect with: ws://localhost:8000/ws?token=YOUR_JWT_TOKEN
        """
        # Get user if authenticated
        user = await get_current_user_ws(token, app.state.db.db)
        
        # Get client info
        client_info = {
            "user_agent": websocket.headers.get("user-agent"),
            "origin": websocket.headers.get("origin"),
            "ip": websocket.client.host if websocket.client else None
        }
        
        if user:
            client_info["user_name"] = user.full_name
            client_info["user_email"] = user.email
        
        # Handle connection
        await websocket_manager.handle_connection(
            websocket, user, client_info
        )
    
    @app.websocket("/ws/vitals/{patient_id}")
    async def vitals_websocket(
        websocket: WebSocket,
        patient_id: str,
        token: Optional[str] = Query(None)
    ):
        """
        Dedicated WebSocket for vital signs monitoring.
        
        Auto-subscribes to patient's vital signs updates.
        """
        # Get user
        user = await get_current_user_ws(token, app.state.db.db)
        
        # Connect
        connection = await websocket_manager.connection_manager.connect(
            websocket, user
        )
        
        # Auto-subscribe to patient vitals
        await websocket_manager.connection_manager.join_room(
            connection.id,
            f"vitals:{patient_id}"
        )
        
        try:
            # Keep connection alive
            while True:
                data = await websocket.receive_json()
                # Simple echo for this endpoint
                await websocket.send_json({
                    "type": "echo",
                    "data": data
                })
        except WebSocketDisconnect:
            pass
        finally:
            await websocket_manager.connection_manager.disconnect(connection.id)
    
    @app.websocket("/ws/notifications")
    async def notifications_websocket(
        websocket: WebSocket,
        token: str = Query(...)
    ):
        """
        Dedicated WebSocket for user notifications.
        
        Requires authentication.
        """
        # Get user (required for notifications)
        user = await get_current_user_ws(token, app.state.db.db)
        if not user:
            await websocket.close(code=4001, reason="Authentication required")
            return
        
        # Connect
        connection = await websocket_manager.connection_manager.connect(
            websocket, user
        )
        
        # Send initial unread count
        handler = websocket_manager.handlers["notification"]
        unread_response = await handler.handle_get_unread(connection, {"action": "get_unread"})
        await websocket.send_json(unread_response)
        
        try:
            # Handle notification-specific messages
            while True:
                data = await websocket.receive_json()
                
                # Add message type for handler routing
                if "type" not in data:
                    data["type"] = "notification"
                
                await websocket_manager.handle_message(connection, data)
                
        except WebSocketDisconnect:
            pass
        finally:
            await websocket_manager.connection_manager.disconnect(connection.id)
    
    # Add WebSocket info to API docs
    app.openapi_tags.append({
        "name": "websocket",
        "description": "WebSocket endpoints for real-time features"
    })
    
    return app


# Example client code
"""
// JavaScript WebSocket client example

// Connect to main WebSocket
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

ws.onopen = () => {
    console.log('Connected to WebSocket');
    
    // Subscribe to patient vital signs
    ws.send(JSON.stringify({
        type: 'vital_signs',
        action: 'subscribe',
        patient_id: 'patient123'
    }));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
    
    if (message.type === 'vital_signs_update') {
        // Handle vital signs update
        updateVitalSignsDisplay(message.vital_signs);
    } else if (message.type === 'notification') {
        // Show notification
        showNotification(message.notification);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('WebSocket connection closed');
    // Implement reconnection logic
};

// Send vital signs data
function recordVitalSigns(data) {
    ws.send(JSON.stringify({
        type: 'vital_signs',
        action: 'record',
        data: {
            patient_id: 'patient123',
            systolic: data.systolic,
            diastolic: data.diastolic,
            pulse: data.pulse
        }
    }));
}

// Send chat message
function sendChatMessage(room, text) {
    ws.send(JSON.stringify({
        type: 'chat',
        action: 'send',
        room: room,
        text: text
    }));
}
"""


from typing import Any