"""
Schema definition for Department data validation.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
import re
import pandera as pa
from pandera.typing import Series, DataFrame
from datetime import datetime

class DepartmentModelSchema(BaseModel):
    """
    Schema for validating Department data returned from Shiftbase API.
    """
    # Readonly fields
    id: Optional[str] = Field(
        description="The unique identifier of the department",
        pattern=r"^[0-9]+$",
        default=None
    )
    account_id: Optional[str] = Field(
        description="The account identifier",
        pattern=r"^[0-9]+$",
        default=None
    )
    
    # Required fields
    name: str = Field(
        description="Department name",
        min_length=1
    )
    
    # Optional fields
    location_id: Optional[str] = Field(
        description="Location identifier",
        pattern=r"^[0-9]+$",
        default=None
    )
    address: Optional[str] = Field(
        description="Department address",
        default=None
    )
    longitude: Optional[str] = Field(
        description="Longitude of the department's location",
        pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,16})?))$",
        default=None
    )
    latitude: Optional[str] = Field(
        description="Latitude of the department's location",
        pattern=r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,16})?))$",
        default=None
    )
    holiday_group_id: Optional[str] = Field(
        description="UUID of the holiday group",
        default=None
    )
    order: Optional[str] = Field(
        description="Used for sorting departments",
        pattern=r"^[0-9]+$",
        default=None
    )
    price: Optional[str] = Field(
        description="Price information",
        default=None
    )
    timesheet_copy_starttime: Optional[str] = Field(
        description="If an employee clocks in later than the given time before the start of her shift, copy the starttime from their shift",
        default=None
    )
    timesheet_copy_endtime: Optional[str] = Field(
        description="If an employee clocks out earlier than the given time after the end of her shift, copy the endtime from their shift",
        default=None
    )
    break_rule_type: Optional[str] = Field(
        description="Break rule type",
        default="based_on_length"
    )
    timesheet_surcharges: Optional[bool] = Field(
        description="Show surcharges in timesheet",
        default=True
    )
    meal_registration: Optional[bool] = Field(
        description="Show meal registration in timesheet",
        default=False
    )
    km_registration: Optional[bool] = Field(
        description="Show km-registration in timesheet",
        default=False
    )
    timesheet_copy_schedule: Optional[bool] = Field(
        description="Copy schedule to timesheet. Useful when you manually record worked hours",
        default=True
    )
    timesheet_interval: Optional[str] = Field(
        description="The interval of minutes you can select in the timesheets and schedule",
        pattern=r"^[0-9]+$",
        default=None
    )
    break_interval: Optional[str] = Field(
        description="Value is in minutes",
        pattern=r"^[0-9]+$",
        default=None
    )
    round_clock_in: Optional[str] = Field(
        description="How the clock in time should be rounded according to the timesheet interval setting",
        default=None
    )
    round_clock_out: Optional[str] = Field(
        description="How the clock out time should be rounded according to the timesheet interval setting",
        default=None
    )
    round_clock_break: Optional[str] = Field(
        description="How break times should be rounded",
        default=None
    )
    clock_out_after: Optional[str] = Field(
        description="Automatically clocked-out after x hours",
        pattern=r"^[0-9]+$",
        default=None
    )
    approve_clock: Optional[str] = Field(
        description="Clock approval settings",
        default=None
    )
    allow_clock_in_without_roster: Optional[bool] = Field(
        description="Clock always, even if you are not on the schedule",
        default=True
    )
    approve_schedule: Optional[bool] = Field(
        description="Automatically approve scheduled hours. Useful if you manually register hours worked",
        default=None
    )
    split_clocked_shifts: Optional[str] = Field(
        description="When a clocked break is longer then the given time in minutes, it should start a new shift",
        pattern=r"^[0-9]+$",
        default=None
    )
    default_clock_shift: Optional[str] = Field(
        description="When a clock-in action does not match a scheduled shift, it falls back to this Shift ID",
        pattern=r"^[0-9]+$",
        default=None
    )
    send_availability_reminder: Optional[bool] = Field(
        description="Send availability reminders",
        default=False
    )
    reminder_days_before: Optional[str] = Field(
        description="Send reminder for filling in availability x days before start of the week",
        pattern=r"^[0-9]+$",
        default=None
    )
    lock_availability_days_before_period: Optional[str] = Field(
        description="Allow editing of availability until x days before start of the week",
        pattern=r"^[0-9]+$",
        default=None
    )
    required_days_per_week: Optional[str] = Field(
        description="Required amount of available days per week",
        pattern=r"^[0-9]+$",
        default=None
    )
    publish_schedules: Optional[str] = Field(
        description="Publish the schedules given x days ahead of current date",
        pattern=r"^[0-9]+$",
        default=None
    )
    show_open_shifts: Optional[bool] = Field(
        description="Show open shift option in schedule",
        default=True
    )
    show_required_shifts: Optional[bool] = Field(
        description="Show required shift option in schedule",
        default=True
    )
    deleted: Optional[bool] = Field(
        description="Whether the department is deleted",
        default=False
    )
    deleted_date: Optional[datetime] = Field(
        description="Date when the department was deleted",
        default=None
    )
    created: Optional[datetime] = Field(
        description="Creation timestamp",
        default=None
    )
    updated: Optional[datetime] = Field(
        description="Last update timestamp",
        default=None
    )
    created_by: Optional[str] = Field(
        description="ID of the user who created the department",
        pattern=r"^[0-9]+$",
        default=None
    )
    modified_by: Optional[str] = Field(
        description="ID of the user who last modified the department",
        pattern=r"^[0-9]+$",
        default=None
    )
    availability_deadline: Optional[Dict[str, Any]] = Field(
        None,
        description="Deadline Information")

    
    @field_validator('holiday_group_id')
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
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields 

class DepartmentEmployeeSchema(pa.DataFrameModel):
    """
    Schema for validating Department Employee data returned from Shiftbase API.
    """
    id: Series[str] = pa.Field(coerce=True)  # Changed from int to str with coerce=True
    fullName: Series[str] = pa.Field()
    teamId: Series[str] = pa.Field(coerce=True)  # Changed from int to str with coerce=True
    type: Series[str] = pa.Field()
    
    @pa.check("id", "teamId")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid

    class Config:
        """Schema configuration"""
        coerce = True
        strict = False

class DepartmentTargetSchema(pa.DataFrameModel):
    """
    Validation schema for Department Target data from Shiftbase API
    """
    startDate: Series[str] = pa.Field(description="Start date for the target")
    endDate: Series[str] = pa.Field(description="End date for the target")
    productivity: Series[float] = pa.Field(description="Productivity target")
    averageHourlyWage: Series[float] = pa.Field(description="Average hourly wage target")
    laborCostPercentage: Series[float] = pa.Field(description="Labor cost percentage target")
    created: Series[datetime] = pa.Field(description="The datetime when the target was created")
    modified: Series[datetime] = pa.Field(description="The datetime when the target was last modified")
    createdBy: Series[str] = pa.Field(description="ID of the user that created this target")
    modifiedBy: Series[str] = pa.Field(description="ID of the user that last modified this target")
    
    @pa.check("startDate", "endDate")
    def check_date_format(cls, series: Series[str]) -> Series[bool]:
        """Validate date is in YYYY-MM-DD format."""
        valid = series.str.match(r"^\d{4}-\d{2}-\d{2}$") | series.isna()
        return valid
    
    @pa.check("createdBy", "modifiedBy")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid

    class Config:
        """Schema configuration"""
        coerce = True
        strict = False

class LocationModelSchema(BaseModel):
    """
    Schema for validating Location data returned from Shiftbase API.
    """
    # Readonly fields
    id: Optional[str] = Field(
        description="The unique identifier of the location",
        pattern=r"^[0-9]+$",
        default=None,
        min_length=1
    )
    account_id: Optional[str] = Field(
        description="The account identifier",
        pattern=r"^[0-9]+$",
        default=None,
        min_length=1
    )
    
    # Required fields
    name: str = Field(
        description="Name of the location",
        min_length=1
    )
    
    # Optional fields
    street_address: Optional[str] = Field(
        description="Street address of the location",
        default=None
    )
    zipcode: Optional[str] = Field(
        description="Zipcode of the location",
        default=None
    )
    city: Optional[str] = Field(
        description="City of the location",
        default=None
    )
    country: Optional[str] = Field(
        description="Country of the location",
        default=None
    )
    email: Optional[str] = Field(
        description="Email address for the location",
        default=None
    )
    telephone: Optional[str] = Field(
        description="Telephone number for the location",
        default=None
    )
    order: Optional[str] = Field(
        description="Used for sorting the location",
        pattern=r"^[0-9]+$",
        default=None,
        min_length=1
    )
    deleted: Optional[bool] = Field(
        description="Indicates whether the location has been deactivated/deleted",
        default=False
    )
    created: Optional[datetime] = Field(
        description="The datetime when the location has been created",
        default=None,
    )
    updated: Optional[datetime] = Field(
        description="The datetime when the location has been updated",
        default=None,
    )
    created_by: Optional[str] = Field(
        description="ID of the user who created the location",
        default=None
    )
    modified_by: Optional[str] = Field(
        description="ID of the user who last modified the location",
        default=None,
        min_length=1
    )
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields 

class TeamShiftSchema(BaseModel):
    """
    Schema for validating Shift data within Team data structure.
    """
    # Define the fields for the Shift object here
    pass

class TeamModelSchema(BaseModel):
    """
    Schema for validating Team data returned from Shiftbase API.
    """
    # Readonly fields
    id: Optional[str] = Field(
        description="The unique identifier for the team",
        pattern=r"^[0-9]+$",
        default=None
    )
    account_id: Optional[str] = Field(
        description="The account ID to which this team belongs to",
        pattern=r"^[0-9]+$",
        default=None
    )
    department_id: Optional[str] = Field(
        description="The department ID this team belongs to",
        pattern=r"^[0-9]+$",
        default=None
    )
    
    # Required fields
    name: str = Field(
        description="The name of the team",
        min_length=1
    )
    
    # Optional fields
    color: Optional[str] = Field(
        description="This must be a valid hexadecimal color like \"#FFFFFF\" for white",
        min_length=1,
        default=None
    )
    order: Optional[str] = Field(
        description="In which order the teams are displayed",
        pattern=r"^[0-9]+$",
        default=None
    )
    created: Optional[datetime] = Field(
        description="When the team was created",
        default=None
    )
    created_by: Optional[str] = Field(
        description="The user ID that created the team",
        pattern=r"^[0-9]+$",
        default=None
    )
    updated: Optional[datetime] = Field(
        description="When the team was last updated",
        default=None
    )
    modified_by: Optional[str] = Field(
        description="The user ID that last updated the team",
        pattern=r"^[0-9]+$",
        default=None
    )
    deleted: Optional[bool] = Field(
        description="If the team is deleted",
        default=False
    )
    deleted_date: Optional[datetime] = Field(
        description="When the team was deleted",
        default=None
    )
    hidden: Optional[bool] = Field(
        description="If the team is hidden",
        default=False
    )
    type: Optional[str] = Field(
        description="default: The team is shown in the schedule an timesheet. "
                    "flexpool: The team is not shown, but the employees within this team can be scheduled in the standard teams. "
                    "hidden: The team is not shown in the schedule and the timesheet, but it is shown in the list of employees.",
        default="default"
    )
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validates team type is one of the allowed values"""
        allowed_values = ["default", "flexpool", "hidden"]
        if v not in allowed_values:
            raise ValueError(f"Invalid team type: {v}. Must be one of {allowed_values}")
        return v
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """Validates color is a valid hex color code"""
        if v is None:
            return v
            
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', v):
            raise ValueError(f"Invalid color format: {v}. Must be a valid hex color code like #FFFFFF")
            
        return v
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields

