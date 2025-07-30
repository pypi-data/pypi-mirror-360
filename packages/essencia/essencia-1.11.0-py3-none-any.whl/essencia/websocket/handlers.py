"""
WebSocket message handlers for different features.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from essencia.models import User
from essencia.models.vital_signs import BloodPressure, Temperature, HeartRate
from essencia.models.notification import Notification
from .manager import Connection


class BaseHandler(ABC):
    """Base class for WebSocket handlers."""
    
    def __init__(self, db=None, cache=None):
        self.db = db
        self.cache = cache
    
    @abstractmethod
    async def handle(self, connection: Connection, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming message."""
        pass
    
    def require_auth(self, connection: Connection):
        """Require authenticated connection."""
        if not connection.user_id:
            raise Exception("Authentication required")
    
    def require_permission(self, connection: Connection, permission: str):
        """Require specific permission."""
        self.require_auth(connection)
        # In real implementation, check user permissions
        if connection.user_role == "patient" and permission != "own_data:read":
            raise Exception(f"Permission denied: {permission}")


class VitalSignsHandler(BaseHandler):
    """Handle vital signs real-time updates."""
    
    async def handle(self, connection: Connection, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle vital signs messages."""
        action = message.get("action")
        
        if action == "subscribe":
            return await self.handle_subscribe(connection, message)
        elif action == "record":
            return await self.handle_record(connection, message)
        elif action == "get_latest":
            return await self.handle_get_latest(connection, message)
        else:
            raise Exception(f"Unknown action: {action}")
    
    async def handle_subscribe(self, connection: Connection, message: Dict[str, Any]) -> Dict[str, Any]:
        """Subscribe to vital signs updates for a patient."""
        patient_id = message.get("patient_id")
        if not patient_id:
            raise Exception("patient_id required")
        
        # Check permission
        if connection.user_role == "patient" and str(connection.user_id) != patient_id:
            raise Exception("Cannot subscribe to other patient's data")
        
        # Join patient's vital signs room
        from .manager import websocket_manager
        await websocket_manager.connection_manager.join_room(
            connection.id,
            f"vitals:{patient_id}"
        )
        
        return {
            "type": "vital_signs_subscribed",
            "patient_id": patient_id,
            "status": "success"
        }
    
    async def handle_record(self, connection: Connection, message: Dict[str, Any]) -> Dict[str, Any]:
        """Record new vital signs."""
        self.require_permission(connection, "vital_signs:write")
        
        data = message.get("data", {})
        patient_id = data.get("patient_id")
        
        # Record blood pressure
        if "systolic" in data and "diastolic" in data:
            BloodPressure.set_db(self.db)
            bp = BloodPressure(
                patient_id=patient_id,
                systolic=data["systolic"],
                diastolic=data["diastolic"],
                pulse=data.get("pulse"),
                recorded_by=connection.user_id,
                notes="Recorded via WebSocket"
            )
            await bp.save()
            
            # Broadcast to subscribers
            from .manager import websocket_manager
            await websocket_manager.connection_manager.send_to_room(
                f"vitals:{patient_id}",
                {
                    "type": "vital_signs_update",
                    "patient_id": patient_id,
                    "vital_signs": {
                        "id": str(bp.id),
                        "systolic": data["systolic"],
                        "diastolic": data["diastolic"],
                        "pulse": data.get("pulse"),
                        "category": bp.categorize().value,
                        "recorded_at": bp.recorded_at.isoformat()
                    }
                }
            )
            
            return {
                "type": "vital_signs_recorded",
                "id": str(bp.id),
                "status": "success"
            }
        
        return {"type": "error", "error": "Invalid vital signs data"}
    
    async def handle_get_latest(self, connection: Connection, message: Dict[str, Any]) -> Dict[str, Any]:
        """Get latest vital signs for a patient."""
        patient_id = message.get("patient_id")
        
        # Check permission
        if connection.user_role == "patient" and str(connection.user_id) != patient_id:
            self.require_permission(connection, "vital_signs:read")
        
        # Get latest readings
        BloodPressure.set_db(self.db)
        latest_bp = await BloodPressure.find_one(
            {"patient_id": patient_id},
            sort=[("recorded_at", -1)]
        )
        
        vital_signs = {}
        if latest_bp:
            vital_signs["blood_pressure"] = {
                "systolic": latest_bp.systolic.get_secret_value(),
                "diastolic": latest_bp.diastolic.get_secret_value(),
                "pulse": latest_bp.pulse,
                "category": latest_bp.categorize().value,
                "recorded_at": latest_bp.recorded_at.isoformat()
            }
        
        return {
            "type": "latest_vital_signs",
            "patient_id": patient_id,
            "vital_signs": vital_signs
        }


class NotificationHandler(BaseHandler):
    """Handle real-time notifications."""
    
    async def handle(self, connection: Connection, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle notification messages."""
        action = message.get("action")
        
        if action == "mark_read":
            return await self.handle_mark_read(connection, message)
        elif action == "get_unread":
            return await self.handle_get_unread(connection, message)
        else:
            raise Exception(f"Unknown action: {action}")
    
    async def handle_mark_read(self, connection: Connection, message: Dict[str, Any]) -> Dict[str, Any]:
        """Mark notification as read."""
        self.require_auth(connection)
        
        notification_id = message.get("notification_id")
        if not notification_id:
            raise Exception("notification_id required")
        
        Notification.set_db(self.db)
        notification = await Notification.find_by_id(notification_id)
        
        if not notification:
            raise Exception("Notification not found")
        
        if notification.user_id != connection.user_id:
            raise Exception("Permission denied")
        
        notification.mark_as_read()
        await notification.save()
        
        return {
            "type": "notification_marked_read",
            "notification_id": notification_id,
            "status": "success"
        }
    
    async def handle_get_unread(self, connection: Connection, message: Dict[str, Any]) -> Dict[str, Any]:
        """Get unread notifications."""
        self.require_auth(connection)
        
        Notification.set_db(self.db)
        notifications = await Notification.find_many(
            {
                "user_id": connection.user_id,
                "read_at": None
            },
            limit=50,
            sort=[("created_at", -1)]
        )
        
        return {
            "type": "unread_notifications",
            "notifications": [
                {
                    "id": str(n.id),
                    "type": n.notification_type,
                    "title": n.title,
                    "message": n.message,
                    "priority": n.priority,
                    "created_at": n.created_at.isoformat()
                }
                for n in notifications
            ],
            "count": len(notifications)
        }
    
    @staticmethod
    async def send_notification(user_id: str, notification: Dict[str, Any]):
        """Send notification to user via WebSocket."""
        from .manager import websocket_manager
        
        # Save to database
        Notification.set_db(websocket_manager.handlers.get("notification").db)
        notif = Notification(
            user_id=user_id,
            notification_type=notification.get("type", "general"),
            title=notification["title"],
            message=notification["message"],
            priority=notification.get("priority", "medium"),
            data=notification.get("data", {})
        )
        await notif.save()
        
        # Send via WebSocket
        await websocket_manager.send_notification(user_id, {
            "id": str(notif.id),
            **notification
        })


class ChatHandler(BaseHandler):
    """Handle real-time chat/messaging."""
    
    async def handle(self, connection: Connection, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle chat messages."""
        action = message.get("action")
        
        if action == "send":
            return await self.handle_send_message(connection, message)
        elif action == "typing":
            return await self.handle_typing(connection, message)
        else:
            raise Exception(f"Unknown action: {action}")
    
    async def handle_send_message(self, connection: Connection, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send chat message."""
        self.require_auth(connection)
        
        room = message.get("room")
        text = message.get("text")
        
        if not room or not text:
            raise Exception("room and text required")
        
        # Check if user is in room
        if room not in connection.rooms:
            raise Exception("Not in room")
        
        # Create message
        chat_message = {
            "id": str(datetime.now().timestamp()),
            "user_id": connection.user_id,
            "user_name": connection.client_info.get("user_name", "Unknown"),
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to room
        from .manager import websocket_manager
        await websocket_manager.connection_manager.send_to_room(
            room,
            {
                "type": "chat_message",
                "room": room,
                "message": chat_message
            }
        )
        
        return {
            "type": "message_sent",
            "message_id": chat_message["id"],
            "status": "success"
        }
    
    async def handle_typing(self, connection: Connection, message: Dict[str, Any]) -> None:
        """Handle typing indicator."""
        self.require_auth(connection)
        
        room = message.get("room")
        is_typing = message.get("is_typing", False)
        
        if not room:
            raise Exception("room required")
        
        # Broadcast typing status
        from .manager import websocket_manager
        await websocket_manager.connection_manager.send_to_room(
            room,
            {
                "type": "typing_status",
                "room": room,
                "user_id": connection.user_id,
                "user_name": connection.client_info.get("user_name", "Unknown"),
                "is_typing": is_typing
            },
            exclude=[connection.id]
        )
        
        return None  # No response needed


class MonitoringHandler(BaseHandler):
    """Handle real-time monitoring updates."""
    
    async def handle(self, connection: Connection, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle monitoring messages."""
        action = message.get("action")
        
        if action == "subscribe_patient":
            return await self.handle_subscribe_patient(connection, message)
        elif action == "subscribe_department":
            return await self.handle_subscribe_department(connection, message)
        else:
            raise Exception(f"Unknown action: {action}")
    
    async def handle_subscribe_patient(self, connection: Connection, message: Dict[str, Any]) -> Dict[str, Any]:
        """Subscribe to patient monitoring."""
        self.require_permission(connection, "monitoring:read")
        
        patient_id = message.get("patient_id")
        monitor_types = message.get("types", ["vitals", "alerts"])
        
        # Join monitoring rooms
        from .manager import websocket_manager
        for monitor_type in monitor_types:
            await websocket_manager.connection_manager.join_room(
                connection.id,
                f"monitor:{monitor_type}:{patient_id}"
            )
        
        return {
            "type": "monitoring_subscribed",
            "patient_id": patient_id,
            "types": monitor_types,
            "status": "success"
        }
    
    async def handle_subscribe_department(self, connection: Connection, message: Dict[str, Any]) -> Dict[str, Any]:
        """Subscribe to department-wide monitoring."""
        self.require_permission(connection, "monitoring:department")
        
        department = message.get("department")
        if not department:
            raise Exception("department required")
        
        # Join department monitoring room
        from .manager import websocket_manager
        await websocket_manager.connection_manager.join_room(
            connection.id,
            f"monitor:department:{department}"
        )
        
        return {
            "type": "department_monitoring_subscribed",
            "department": department,
            "status": "success"
        }
    
    @staticmethod
    async def broadcast_alert(alert: Dict[str, Any]):
        """Broadcast monitoring alert."""
        from .manager import websocket_manager
        
        # Determine target rooms
        rooms = []
        
        if alert.get("patient_id"):
            rooms.append(f"monitor:alerts:{alert['patient_id']}")
        
        if alert.get("department"):
            rooms.append(f"monitor:department:{alert['department']}")
        
        if alert.get("priority") == "critical":
            # Broadcast to all monitoring staff
            await websocket_manager.broadcast_update(
                "critical_alert",
                alert,
                role="doctor"
            )
            await websocket_manager.broadcast_update(
                "critical_alert",
                alert,
                role="nurse"
            )
        else:
            # Send to specific rooms
            for room in rooms:
                await websocket_manager.connection_manager.send_to_room(
                    room,
                    {
                        "type": "monitoring_alert",
                        "alert": alert,
                        "timestamp": datetime.now().isoformat()
                    }
                )