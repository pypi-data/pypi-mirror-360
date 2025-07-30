"""Notification system models.

This module provides models for managing notifications,
templates, and user preferences.
"""

import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import Field, field_validator, model_validator

from .bases import MongoModel, ObjectReferenceId, StrEnum
from essencia import fields as fd


class NotificationType(StrEnum):
    """Types of notifications."""
    APPOINTMENT_REMINDER = 'APPOINTMENT_REMINDER'
    APPOINTMENT_CONFIRMATION = 'APPOINTMENT_CONFIRMATION'
    APPOINTMENT_CANCELLATION = 'APPOINTMENT_CANCELLATION'
    PRESCRIPTION_READY = 'PRESCRIPTION_READY'
    LAB_RESULTS = 'LAB_RESULTS'
    PAYMENT_DUE = 'PAYMENT_DUE'
    PAYMENT_RECEIVED = 'PAYMENT_RECEIVED'
    BIRTHDAY = 'BIRTHDAY'
    FOLLOW_UP = 'FOLLOW_UP'
    SYSTEM = 'SYSTEM'
    MARKETING = 'MARKETING'
    EMERGENCY = 'EMERGENCY'


class NotificationChannel(StrEnum):
    """Delivery channels for notifications."""
    EMAIL = 'EMAIL'
    SMS = 'SMS'
    WHATSAPP = 'WHATSAPP'
    IN_APP = 'IN_APP'
    PUSH = 'PUSH'


class NotificationStatus(StrEnum):
    """Status of notifications."""
    PENDING = 'PENDING'
    SCHEDULED = 'SCHEDULED'
    SENDING = 'SENDING'
    SENT = 'SENT'
    DELIVERED = 'DELIVERED'
    READ = 'READ'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class NotificationTemplate(MongoModel):
    """Reusable notification templates."""
    COLLECTION_NAME = 'notification_templates'
    
    name: str = Field(..., description="Template name")
    type: NotificationType = Field(..., description="Notification type")
    channel: NotificationChannel = Field(..., description="Delivery channel")
    
    # Template content
    subject: Optional[str] = Field(None, description="Subject/title (for email)")
    content: str = Field(..., description="Template content with {variables}")
    
    # Available variables for this template
    variables: List[str] = Field(
        default_factory=list,
        description="Available template variables"
    )
    
    # Channel-specific settings
    sms_sender_id: Optional[str] = None
    whatsapp_template_id: Optional[str] = None
    
    # Metadata
    is_active: bool = True
    creator: ObjectReferenceId = 'doctor.admin'
    created: fd.DefaultDateTime
    last_updated: Optional[datetime.datetime] = None
    
    def render(self, **kwargs) -> str:
        """Render template with provided variables."""
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"Missing required variable: {missing_var}")
    
    def validate_variables(self, provided: Dict[str, Any]) -> bool:
        """Validate that all required variables are provided."""
        # Extract variables from template
        import re
        pattern = r'\{(\w+)\}'
        required = set(re.findall(pattern, self.content))
        if self.subject:
            required.update(re.findall(pattern, self.subject))
        
        # Check if all required variables are provided
        provided_keys = set(provided.keys())
        missing = required - provided_keys
        
        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")
        
        return True


