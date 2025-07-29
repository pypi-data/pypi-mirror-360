import pandas as pd
import pandera as pa
from pandera.typing import Series
from datetime import datetime
class SkillSchema(pa.DataFrameModel):
    """
    Validation schema for Skill data from Shiftbase API
    """
    id: Series[str] = pa.Field(regex=r"^[0-9]+$", description="The skill ID")
    account_id: Series[str] = pa.Field(regex=r"^[0-9]+$", description="The account ID")
    skill_group_id: Series[str] = pa.Field(regex=r"^[0-9]+$", description="The skill group ID")
    name: Series[str] = pa.Field(description="The name of the skill")
    created: Series[datetime] = pa.Field(description="The datetime when the skill has been created")
    modified: Series[datetime] = pa.Field(description="The datetime when the skill has been updated")
    created_by: Series[str] = pa.Field(description="Id of the employee that added this skill")
    modified_by: Series[str] = pa.Field(description="Id of the employee that modified this skill")
    deleted: Series[bool] = pa.Field(description="Indicates whether the skill has been deleted")
    

class SkillGroupSchema(pa.DataFrameModel):
    """
    Validation schema for Skill Group data from Shiftbase API
    """
    id: Series[str] = pa.Field(description="The skill group ID")
    account_id: Series[str] = pa.Field(description="The account ID")
    name: Series[str] = pa.Field(description="The name of the skill group")
    created: Series[datetime] = pa.Field(description="The datetime when the skill group has been created")
    modified: Series[datetime] = pa.Field(description="The datetime when the skill group has been updated")
    created_by: Series[str] = pa.Field(description="Id of the user that added this skill group")
    modified_by: Series[str] = pa.Field(description="Id of the user that modified this skill group")
    deleted: Series[bool] = pa.Field(description="Indicates whether the skill group has been deleted")
    
    @pa.check("id", "account_id")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid
        