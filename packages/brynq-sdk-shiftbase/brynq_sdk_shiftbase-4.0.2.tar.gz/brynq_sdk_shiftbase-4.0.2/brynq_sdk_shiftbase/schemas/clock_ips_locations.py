from pandera.typing import DateTime
import pandera as pa
from pandera.typing import Series

class ClockIpSchema(pa.DataFrameModel):
    """
    Validation schema for Clock IP data from Shiftbase API
    """
    id: Series[str] = pa.Field()
    account_id: Series[str] = pa.Field()
    name: Series[str] = pa.Field()
    ip: Series[str] = pa.Field()
    created: Series[DateTime] = pa.Field()
    modified: Series[DateTime] = pa.Field()
    created_by: Series[str] = pa.Field()
    modified_by: Series[str] = pa.Field()
    deleted: Series[str] = pa.Field()
    deleted_date: Series[DateTime] = pa.Field(nullable=True)
    
    @pa.check("id", "account_id")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid
    
    @pa.check("ip")
    def check_ip_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IP address format."""
        valid = series.str.match(r"^(\d{1,3}\.){3}\d{1,3}$") | series.isna()
        return valid
    
    class Config:
        coerce = True

class ClockLocationSchema(pa.DataFrameModel):
    """
    Validation schema for Clock Location data from Shiftbase API
    """
    id: Series[str] = pa.Field()
    account_id: Series[str] = pa.Field()
    name: Series[str] = pa.Field()
    latitude: Series[str] = pa.Field(regex=r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$")
    longitude: Series[str] = pa.Field(regex=r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$")
    radius: Series[str] = pa.Field(regex=r"^[0-9]+$")
    created: Series[DateTime] = pa.Field()
    modified: Series[DateTime] = pa.Field()
    created_by: Series[str] = pa.Field()
    modified_by: Series[str] = pa.Field()
    deleted: Series[bool] = pa.Field()
    deleted_date: Series[DateTime] = pa.Field(nullable=True)
    
    @pa.check("id", "account_id", "created_by", "modified_by")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid

    class Config:
        coerce = True