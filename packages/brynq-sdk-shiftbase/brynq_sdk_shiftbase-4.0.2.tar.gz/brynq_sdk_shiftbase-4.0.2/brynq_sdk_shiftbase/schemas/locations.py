"""
Schema definition for Location data validation.
"""
import pandera as pa
from pandera.typing import Series
from datetime import datetime
class LocationSchema(pa.DataFrameModel):
    """
    Schema for validating Location data returned from Shiftbase API.
    """
    # Read-only fields
    id: Series[str] = pa.Field()
    account_id: Series[str] = pa.Field()
    deleted: Series[bool] = pa.Field(nullable=True)
    created: Series[datetime] = pa.Field(nullable=True)
    created_by: Series[str] = pa.Field(nullable=True)
    modified_by: Series[str] = pa.Field(nullable=True)
    
    # Required fields
    name: Series[str] = pa.Field()
    
    # Optional fields
    street_address: Series[str] = pa.Field(nullable=True)
    zipcode: Series[str] = pa.Field(nullable=True)
    city: Series[str] = pa.Field(nullable=True)
    country: Series[str] = pa.Field(nullable=True)
    email: Series[str] = pa.Field(nullable=True)
    telephone: Series[str] = pa.Field(nullable=True)
    order: Series[str] = pa.Field(nullable=True)
    
    @pa.check("id")
    def validate_id(cls, series: Series[str]) -> Series[bool]:
        """Validates ID format"""
        return series.str.match(r"^[0-9]+$")

    class Config:
        coerce = True