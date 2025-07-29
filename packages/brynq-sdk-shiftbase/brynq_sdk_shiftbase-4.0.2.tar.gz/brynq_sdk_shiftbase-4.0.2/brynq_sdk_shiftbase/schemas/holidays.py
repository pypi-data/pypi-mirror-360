"""
Schema definition for Holiday data validation.
"""
from typing import Optional
import re
import pandera as pa
from pandera.typing import Series
from datetime import datetime
from datetime import date as date_type

class HolidayGroupSchema(pa.DataFrameModel):
    """
    Schema for validating Holiday Group data returned from Shiftbase API.
    """
    # Read-only fields
    id: Series[str] = pa.Field(coerce=True)
    created: Series[datetime] = pa.Field(nullable=True)

    # Required fields
    name: Series[str] = pa.Field()

    
    @pa.check("id")
    def validate_uuid(cls, series: Series[str]) -> Series[bool]:
        """Validates UUID format"""
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return series.str.match(uuid_pattern)
    class Config:
        strict = False
        coerce = True

class PublicHolidaySchema(pa.DataFrameModel):
    """
    Schema for validating Public Holiday data returned from Shiftbase API.
    """
    # Fields will depend on the API response structure
    # These are assumed fields based on typical holiday API responses
    name: Series[str] = pa.Field()
    date: Series[date_type] = pa.Field()
    country_code: Series[str] = pa.Field(nullable=True)
    region: Series[str] = pa.Field(nullable=True)
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields
        strict = False
        coerce = True