"""
Schema definition for Absentee data validation.
"""
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from datetime import date as date_type
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class RosterAction(str, Enum):
    """Roster action options"""
    NONE = "none"
    HIDE = "hide"
    MOVE_TO_OPEN_SHIFT = "move_to_open_shift"


class AbsenteeStatus(str, Enum):
    """Absentee status options"""
    APPROVED = "Approved"
    DECLINED = "Declined"
    PENDING = "Pending"


class AbsenteeDayDetail(BaseModel):
    """
    Absentee day details for a specific date.
    This model can be used for both days and hours units.
    """
    date: date_type = Field(
        description="Date of the absence day"
    )
    partial_day: bool = Field(
        description="Indicates if the absence is for part of the day"
    )
    start_time: str = Field(
        description="Start time of the absence"
    )
    hours: str = Field(
        description="Hours of absence for this day"
    )
    wait_hours: str = Field(
        description="Wait hours for this day"
    )
    wait_hours_balance_id: Optional[UUID] = Field(
        description="UUID of the wait hours balance",
        default=None
    )
    time_off_balance_id: Optional[UUID] = Field(
        description="UUID of the time off balance",
        default=None
    )
    salary: float = Field(
        description="Salary amount"
    )
    coc: float = Field(
        description="Cost of compensation"
    )
    department_id: Optional[str] = Field(
        description="Department ID for this absence day",
        default=None
    )


