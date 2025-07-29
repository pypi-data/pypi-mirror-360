import pandera as pa
from pandera.typing import Series
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum
from datetime import date as date_type
class ClockBreakSchema(pa.DataFrameModel):
    """
    Validation schema for ClockBreak data from Shiftbase API
    """
    id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    account_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    timesheet_id: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    
    # Clock in data
    clocked_in: Series[str] = pa.Field(nullable=True)
    clocked_in_latitude: Series[str] = pa.Field(nullable=True)
    clocked_in_longitude: Series[str] = pa.Field(nullable=True)
    clocked_in_accuracy: Series[str] = pa.Field(nullable=True)
    clocked_in_ip: Series[str] = pa.Field(nullable=True)
    clocked_in_origin: Series[str] = pa.Field(nullable=True)
    clocked_in_verified_by: Series[str] = pa.Field(nullable=True)
    
    # Clock out data
    clocked_out: Series[str] = pa.Field(nullable=True)
    clocked_out_latitude: Series[str] = pa.Field(nullable=True)
    clocked_out_longitude: Series[str] = pa.Field(nullable=True)
    clocked_out_accuracy: Series[str] = pa.Field(nullable=True)
    clocked_out_ip: Series[str] = pa.Field(nullable=True)
    clocked_out_origin: Series[str] = pa.Field(nullable=True)
    clocked_out_verified_by: Series[str] = pa.Field(nullable=True)
    
    # Management data
    created: Series[datetime] = pa.Field()
    modified: Series[datetime] = pa.Field()
    created_by: Series[str] = pa.Field(regex=r"^[0-9]+$")
    modified_by: Series[str] = pa.Field(regex=r"^[0-9]+$")
    duration: Series[str] = pa.Field(nullable=True)
    
    @pa.check("duration")
    def check_duration_format(cls, series: Series[str]) -> Series[bool]:
        """Validate duration has correct format."""
        valid = series.str.match(r"^([0-9]*[.])?[0-9]+$") | series.isna()
        return valid 

class ClockSchema(pa.DataFrameModel):
    """
    Validation schema for Clock data from Shiftbase API
    """
    department_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    team_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    shift_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    user_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    roster_id: Series[str] = pa.Field(nullable=True, regex=r"^[0-9]+$")
    break_time: Series[int] = pa.Field(ge=0)
    date: Series[date_type] = pa.Field(coerce=True)
    starttime: Series[str] = pa.Field(coerce=True)

    class Config:
        strict = False
        coerce = True

class CreateTimeSheetSchema(pa.DataFrameModel):
    """
    Validation schema for creating new Timesheet data in Shiftbase API
    """
    user_id: Series[str] = pa.Field()
    team_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    shift_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    roster_id: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    rate_card_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    date: Series[date_type] = pa.Field(coerce=True)
    starttime: Series[str] = pa.Field(coerce=True)
    endtime: Series[str] = pa.Field(nullable=True, coerce=True)
    clocked_in: Series[datetime] = pa.Field(nullable=True)
    clocked_in_latitude: Series[str] = pa.Field(nullable=True, regex=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$")
    clocked_in_longitude: Series[str] = pa.Field(nullable=True, regex=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$")
    clocked_in_accuracy: Series[str] = pa.Field(nullable=True, regex=r"^([0-9]*[.])?[0-9]+$")
    clocked_out: Series[str] = pa.Field(nullable=True)
    clocked_out_latitude: Series[str] = pa.Field(nullable=True, regex=r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$")
    clocked_out_longitude: Series[str] = pa.Field(nullable=True, regex=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$")
    clocked_out_accuracy: Series[str] = pa.Field(nullable=True, regex=r"^([0-9]*[.])?[0-9]+$")
    clocked_out_verified_by: Series[str] = pa.Field(nullable=True)
    total: Series[str] = pa.Field(nullable=True)
    status: Series[str] = pa.Field(nullable=True)
    break_time: Series[str] = pa.Field(nullable=True)
    meals: Series[str] = pa.Field(nullable=True)
    kilometers: Series[str] = pa.Field(nullable=True)
    note: Series[str] = pa.Field(nullable=True)
    clock: Series[bool] = pa.Field(nullable=True)
    custom_fields: Series[object] = pa.Field(nullable=True)
    department_id: Series[str] = pa.Field(nullable=True)
    notify: Series[bool] = pa.Field(nullable=True)

    @pa.check("status")
    def check_status_values(cls, series: Series[str]) -> Series[bool]:
        """Validate status is one of: Approved, Declined, Pending"""
        valid = series.isin(["Approved", "Declined", "Pending"]) | series.isna()
        return valid

    class Config:
        strict = False
        coerce = True

class CreateTimeSheetPydanticSchema(BaseModel):
    """
    Pydantic validation schema for creating new Timesheet data in Shiftbase API
    """
    user_id: str
    team_id: str = Field(..., pattern=r"^[0-9]+$")
    shift_id: str = Field(..., pattern=r"^[0-9]+$")
    roster_id: Optional[str] = Field(None, pattern=r"^[0-9]+$")
    rate_card_id: str = Field(..., pattern=r"^[0-9]+$")
    date: date_type
    starttime: str
    endtime: Optional[str] = None
    clocked_in: Optional[datetime] = None
    clocked_in_latitude: Optional[str] = Field(None, pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$")
    clocked_in_longitude: Optional[str] = Field(None, pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$")
    clocked_in_accuracy: Optional[str] = Field(None, pattern=r"^([0-9]*[.])?[0-9]+$")
    clocked_out: Optional[datetime] = None
    clocked_out_latitude: Optional[str] = Field(None, pattern=r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$")
    clocked_out_longitude: Optional[str] = Field(None, pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$")
    clocked_out_accuracy: Optional[str] = Field(None, pattern=r"^([0-9]*[.])?[0-9]+$")
    clocked_out_verified_by: Optional[str] = None
    total: Optional[str] = None
    status: Optional[str] = None
    break_time: Optional[str] = None
    meals: Optional[str] = None
    kilometers: Optional[str] = None
    note: Optional[str] = None
    clock: Optional[bool] = None
    custom_fields: Optional[Dict[str, Any]] = None

    @field_validator('status')
    @classmethod
    def validate_status_values(cls, v):
        """Validate status is one of: Approved, Declined, Pending"""
        if v is None:
            return v
        valid_statuses = ["Approved", "Declined", "Pending"]
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {", ".join(valid_statuses)}')
        return v


    def model_dump(self):
        data = super().model_dump(exclude_none=True)
        # Convert date and time fields to strings for API compatibility
        if 'date' in data:
            data['date'] = data['date'].isoformat()

        if 'clocked_in' in data:
            data['clocked_in'] = data['clocked_in'].isoformat()

        if 'clocked_out' in data:
            data['clocked_out'] = data['clocked_out'].isoformat()

        # Rename break_time to break for API compatibility if it exists
        if "break_time" in data:
            data["break"] = data.pop("break_time")

        return data
    
# New nested Pydantic schemas based on the provided data structure

class ClockOrigin(str, Enum):
    """Enum for clock origin values"""
    TERMINAL = "terminal"
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API = "api"

class TimesheetStatus(str, Enum):
    """Enum for timesheet status values"""
    APPROVED = "Approved"
    DECLINED = "Declined"
    PENDING = "Pending"

class RateBlockModel(BaseModel):
    """Pydantic model for Rate Block"""
    date: Optional[date_type] = Field(None, description="Date of the rate block")
    starttime: Optional[str] = Field(None, description="Start time of the rate block")
    endtime: Optional[str] = Field(None, description="End time of the rate block")
    duration: Optional[float] = Field(None, description="Duration of rate block in minutes")
    paid_percentage: Optional[str] = Field(None, description="Surcharge of the rate block (e.g. 100, 150)")
    paid_percentage_id: Optional[str] = Field(None, description="ID of the paid percentage")
    time_percentage: Optional[str] = Field(None, description="Surcharge of the rate block")
    time_percentage_id: Optional[str] = Field(None, description="ID of the time percentage")
    break_time: Optional[str] = Field(None, alias="break", description="Duration of break in minutes")
    surcharge_pay: Optional[float] = Field(None, description="Surcharge hours (Paid)")
    surcharge_time: Optional[float] = Field(None, description="Surcharge hours (time)")

class RatesModel(BaseModel):
    """Pydantic model for Rates"""
    duration: Optional[float] = Field(None, description="Duration of rate in minutes")
    surcharge_pay: Optional[float] = Field(None, description="Surcharge hours (paid)")
    surcharge_time: Optional[float] = Field(None, description="Surcharge hours (time)")
    worked_for_vacation: Optional[float] = Field(None, description="Hours worked for vacation calculation")
    RateBlock: Optional[List[RateBlockModel]] = Field(description="Calculated rate blocks based on Rate Card settings")

class ClockBreakModel(BaseModel):
    """Pydantic model for Clock Break"""
    id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="Clock break ID")
    account_id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="Account ID")
    timesheet_id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="Timesheet ID")
    
    # Clock in data
    clocked_in: Optional[datetime] = Field(None, description="Date of the clock in action")
    clocked_in_latitude: Optional[str] = Field(
        None, 
        pattern=r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$",
        description="Latitude of the clock in location"
    )
    clocked_in_longitude: Optional[str] = Field(
        None, 
        pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$",
        description="Longitude of the clock in location"
    )
    clocked_in_accuracy: Optional[str] = Field(
        None, 
        pattern=r"^([0-9]*[.])?[0-9]+$",
        description="The accuracy of the latitude and longitude in meters"
    )
    clocked_in_ip: Optional[str] = Field(None, description="IP address of the clock in action")
    clocked_in_origin: Optional[ClockOrigin] = Field(None, description="Origin of the clocking in action")
    clocked_in_verified_by: Optional[str] = Field(None, description="User id of the employee who verified the clock in action")
    
    # Clock out data
    clocked_out: Optional[datetime] = Field(None, description="Date of the clock out action")
    clocked_out_latitude: Optional[str] = Field(
        None, 
        pattern=r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$",
        description="Latitude of the clock out location"
    )
    clocked_out_longitude: Optional[str] = Field(
        None, 
        pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$",
        description="Longitude of the clock out location"
    )
    clocked_out_accuracy: Optional[str] = Field(
        None, 
        pattern=r"^([0-9]*[.])?[0-9]+$",
        description="The accuracy of the latitude and longitude in meters"
    )
    clocked_out_ip: Optional[str] = Field(None, description="IP address of the clock out action")
    clocked_out_origin: Optional[ClockOrigin] = Field(None, description="Origin of the clocking out action")
    clocked_out_verified_by: Optional[str] = Field(None, description="User id of the employee who verified the clock out action")
    
    # Management data
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="ID of user who created the record")
    modified_by: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="ID of user who last modified the record")
    duration: Optional[str] = Field(None, description="Duration in minutes")

class TimesheetModel(BaseModel):
    """Pydantic model for Timesheet"""
    id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="Timesheet ID")
    account_id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="Account ID")
    user_id: Optional[str] = Field(None, description="User ID")
    team_id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="Team ID")
    shift_id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="Shift ID")
    roster_id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="ID of the schedule")
    rate_card_id: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="Rate Card ID")
    date: Optional[date_type] = Field(None, description="Date of the timesheet")
    starttime: Optional[str] = Field(None, description="Start time of the timesheet")

    # Clock in data
    clocked_in: Optional[datetime] = Field(None, description="Date of the clock in action")
    clocked_in_latitude: Optional[str] = Field(
        None, 
        pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$",
        description="Latitude of the clock in location"
    )
    clocked_in_longitude: Optional[str] = Field(
        None, 
        pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$",
        description="Longitude of the clock in location"
    )
    clocked_in_accuracy: Optional[str] = Field(
        None, 
        pattern=r"^([0-9]*[.])?[0-9]+$",
        description="The accuracy of the latitude and longitude in meters"
    )
    clocked_in_ip: Optional[str] = Field(None, description="IP address of the clock in action")
    clocked_in_origin: Optional[ClockOrigin] = Field(None, description="Origin of the clocking action")
    clocked_in_verified_by: Optional[str] = Field(None, description="User id of the employee who verified the clock in action")
    
    # End time and clock out data
    endtime: Optional[str] = Field(None, description="End time of the timesheet")
    clocked_out: Optional[datetime] = Field(None, description="Date of the clock out action")
    clocked_out_latitude: Optional[str] = Field(
        None, 
        pattern=r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$",
        description="Latitude of the clock out location"
    )
    clocked_out_longitude: Optional[str] = Field(
        None, 
        pattern=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$",
        description="Longitude of the clock out location"
    )
    clocked_out_accuracy: Optional[str] = Field(
        None, 
        pattern=r"^([0-9]*[.])?[0-9]+$",
        description="The accuracy of the latitude and longitude in meters"
    )
    clocked_out_ip: Optional[str] = Field(None, description="IP address of the clock out action")
    clocked_out_origin: Optional[ClockOrigin] = Field(None, description="Origin of the clockout action")
    clocked_out_verified_by: Optional[str] = Field(None, description="User id of the employee who verified the clock out action")
    
    # Break and additional data
    clocked_break: Optional[str] = Field(None, description="Clocked break in minutes")
    total: Optional[str] = Field(None, description="Total worked hours")
    worked_for_vacation: Optional[str] = Field(None, description="Worked hours for vacation calculation")
    surcharge_time: Optional[str] = Field(None, description="Surcharge hours (time)")
    surcharge_pay: Optional[str] = Field(None, description="Surcharge hours (paid)")
    status: Optional[TimesheetStatus] = Field(None, description="Status of the timesheet")
    break_time: Optional[str] = Field(None, alias="break", description="Duration of break in minutes")
    meals: Optional[str] = Field(None, description="Registered number of Meals")
    kilometers: Optional[str] = Field(None, description="Registered driven kilometers")
    note: Optional[str] = Field(None, description="Note for the timesheet")
    clock: Optional[bool] = Field(None, description="If the timesheet is clock based")
    custom_fields: Optional[List[Dict[str, Any]]] = Field(description="Timesheet custom fields")
    
    # Management data
    deleted: Optional[bool] = Field(None, description="Whether the timesheet is deleted")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    reviewed: Optional[str] = Field(None, description="Review timestamp")
    created_by: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="ID of user who created the record")
    modified_by: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="ID of user who last modified the record")
    reviewed_by: Optional[str] = Field(None, pattern=r"^[0-9]+$", description="ID of user who reviewed the record")
    
    # Financial data
    wage: Optional[str] = Field(None, description="Wage per hour")
    surcharge_total: Optional[float] = Field(None, description="Total surcharge")
    salary: Optional[float] = Field(None, description="Salary of the worked hours")
    coc: Optional[float] = Field(None, description="Cost to company")
    active_clock: Optional[bool] = Field(None, description="If the timesheet is an active clock")
    
    # Related data
    Rates: Optional[RatesModel] = Field(None, description="Calculated rate model")

class TimesheetSchema(BaseModel):
    """Pydantic model for Timesheet response"""
    Timesheet: Optional[TimesheetModel] = Field(None)
    ClockBreak: Optional[List[ClockBreakModel]] = Field()
