"""
Schema definition for Contract data validation.
"""
from typing import Dict, List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import re
from pandera.typing import Series
import pandera as pa
from datetime import date


class ContractSchema(BaseModel):
    """
    Schema for validating Contract data returned from Shiftbase API.
    Each employee has their own contract, which defines working hours, job details, etc.
    """
    # Required fields
    id: Optional[str] = Field(
        description="The unique identifier of the contract",
        pattern=r"^[0-9]+$",
        default=None
    )
    user_id: str = Field(
        description="User identifier",
        pattern=r"^[0-9]+$"
    )
    department_id: str = Field(
        description="Department identifier",
        pattern=r"^[0-9]+$"
    )
    contract_type_id: str = Field(
        description="Id of the contract type",
        pattern=r"^[0-9]+$"
    )
    startdate: date = Field(
        description="Start date of the contract (YYYY-MM-DD)"
    )
    
    # Optional fields
    vacation_calc: Optional[str] = Field(
        description="Deprecated field",
        default="0.000000000"
    )
    function: Optional[str] = Field(
        description="Job title",
        default=""
    )
    mo: Optional[str] = Field(
        description="Hours scheduled to work on Monday",
        default="0.0000000"
    )
    tu: Optional[str] = Field(
        description="Hours scheduled to work on Tuesday",
        default="0.0000000"
    )
    we: Optional[str] = Field(
        description="Hours scheduled to work on Wednesday",
        default="0.0000000"
    )
    th: Optional[str] = Field(
        description="Hours scheduled to work on Thursday",
        default="0.0000000"
    )
    fr: Optional[str] = Field(
        description="Hours scheduled to work on Friday",
        default="0.0000000"
    )
    sa: Optional[str] = Field(
        description="Hours scheduled to work on Saturday",
        default="0.0000000"
    )
    su: Optional[str] = Field(
        description="Hours scheduled to work on Sunday",
        default="0.0000000"
    )
    enddate: Optional[date] = Field(
        description="End date of the contract (YYYY-MM-DD), null means indefinite",
        default=None
    )
    wage_tax: Optional[bool] = Field(
        description="Should the employer withold wage taxes",
        default=True
    )
    note: Optional[str] = Field(
        description="Additional notes",
        default=None
    )
    time_off_accrual: Optional[Dict[str, float]] = Field(
        description="Key-Value pair of the time off balance id with a build up factor",
    )
    wage: Optional[str] = Field(
        description="Hourly wage",
        default="0.00"
    )
    coc: Optional[Union[str, float, int]] = Field(
        description="Wage included Cost of Company",
        default="0.00"
    )
    contract_hours: Optional[str] = Field(
        description="Sum of the contract hours from the separate days",
        default="0.00"
    )
    day_list: Optional[List[int]] = Field(
        description="List of day numbers (1=Monday, 7=Sunday)",
    )
        
    @field_validator('mo', 'tu', 'we', 'th', 'fr', 'sa', 'su', 'wage', 'contract_hours')
    @classmethod
    def validate_numeric_string(cls, v):
        """Validates numeric string format"""
        if v is None:
            return "0.0000000"
            
        # Allow numeric strings like "0.00" or "12.3456789"
        numeric_pattern = r"^\d+(\.\d+)?$"
        if not re.match(numeric_pattern, v):
            raise ValueError(f"Invalid numeric string: {v}. Expected format: digits with optional decimal places")
        return v
    
    @field_validator('coc')
    @classmethod
    def validate_coc(cls, v):
        """Validates coc value - can be string, float or int"""
        if v is None:
            return "0.00"
            
        # If it's already a number, convert to string
        if isinstance(v, (int, float)):
            return str(v)
            
        # If it's a string, validate the format
        if isinstance(v, str):
            numeric_pattern = r"^\d+(\.\d+)?$"
            if not re.match(numeric_pattern, v):
                raise ValueError(f"Invalid coc value: {v}. Expected format: digits with optional decimal places")
            return v
            
        raise ValueError(f"Invalid coc type: {type(v)}. Expected string, float, or int")
    
    @field_validator('time_off_accrual')
    @classmethod
    def validate_time_off_accrual(cls, v):
        """Validates time_off_accrual structure"""
        if v is None:
            return {}
            
        # Check that all keys are valid UUIDs and values are numbers
        for key, value in v.items():
            try:
                UUID(key)
            except ValueError:
                raise ValueError(f"Invalid UUID as key in time_off_accrual: {key}")
                
            if not isinstance(value, (int, float)):
                raise ValueError(f"Invalid value in time_off_accrual: {value}. Expected numeric value")
                
        return v
    
    @field_validator('day_list')
    @classmethod
    def validate_day_list(cls, v):
        """Validates day_list values"""
        if v is None:
            return []
            
        # Check that all values are between 1 and 7
        for day in v:
            if not isinstance(day, int) or day < 1 or day > 7:
                raise ValueError(f"Invalid day in day_list: {day}. Expected an integer between 1 and 7")
                
        return v
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields 


