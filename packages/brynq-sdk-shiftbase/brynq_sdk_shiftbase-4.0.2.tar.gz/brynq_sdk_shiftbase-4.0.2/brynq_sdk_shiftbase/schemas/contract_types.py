"""
Schema definition for Contract Type data validation.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
import re

class ContractTypeSchema(BaseModel):
    """
    Schema for validating Contract Type data returned from Shiftbase API.
    Every employee in Shiftbase has a contract associated with a contract type. 
    A contract type is a set of rules related to a contract.
    """
    # Required fields
    name: str = Field(
        description="Name of the contract type"
    )
    salary_calc_type: str = Field(
        description="This is used for payroll and indicates whether the employee is paid based on worked or contract hours"
    )
    absence_policy_id: str = Field(
        description="The absence policy linked to the contract type"
    )
    
    # Read-only fields
    id: Optional[str] = Field(
        description="The id of the contract type",
        pattern=r"^[0-9]+$",
        default=None
    )
    account_id: Optional[str] = Field(
        description="The account ID the contract type is linked to",
        pattern=r"^[0-9]+$",
        default=None
    )
    created: Optional[datetime] = Field(
        description="The datetime when the contract type has been created",
        default=None
    )
    modified: Optional[datetime] = Field(
        description="The datetime when the contract type has been modified",
        default=None
    )
    created_by: Optional[str] = Field(
        description="Id of the employee that created the contract type",
        default=None
    )
    modified_by: Optional[str] = Field(
        description="Id of the employee that modified the contract type",
        default=None
    )
    deleted: Optional[bool] = Field(
        description="If the contract type is deleted",
        default=False
    )
    deleted_date: Optional[str] = Field(
        description="The datetime of the deletion",
        default=None
    )
    salary_calc_option: Optional[str] = Field(
        description="Translated label of salary_calc_type",
        default=None
    )
    
    # Optional fields
    plus_min: Optional[bool] = Field(
        description="By turning on plus-minus calculation, the plus and minus hours are calculated for all employees with the concerning contract type",
        default=None
    )
    vacation_calc_type: Optional[str] = Field(
        description="Deprecated - Moved to absence policy",
        default=None
    )
    time_off_accrual_source_hours: Optional[str] = Field(
        description="Deprecated - Moved to absence policy",
        default=None
    )
    absence_calculation: Optional[str] = Field(
        description="Deprecated",
        default=None
    )
    wait_hours_from: Optional[str] = Field(
        description="Deprecated - Moved to absence policy",
        default=None
    )
    wait_hours_from_time_off_balance_id: Optional[str] = Field(
        description="Deprecated - Moved to absence policy",
        default=None
    )
    rate_card_id: Optional[str] = Field(
        description="The rate card that applies to the contract type",
        pattern=r"^[0-9]+$",
        default=None
    )
    overtime_policy_id: Optional[str] = Field(
        description="The overtime policy linked to the contract type",
        default=None
    )
    coc: Optional[str] = Field(
        description="The cost of company factor. Can be used to calculate a more accurate cost per hour worked",
        default="1.35"
    )
    
    @field_validator('absence_policy_id', 'overtime_policy_id', 'wait_hours_from_time_off_balance_id')
    @classmethod
    def validate_uuid(cls, v):
        """Validates UUID format when present"""
        if v is None:
            return v
            
        try:
            UUID(v)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")
            
        return v
    
    @field_validator('salary_calc_type')
    @classmethod
    def validate_salary_calc_type(cls, v):
        """Validates salary_calc_type values"""
        allowed_values = ["CONTRACT", "WORKED"]
        if v not in allowed_values:
            raise ValueError(f"Invalid salary_calc_type: {v}. Must be one of {allowed_values}")
        return v
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields 