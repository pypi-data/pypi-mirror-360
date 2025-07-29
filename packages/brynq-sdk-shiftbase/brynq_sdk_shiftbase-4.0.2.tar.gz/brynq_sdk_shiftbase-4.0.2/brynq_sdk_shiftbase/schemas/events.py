"""
Schema definition for Event data validation.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
import re
from datetime import datetime

class EventSchema(BaseModel):
    """
    Schema for validating Event data returned from Shiftbase API.
    Represents an event in the calendar of a department.
    """
    # Required fields
    department_id: str = Field(
        description="The department ID"
    )
    starttime: str = Field(
        description="The time when the event starts"
    )
    endtime: str = Field(
        description="The time when the event ends"
    )
    title: str = Field(
        description="The title of the event",
        max_length=255
    )
    
    # Read-only fields
    id: Optional[str] = Field(
        description="The event ID",
        default=None
    )
    sequence_id: Optional[str] = Field(
        description="The sequence ID. The ID that all other events are related to as well",
        default=None
    )
    account_id: Optional[str] = Field(
        description="The account ID",
        default=None
    )
    date: Optional[str] = Field(
        description="The date when the event takes place",
        default=None
    )
    created: Optional[datetime] = Field(
        description="The date and time when the event has been created",
        default=None
    )
    updated: Optional[datetime] = Field(
        description="The date and time when the event has been updated",
        default=None
    )
    created_by: Optional[str] = Field(
        description="The user ID that created the event",
        default=None
    )
    modified_by: Optional[str] = Field(
        description="The user ID that modified the event",
        default=None
    )
    start_seconds: Optional[int] = Field(
        description="The date and start time in timestamp",
        default=None
    )
    end_seconds: Optional[int] = Field(
        description="The date and end time in timestamp",
        default=None
    )
    
    # Optional fields
    team_id: Optional[str] = Field(
        description="ID of the team within the selected department. This is optional",
        default=None
    )
    description: Optional[str] = Field(
        description="Description what the event is about",
        default=None
    )
    deleted: Optional[bool] = Field(
        description="Determines that the event has been deleted",
        default=False
    )
    
    @field_validator('sequence_id')
    @classmethod
    def validate_uuid(cls, v):
        """Validates UUID format when present"""
        if v is None:
            return v
            
        try:
            UUID(v)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")
            
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        """Validates date format YYYY-MM-DD"""
        if v is None:
            return v
            
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, v):
            raise ValueError(f"Invalid date format: {v}. Expected format: YYYY-MM-DD")
        return v
    
    @field_validator('starttime', 'endtime')
    @classmethod
    def validate_time(cls, v):
        """Validates time format HH:MM:SS"""
        if v is None:
            return v
            
        time_pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$"
        if not re.match(time_pattern, v):
            raise ValueError(f"Invalid time format: {v}. Expected format: HH:MM:SS")
        return v
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields 