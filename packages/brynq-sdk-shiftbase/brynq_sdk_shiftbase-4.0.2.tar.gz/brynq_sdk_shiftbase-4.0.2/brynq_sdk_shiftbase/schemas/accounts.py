import pandera as pa
from pandera.typing import Series, DateTime, Date
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date

class AccountSchema(pa.DataFrameModel):
    """
    Schema for validating Account data returned from Shiftbase API.
    """
    # Read-only fields
    id: Series[str] = pa.Field(coerce=True)
    created: Series[DateTime] = pa.Field(nullable=True)
    
    # Required fields
    company: Series[str] = pa.Field(coerce=True)
    email: Series[str] = pa.Field(coerce=True)
    country: Series[str] = pa.Field(coerce=True)
    time_zone: Series[str] = pa.Field(coerce=True)
    
    # Optional fields
    account_type_id: Series[str] = pa.Field(nullable=True)
    subscription_id: Series[str] = pa.Field(nullable=True)
    currency_id: Series[str] = pa.Field(nullable=True)
    domain: Series[str] = pa.Field(nullable=True)
    host: Series[str] = pa.Field(nullable=True)
    day_start: Series[str] = pa.Field(nullable=True)
    day_end: Series[str] = pa.Field(nullable=True)
    locale: Series[str] = pa.Field(nullable=True)
    user_sortfield: Series[str] = pa.Field(nullable=True)
    user_sortdirection: Series[str] = pa.Field(nullable=True)
    user_name_format: Series[str] = pa.Field(nullable=True)
    enforce_mfa: Series[bool] = pa.Field(nullable=True)
    servicedesk_access_enabled: Series[bool] = pa.Field(nullable=True)
    test: Series[bool] = pa.Field(nullable=True)
    onboarding: Series[str] = pa.Field(nullable=True)
    estimated_users: Series[str] = pa.Field(nullable=True)
    group_id: Series[str] = pa.Field(nullable=True)
    schedule_compliance_check: Series[bool] = pa.Field(nullable=True)
    integration_plus: Series[bool] = pa.Field(nullable=True)
    self_onboarding: Series[str] = pa.Field(nullable=True)
    publish_schedules: Series[bool] = pa.Field(nullable=True)
    coc_in_schedule: Series[bool] = pa.Field(nullable=True)
    contract_reminder_first: Series[str] = pa.Field(nullable=True)
    contract_reminder_second: Series[str] = pa.Field(nullable=True)
    invoice_company: Series[str] = pa.Field(nullable=True)
    first_name: Series[str] = pa.Field(nullable=True)
    last_name: Series[str] = pa.Field(nullable=True)
    street_address: Series[str] = pa.Field(nullable=True)
    zipcode: Series[str] = pa.Field(nullable=True)
    city: Series[str] = pa.Field(nullable=True)
    invoice_email: Series[str] = pa.Field(nullable=True)
    vat: Series[str] = pa.Field(nullable=True)
    vat_valid: Series[bool] = pa.Field(nullable=True)
    vat_reverse_charge: Series[str] = pa.Field(nullable=True)
    user_id: Series[str] = pa.Field(nullable=True)
    start_date: Series[DateTime] = pa.Field(nullable=True)
    continue_subscription: Series[bool] = pa.Field(nullable=True)
    vacationhours_default: Series[str] = pa.Field(nullable=True)
    wait_hours: Series[str] = pa.Field(nullable=True)
    invoice_send_method: Series[str] = pa.Field(nullable=True)
    invoice_due_date_interval: Series[str] = pa.Field(nullable=True)
    payment_method: Series[str] = pa.Field(nullable=True)
    debit_name: Series[str] = pa.Field(nullable=True)
    debit_banknr: Series[str] = pa.Field(nullable=True)
    debit_bic: Series[str] = pa.Field(nullable=True)
    phone_nr: Series[str] = pa.Field(nullable=True)
    deleted: Series[bool] = pa.Field(nullable=True)
    send_invoice_to_reseller: Series[bool] = pa.Field(nullable=True)
    language: Series[str] = pa.Field(nullable=True)
    support_phone: Series[str] = pa.Field(nullable=True)
    support: Series[str] = pa.Field(nullable=True)
        
    class Config:
        strict = False
        coerce = True


class AccountUpdateSchema(BaseModel):
    """
    Schema for validating Account update data.
    This schema is used when updating existing accounts in Shiftbase.
    """
    # Required fields
    id: str = Field(
        description="Unique identifier for the account"
    )
    account_type_id: str = Field(
        description="Account type identifier"
    )
    company: str = Field(
        description="Company name"
    )
    country: str = Field(
        description="Country code (e.g., NL)"
    )
    domain: str = Field(
        description="Domain for the account"
    )
    host: str = Field(
        description="Host information"
    )
    user_sortfield: str = Field(
        description="Field used for sorting users"
    )
    user_sortdirection: str = Field(
        description="Direction for user sorting (ASC/DESC)"
    )
    user_name_format: str = Field(
        description="Format for displaying user names"
    )
    enforce_mfa: bool = Field(
        description="Whether multi-factor authentication is required"
    )
    servicedesk_access_enabled: bool = Field(
        description="Whether servicedesk access is enabled"
    )
    test: bool = Field(
        description="Whether this is a test account"
    )
    onboarding: str = Field(
        description="Onboarding status"
    )
    estimated_users: str = Field(
        description="Estimated number of users"
    )
    group_id: str = Field(
        description="Group identifier"
    )
    schedule_compliance_check: bool = Field(
        description="Whether schedule compliance check is enabled"
    )
    publish_schedules: bool = Field(
        description="Whether schedules are published"
    )
    coc_in_schedule: bool = Field(
        description="Whether COC is included in schedule"
    )
    contract_reminder_first: str = Field(
        description="Days for first contract reminder"
    )
    contract_reminder_second: str = Field(
        description="Days for second contract reminder"
    )
    invoice_company: str = Field(
        description="Invoice company name"
    )
    first_name: str = Field(
        description="First name of account owner"
    )
    last_name: str = Field(
        description="Last name of account owner"
    )
    street_address: str = Field(
        description="Street address"
    )
    zipcode: str = Field(
        description="Zip/postal code"
    )
    city: str = Field(
        description="City"
    )
    email: str = Field(
        description="Primary email address"
    )
    invoice_email: str = Field(
        description="Email address for invoices"
    )
    user_id: str = Field(
        description="User identifier"
    )
    start_date: date = Field(
        description="Account start date"
    )
    continue_subscription: bool = Field(
        description="Whether to continue subscription"
    )
    vacationhours_default: str = Field(
        description="Default vacation hours"
    )
    wait_hours: str = Field(
        description="Wait hours"
    )
    invoice_send_method: str = Field(
        description="Method for sending invoices"
    )
    invoice_due_date_interval: str = Field(
        description="Due date interval for invoices"
    )
    payment_method: str = Field(
        description="Payment method"
    )
    deleted: bool = Field(
        description="Whether the account is deleted"
    )
    send_invoice_to_reseller: bool = Field(
        description="Whether to send invoice to reseller"
    )
    integration_plus: bool = Field(
        description="Whether integration plus is enabled"
    )
    
    # Optional fields
    vat: Optional[str] = Field(
        description="VAT number",
        default=None
    )
    vat_valid: Optional[bool] = Field(
        description="Whether VAT is valid",
        default=None
    )
    vat_reverse_charge: Optional[str] = Field(
        description="VAT reverse charge",
        default=None
    )
    debit_name: Optional[str] = Field(
        description="Debit name",
        default=None
    )
    debit_banknr: Optional[str] = Field(
        description="Bank account number",
        default=None
    )
    debit_bic: Optional[str] = Field(
        description="BIC code",
        default=None
    )
    phone_nr: Optional[str] = Field(
        description="Phone number",
        default=None
    )
    language: Optional[str] = Field(
        description="Language",
        default=None
    )
    support_phone: Optional[str] = Field(
        description="Support phone number",
        default=None
    )
    support: Optional[str] = Field(
        description="Support information",
        default=None
    )
    is_beta_account: Optional[bool] = Field(
        description="Whether this is a beta account",
        default=False
    )
    time_zone: Optional[str] = Field(
        description="Time zone (e.g., Europe/Amsterdam)",
        default=None
    )
    day_start: Optional[str] = Field(
        description="Default start time of day (e.g., 08:00:00)",
        default=None
    )
    day_end: Optional[str] = Field(
        description="Default end time of day (e.g., 18:00:00)",
        default=None
    )
    created: Optional[DateTime] = Field(
        description="Creation date and time",
        default=None
    )
    subscription_id: Optional[str] = Field(
        description="Subscription identifier",
        default=None
    )
    
    class Config:
        """Pydantic configuration"""
        extra = "allow"  # Allow additional fields not defined in the schema
        coerce = True