"""
Schema definition for Roster data validation.
"""
import pandera as pa
from pandera.typing import Series
from datetime import datetime, date as date_type

class RosterSchema(pa.DataFrameModel):
    """
    Schema for validating Roster data returned from Shiftbase API.
    """
    # Read-only fields
    id: Series[str] = pa.Field(nullable=True, regex=r"^[0-9]+$")
    occurrence_id: Series[str] = pa.Field(regex=r"^[0-9]+:[0-9]{4}\-[0-9]{2}\-[0-9]{2}$")
    account_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    created: Series[datetime] = pa.Field(nullable=True)
    modified: Series[datetime] = pa.Field(nullable=True)
    deleted: Series[bool] = pa.Field(nullable=True)
    color: Series[str] = pa.Field(nullable=True)
    name: Series[str] = pa.Field(nullable=True)
    is_task: Series[bool] = pa.Field(nullable=True)
    created_by: Series[str] = pa.Field(nullable=True)
    modified_by: Series[str] = pa.Field(nullable=True)
    rate_card_id: Series[str] = pa.Field(nullable=True)
    start_seconds: Series[int] = pa.Field(nullable=True)
    end_seconds: Series[int] = pa.Field(nullable=True)
    
    # Required fields
    team_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    shift_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    user_id: Series[str] = pa.Field()  # Can be string or array
    date: Series[date_type] = pa.Field()
    starttime: Series[str] = pa.Field()
    endtime: Series[str] = pa.Field()
    break_time: Series[str] = pa.Field()  # Rename break to break_time to avoid Python keyword
    
    # Optional fields
    department_id: Series[str] = pa.Field(nullable=True)
    first_occurrence: Series[str] = pa.Field(nullable=True)
    hide_end_time: Series[bool] = pa.Field(nullable=True)
    description: Series[str] = pa.Field(nullable=True)
    
    # Recurring fields
    recurring: Series[bool] = pa.Field(nullable=True)
    repeat_until: Series[str] = pa.Field(nullable=True)
    nr_of_repeats: Series[str] = pa.Field(nullable=True)
    interval: Series[str] = pa.Field(nullable=True, regex=r"^[0-9]+$")
    mo: Series[bool] = pa.Field(nullable=True)
    tu: Series[bool] = pa.Field(nullable=True)
    we: Series[bool] = pa.Field(nullable=True)
    th: Series[bool] = pa.Field(nullable=True)
    fr: Series[bool] = pa.Field(nullable=True)
    sa: Series[bool] = pa.Field(nullable=True)
    su: Series[bool] = pa.Field(nullable=True)
    
    # Additional fields
    wage: Series[str] = pa.Field(nullable=True)
    loaned: Series[bool] = pa.Field(nullable=True)
    total: Series[float] = pa.Field(nullable=True)
    