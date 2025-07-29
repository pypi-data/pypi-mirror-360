"""
Schema definition for AbsenteeOption data validation.
"""
import pandera as pa
from pandera.typing import Series
from typing import Optional, Literal, List
from enum import Enum
from pydantic import BaseModel, Field


class AbsenteeIcon(str, Enum):
    """Allowed values for absence icons"""
    LEAVE_1 = "leave-1"
    LEAVE_2 = "leave-2"
    LEAVE_4 = "leave-4"
    LEAVE_5 = "leave-5"
    LEAVE_6 = "leave-6"
    BAN = "ban"
    BELL = "bell"
    BOOK = "book"
    BULLHORN = "bullhorn"
    CALCULATOR = "calculator"
    CALENDAR = "calendar"
    CALENDAR_DAY = "calendar-day"
    CALENDAR_GROUP = "calendar-group"
    CALENDAR_MONTH = "calendar-month"
    CALENDAR_WEEK = "calendar-week"
    CALENDAR_APPROVED = "calendar_approved"
    CALENDAR_DENIED = "calendar_denied"
    CAR = "car"
    CHANGE_SHIFT = "change_shift"
    COFFEE = "coffee"
    COMMENT = "comment"
    CLIPBOARD = "clipboard"
    CUTLERY = "cutlery"
    EXCLAMATION_TRIANGLE = "exclamation-triangle"
    DELETE = "delete"
    EYE = "eye"
    FLAG = "flag"
    INFO = "info"
    MAP_MARKER = "map-marker"
    PAPER_PLANE = "paper-plane"
    PAYMENT = "payment"
    RECLOCK = "reclock"
    TEAM = "team"
    STOPWATCH = "stopwatch"
    TOUR = "tour"
    ZOOM = "zoom"
    OVERTIME = "overtime"
    ABSENTEE_VACATION = "absentee-vacation"
    ABSENTEE_SICK = "absentee-sick"
    ABSENTEE_UNAVAILABLE = "absentee-unavailable"
    ABSENTEE_NATIONAL_DAY = "absentee-national_day"
    ABSENTEE_MATERNITY_LEAVE = "absentee_maternity_leave"
    ABSENTEE_OTHER = "absentee_other"
    RATECARD = "ratecard"


class RosterAction(str, Enum):
    """Allowed values for default_roster_action"""
    HIDE = "hide"
    NONE = "none"
    MOVE_TO_OPEN_SHIFT = "move_to_open_shift"


class UnitType(str, Enum):
    """Allowed values for unit"""
    HOURS = "hours"
    DAYS = "days"


class AbsenteeOptionSchema(pa.DataFrameModel):
    """
    Schema for validating AbsenteeOption data returned from Shiftbase API.
    """
    # Required Fields
    id: Series[str] = pa.Field(
        description="Unique identifier for the absence type",
        coerce=True,
        nullable=False
    )
    account_id: Series[str] = pa.Field(
        description="Account identifier for the absence type",
        coerce=True,
        nullable=False
    )
    option: Series[str] = pa.Field(
        description="Name of the absence type",
        coerce=True,
        nullable=False
    )
    percentage: Series[str] = pa.Field(
        description="Surcharge percentage by which the absence should be recorded",
        coerce=True,
        nullable=False
    )
    weight: Series[str] = pa.Field(
        description="Used for ordering the absence types",
        coerce=True,
        nullable=False
    )
    has_vacation_accrual: Series[bool] = pa.Field(
        description="Leave hours are accrued during the absence",
        coerce=True,
        nullable=False
    )
    costs_vacation_hours: Series[bool] = pa.Field(
        description="Deduct hours from vacation hours",
        coerce=True,
        nullable=False
    )
    is_counted: Series[bool] = pa.Field(
        description="If set to false no hours are calculated for this type",
        coerce=True,
        nullable=False
    )
    has_wait_hours: Series[bool] = pa.Field(
        description="When an absence of this type is requested, wait hours can be specified",
        coerce=True,
        nullable=False
    )
    leave: Series[bool] = pa.Field(
        description="Determines if absence falls under leave or non-attendance group",
        coerce=True,
        nullable=False
    )
    color: Series[str] = pa.Field(
        description="Color of the absence in the schedule (hexadecimal)",
        coerce=True,
        nullable=False
    )
    icon: Series[str] = pa.Field(
        description="Icon shown with the absence type",
        coerce=True,
        nullable=False,
        # Validation will be handled separately in a schema level check
    )
    deleted: Series[bool] = pa.Field(
        description="Whether the absence type is deleted (read-only)",
        coerce=True,
        nullable=False
    )
    
    # Optional Fields
    permission: Series[str] = pa.Field(
        description="Permission name (deprecated, read-only)",
        coerce=True,
        nullable=True
    )
    default_roster_action: Series[str] = pa.Field(
        description="Sets the default intermediate shift option on an absence request",
        coerce=True,
        nullable=True
    )
    allow_open_ended: Series[bool] = pa.Field(
        description="Whether the absence type allows open-ended requests",
        coerce=True,
        nullable=True
    )
    unit: Series[str] = pa.Field(
        description="Whether absence is measured in days or hours",
        coerce=True,
        nullable=True
    )

        
    @pa.check("icon")
    def check_icon_values(cls, series: Series) -> Series:
        """Validates that icon values are from the allowed list"""
        allowed_values = [icon.value for icon in AbsenteeIcon]
        mask = series.isin(allowed_values)
        if not mask.all():
            invalid_values = series[~mask].unique().tolist()
            # Just emit a warning but don't fail - new icon values might be added in the future
            pa.errors.SchemaWarning(
                f"Found invalid icon values: {invalid_values}. "
                f"Allowed values are: {allowed_values}"
            )
        return mask
    
    @pa.check("default_roster_action")
    def check_roster_action_values(cls, series: Series) -> Series:
        """Validates that default_roster_action values are from the allowed list"""
        allowed_values = [action.value for action in RosterAction]
        # Skip None/NaN values
        mask = series.isnull() | series.isin(allowed_values)
        return mask
    
    @pa.check("unit")
    def check_unit_values(cls, series: Series) -> Series:
        """Validates that unit values are from the allowed list"""
        allowed_values = [unit.value for unit in UnitType]
        # Skip None/NaN values
        mask = series.isnull() | series.isin(allowed_values)
        return mask

    class Config:
        """Schema configuration"""
        coerce = True
        strict = False


