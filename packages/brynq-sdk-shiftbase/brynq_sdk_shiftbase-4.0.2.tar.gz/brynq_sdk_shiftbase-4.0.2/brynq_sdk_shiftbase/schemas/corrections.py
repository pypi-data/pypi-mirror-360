"""
Schema definition for Correction data validation.
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import re
from datetime import datetime
from datetime import date as date_type

class CorrectionType(str, Enum):
    """Correction type options"""
    HOURS = "hours"
    TIME_OFF_BALANCE = "time_off_balance"
    WAGE = "wage"

class CorrectionSchema(BaseModel):
    """
    Schema for validating Correction data returned from Shiftbase API.
    Corrections model for overtime, time off balances, etc.
    """
    # Required fields
    user_id: str = Field(
        description="The user ID this correction is for",
        pattern=r"^[0-9]+$"
    )
    date: date_type = Field(
        description="The date on which the correction should take place"
    )
    type: CorrectionType = Field(
        description="The type of correction"
    )
    
    # Read-only fields
    id: Optional[UUID] = Field(
        description="The unique identifier of the correction",
        default=None
    )
    account_id: Optional[str] = Field(
        description="The account ID the correction is linked to",
        default=None
    )
    created: Optional[datetime] = Field(
        description="Creation timestamp",
        default=None
    )
    updated: Optional[datetime] = Field(
        description="Last update timestamp",
        default=None
    )
    created_by: Optional[str] = Field(
        description="ID of the user who created the correction",
        default=None
    )
    modified_by: Optional[str] = Field(
        description="ID of the user who last modified the correction",
        default=None
    )
    
    # Optional fields
    payout_date: Optional[datetime] = Field(
        description="The date on which the correction should be paid out",
        default=None
    )
    amount: Optional[float] = Field(
        description="Amount of the correction",
        default=None
    )
    coc: Optional[float] = Field(
        description="Cost of the correction",
        default=None
    )
    note: Optional[str] = Field(
        description="Note about the correction",
        default=None
    )
    time_off_balance_id: Optional[UUID] = Field(
        description="For which time off balance the correction is. Is required when type is Time off balance",
        default=None
    )
    pay: Optional[bool] = Field(
        description="If the correction is a payout correction",
        default=None
    )
    public: Optional[bool] = Field(
        description="If the correction is public",
        default=None
    )
    expire_date: Optional[datetime] = Field(
        description="Expiration date for the correction",
        default=None
    )
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validates correction type values"""
        if v not in [t.value for t in CorrectionType]:
            raise ValueError(f"Invalid correction type: {v}")
        return v
    
    @field_validator('date', 'payout_date', 'expire_date')
    @classmethod
    def validate_date(cls, v):
        """Validates date format YYYY-MM-DD"""
        if v is None:
            return v
            
        if not isinstance(v, datetime):
            date_pattern = r"^\d{4}-\d{2}-\d{2}$"
            if not re.match(date_pattern, v):
                raise ValueError(f"Invalid date format: {v}. Expected format: YYYY-MM-DD")
        return v
    
    @field_validator('user_id')
    @classmethod
    def validate_uuid(cls, v):
        """Validates UUID format when present"""
        if not re.match(r"^[0-9]+$", v):
            raise ValueError(f"Invalid user_id format: {v}. Expected numeric string.")
        return v
    
    @field_validator('time_off_balance_id')
    @classmethod
    def validate_time_off_balance_required(cls, v, values):
        """Validates time_off_balance_id is present when type is Time off balance"""
        if values.get('type') == CorrectionType.TIME_OFF_BALANCE and v is None:
            raise ValueError("time_off_balance_id is required when type is time_off_balance")
        return v
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields 