"""
Schema definition for Shift data validation.
"""
import pandera as pa
from pandera.typing import Series, DataFrame
from datetime import datetime
from typing import Optional

class ShiftSchema(pa.DataFrameModel):
    """
    Schema for validating Shift data returned from Shiftbase API.
    """
    # Read-only fields
    id: Series[str] = pa.Field()
    account_id: Series[str] = pa.Field()
    created: Series[datetime] = pa.Field(nullable=True)
    deleted: Series[bool] = pa.Field(nullable=True)
    created_by: Series[str] = pa.Field(nullable=True)
    modified_by: Series[str] = pa.Field(nullable=True)
    
    # Required fields
    department_id: Series[str] = pa.Field()
    name: Series[str] = pa.Field()  # Short name of the shift
    long_name: Series[str] = pa.Field()  # Full name of the shift
    starttime: Series[str] = pa.Field()  # Start time (HH:MM:SS)
    break_time: Optional[Series[str]] = pa.Field(nullable=True, alias="break")

    # Optional fields
    description: Series[str] = pa.Field(nullable=True)
    endtime: Series[str] = pa.Field(nullable=True)
    hide_end_time: Series[bool] = pa.Field(nullable=True)
    is_task: Series[bool] = pa.Field(nullable=True)
    meals: Series[str] = pa.Field(nullable=True)
    rate_card_id: Series[str] = pa.Field(nullable=True)
    color: Series[str] = pa.Field(nullable=True)
    order: Series[str] = pa.Field(nullable=True)

        
    @pa.check("color")
    def check_color_format(cls, series: Series[str]) -> Series[bool]:
        """Validate color is in hexadecimal format."""
        valid = series.str.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$") | series.isna()
        return valid

    class Config:
        coerce = True
        strict = False