class AbsenteeOptionCreateSchema(BaseModel):
    """
    Schema for validating AbsenteeOption creation data.
    This schema is used when creating new absence types in Shiftbase.
    """
    # Required fields
    option: str = Field(
        description="Name of the absence type",
        max_length=160
    )
    percentage: str = Field(
        description="Surcharge percentage by which the absence should be recorded",
        pattern=r"^[0-9]+$"
    )
    weight: str = Field(
        description="Used for ordering the absence types",
        pattern=r"^[0-9]+$"
    )
    has_vacation_accrual: bool = Field(
        description="Leave hours are accrued during the absence"
    )
    costs_vacation_hours: bool = Field(
        description="Deduct hours from vacation hours"
    )
    is_counted: bool = Field(
        description="If set to false no hours are calculated for this type"
    )
    has_wait_hours: bool = Field(
        description="When an absence of this type is requested, wait hours can be specified"
    )
    leave: bool = Field(
        description="Determines if absence falls under leave or non-attendance group"
    )
    color: str = Field(
        description="Color of the absence in the schedule (hexadecimal)",
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    icon: str = Field(
        description="Icon shown with the absence type"
    )
    
    # Optional fields
    default_roster_action: Optional[RosterAction] = Field(
        description="Sets the default intermediate shift option on an absence request",
        default=RosterAction.HIDE
    )
    allow_open_ended: Optional[bool] = Field(
        description="Whether the absence type allows open-ended requests",
        default=False
    )
    unit: Optional[UnitType] = Field(
        description="Whether absence is measured in days or hours",
        default=UnitType.HOURS
    )
    group_ids: Optional[List[str]] = Field(
        description="List of group IDs that can request the absence type",
    )
    
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True 


class AbsenteeOptionUpdateSchema(BaseModel):
    """
    Schema for validating AbsenteeOption update data.
    This schema is used when updating existing absence types in Shiftbase.
    """
    # Required fields
    option: str = Field(
        description="Name of the absence type",
        max_length=160
    )
    percentage: str = Field(
        description="Surcharge percentage by which the absence should be recorded",
        pattern=r"^[0-9]+$"
    )
    weight: str = Field(
        description="Used for ordering the absence types",
        pattern=r"^[0-9]+$"
    )
    has_vacation_accrual: bool = Field(
        description="Leave hours are accrued during the absence"
    )
    costs_vacation_hours: bool = Field(
        description="Deduct hours from vacation hours"
    )
    is_counted: bool = Field(
        description="If set to false no hours are calculated for this type"
    )
    has_wait_hours: bool = Field(
        description="When an absence of this type is requested, wait hours can be specified"
    )
    leave: bool = Field(
        description="Determines if absence falls under leave or non-attendance group"
    )
    color: str = Field(
        description="Color of the absence in the schedule (hexadecimal)",
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    icon: str = Field(
        description="Icon shown with the absence type"
    )
    
    # Optional fields
    default_roster_action: Optional[str] = Field(
        description="Sets the default intermediate shift option on an absence request",
        default="hide"
    )
    allow_open_ended: Optional[bool] = Field(
        description="Whether the absence type allows open-ended requests",
        default=False
    )
    unit: Optional[str] = Field(
        description="Whether absence is measured in days or hours",
        default="hours"
    )
    group_ids: Optional[List[str]] = Field(
        description="List of group IDs that can request the absence type",
    )
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True 