class ContractCreateSchema(BaseModel):
    """
    Schema for validating Contract creation data.
    This schema is used when creating new contracts in Shiftbase.
    """
    # Required fields
    user_id: str = Field(
        description="User identifier",
        pattern=r"^[0-9]+$"
    )
    department_id: str = Field(
        description="Department identifier",
        pattern=r"^[0-9]+$"
    )
    contract_type_id: str = Field(
        description="Id of the contract type",
        pattern=r"^[0-9]+$"
    )
    startdate: date = Field(
        description="Start date of the contract (YYYY-MM-DD)"
    )
    time_off_accrual:Dict[str, float] = Field(
        description="Key-Value pair of the time off balance id with a build up factor",
    )
    
    # Optional fields
    vacation_calc: Optional[str] = Field(
        description="Deprecated field",
        default="0.000000000"
    )
    function: Optional[str] = Field(
        description="Job title",
        default=""
    )
    mo: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Monday",
        default="0.0000000"
    )
    tu: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Tuesday",
        default="0.0000000"
    )
    we: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Wednesday",
        default="0.0000000"
    )
    th: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Thursday",
        default="0.0000000"
    )
    fr: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Friday",
        default="0.0000000"
    )
    sa: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Saturday",
        default="0.0000000"
    )
    su: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Sunday",
        default="0.0000000"
    )
    enddate: Optional[date] = Field(
        description="End date of the contract (YYYY-MM-DD), null means indefinite",
        default=None
    )
    wage_tax: Optional[bool] = Field(
        description="Should the employer withold wage taxes",
        default=True
    )
    note: Optional[str] = Field(
        description="Additional notes",
        default=None
    )
    wage: Optional[Union[str, float]] = Field(
        description="Hourly wage",
        default="0.00"
    )
    coc: Optional[Union[str, float, int]] = Field(
        description="Wage included Cost of Company",
        default="0.00"
    )
    
    @field_validator('mo', 'tu', 'we', 'th', 'fr', 'sa', 'su')
    @classmethod
    def validate_day_hours(cls, v):
        """Validates and converts day hours to string format"""
        if v is None:
            return "0.0000000"
            
        # Convert numeric values to string
        if isinstance(v, (int, float)):
            return str(v)
            
        # Validate string format
        if isinstance(v, str):
            numeric_pattern = r"^\d+(\.\d+)?$"
            if not re.match(numeric_pattern, v):
                raise ValueError(f"Invalid numeric string: {v}. Expected format: digits with optional decimal places")
            return v
            
        raise ValueError(f"Invalid type: {type(v)}. Expected string, int, or float")
    
    @field_validator('wage')
    @classmethod
    def validate_wage(cls, v):
        """Validates wage value"""
        if v is None:
            return "0.00"
            
        # Convert numeric to string
        if isinstance(v, (int, float)):
            return str(v)
            
        # Validate string format
        if isinstance(v, str):
            numeric_pattern = r"^\d+(\.\d+)?$"
            if not re.match(numeric_pattern, v):
                raise ValueError(f"Invalid wage value: {v}. Expected format: digits with optional decimal places")
            return v
            
        raise ValueError(f"Invalid wage type: {type(v)}. Expected string, float, or int")
    
    @field_validator('coc')
    @classmethod
    def validate_coc(cls, v):
        """Validates coc value"""
        if v is None:
            return "0.00"
            
        # Convert numeric to string
        if isinstance(v, (int, float)):
            return str(v)
            
        # Validate string format
        if isinstance(v, str):
            numeric_pattern = r"^\d+(\.\d+)?$"
            if not re.match(numeric_pattern, v):
                raise ValueError(f"Invalid coc value: {v}. Expected format: digits with optional decimal places")
            return v
            
        raise ValueError(f"Invalid coc type: {type(v)}. Expected string, float, or int")
    
    @field_validator('time_off_accrual')
    @classmethod
    def validate_time_off_accrual(cls, v):
        """Validates time_off_accrual structure"""
        if v is None:
            return {}
            
        # Check that all keys are valid UUIDs and values are numbers
        for key, value in v.items():
            try:
                UUID(key)
            except ValueError:
                raise ValueError(f"Invalid UUID as key in time_off_accrual: {key}")
                
            if not isinstance(value, (int, float)):
                raise ValueError(f"Invalid value in time_off_accrual: {value}. Expected numeric value")
                
        return v
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields


class ContractUpdateSchema(BaseModel):
    """
    Schema for validating Contract update data.
    This schema is used when updating existing contracts in Shiftbase.
    """
    # Required fields for update
    id: str = Field(
        description="The unique identifier of the contract",
        pattern=r"^[0-9]+$",
        coerce_numbers_to_str=True
    )
    user_id: str = Field(
        description="User identifier",
        pattern=r"^[0-9]+$"
    )
    department_id: str = Field(
        description="Department identifier",
        pattern=r"^[0-9]+$"
    )
    contract_type_id: str = Field(
        description="Id of the contract type",
        pattern=r"^[0-9]+$"
    )
    startdate: date = Field(
        description="Start date of the contract (YYYY-MM-DD)"
    )
    
    # Optional fields
    vacation_calc: Optional[str] = Field(
        description="Deprecated field",
        default="0.000000000"
    )
    function: Optional[str] = Field(
        description="Job title",
        default=""
    )
    mo: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Monday",
        default="0.0000000"
    )
    tu: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Tuesday",
        default="0.0000000"
    )
    we: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Wednesday",
        default="0.0000000"
    )
    th: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Thursday",
        default="0.0000000"
    )
    fr: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Friday",
        default="0.0000000"
    )
    sa: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Saturday",
        default="0.0000000"
    )
    su: Optional[Union[str, int, float]] = Field(
        description="Hours scheduled to work on Sunday",
        default="0.0000000"
    )
    enddate: Optional[date] = Field(
        description="End date of the contract (YYYY-MM-DD), null means indefinite",
        default=None
    )
    wage_tax: Optional[bool] = Field(
        description="Should the employer withold wage taxes",
        default=True
    )
    note: Optional[str] = Field(
        description="Additional notes",
        default=None
    )
    time_off_accrual: Optional[Dict[str, float]] = Field(
        description="Key-Value pair of the time off balance id with a build up factor",
    )
    wage: Optional[Union[str, float]] = Field(
        description="Hourly wage",
        default="0.00"
    )
    coc: Optional[Union[str, float, int]] = Field(
        description="Wage included Cost of Company",
        default="0.00"
    )
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields
