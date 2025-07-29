"""
Operational models for task and workflow management.
"""

from pydantic import Field

from .bases import MongoModel, ObjectReferenceId
from .. import fields as fd


class Task(MongoModel):
    """Represents a task in the system for medical professionals.
    
    Attributes:
        text: The description/content of the task
        creator: Reference to the profile who created the task (default: 'doctor.admin')
        created: Auto-generated timestamp of task creation
        completed: Completion status flag (default: False)
    """
    COLLECTION_NAME = 'task'
    
    text: str
    creator: ObjectReferenceId = Field(default=ObjectReferenceId('doctor.admin'))
    created: fd.DefaultDateTime = Field(default_factory=lambda: fd.DefaultDateTime.now())
    completed: bool = Field(default=False)
    
    def __str__(self):
        """Return the task's text content for human-readable representation."""
        return self.text
    
    def __lt__(self, other):
        """Compare tasks by creation date for sorting/ordering."""
        return self.created < other.created