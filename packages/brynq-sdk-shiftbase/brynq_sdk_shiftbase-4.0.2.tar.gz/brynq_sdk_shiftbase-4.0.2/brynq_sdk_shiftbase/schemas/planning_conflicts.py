import pandera as pa
from pandera.typing import Series

class PlanningConflictSchema(pa.DataFrameModel):
    """
    Validation schema for Planning Conflict data from Shiftbase API
    """
    occurrence_id: Series[str] = pa.Field()
    employee_id: Series[str] = pa.Field()
    topic: Series[str] = pa.Field(isin=["availability", "schedule", "skill", "timeoff"])
    message: Series[str] = pa.Field()
    
    @pa.check("occurrence_id", "employee_id")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid

class EmployabilitySchema(pa.DataFrameModel):
    """
    Validation schema for Employability data from Shiftbase API
    """
    employeeId: Series[str] = pa.Field()
    employable: Series[bool] = pa.Field()
    
    @pa.check("employeeId")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate employee ID is a numeric string."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid 