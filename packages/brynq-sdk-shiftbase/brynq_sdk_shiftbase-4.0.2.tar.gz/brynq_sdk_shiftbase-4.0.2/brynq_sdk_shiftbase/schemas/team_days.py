"""
Schema definition for TeamDay data validation.
"""
import pandera as pa
from pandera.typing import Series
from datetime import datetime, date as date_type

class TeamDaySchema(pa.DataFrameModel):
    """
    Schema for validating TeamDay data returned from Shiftbase API.
    """
    # Read-only fields
    id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    account_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    created: Series[datetime] = pa.Field(nullable=True)
    modified: Series[datetime] = pa.Field(nullable=True)
    created_by: Series[str] = pa.Field(nullable=True)
    modified_by: Series[str] = pa.Field(nullable=True)
    
    # Required fields
    team_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    date: Series[date_type] = pa.Field()  # Date in YYYY-MM-DD format
    
    # Optional fields
    note: Series[str] = pa.Field(nullable=True)  # Team note for the day
    budget_cost: Series[str] = pa.Field(nullable=True)  # Budget for the day
    budget_time: Series[str] = pa.Field(nullable=True)  # Budgeted time in hours
    turnover: Series[str] = pa.Field(nullable=True)  # Turnover for the day
    expenses: Series[str] = pa.Field(nullable=True)  # Expenses for the day
    

    @pa.check("budget_cost", "budget_time", "turnover", "expenses")
    def check_numeric_format(cls, series: Series[str]) -> Series[bool]:
        """Validate numeric fields have correct format (decimal)."""
        valid = series.str.match(r"^([0-9]*[.])?[0-9]+$") | series.isna()
        return valid 