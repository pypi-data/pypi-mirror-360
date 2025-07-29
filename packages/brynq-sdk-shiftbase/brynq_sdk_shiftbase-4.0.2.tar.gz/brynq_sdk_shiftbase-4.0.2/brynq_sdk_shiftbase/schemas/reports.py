"""
Schema definition for Reporting data validation.
"""
import pandera as pa
from pandera.typing import Series
from typing import Dict, List, Optional
import re
from pydantic import BaseModel, Field,  model_validator, field_validator
from datetime import datetime, date as date_type
# Pydantic models for nested JSON structures in report parameters
class ReportPeriod(BaseModel):
    """Represents a date period with from and to dates."""
    from_date: str = Field(alias="from")
    to_date: str = Field(alias="to")
    
    class Config:
        validate_by_name = True

class ReportParameters(BaseModel):
    """
    The Report parameters model contains all the possible parameters.
    It depends on the report type, which parameters are available.
    """
    from_date: Optional[date_type] = Field(None, alias="from", pattern=r"^\d{4}-\d{2}-\d{2}$")
    to_date: Optional[date_type] = Field(None, alias="to", pattern=r"^\d{4}-\d{2}-\d{2}$")
    user: Optional[str] = Field(None, pattern=r"^[0-9]*$")
    team: Optional[List[str]] = None
    shift: Optional[List[str]] = None
    contractDepartment: Optional[List[str]] = None
    contractType: Optional[List[str]] = None
    absenteeOption: Optional[str] = None
    approvalStatus: Optional[List[str]] = None
    availabilityStatus: Optional[str] = None
    department: Optional[List[str]] = None
    finishedTimesheet: Optional[str] = "both"
    contractPeriod: Optional[ReportPeriod] = None
    workedPeriod: Optional[ReportPeriod] = None
    integration_id: Optional[str] = None
    exportContract: Optional[bool] = None
    exportWorked: Optional[bool] = None
    payrollYear: Optional[str] = None
    payrollFrequency: Optional[str] = None
    payslipType: Optional[int] = None
    groupDayStats: Optional[str] = "total"
    groupByLocationWithTeam: Optional[str] = "department"
    groupByPeriod: Optional[str] = "day"
    employeeCurrentStatus: Optional[str] = "both"
    timeOffBalance: Optional[str] = None
    columns: Optional[List[str]] = None
    
    @model_validator(mode='after')
    def validate_fields(self):
        # Validate approval status values
        approval_statuses = self.approvalStatus
        if approval_statuses:
            valid_statuses = ["Approved", "Pending", "Declined"]
            for status in approval_statuses:
                if status not in valid_statuses:
                    raise ValueError(f"Invalid approval status: {status}. Must be one of {valid_statuses}")
        
        # Validate availability status
        availability_status = self.availabilityStatus
        if availability_status:
            valid_statuses = ["Available all day", "Available from", "Unavailable all day", "Unavailable from"]
            if availability_status not in valid_statuses:
                raise ValueError(f"Invalid availability status: {availability_status}. Must be one of {valid_statuses}")
        
        # Validate finished timesheet
        finished_timesheet = self.finishedTimesheet
        if finished_timesheet and finished_timesheet not in ["both", "closed", "open"]:
            raise ValueError("finishedTimesheet must be 'both', 'closed' or 'open'")
            
        # Validate payroll frequency
        payroll_frequency = self.payrollFrequency
        if payroll_frequency and payroll_frequency not in ["month", "weeks-4"]:
            raise ValueError("payrollFrequency must be 'month' or 'weeks-4'")
            
        return self
    
    class Config:
        validate_by_name = True

class PeriodSettings(BaseModel):
    """Period settings for recurring reports."""
    type: str
    
    @model_validator(mode='after')
    def validate_type(self):
        valid_types = [
            "today", "yesterday", "last-week", "last-calendar-month", 
            "last-7-days", "last-30-days", "tomorrow", "next-week", 
            "next-calendar-month", "next-7-days", "next-30-days"
        ]
        if self.type not in valid_types:
            raise ValueError(f"Invalid period type: {self.type}. Must be one of {valid_types}")
        return self

class RecurrenceSettings(BaseModel):
    """Recurrence settings for recurring reports."""
    interval: str
    runTime: str
    dayOfWeek: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_fields(self):
        # Validate interval
        if self.interval not in ["daily", "weekly", "monthly", "quarterly"]:
            raise ValueError(f"Invalid interval: {self.interval}. Must be one of ['daily', 'weekly', 'monthly', 'quarterly']")
        
        # Validate day of week for weekly interval
        if self.interval == "weekly":
            if not self.dayOfWeek:
                raise ValueError("dayOfWeek is required for weekly interval")
            valid_days = ["mo", "tu", "we", "th", "fr", "sa", "su"]
            if self.dayOfWeek not in valid_days:
                raise ValueError(f"Invalid dayOfWeek: {self.dayOfWeek}. Must be one of {valid_days}")
            
        return self

