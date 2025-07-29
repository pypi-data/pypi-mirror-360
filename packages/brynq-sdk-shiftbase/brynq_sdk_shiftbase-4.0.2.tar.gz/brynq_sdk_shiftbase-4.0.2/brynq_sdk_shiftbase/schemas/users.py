import pandas as pd
import pandera as pa
from pandera.typing import Series
from typing import Optional, Any, Dict, List, Union
from pydantic import BaseModel, Field, field_validator
import re
from datetime import date, datetime


class UsersGroupSchema(pa.DataFrameModel):
    """
    Validation schema for User Group data from Shiftbase API
    """
    id: Series[str] = pa.Field()
    department_id: Series[str] = pa.Field()
    user_id: Series[str] = pa.Field()
    group_id: Series[str] = pa.Field()

    @pa.check("id", "department_id", "user_id", "group_id")
    def check_id_format(cls, series: Series[str]) -> Series[bool]:
        """Validate IDs are numeric strings."""
        valid = series.str.match(r"^[0-9]+$") | series.isna()
        return valid

class UserModel(BaseModel):
    """
    Pydantic validation schema for User data from Shiftbase API
    """
    id: str = Field(description="User ID")
    account_id: str = Field(description="Account ID")
    first_name: str = Field(description="First name of user")
    prefix: str = Field(description="Prefix of last name")
    last_name: str = Field(description="Last name of user")
    avatar_file_name: Optional[str] = Field(default=None, description="Avatar file name")
    locale: str = Field(description="The locale of the user", pattern=r"^(nl-NL|en-GB|fr-FR|de-DE|es-ES|pl-PL|sv-SE|ro-RO)$")
    order: str = Field(description="Used for sorting users")
    startdate: date = Field(description="Date the user is active in the system")
    enddate: Optional[date] = Field(default=None, description="Date the user is inactive in the system")
    anonymized: bool = Field(description="Whether the user is anonymized")

    # Fields only with specific permissions
    street_address: Optional[str] = Field(default=None, description="Street address")
    post_code: Optional[str] = Field(default=None, description="Postal code")
    city: Optional[str] = Field(default=None, description="City")
    phone_nr: Optional[str] = Field(default=None, description="Phone number")
    mobile_nr: Optional[str] = Field(default=None, description="Mobile number")
    emergency_nr: Optional[str] = Field(default=None, description="Emergency contact number")
    email: Optional[str] = Field(default=None, description="Email address of the user")
    verified: Optional[bool] = Field(default=None, description="Whether the user is verified")
    hire_date: Optional[date] = Field(default=None, description="Date the user is hired")
    birthplace: Optional[str] = Field(default=None, description="Birthplace")
    birthdate: Optional[date] = Field(default=None, description="Birth date")
    nationality: Optional[str] = Field(default=None, description="Nationality of user")
    ssn: Optional[str] = Field(default=None, description="Social security number")
    passport_number: Optional[str] = Field(default=None, description="Document number of passport")
    banknr: Optional[str] = Field(default=None, description="Bank number of user")
    nr_of_logins: Optional[int] = Field(default=None, description="Number of logins")
    last_login: Optional[datetime] = Field(default=None, description="Date and time of last login")
    employee_nr: Optional[str] = Field(default=None, description="Employee number")
    custom_fields: Optional[Union[Dict[str, Any], str]] = Field(default=None, description="User custom fields")
    roster_note: Optional[str] = Field(default=None, description="Note that shows up in the schedule")
    invited: Optional[bool] = Field(default=None, description="Whether the user is invited")
    plus_min_hours: Optional[str] = Field(default=None, description="Plus/minus hours")
    birthday: Optional[datetime] = Field(default=None, description="User's birthday")
    birthday_age: Optional[str] = Field(default=None, description="User's age on birthday")
    age: Optional[str] = Field(default=None, description="User's age")
    has_login: Optional[bool] = Field(default=None, description="Whether the user has login credentials")
    mfa_enabled: Optional[bool] = Field(default=None, description="Whether multi-factor authentication is enabled")

    # Auto-generated fields
    name: str = Field(description="Full name of the user")
    display_name: str = Field(description="Display name of the user")
    avatar_15x15: str = Field(description="URL to 15x15 avatar image")
    avatar_24x24: str = Field(description="URL to 24x24 avatar image")
    avatar_30x30: str = Field(description="URL to 30x30 avatar image")
    avatar_45x45: str = Field(description="URL to 45x45 avatar image")
    avatar_60x60: str = Field(description="URL to 60x60 avatar image")
    avatar_150x200: str = Field(description="URL to 150x200 avatar image")

    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields

class UsersGroupModel(BaseModel):
    """
    Pydantic validation schema for User Group data from Shiftbase API
    """
    id: str = Field(description="User group ID")
    department_id: str = Field(description="Department ID")
    user_id: str = Field(description="User ID")
    group_id: str = Field(description="Group ID")

    @field_validator('id', 'department_id', 'user_id', 'group_id')
    @classmethod
    def validate_id_format(cls, v):
        """Validates IDs are numeric strings."""
        if not re.match(r"^[0-9]+$", v):
            raise ValueError(f"Invalid ID format: {v}. Expected numeric string.")
        return v

    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields

class TeamModel(BaseModel):
    """
    Pydantic validation schema for Team data from Shiftbase API
    """
    id: str = Field(description="The unique identifier for the team", pattern=r"^[0-9]+$")
    account_id: str = Field(default=None,description="The account ID to which this team belongs to", pattern=r"^[0-9]+$")
    department_id: str = Field(description="The department ID this team belongs to", pattern=r"^[0-9]+$")
    name: str = Field(description="The name of the team", min_length=1)
    color: str = Field(description="This must be a valid hexadecimal color like '#FFFFFF' for white", min_length=1)
    order: str = Field(description="In which order the teams are displayed", pattern=r"^[0-9]+$")
    created: datetime = Field(default=None,description="When the team was created")
    created_by: Optional[str] = Field(default=None, description="The user ID that created the team", pattern=r"^[0-9]+$")
    updated: datetime = Field(default=None,description="When the team was last updated")
    modified_by: Optional[str] = Field(default=None, description="The user ID that last updated the team", pattern=r"^[0-9]+$")
    deleted: bool = Field(default=False, description="If the team is deleted")
    deleted_date: Optional[datetime] = Field(default=None, description="When the team was deleted")
    hidden: bool = Field(default=False, description="Whether the team is hidden")
    type: str = Field(
        default="default",
        description="default: The team is shown in the schedule an timesheet. "
                   "flexpool: The team is not shown, but the employees within this team can be scheduled in the standard teams. "
                   "hidden: The team is not shown in the schedule and the timesheet, but it is shown in the list of employees.",
        pattern=r"^(default|flexpool|hidden)$"
    )

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """Validates hexadecimal color format"""
        color_pattern = r"^#[0-9A-Fa-f]{6}$"
        if not re.match(color_pattern, v):
            raise ValueError(f"Invalid color format: {v}. Expected format: #RRGGBB (e.g. #FFFFFF)")
        return v

    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserSchema(BaseModel):
    """Pydantic model for UserSchema response"""
    User: Optional[UserModel] = Field(None)
    UsersGroup: Optional[List[UsersGroupModel]] = Field(default_factory=list)
    Team: Optional[List[TeamModel]] = Field(default_factory=list)
    Skill: Optional[List] = Field(default_factory=list)

