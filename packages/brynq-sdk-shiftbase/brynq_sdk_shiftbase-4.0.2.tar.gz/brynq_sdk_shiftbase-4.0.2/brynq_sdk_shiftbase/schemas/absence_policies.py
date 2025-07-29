"""
Schema definition for AbsencePolicy data validation.
"""
from typing import List, Optional, Union, Literal, Annotated
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, validator


class TimeOffDetermination(str, Enum):
    """Time off determination options"""
    SCHEDULED = "SCHEDULED"
    CONTRACT = "CONTRACT"
    NONE = "NONE"


class DayValueDetermination(str, Enum):
    """Day value determination options"""
    CONTRACT = "CONTRACT"
    GERMAN_13_WEEK = "GERMAN_13_WEEK"
    NONE = "NONE"


class TimeOffAccrualSourceHours(str, Enum):
    """Time off accrual source hours options"""
    CONTRACT = "CONTRACT"
    WORKED = "WORKED"
    NONE = "NONE"


class WaitHoursFrom(str, Enum):
    """Wait hours from options"""
    SALARY = "SALARY"
    TIME_OFF_BALANCE = "TIME_OFF_BALANCE"


class AbsencePolicyConfiguration(BaseModel):
    """
    Configuration for absence policy.
    Make absence types available in the policy and possibly link time off balances to the absence type.
    """
    absenceTypeId: str = Field(
        description="The unique identifier of an absence type",
        pattern=r"^[0-9]+$"
    )
    balanceIds: List[UUID] = Field(
        description="The unique identifiers of time off balances",
    )
    timeOffDetermination: TimeOffDetermination = Field(
        description="Time off determination - defines how time-off hours are calculated for the absence type"
    )
    dayValueDetermination: Optional[DayValueDetermination] = Field(
        description="Day value determination. Only available when the unit of the absence type is days",
        default=None
    )
    autoSelectBalance: Optional[bool] = Field(
        description="When enabled, automatically deducts leave from available balances prioritizing those closest to expiration first",
        default=None
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


class AbsencePolicySchema(BaseModel):
    """
    Schema for validating AbsencePolicy data returned from Shiftbase API.
    An AbsencePolicy is a wrapper around a group of absence settings that can be linked
    to a user on ContractType level.
    """
    id: Optional[UUID] = Field(
        description="The unique identifier of the policy",
        default=None
    )
    name: str = Field(
        description="A short name for the policy",
        max_length=160
    )
    description: Optional[str] = Field(
        description="Optional extra description for the policy",
        default="",
        max_length=360
    )
    configuration: List[AbsencePolicyConfiguration] = Field(
        description="Make absence types available in the policy and possible link time off balances to the absence type",
    )
    timeOffAccrualSourceHours: TimeOffAccrualSourceHours = Field(
        description="Specify how the time off balances should be accrued"
    )
    waitHoursFrom: WaitHoursFrom = Field(
        description="Specify where the waiting hours will be deducted from",
        default=WaitHoursFrom.SALARY
    )
    waitHoursFromTimeOffBalanceId: Optional[UUID] = Field(
        description="If the waitHoursFrom is set to TIME_OFF_BALANCE here, you can specify which time off balance the wait hours are deducted from",
        default=None
    )
    publicHolidayAbsenceTypeId: Optional[str] = Field(
        description="Specify the absence type to automatically create absences on public holidays",
        default=None,
        pattern=r"^[0-9]+$"
    )
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
