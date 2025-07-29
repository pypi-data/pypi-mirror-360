from typing import Dict, Optional, List
import pandas as pd
from .schemas.open_shifts import OpenShiftSchema
from brynq_sdk_functions import Functions
import re
from datetime import date
class OpenShifts:
    """
    Handles all open shift related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "open_shifts"

    def get(self, 
           department_id: Optional[str] = None,
           max_date: Optional[date] = None,
           min_date: Optional[date] = None,
           user_id: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves a list of open shifts from Shiftbase.
        
        Args:
            department_id (str, optional): Filter on department ID. Must contain only digits.
            max_date (date, optional): The maximum date for the returned open shifts (YYYY-MM-DD).
                                     If not present the current day will be used.
            min_date (date, optional): The minimal date for the returned open shifts (YYYY-MM-DD).
                                     If not present the current day will be used.
            user_id (str, optional): Filter on user ID. Must contain only digits.
            
        Returns:
            pd.DataFrame: Open shifts data
            
        Raises:
            ValueError: If parameters are invalid or open shift data fails validation
            requests.HTTPError: If the API request fails
        """
        # Validate parameters
        if department_id and not re.match(r"^[0-9]+$", department_id):
            raise ValueError("department_id must contain only digits")
            
        if user_id and not re.match(r"^[0-9]+$", user_id):
            raise ValueError("user_id must contain only digits")
            
        if max_date and not re.match(r"^\d{4}-\d{2}-\d{2}$", max_date):
            raise ValueError("max_date must be in YYYY-MM-DD format")
            
        if min_date and not re.match(r"^\d{4}-\d{2}-\d{2}$", min_date):
            raise ValueError("min_date must be in YYYY-MM-DD format")
        
        # Prepare query parameters
        params = {}
        if department_id:
            params["department_id"] = department_id
        if max_date:
            if not isinstance(max_date, date):
                raise TypeError("max_date must be a datetime object")
            params["max_date"] = max_date.strftime("%Y-%m-%d")
        if min_date:
            if not isinstance(min_date, date):
                raise TypeError("min_date must be a datetime object")
            params["min_date"] = min_date.strftime("%Y-%m-%d")
        if user_id:
            params["user_id"] = user_id
            
        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        
        # The API returns a list of objects, each with an OpenShift property
        open_shifts = [item.get("OpenShift") for item in response_data]
        
        # Convert to DataFrame
        df = pd.DataFrame(open_shifts)
        
        # If no data is returned, return an empty DataFrame
        if df.empty:
            return df
        
        # Validate with Functions.validate_data
        try:
            valid_data,_ = Functions.validate_data(df, OpenShiftSchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid open shift data: {str(e)}"
            raise ValueError(error_message)
        
    def get_by_id(self, occurrence_id: str) -> pd.DataFrame:
        """
        Retrieves a specific open shift by its occurrence ID.
        
        Endpoint: GET https://api.shiftbase.com/api/open_shifts/{occurrenceId}
        
        Args:
            occurrence_id (str): The unique identifier of the open shift occurrence
            
        Returns:
            Dict: Open shift details
            
        Raises:
            ValueError: If occurrence_id is invalid or open shift data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
                - 404: Open shift not found
        """
        # Validate occurrence_id
        if not occurrence_id:
            raise ValueError("occurrence_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{occurrence_id}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract open shift data and convert to DataFrame for validation
            open_shift_data = response_data.get("OpenShift", {})
            df = pd.DataFrame([open_shift_data])
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, OpenShiftSchema)
                # Return the first row as a dictionary
                return valid_data
            except Exception as e:
                error_message = f"Invalid open shift data: {str(e)}"
                raise ValueError(error_message)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View all rosters' permission.")
            elif "404" in str(e):
                raise ValueError(f"Open shift with occurrence ID {occurrence_id} not found.")
            raise 