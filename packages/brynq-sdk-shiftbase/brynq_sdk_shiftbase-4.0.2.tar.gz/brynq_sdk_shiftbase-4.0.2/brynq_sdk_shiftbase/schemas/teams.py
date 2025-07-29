"""
Schema definition for Team data validation.
"""
import pandas as pd
import pandera as pa
from pandera.typing import Series
from datetime import datetime

class TeamSchema(pa.DataFrameModel):
    """
    Validation schema for Team data from Shiftbase API
    """
    id: Series[str] = pa.Field()
    account_id: Series[str] = pa.Field(nullable=True)
    department_id: Series[str] = pa.Field()
    name: Series[str] = pa.Field()
    color: Series[str] = pa.Field()
    order: Series[str] = pa.Field(nullable=True)
    created: Series[datetime] = pa.Field(nullable=True)
    created_by: Series[str] = pa.Field(nullable=True)
    modified_by: Series[str] = pa.Field(nullable=True)
    deleted: Series[bool] = pa.Field(nullable=True, coerce=True)
    deleted_date: Series[datetime] = pa.Field(nullable=True)
    hidden: Series[bool] = pa.Field(nullable=True, coerce=True)
    type: Series[str] = pa.Field(nullable=True)
    
    @pa.check("color")
    def check_color_format(cls, series: Series[str]) -> Series[bool]:
        """Validate color is in hexadecimal format."""
        valid = series.str.match(r"^#[0-9A-Fa-f]{6}$")
        return valid
    
    @pa.check("type")
    def check_type_values(cls, series: Series[str]) -> Series[bool]:
        """Validate type field has correct value."""
        valid = series.str.match(r"^(default|flexpool|hidden)$") | series.isna()
        return valid

    class Config:
        coerce = True