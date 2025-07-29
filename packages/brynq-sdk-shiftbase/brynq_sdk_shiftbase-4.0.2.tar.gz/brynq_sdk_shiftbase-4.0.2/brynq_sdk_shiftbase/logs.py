from typing import Dict, Optional, List
import pandas as pd
from .schemas.logs import LogSchema
from brynq_sdk_functions import Functions
from datetime import date
class Logs:
    """
    Handles all log related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "logs"

    def get(self, 
           department_id: Optional[str] = None,
            max_date: Optional[date] = None,
            min_date: Optional[date] = None,) -> pd.DataFrame:
        """
        Retrieves the logs from Shiftbase.
        
        The log contains daily information per department such as the turnover and
        expected turnover as well as the publishing status of a schedule and
        if timesheets are open for modification.
        
        Args:
            department_id (str, optional): Filter on a department ID
            min_date (date, optional): The minimum date for the returned logs (YYYY-MM-DD).
                                     If not present the current day will be used.
            max_date (date, optional): The maximum date for the returned logs (YYYY-MM-DD).
                                     If not present the current day will be used.
            
        Returns:
            pd.DataFrame: Log data
            
        Raises:
            ValueError: If parameters are invalid or log data fails validation
            requests.HTTPError: If the API request fails
        """
        # Validate parameters
        if department_id and not department_id.isdigit():
            raise ValueError("department_id must contain only digits")
            
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
            
        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        
        # Convert to DataFrame
        df = pd.DataFrame(response_data)
        
        # Validate with Functions.validate_data

        if not df.empty:
            try:
                valid_data,_ = Functions.validate_data(df, LogSchema)
                return valid_data
            except Exception as e:
                error_message = f"Invalid log data: {str(e)}"
                raise ValueError(error_message)
        else:
            return df