class ReportSettings(BaseModel):
    """Report settings for recurring reports."""
    type: str
    parameters: ReportParameters
    
    @model_validator(mode='after')
    def validate_type(self):
        valid_types = [
            "Dashboard", "PeriodOverview", "DailyPeriodOverview", "ScheduleSummary",
            "Schedules", "TimesheetSummary", "Timesheets", "FinishedTimesheets",
            "DayLog", "ScheduleVsTimesheet", "Employees", "Absence", "Availabilities",
            "PlusMin", "EmployeeBalanceSummary", "EmployeeBalanceDetails", "Turnover",
            "Payroll", "PayrollIntegration", "OpenShifts", "Skills", "PermissionGroups",
            "RequiredShifts"
        ]
        if self.type not in valid_types:
            raise ValueError(f"Invalid report type: {self.type}. Must be one of {valid_types}")
        return self

class RecurringReportSchema(BaseModel):
    """Schema for validating RecurringReport data."""
    id: Optional[str] = None
    name: str
    periodSettings: PeriodSettings
    recurrenceSettings: RecurrenceSettings
    reportSettings: ReportSettings
    nextRun: Optional[datetime] = None

class ReportingFavoriteSchema(BaseModel):
    """Schema for validating ReportingFavorite data."""
    id: Optional[str] = None
    name: str
    type: str
    parameters: Dict
    
    @model_validator(mode='after')
    def validate_type(self):
        valid_types = [
            "Dashboard", "PeriodOverview", "DailyPeriodOverview", "ScheduleSummary",
            "Schedules", "TimesheetSummary", "Timesheets", "FinishedTimesheets",
            "DayLog", "ScheduleVsTimesheet", "Employees", "Absence", "Availabilities",
            "PlusMin", "EmployeeBalanceSummary", "EmployeeBalanceDetails", "Turnover",
            "Payroll", "PayrollIntegration", "OpenShifts", "Skills", "PermissionGroups",
            "RequiredShifts"
        ]
        if self.type not in valid_types:
            raise ValueError(f"Invalid report type: {self.type}. Must be one of {valid_types}")
        return self

class AbsenteeReportRequestSchema(BaseModel):
    """Schema for validating Absentee Report request data."""
    export: Optional[str] = Field(
        "raw", 
        description="The format of the returned report",
        pattern=r"^(raw|json|csv|xlxs)$"
    )
    from_date: str = Field(
        ..., 
        alias="from",
        description="Start of period (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    to_date: str = Field(
        ..., 
        alias="to",
        description="End of period (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    columns: Optional[List[str]] = Field(
        None,
        description="Specify the desired columns, if empty all available columns are returned"
    )
    user: Optional[str] = Field(
        None,
        description="User ID filter",
        pattern=r"^[0-9]+$"
    )
    absenteeOption: Optional[str] = Field(
        None,
        description="Absentee option filter"
    )
    contractType: Optional[List[str]] = Field(
        None,
        description="Contract type filter"
    )
    contractDepartment: Optional[List[str]] = Field(
        None,
        description="Contract department filter"
    )
    approvalStatus: Optional[List[str]] = Field(
        None,
        description="Approval status filter",
    )
    
    @field_validator('approvalStatus')
    @classmethod
    def validate_approval_status(cls, v):
        """Validates approval status values"""
        if v is None:
            return v
        
        valid_values = ["Approved", "Pending", "Declined"]
        for status in v:
            if status not in valid_values:
                raise ValueError(f"Invalid approval status: {status}. Must be one of {valid_values}")
        return v
    
    @field_validator('contractType', 'contractDepartment')
    @classmethod
    def validate_numeric_id_list(cls, v):
        """Validates numeric ID lists"""
        if v is None:
            return v
        
        for id_value in v:
            if not re.match(r"^[0-9]+$", id_value):
                raise ValueError(f"Invalid ID format: {id_value}. Must contain only digits")
        return v
    
    class Config:
        """Pydantic configuration"""
        populate_by_name = True

# Pandera schema for requested reports list
class ReportSchema(pa.DataFrameModel):
    """
    Schema for validating Report data returned from Shiftbase API.
    """
    id: Series[str] = pa.Field()
    name: Series[str] = pa.Field()
    status: Series[str] = pa.Field()
    created: Series[str] = pa.Field(nullable=True)
    updated: Series[str] = pa.Field(nullable=True)
    
    @pa.check("status")
    def check_status_value(cls, series: Series[str]) -> Series[bool]:
        """Validate status field has correct value."""
        valid_values = ["created", "running", "completed", "failed"]
        valid = series.isin(valid_values) | series.isna()
        return valid 