from typing import Dict, Optional, List, Union
import pandas as pd
import re
from .schemas.rosters import RosterSchema
from brynq_sdk_functions import Functions
from datetime import date

class Rosters:
    """
    Handles all roster (shift schedule) related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "rosters"

    def get(self,
           department_id: Optional[Union[str, List[str]]] = None,
           max_date: Optional[date] = None,
           min_date: Optional[date] = None,
           optimized: Optional[str] = None,
           user_id: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves a list of rosters (shift schedules) from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/rosters
        
        Args:
            department_id (str or List[str], optional): Filter on one or multiple department IDs.
                String or array accepted. Example: ["123","456","789"]
            max_date (date, optional): The maximum date for the returned rosters.
                If not present the current day will be used.
            min_date (date, optional): The minimum date for the returned rosters.
                If not present the current day will be used.
            optimized (str, optional): With this enabled an optimized dataset will be returned,
                containing less data.
            user_id (str, optional): Filter on a user ID.
            
        Returns:
            pd.DataFrame: Rosters data
            
        Raises:
            ValueError: If parameters are invalid or roster data fails validation
            requests.HTTPError: If the API request fails
        """
        # Validate parameters
        if isinstance(department_id, str) and not re.match(r"^[0-9]+$", department_id):
            raise ValueError("department_id must contain only digits")
            
        if isinstance(department_id, list):
            for dept_id in department_id:
                if not re.match(r"^[0-9]+$", dept_id):
                    raise ValueError(f"Invalid department_id: {dept_id}. Must contain only digits.")
            
        if user_id and not re.match(r"^[0-9]+$", user_id):
            raise ValueError("user_id must contain only digits")
        
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
        if optimized:
            params["optimized"] = optimized
        if user_id:
            params["user_id"] = user_id
            
        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        
        # Convert to DataFrame
        rosters = []
        for roster_data in response_data:
            # Extract roster from the potentially nested structure
            roster = roster_data.get("Roster", roster_data)
            rosters.append(roster)
            
        df = pd.DataFrame(rosters)
        
        # If no data is returned, return an empty DataFrame
        if df.empty:
            return df
        
        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, RosterSchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid roster data: {str(e)}"
            raise ValueError(error_message)
        
    def get_by_id(self, occurrence_id: str) -> pd.DataFrame:
        """
        Retrieves a specific roster by its occurrence ID.
        
        Endpoint: GET https://api.shiftbase.com/api/rosters/{occurrenceId}
        
        The occurrenceId is the id that is unique for a date. It can consist of:
        - just an id for non-recurring shifts 
        - a combination of id:date for recurring shifts (e.g., 1:2017-01-01)
        
        Args:
            occurrence_id (str): The unique identifier of the roster occurrence
            
        Returns:
            Dict: Roster details
            
        Raises:
            ValueError: If occurrence_id is invalid or roster data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
                - 404: Roster not found
        """
        # Validate occurrence_id
        if not occurrence_id:
            raise ValueError("occurrence_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{occurrence_id}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract roster data and convert to DataFrame for validation
            roster_data = response_data.get("Roster", response_data)
            df = pd.DataFrame([roster_data])
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, RosterSchema)
                # Return the first row as a dictionary
                return valid_data
            except Exception as e:
                error_message = f"Invalid roster data: {str(e)}"
                raise ValueError(error_message)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View all rosters' permission.")
            elif "404" in str(e):
                raise ValueError(f"Roster with occurrence ID {occurrence_id} not found.")
            raise 