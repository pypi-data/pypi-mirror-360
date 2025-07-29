"""
Schema definition for RequiredShift data validation.
"""
import pandera as pa
from pandera.typing import Series
from datetime import datetime, date as date_type

class RequiredShiftSchema(pa.DataFrameModel):
    """
    Schema for validating RequiredShift data returned from Shiftbase API.
    """
    # Read-only fields
    id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    occurrence_id: Series[str] = pa.Field(nullable=True, regex=r"^[0-9]+:[0-9]{4}\-[0-9]{2}\-[0-9]{2}$")
    account_id: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    created_by: Series[str] = pa.Field(nullable=True)
    modified_by: Series[str] = pa.Field(nullable=True)
    created: Series[datetime] = pa.Field(nullable=True)
    updated: Series[datetime] = pa.Field(nullable=True)
    deleted: Series[bool] = pa.Field(nullable=True)
    
    # Required fields
    department_id: Series[str] = pa.Field(regex=r"^[0-9]+$")
    date: Series[date_type] = pa.Field()
    starttime: Series[str] = pa.Field()
    endtime: Series[str] = pa.Field()
    break_time: Series[str] = pa.Field()
    
    # Optional fields
    team_id: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    shift_id: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    instances: Series[str] = pa.Field(regex=r"^[0-9]+$", nullable=True)
    hide_end_time: Series[bool] = pa.Field(nullable=True)
    description: Series[str] = pa.Field(nullable=True)
    
    # Recurring pattern fields
    recurring: Series[bool] = pa.Field(nullable=True)
    repeat_until: Series[str] = pa.Field(nullable=True)
    interval: Series[str] = pa.Field(nullable=True)
    mo: Series[bool] = pa.Field(nullable=True)
    tu: Series[bool] = pa.Field(nullable=True)
    we: Series[bool] = pa.Field(nullable=True)
    th: Series[bool] = pa.Field(nullable=True)
    fr: Series[bool] = pa.Field(nullable=True)
    sa: Series[bool] = pa.Field(nullable=True)
    su: Series[bool] = pa.Field(nullable=True)
    
    # Match settings
    match: Series[str] = pa.Field(nullable=True)
    time_settings: Series[str] = pa.Field(nullable=True)
    
    @pa.check("id", "department_id", "team_id", "account_id")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid
    
    @pa.check("match")
    def check_match_value(cls, series: Series[str]) -> Series[bool]:
        """Validate match field has correct value."""
        valid_values = ["min", "max", "exact"]
        valid = series.isin(valid_values) | series.isna()
        return valid
    
    @pa.check("time_settings")
    def check_time_settings_value(cls, series: Series[str]) -> Series[bool]:
        """Validate time_settings field has correct value."""
        valid_values = ["any", "exact", "starting", "ending", "outside"]
        valid = series.isin(valid_values) | series.isna()
        return valid 