class Notification(MongoModel):
    """Individual notification records."""
    COLLECTION_NAME = 'notifications'
    
    # Type and channel
    type: NotificationType
    channel: NotificationChannel
    template_key: Optional[ObjectReferenceId] = Field(None, description="Template used")
    
    # Recipient
    recipient_key: ObjectReferenceId = Field(..., description="Recipient reference")
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_name: Optional[str] = None
    
    # Content
    subject: Optional[str] = None
    content: str
    
    # Scheduling
    scheduled_for: Optional[datetime.datetime] = None
    send_after: Optional[datetime.datetime] = None
    
    # Status tracking
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: Optional[datetime.datetime] = None
    delivered_at: Optional[datetime.datetime] = None
    read_at: Optional[datetime.datetime] = None
    failed_at: Optional[datetime.datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3
    last_attempt_at: Optional[datetime.datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    creator: ObjectReferenceId = 'system'
    created: fd.DefaultDateTime
    
    # Related entities
    related_entity_type: Optional[str] = None  # e.g., 'appointment', 'prescription'
    related_entity_key: Optional[ObjectReferenceId] = None
    
    @property
    def can_retry(self) -> bool:
        """Check if notification can be retried."""
        return (
            self.status == NotificationStatus.FAILED and
            self.attempts < self.max_attempts
        )
    
    @property
    def recipient_contact(self) -> Optional[str]:
        """Get recipient contact based on channel."""
        if self.channel == NotificationChannel.EMAIL:
            return self.recipient_email
        elif self.channel in [NotificationChannel.SMS, NotificationChannel.WHATSAPP]:
            return self.recipient_phone
        return None
    
    def mark_sent(self) -> None:
        """Mark notification as sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.datetime.now()
        self.attempts += 1
        self.last_attempt_at = datetime.datetime.now()
    
    def mark_delivered(self) -> None:
        """Mark notification as delivered."""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.datetime.now()
    
    def mark_read(self) -> None:
        """Mark notification as read."""
        self.status = NotificationStatus.READ
        self.read_at = datetime.datetime.now()
    
    def mark_failed(self, error: str) -> None:
        """Mark notification as failed."""
        self.status = NotificationStatus.FAILED
        self.failed_at = datetime.datetime.now()
        self.error_message = error
        self.attempts += 1
        self.last_attempt_at = datetime.datetime.now()
    
    def cancel(self) -> None:
        """Cancel the notification."""
        if self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED, NotificationStatus.READ]:
            raise ValueError("Cannot cancel a notification that has already been sent")
        
        self.status = NotificationStatus.CANCELLED
    
    @classmethod
    def create_from_template(cls, template: NotificationTemplate, 
                           recipient_key: str,
                           variables: Dict[str, Any],
                           **kwargs) -> 'Notification':
        """Create a notification from a template."""
        # Validate variables
        template.validate_variables(variables)
        
        # Render content
        content = template.render(**variables)
        subject = None
        if template.subject:
            subject = template.subject.format(**variables)
        
        # Create notification
        notification_data = {
            'type': template.type,
            'channel': template.channel,
            'template_key': template.key,
            'recipient_key': recipient_key,
            'subject': subject,
            'content': content,
            **kwargs
        }
        
        return cls(**notification_data)


class NotificationPreference(MongoModel):
    """User notification preferences."""
    COLLECTION_NAME = 'notification_preferences'
    
    user_key: ObjectReferenceId = Field(..., description="User reference")
    
    # Channel preferences by notification type
    channel_preferences: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Preferred channels per notification type"
    )
    
    # Opt-out settings
    opt_out_all: bool = False
    opt_out_types: List[NotificationType] = Field(default_factory=list)
    opt_out_channels: List[NotificationChannel] = Field(default_factory=list)
    
    # Quiet hours (local time)
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[datetime.time] = Field(default=datetime.time(22, 0))
    quiet_hours_end: Optional[datetime.time] = Field(default=datetime.time(8, 0))
    quiet_hours_timezone: str = Field(default='America/Sao_Paulo')
    
    # Language preference
    language: str = Field(default='pt-BR')
    
    # Frequency limits
    max_daily_notifications: Optional[int] = None
    marketing_frequency: str = Field(default='weekly')  # 'daily', 'weekly', 'monthly', 'never'
    
    # Metadata
    created: fd.DefaultDateTime
    last_updated: Optional[datetime.datetime] = None
    
    def get_channels_for_type(self, notification_type: NotificationType) -> List[NotificationChannel]:
        """Get preferred channels for a notification type."""
        if self.opt_out_all:
            return []
        
        if notification_type in self.opt_out_types:
            return []
        
        # Get type-specific preferences
        type_channels = self.channel_preferences.get(notification_type.value, [])
        
        # Filter out opted-out channels
        allowed_channels = [
            NotificationChannel(ch) for ch in type_channels 
            if NotificationChannel(ch) not in self.opt_out_channels
        ]
        
        # If no specific preferences, use defaults based on type
        if not allowed_channels:
            if notification_type in [NotificationType.EMERGENCY, NotificationType.APPOINTMENT_REMINDER]:
                defaults = [NotificationChannel.SMS, NotificationChannel.WHATSAPP]
            elif notification_type in [NotificationType.LAB_RESULTS, NotificationType.PRESCRIPTION_READY]:
                defaults = [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            else:
                defaults = [NotificationChannel.EMAIL]
            
            allowed_channels = [ch for ch in defaults if ch not in self.opt_out_channels]
        
        return allowed_channels
    
    def is_quiet_hours(self, check_time: Optional[datetime.datetime] = None) -> bool:
        """Check if current time is within quiet hours."""
        if not self.quiet_hours_enabled:
            return False
        
        if not check_time:
            check_time = datetime.datetime.now()
        
        # Convert to user's timezone
        try:
            import pytz
            tz = pytz.timezone(self.quiet_hours_timezone)
            local_time = check_time.astimezone(tz).time()
        except:
            # Fallback to system time if timezone handling fails
            local_time = check_time.time()
        
        # Handle quiet hours that span midnight
        if self.quiet_hours_start > self.quiet_hours_end:
            return local_time >= self.quiet_hours_start or local_time <= self.quiet_hours_end
        else:
            return self.quiet_hours_start <= local_time <= self.quiet_hours_end
    
    def can_send_marketing(self, last_sent: Optional[datetime.datetime] = None) -> bool:
        """Check if marketing notifications can be sent based on frequency."""
        if self.marketing_frequency == 'never':
            return False
        
        if not last_sent:
            return True
        
        days_since = (datetime.datetime.now() - last_sent).days
        
        if self.marketing_frequency == 'daily':
            return days_since >= 1
        elif self.marketing_frequency == 'weekly':
            return days_since >= 7
        elif self.marketing_frequency == 'monthly':
            return days_since >= 30
        
        return True