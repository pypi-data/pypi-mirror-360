"""
WebSocket module for real-time features in Essencia.
"""
from .manager import WebSocketManager, ConnectionManager
from .handlers import (
    VitalSignsHandler,
    NotificationHandler,
    ChatHandler,
    MonitoringHandler
)
from .app import setup_websocket_endpoints

__all__ = [
    "WebSocketManager",
    "ConnectionManager",
    "VitalSignsHandler",
    "NotificationHandler", 
    "ChatHandler",
    "MonitoringHandler",
    "setup_websocket_endpoints"
]