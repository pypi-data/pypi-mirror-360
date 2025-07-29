from typing import Dict, Optional, List
import pandas as pd
from .schemas.holidays import HolidayGroupSchema, PublicHolidaySchema
from brynq_sdk_functions import Functions

class Holidays:
    """
    Handles all holiday related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.base_uri = "holidays"

    def get_public_holidays(self, country: str, year: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves public holidays for a given country and optionally a region.
        
        Args:
            country (str): Alpha-3 country code (e.g., "NLD" for Netherlands)
            year (str, optional): Selected year (e.g., "2023")
            region (str, optional): Either Alpha-2 or Alpha-3 region code
            
        Returns:
            pd.DataFrame: Public holidays data
            
        Raises:
            ValueError: If parameters are invalid
            ValueError: If holiday data fails validation
            requests.HTTPError: If the API request fails
        """
            
        # Construct the endpoint URL
        endpoint = f"{self.base_uri}/calendars/{country}"
        
        # Prepare query parameters
        params = {}
        if year:
            params["year"] = year
        if region:
            params["region"] = region
            
        # Make the request
        response_data = self.shiftbase.get(endpoint, params)
        
        # Extract holidays data
        holidays = response_data.get("data", [])
        
        # Convert to DataFrame
        df = pd.DataFrame(holidays)
        
        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, PublicHolidaySchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid holiday data: {str(e)}"
            raise ValueError(error_message)
        
    def get_holiday_groups(self) -> pd.DataFrame:
        """
        Retrieves the list of holiday groups from Shiftbase.
        
        Returns:
            pd.DataFrame: Holiday groups data
            
        Raises:
            ValueError: If the holiday groups data fails validation
            requests.HTTPError: If the API request fails
        """
        # Construct the endpoint URL
        endpoint = f"{self.base_uri}/groups"
        
        # Make the request
        response_data = self.shiftbase.get(endpoint)

        # Convert to DataFrame
        df = pd.DataFrame(response_data)
        
        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, HolidayGroupSchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid holiday group data: {str(e)}"
            raise ValueError(error_message) 