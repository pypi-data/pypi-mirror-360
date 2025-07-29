from typing import Dict, Optional, List
import pandas as pd
from datetime import date
from .schemas.corrections import CorrectionSchema
from brynq_sdk_functions import Functions

class Corrections:
    """
    Handles all correction related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "corrections"

    def get(self, 
            max_date: Optional[date] = None,
            min_date: Optional[date] = None,
            type: Optional[str] = None, 
            user_id: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves the list of corrections from Shiftbase.
        
        Args:
            max_date (str, optional): The maximum date for the returned corrections. 
                                      If not present the current day will be used.
            min_date (str, optional): The minimum date for the returned corrections. 
                                      If not present the current day will be used.
            type (str, optional): Filter on correction type. 
                                  Allowed values: Overtime, Time off balance
            user_id (str, optional): Returns correction from a specific user.
            
        Returns:
            pd.DataFrame: Correction data
            
        Raises:
            ValueError: If the correction data fails validation or parameters are invalid
        """
        # Validate parameters
        if type and type not in ["Overtime", "Time off balance", "Time off balance cycle"]:
            raise ValueError("type must be one of: Overtime, Time off balance, Time off balance cycle")
            
        # Prepare query parameters
        params = {}
        if max_date:
            if not isinstance(max_date, date):
                raise TypeError("max_date must be a datetime object")
            params["max_date"] = max_date.strftime("%Y-%m-%d")
        if min_date:
            if not isinstance(min_date, date):
                raise TypeError("min_date must be a datetime object")
            params["min_date"] = min_date.strftime("%Y-%m-%d")
        if type:
            params["type"] = type
        if user_id:
            params["user_id"] = user_id
            
        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        if response_data:
            # Extract corrections data
            corrections = response_data.get("data", [])

            # Validate the data using brynq_sdk_functions
            valid_data, invalid_data = Functions.validate_pydantic_data(
                corrections,
                CorrectionSchema
            )

            # Raise error if there are invalid records
            if invalid_data:
                error_message = f"Invalid correction data: {len(invalid_data)} records failed validation"
                raise ValueError(error_message)

            # Return as DataFrame
            return pd.DataFrame(valid_data)
        else:
            return pd.DataFrame()
        
    def get_by_id(self, correction_id: str) -> pd.DataFrame:
        """
        Retrieves a specific correction by ID.
        
        Args:
            correction_id (str): The unique identifier of the correction
            
        Returns:
            Dict: Correction details
            
        Raises:
            ValueError: If correction_id is invalid or correction data fails validation
            requests.HTTPError: 
                - 403: If the user doesn't have required permissions
                - 404: If the correction is not found
        """
        # Validate correction_id
        if not correction_id:
            raise ValueError("correction_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{correction_id}"
        
        # Make the request
        response_data = self.shiftbase.get(endpoint)
        
        # Extract correction data
        correction_data = response_data.get("data", {})
        
        # Validate correction data if present
        if correction_data:
            correction_list = [correction_data]
            valid_data, invalid_data = Functions.validate_pydantic_data(
                correction_list,
                CorrectionSchema
            )
            
            if invalid_data:
                error_message = f"Invalid correction data: {len(invalid_data)} record failed validation"
                raise ValueError(error_message)
                
            # Update with validated data
            correction_data = valid_data[0]
        
        # Return the correction data
        return pd.DataFrame(correction_data)