class DepartmentSchema(BaseModel):
    """Pydantic model for Timesheet response"""
    Department: Optional[DepartmentModelSchema] = Field(None)
    Location: Optional[LocationModelSchema] = Field()
    Team: Optional[List[TeamModelSchema]] = Field()
    Shift: Optional[List] = Field()

class DepartmentCreateSchema(BaseModel):
    """
    Schema for validating department creation data.
    """
    location_id: Optional[str] = Field(
        description="Location identifier",
        pattern=r"^[0-9]+$",
        default=None
    )
    name: str = Field(
        description="Department name",
        min_length=1
    )
    address: Optional[str] = Field(
        description="Department address",
        default=None
    )
    longitude: Optional[str] = Field(
        description="Longitude of the department's location",
        pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,16})?))$",
        default=None
    )
    latitude: Optional[str] = Field(
        description="Latitude of the department's location",
        pattern=r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,16})?))$",
        default=None
    )
    holiday_group_id: Optional[str] = Field(
        description="UUID of the holiday group",
        default=None
    )
    order: Optional[str] = Field(
        description="Used for sorting departments",
        pattern=r"^[0-9]+$",
        default=None
    )
    
    @field_validator('holiday_group_id')
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
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields

class DepartmentCreateResponseSchema(pa.DataFrameModel):
    """
    Validation schema for Department Create response data
    """
    id: Series[str] = pa.Field(description="The unique identifier of the created department")
    
    @pa.check("id")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid

    class Config:
        """Schema configuration"""
        coerce = True
        strict = False
