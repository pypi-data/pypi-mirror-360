"""
Schema definition for Log data validation.
"""
import pandera as pa
from pandera.typing import Series
from datetime import datetime
from datetime import date as date_type
class LogSchema(pa.DataFrameModel):
    """
    Schema for validating Log data returned from Shiftbase API.
    
    The log contains daily information per department such as the turnover and 
    expected turnover as well as the publishing status of a schedule and 
    if timesheets are open for modification.
    """
    # Required fields
    id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    department_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    date: Series[date_type] = pa.Field()
    
    # Read-only fields
    account_id: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    created: Series[datetime] = pa.Field(nullable=True)
    modified: Series[datetime] = pa.Field(nullable=True)
    created_by: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    modified_by: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    turnover: Series[str] = pa.Field(nullable=True)
    expenses: Series[str] = pa.Field(nullable=True)
    
    # Optional fields
    finished_timesheet: Series[bool] = pa.Field(nullable=True)
    published_schedule: Series[bool] = pa.Field(nullable=True)
    log: Series[str] = pa.Field(nullable=True)
    expected_turnover: Series[str] = pa.Field(nullable=True)
    
    @pa.check("date")
    def validate_date(cls, series: Series[str]) -> Series[bool]:
        """Validates date format YYYY-MM-DD"""
        return series.str.match(r"^\d{4}-\d{2}-\d{2}$") 