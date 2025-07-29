"""
Schema definition for OpenShift data validation.
"""
import pandera as pa
from pandera.typing import Series
from datetime import datetime, date as date_type

class OpenShiftSchema(pa.DataFrameModel):
    """
    Validation schema for Open Shifts data from Shiftbase API
    """
    # Identifier and reference fields
    id: Series[str] = pa.Field()
    account_id: Series[str] = pa.Field()
    department_id: Series[str] = pa.Field()
    team_id: Series[str] = pa.Field()
    roster_id: Series[str] = pa.Field(nullable=True)
    skill_id: Series[str] = pa.Field(nullable=True)
    user_id: Series[str] = pa.Field(nullable=True)
    
    # Date and time fields
    date: Series[date_type] = pa.Field(nullable=True)
    starttime: Series[str] = pa.Field(nullable=True)
    endtime: Series[str] = pa.Field(nullable=True)
    
    # Status fields
    status: Series[str] = pa.Field(nullable=True)
    active: Series[bool] = pa.Field(nullable=True, coerce=True)
    deleted: Series[bool] = pa.Field(nullable=True, coerce=True)
    private: Series[bool] = pa.Field(nullable=True, coerce=True)
    
    # Tracking fields
    created_by: Series[str] = pa.Field(nullable=True)
    modified_by: Series[str] = pa.Field(nullable=True)
    created: Series[datetime] = pa.Field(nullable=True)
    modified: Series[datetime] = pa.Field(nullable=True)
    
    # Other fields
    note: Series[str] = pa.Field(nullable=True)
    wage: Series[str] = pa.Field(nullable=True)
    auto_accept: Series[bool] = pa.Field(nullable=True, coerce=True)
    
    @pa.check("id", "account_id", "department_id", "team_id", "roster_id", "skill_id", "user_id")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid
    