import pandera as pa
from pandera.typing import Series

class KioskSchema(pa.DataFrameModel):
    """
    Validation schema for Kiosk data from Shiftbase API
    """
    id: Series[str] = pa.Field()
    name: Series[str] = pa.Field()
    team_ids: Series[object] = pa.Field()  # List of team IDs as a Series of objects
    clock_department: Series[str] = pa.Field(nullable=True)
    ip_restricted: Series[bool] = pa.Field()
    link: Series[str] = pa.Field()
    short_id: Series[str] = pa.Field()
    account_id: Series[int] = pa.Field()
    
    @pa.check("id", "clock_department")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid 