"""Appointment scheduling and management models.

This module provides models for managing medical appointments,
doctor schedules, and scheduling blocks.
"""

import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import Field, field_validator, model_validator

from .bases import MongoModel, ObjectReferenceId, StrEnum
from essencia import fields as fd


class AppointmentType(StrEnum):
    """Types of medical appointments."""
    CONSULTATION = 'CONSULTATION'
    RETURN = 'RETURN'
    EMERGENCY = 'EMERGENCY'
    PROCEDURE = 'PROCEDURE'
    EXAM = 'EXAM'
    THERAPY = 'THERAPY'
    GROUP_THERAPY = 'GROUP_THERAPY'
    TELEMEDICINE = 'TELEMEDICINE'


class AppointmentStatus(StrEnum):
    """Status of appointments."""
    SCHEDULED = 'SCHEDULED'
    CONFIRMED = 'CONFIRMED'
    WAITING = 'WAITING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    NO_SHOW = 'NO_SHOW'
    RESCHEDULED = 'RESCHEDULED'


class RecurrencePattern(StrEnum):
    """Recurrence patterns for appointments."""
    NONE = 'NONE'
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    BIWEEKLY = 'BIWEEKLY'
    MONTHLY = 'MONTHLY'


class BlockType(StrEnum):
    """Types of schedule blocks."""
    VACATION = 'VACATION'
    MEETING = 'MEETING'
    PERSONAL = 'PERSONAL'
    LUNCH = 'LUNCH'
    TRAINING = 'TRAINING'
    OTHER = 'OTHER'