class AbsenteeModel(BaseModel):
    """
    Schema for validating Absentee data returned from Shiftbase API.
    An Absentee represents an absence record for a user.
    """
    # Required fields
    id: Optional[str] = Field(
        description="The unique identifier of the absentee",
        pattern=r"^[0-9]+$",
        default=None
    )
    account_id: Optional[str] = Field(
        description="Account identifier",
        pattern=r"^[0-9]+$",
        default=None
    )
    user_id: str = Field(
        description="User identifier",
        pattern=r"^[0-9]+$"
    )
    startdate: date_type = Field(
        description="First day of the absentee (YYYY-MM-DD)"
    )
    enddate: date_type = Field(
        description="Last day of the absentee (YYYY-MM-DD)"
    )
    absentee_option_id: str = Field(
        description="Identifier of the absence type",
        pattern=r"^[0-9]+$"
    )

    # Optional fields
    exclude: Optional[bool] = Field(
        description="Deprecated field",
        default=False
    )
    roster_action: RosterAction = Field(
        description="What to do with the shift in the schedule",
        default=RosterAction.NONE
    )
    note: Optional[str] = Field(
        description="Optional text added by the requester",
        default=None
    )
    created: Optional[datetime] = Field(
        description="Creation date and time",
        default=None
    )
    updated: Optional[datetime] = Field(
        description="Last update date and time",
        default=None
    )
    reviewed: Optional[datetime] = Field(
        description="Review date and time",
        default=None
    )
    status: AbsenteeStatus = Field(
        description="Status of the absence request",
        default=AbsenteeStatus.PENDING
    )
    hours: Optional[str] = Field(
        description="Total hours of absence",
        default=None
    )
    wait_hours: Optional[str] = Field(
        description="Total wait hours",
        default=None
    )
    wait_days: Optional[str] = Field(
        description="Total wait days",
        default=None
    )
    partial_day: Optional[bool] = Field(
        description="Indicates if the absence is for part of the day",
        default=False
    )
    start_time: Optional[str] = Field(
        description="Start time of the absence",
        default=None
    )
    end_time: Optional[str] = Field(
        description="End time of the absence",
        default=None
    )
    deleted: Optional[bool] = Field(
        description="Indicates if the absence is deleted",
        default=False
    )
    created_by: Optional[str] = Field(
        description="User ID of the creator",
        pattern=r"^[0-9]+$",
        default=None
    )
    modified_by: Optional[str] = Field(
        description="User ID of the last modifier",
        pattern=r"^[0-9]+$",
        default=None
    )
    reviewed_by: Optional[str] = Field(
        description="User ID of the reviewer",
        pattern=r"^[0-9]+$",
        default=None
    )
    hide_days_without_hours: Optional[bool] = Field(
        description="Whether to hide days without hours",
        default=False
    )
    days: Optional[int] = Field(
        description="Number of days of absence",
        default=None
    )
    hours_per_day: Optional[float] = Field(
        description="Average hours per day",
        default=None
    )
    total: Optional[float] = Field(
        description="Total hours",
        default=None
    )
    total_days: Optional[float] = Field(
        description="Total days",
        default=None
    )
    percentage: Optional[str] = Field(
        description="Percentage from the AbsenteeOption",
        pattern=r"^[0-9]+$",
        default=None
    )
    surcharge_name: Optional[str] = Field(
        description="Surcharge name from the AbsenteeOption",
        default=None
    )
    surcharge_total: Optional[float] = Field(
        description="Surcharge total",
        default=None
    )
    salary: Optional[float] = Field(
        description="Salary amount",
        default=None
    )
    AbsenteeDay: Optional[Dict[str, AbsenteeDayDetail]] = Field(
        description="Absentee details per day in the absence",
        default_factory=dict
    )
    absence_unit: Optional[str] = Field(
        description="Unit of absence (days or hours)",
        default=None
    )
    open_ended: Optional[bool] = Field(
        description="Indicates if the absentee is open-ended",
        default=False
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


class AbsenteeCreateSchema(BaseModel):
    """
    Schema for validating Absentee creation data.
    This schema is used when creating new absences in Shiftbase.
    """
    # Required fields
    user_id: str = Field(
        description="User identifier",
        pattern=r"^[0-9]+$"
    )
    startdate: str = Field(
        description="First day of the absentee (YYYY-MM-DD)"
    )
    enddate: str = Field(
        description="Last day of the absentee (YYYY-MM-DD)"
    )
    absentee_option_id: str = Field(
        description="Identifier of the absence type",
        pattern=r"^[0-9]+$"
    )

    # Optional fields
    roster_action: RosterAction = Field(
        description="What to do with the shift in the schedule",
        default=RosterAction.NONE
    )
    note: Optional[str] = Field(
        description="Optional text added by the requester",
        default=None
    )
    status: AbsenteeStatus = Field(
        description="Status of the absence request",
        default=AbsenteeStatus.PENDING
    )
    hide_days_without_hours: bool = Field(
        description="Whether to hide days without hours",
        default=False
    )
    AbsenteeDay: Optional[List[Dict[str, Any]]] = Field(
        description="Absentee details per day in the absence",
    )
    open_ended: bool = Field(
        description="Indicates if the absentee is open-ended",
        default=False
    )
    notify_employee: bool = Field(
        description="Whether to notify the employee",
        default=False
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


class AbsenteeUpdateSchema(BaseModel):
    """
    Schema for validating Absentee update data.
    This schema is used when updating existing absences in Shiftbase.
    """
    # Required fields
    user_id: str = Field(
        description="User identifier",
        pattern=r"^[0-9]+$"
    )
    startdate: str = Field(
        description="First day of the absentee (YYYY-MM-DD)"
    )
    enddate: str = Field(
        description="Last day of the absentee (YYYY-MM-DD)"
    )
    absentee_option_id: str = Field(
        description="Identifier of the absence type",
        pattern=r"^[0-9]+$"
    )

    # Optional fields
    id: Optional[str] = Field(
        description="The unique identifier of the absentee",
        pattern=r"^[0-9]+$",
        default=None
    )
    roster_action: RosterAction = Field(
        description="What to do with the shift in the schedule",
        default=RosterAction.NONE
    )
    note: Optional[str] = Field(
        description="Optional text added by the requester",
        default=None
    )
    status: AbsenteeStatus = Field(
        description="Status of the absence request",
        default=AbsenteeStatus.PENDING
    )
    hide_days_without_hours: bool = Field(
        description="Whether to hide days without hours",
        default=False
    )
    AbsenteeDay: Optional[List[Dict[str, Any]]] = Field(
        description="Absentee details per day in the absence",
        default_factory=list
    )
    open_ended: bool = Field(
        description="Indicates if the absentee is open-ended",
        default=False
    )
    notify_employee: bool = Field(
        description="Whether to notify the employee",
        default=False
    )
    wait_days: Optional[str] = Field(
        description="Total wait days",
        default=None
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


class ReviewedBySchema(BaseModel):
    """
    Schema for reviewer information when Absences, Timesheets,
    or exchanges are approved or denied.
    This tracks the user that performed the approval/denial action.
    """
    id: Optional[str] = Field(
        description="The unique identifier of the reviewer",
        default=None
    )
    first_name: Optional[str] = Field(
        description="First name of the reviewer",
        default=None
    )
    prefix: Optional[str] = Field(
        description="Name prefix of the reviewer",
        default=None
    )
    last_name: Optional[str] = Field(
        description="Last name of the reviewer",
        default=None
    )
    name: Optional[str] = Field(
        description="Full name of the user. The format is based on account setting. "
                    "The default format is 'first name prefix last name'",
        default=None
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True

class AbsenteeSchema(BaseModel):
    """Pydantic model for Timesheet response"""
    Absentee: Optional[AbsenteeModel] = Field(None)
    ReviewedBy: Optional[ReviewedBySchema] = Field(None)
