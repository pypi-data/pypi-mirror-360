import pandera as pa
from pandera.typing import Series
from datetime import date as date_type

class TimeOffBalanceSchema(pa.DataFrameModel):
    """
    Validation schema for Time Off Balance data from Shiftbase API
    """
    id: Series[str] = pa.Field()
    name: Series[str] = pa.Field()
    default_accrual: Series[float] = pa.Field()
    unit: Series[str] = pa.Field(isin=["hours", "days"])
    allow_request_half_days: Series[bool] = pa.Field()
    active: Series[bool] = pa.Field()
    expiration_in_months: Series["Int64"] = pa.Field(nullable=True, coerce=True)

    class Config:
        strict = False


class BalanceCycleSchema(pa.DataFrameModel):
    """
    Validation schema for Balance Cycle data from Shiftbase API
    """
    balanceId: Series[str] = pa.Field()
    cycleYear: Series[str] = pa.Field()
    expireDate: Series[date_type] = pa.Field(nullable=True)
    total: Series[float] = pa.Field()
    
    @pa.check("balanceId")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid
    
    @pa.check("cycleYear")
    def check_year_format(cls, series: Series[str]) -> Series[bool]:
        """Validate year is in YYYY format."""
        valid = series.str.match(r"^\d{4}$") | series.isna()
        return valid
        
    @pa.check("expireDate")
    def check_date_format(cls, series: Series[str]) -> Series[bool]:
        """Validate date is in YYYY-MM-DD format."""
        valid = series.str.match(r"^\d{4}-\d{2}-\d{2}$") | series.isna()
        return valid 