class Appointment(MongoModel):
    """Medical appointment model."""
    COLLECTION_NAME = 'appointments'
    
    # Core references
    patient_key: ObjectReferenceId = Field(..., description="Patient reference")
    doctor_key: ObjectReferenceId = Field(..., description="Doctor reference")
    
    # Appointment details
    appointment_type: AppointmentType = AppointmentType.CONSULTATION
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    
    # Scheduling
    scheduled_date: datetime.date = Field(..., description="Appointment date")
    scheduled_time: datetime.time = Field(..., description="Appointment time")
    duration_minutes: int = Field(default=30, description="Duration in minutes")
    
    # Recurrence
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    recurrence_end_date: Optional[datetime.date] = None
    parent_appointment_key: Optional[ObjectReferenceId] = None
    
    # Notes and details
    reason: Optional[str] = Field(None, description="Reason for appointment")
    notes: Optional[str] = Field(None, description="Additional notes")
    pre_appointment_instructions: Optional[str] = None
    
    # Tracking
    confirmed_at: Optional[datetime.datetime] = None
    cancelled_at: Optional[datetime.datetime] = None
    cancelled_reason: Optional[str] = None
    completed_at: Optional[datetime.datetime] = None
    
    # Reminders
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime.datetime] = None
    
    # Virtual appointments
    is_virtual: bool = False
    virtual_link: Optional[str] = None
    
    # Metadata
    creator: ObjectReferenceId = 'doctor.admin'
    created: fd.DefaultDateTime
    last_updated: Optional[datetime.datetime] = None
    
    @property
    def start_datetime(self) -> datetime.datetime:
        """Get combined start datetime."""
        return datetime.datetime.combine(self.scheduled_date, self.scheduled_time)
    
    @property
    def end_datetime(self) -> datetime.datetime:
        """Get calculated end datetime."""
        return self.start_datetime + datetime.timedelta(minutes=self.duration_minutes)
    
    def confirm(self) -> None:
        """Mark appointment as confirmed."""
        self.status = AppointmentStatus.CONFIRMED
        self.confirmed_at = datetime.datetime.now()
        self.last_updated = datetime.datetime.now()
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the appointment."""
        self.status = AppointmentStatus.CANCELLED
        self.cancelled_at = datetime.datetime.now()
        self.cancelled_reason = reason
        self.last_updated = datetime.datetime.now()
    
    def mark_no_show(self) -> None:
        """Mark appointment as no-show."""
        self.status = AppointmentStatus.NO_SHOW
        self.last_updated = datetime.datetime.now()
    
    def start(self) -> None:
        """Mark appointment as in progress."""
        self.status = AppointmentStatus.IN_PROGRESS
        self.last_updated = datetime.datetime.now()
    
    def complete(self) -> None:
        """Mark appointment as completed."""
        self.status = AppointmentStatus.COMPLETED
        self.completed_at = datetime.datetime.now()
        self.last_updated = datetime.datetime.now()
    
    def reschedule(self, new_date: datetime.date, new_time: datetime.time) -> 'Appointment':
        """Reschedule the appointment."""
        # Mark current as rescheduled
        self.status = AppointmentStatus.RESCHEDULED
        self.last_updated = datetime.datetime.now()
        self.save_self()
        
        # Create new appointment
        new_data = self.model_dump(exclude={'key', 'id', 'created', 'status'})
        new_data['scheduled_date'] = new_date
        new_data['scheduled_time'] = new_time
        new_data['status'] = AppointmentStatus.SCHEDULED
        new_data['parent_appointment_key'] = self.key
        
        new_appointment = Appointment(**new_data)
        return new_appointment.save_self()


class DoctorSchedule(MongoModel):
    """Doctor availability and schedule configuration."""
    COLLECTION_NAME = 'doctor_schedules'
    
    doctor_key: ObjectReferenceId = Field(..., description="Doctor reference")
    
    # Regular working hours by day of week (0=Monday, 6=Sunday)
    working_hours: Dict[int, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Working hours per weekday"
    )
    # Format: {0: [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "18:00"}]}
    
    # Default appointment durations by type
    default_durations: Dict[str, int] = Field(
        default_factory=lambda: {
            AppointmentType.CONSULTATION: 60,
            AppointmentType.RETURN: 30,
            AppointmentType.EMERGENCY: 45,
            AppointmentType.PROCEDURE: 90,
            AppointmentType.EXAM: 30,
            AppointmentType.THERAPY: 50,
            AppointmentType.GROUP_THERAPY: 90,
            AppointmentType.TELEMEDICINE: 30
        }
    )
    
    # Time between appointments (buffer)
    buffer_minutes: int = Field(default=10, description="Minutes between appointments")
    
    # Special dates (holidays, etc.)
    blocked_dates: List[datetime.date] = Field(default_factory=list)
    special_hours: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Special hours for specific dates"
    )
    
    # Lunch break
    lunch_start: Optional[datetime.time] = Field(default=datetime.time(12, 0))
    lunch_duration_minutes: int = Field(default=60)
    
    # Metadata
    is_active: bool = True
    creator: ObjectReferenceId = 'doctor.admin'
    created: fd.DefaultDateTime
    last_updated: Optional[datetime.datetime] = None
    
    def get_working_hours(self, date: datetime.date) -> List[Dict[str, Any]]:
        """Get working hours for a specific date."""
        date_str = date.isoformat()
        
        # Check if date is blocked
        if date in self.blocked_dates:
            return []
        
        # Check for special hours
        if date_str in self.special_hours:
            return self.special_hours[date_str]
        
        # Get regular hours for this weekday
        weekday = date.weekday()
        return self.working_hours.get(weekday, [])
    
    def get_available_slots(self, date: datetime.date, 
                          appointment_type: AppointmentType,
                          existing_appointments: List[Appointment]) -> List[datetime.time]:
        """Calculate available time slots for a given date."""
        working_hours = self.get_working_hours(date)
        if not working_hours:
            return []
        
        duration = self.default_durations.get(appointment_type, 30)
        total_duration = duration + self.buffer_minutes
        
        # Build list of all possible slots
        available_slots = []
        
        for period in working_hours:
            start = datetime.datetime.strptime(period['start'], '%H:%M').time()
            end = datetime.datetime.strptime(period['end'], '%H:%M').time()
            
            current = datetime.datetime.combine(date, start)
            period_end = datetime.datetime.combine(date, end)
            
            while current + datetime.timedelta(minutes=duration) <= period_end:
                # Check if slot overlaps with lunch
                if self.lunch_start:
                    lunch_start = datetime.datetime.combine(date, self.lunch_start)
                    lunch_end = lunch_start + datetime.timedelta(minutes=self.lunch_duration_minutes)
                    
                    slot_end = current + datetime.timedelta(minutes=duration)
                    
                    if not (slot_end <= lunch_start or current >= lunch_end):
                        current += datetime.timedelta(minutes=15)  # Skip in 15-min increments
                        continue
                
                # Check if slot conflicts with existing appointments
                slot_available = True
                for appt in existing_appointments:
                    if appt.status in [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]:
                        continue
                    
                    appt_start = appt.start_datetime
                    appt_end = appt.end_datetime
                    slot_end = current + datetime.timedelta(minutes=duration)
                    
                    if not (slot_end <= appt_start or current >= appt_end):
                        slot_available = False
                        break
                
                if slot_available:
                    available_slots.append(current.time())
                
                current += datetime.timedelta(minutes=15)  # 15-minute increments
        
        return available_slots
    
    def add_blocked_date(self, date: datetime.date) -> None:
        """Add a blocked date."""
        if date not in self.blocked_dates:
            self.blocked_dates.append(date)
            self.last_updated = datetime.datetime.now()
    
    def remove_blocked_date(self, date: datetime.date) -> None:
        """Remove a blocked date."""
        if date in self.blocked_dates:
            self.blocked_dates.remove(date)
            self.last_updated = datetime.datetime.now()


class ScheduleBlock(MongoModel):
    """Block time periods in doctor's schedule."""
    COLLECTION_NAME = 'schedule_blocks'
    
    doctor_key: ObjectReferenceId = Field(..., description="Doctor reference")
    
    # Block details
    start_datetime: datetime.datetime = Field(..., description="Block start")
    end_datetime: datetime.datetime = Field(..., description="Block end")
    
    block_type: BlockType = BlockType.OTHER
    reason: str = Field(..., description="Reason for block")
    
    # Recurrence
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_end_date: Optional[datetime.date] = None
    
    # Metadata
    creator: ObjectReferenceId = 'doctor.admin'
    created: fd.DefaultDateTime
    cancelled: bool = False
    cancelled_at: Optional[datetime.datetime] = None
    
    @field_validator('end_datetime')
    def validate_end_after_start(cls, v, values):
        """Ensure end time is after start time."""
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError("End time must be after start time")
        return v
    
    def cancel(self) -> None:
        """Cancel this schedule block."""
        self.cancelled = True
        self.cancelled_at = datetime.datetime.now()
    
    def conflicts_with(self, start: datetime.datetime, end: datetime.datetime) -> bool:
        """Check if this block conflicts with a time period."""
        if self.cancelled:
            return False
        
        return not (end <= self.start_datetime or start >= self.end_datetime)