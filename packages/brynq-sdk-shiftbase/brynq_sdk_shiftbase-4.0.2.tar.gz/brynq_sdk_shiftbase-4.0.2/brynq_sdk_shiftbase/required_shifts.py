from typing import Dict, Optional, List
import pandas as pd
import re
from .schemas.required_shifts import RequiredShiftSchema
from brynq_sdk_functions import Functions
from datetime import date

class RequiredShifts:
    """
    Handles all required shift related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "required_shifts"

    def get(self, 
           department_id: Optional[str] = None,
           max_date: Optional[date] = None,
           min_date: Optional[date] = None) -> pd.DataFrame:
        """
        Retrieves a list of required shifts from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/required_shifts
        
        Args:
            department_id (str, optional): Filter on department ID. Must contain only digits.
            max_date (date, optional): The maximum date for the returned required shifts.
                                     If not present the current day will be used.
            min_date (date, optional): The minimum date for the returned required shifts.
                                     If not present the current day will be used.
            
        Returns:
            pd.DataFrame: Required shifts data
            
        Raises:
            ValueError: If parameters are invalid or required shift data fails validation
            requests.HTTPError: If the API request fails
        """
        # Validate parameters
        if department_id and not re.match(r"^[0-9]+$", department_id):
            raise ValueError("department_id must contain only digits")
            
        params = {}
        # Validate date parameters
        if max_date:
            if not isinstance(max_date, date):
                raise TypeError("max_date must be a date object")
            params["max_date"] = max_date.strftime("%Y-%m-%d")

            
        if min_date:
            if not isinstance(min_date, date):
                raise TypeError("min_date must be a date object")
            params["min_date"] = min_date.strftime("%Y-%m-%d")
        # Prepare query parameters
        if department_id:
            params["department_id"] = department_id
            
        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        
        # The API returns a list of objects, each with a RequiredShift property
        required_shifts = [item.get("RequiredShift") for item in response_data]
        
        # Convert to DataFrame
        df = pd.DataFrame(required_shifts)
        
        # If no data is returned, return an empty DataFrame
        if df.empty:
            return df
        
        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, RequiredShiftSchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid required shift data: {str(e)}"
            raise ValueError(error_message)
        
    def get_by_id(self, occurrence_id: str) -> pd.DataFrame:
        """
        Retrieves a specific required shift by its occurrence ID.
        
        Endpoint: GET https://api.shiftbase.com/api/required_shifts/{occurrenceId}
        
        The occurrenceId is the id that is unique for a date. It can consist of:
        - just an id for non-recurring shifts 
        - a combination of id:date for recurring shifts (e.g., 1:2017-01-01)
        
        Args:
            occurrence_id (str): The unique identifier of the required shift occurrence
            
        Returns:
            Dict: Required shift details
            
        Raises:
            ValueError: If occurrence_id is invalid or required shift data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
                - 404: Required shift not found
        """
        # Validate occurrence_id
        if not occurrence_id:
            raise ValueError("occurrence_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{occurrence_id}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract required shift data and convert to DataFrame for validation
            required_shift_data = response_data.get("RequiredShift", {})
            df = pd.DataFrame([required_shift_data])
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, RequiredShiftSchema)
                # Return the first row as a dictionary
                return valid_data
            except Exception as e:
                error_message = f"Invalid required shift data: {str(e)}"
                raise ValueError(error_message)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View required shifts' permission.")
            elif "404" in str(e):
                raise ValueError(f"Required shift with occurrence ID {occurrence_id} not found.")
            raise 