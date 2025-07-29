import pandera as pa
from pandera.typing import Series
from datetime import date as date_type

class InsightDetailSchema(pa.DataFrameModel):
    """
    Validation schema for Insight Detail data from Shiftbase API
    """
    amount: Series[float] = pa.Field(description="The actual amount")
    target: Series[float] = pa.Field(description="The target amount")
    deltaPercentage: Series[float] = pa.Field(description="The percentage difference from target")
    status: Series[str] = pa.Field(isin=["on", "near", "off"], description="Status indicating target achievement")

    class Config:
        """Schema configuration"""
        coerce = True

class DepartmentInsightSchema(pa.DataFrameModel):
    """
    Validation schema for Department Insight data from Shiftbase API
    """
    departmentId: Series[str] = pa.Field(description="The department ID")
    
    @pa.check("departmentId")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid

    class Config:
        """Schema configuration"""
        coerce = True

class TeamInsightSchema(pa.DataFrameModel):
    """
    Validation schema for Team Insight data from Shiftbase API
    """
    departmentId: Series[str] = pa.Field(description="The department ID")
    teamId: Series[str] = pa.Field(description="The team ID")
    
    @pa.check("departmentId", "teamId")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid

    class Config:
        """Schema configuration"""
        coerce = True

class ScheduleInsightDaySchema(pa.DataFrameModel):
    """
    Validation schema for Schedule Insight Day data from Shiftbase API
    """
    date: Series[date_type] = pa.Field(description="The date of the insight")
    departmentId: Series[str] = pa.Field(regex=r"^[0-9]+$", description="The department ID")

    class Config:
        coerce = True

class ScheduleInsightTotalSchema(pa.DataFrameModel):
    """
    Validation schema for Schedule Insight Total data from Shiftbase API
    """
    departmentId: Series[str] = pa.Field(regex=r"^[0-9]+$", description="The department ID")

    class Config:
        """Schema configuration"""
        coerce = True