class UserCreateSchema(BaseModel):
    """
    Schema for validating User creation data.
    This schema is used when creating new users in Shiftbase.
    """
    # Required fields
    first_name: str = Field(description="First name of user")
    last_name: str = Field(description="Last name of user")
    locale: str = Field(
        description="The locale of the user, in RFC5646 format",
        pattern=r"^(nl-NL|en-GB|fr-FR|de-DE|es-ES|pl-PL|sv-SE|ro-RO)$"
    )
    startdate: date = Field(description="Date the user is active in the system")
    email: str = Field(description="Email address of the user")
    department_id: str = Field(description="Department ID the user belongs to")

    # Optional fields
    prefix: Optional[str] = Field(default="", description="Prefix of last name")
    order: Optional[str] = Field(default="50", description="Used for sorting users")
    enddate: Optional[date] = Field(default=None, description="Date the user is inactive in the system")
    street_address: Optional[str] = Field(default=None, description="Street address")
    post_code: Optional[str] = Field(default=None, description="Postal code")
    city: Optional[str] = Field(default=None, description="City")
    phone_nr: Optional[str] = Field(default=None, description="Phone number")
    mobile_nr: Optional[str] = Field(default=None, description="Mobile number")
    emergency_nr: Optional[str] = Field(default=None, description="Emergency contact number")
    hire_date: Optional[date] = Field(default=None, description="Date the user is hired")
    birthplace: Optional[str] = Field(default=None, description="Birthplace")
    birthdate: Optional[date] = Field(default=None, description="Birth date")
    nationality: Optional[str] = Field(default=None, description="Nationality of user")
    ssn: Optional[str] = Field(default=None, description="Social security number")
    passport_number: Optional[str] = Field(default=None, description="Document number of passport")
    banknr: Optional[str] = Field(default=None, description="Bank number of user")
    employee_nr: Optional[str] = Field(default=None, description="Employee number")
    custom_fields: Optional[Union[Dict[str, Any], str]] = Field(default=None, description="User custom fields")
    roster_note: Optional[str] = Field(default=None, description="Note that shows up in the schedule")
    invited: Optional[bool] = Field(default=False, description="Whether the user is invited")

    # Contract fields - Defining what contracts the user should have
    contract: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of contracts for the user"
    )

    # Team membership
    team: Optional[List[Union[str, int]]] = Field(
        default=None,
        description="List of team IDs the user belongs to"
    )

    # Group membership
    users_group: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="User group memberships"
    )

    # Skills
    skill: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="User skills"
    )


    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields

class UserUpdateSchema(BaseModel):
    """
    Schema for validating User update data.
    This schema is used when updating existing users in Shiftbase.
    """
    # Optional fields - all fields are optional for update
    first_name: Optional[str] = Field(default=None, description="First name of user")
    prefix: Optional[str] = Field(default=None, description="Prefix of last name")
    last_name: Optional[str] = Field(default=None, description="Last name of user")
    locale: Optional[str] = Field(
        default=None,
        description="The locale of the user, in RFC5646 format",
        pattern=r"^(nl-NL|en-GB|fr-FR|de-DE|es-ES|pl-PL|sv-SE|ro-RO)$"
    )
    order: Optional[str] = Field(default=None, description="Used for sorting users")
    startdate: Optional[date] = Field(default=None, description="Date the user is active in the system")
    enddate: Optional[date] = Field(default=None, description="Date the user is inactive in the system")
    street_address: Optional[str] = Field(default=None, description="Street address")
    post_code: Optional[str] = Field(default=None, description="Postal code")
    city: Optional[str] = Field(default=None, description="City")
    phone_nr: Optional[str] = Field(default=None, description="Phone number")
    mobile_nr: Optional[str] = Field(default=None, description="Mobile number")
    emergency_nr: Optional[str] = Field(default=None, description="Emergency contact number")
    email: Optional[str] = Field(default=None, description="Email address of the user")
    hire_date: Optional[date] = Field(default=None, description="Date the user is hired")
    birthplace: Optional[str] = Field(default=None, description="Birthplace")
    birthdate: Optional[date] = Field(default=None, description="Birth date")
    nationality: Optional[str] = Field(default=None, description="Nationality of user")
    ssn: Optional[str] = Field(default=None, description="Social security number")
    passport_number: Optional[str] = Field(default=None, description="Document number of passport")
    banknr: Optional[str] = Field(default=None, description="Bank number of user")
    employee_nr: Optional[str] = Field(default=None, description="Employee number")
    custom_fields: Optional[Union[Dict[str, Any], str]] = Field(default=None, description="User custom fields")
    roster_note: Optional[str] = Field(default=None, description="Note that shows up in the schedule")
    invited: Optional[bool] = Field(default=None, description="Whether the user is invited")

    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields
