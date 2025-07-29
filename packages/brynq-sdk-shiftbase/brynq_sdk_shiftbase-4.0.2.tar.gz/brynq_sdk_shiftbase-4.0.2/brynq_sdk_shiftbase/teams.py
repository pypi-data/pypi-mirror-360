from typing import Dict, Optional, List, Union
import pandas as pd
import re
from .schemas.teams import TeamSchema
from brynq_sdk_functions import Functions

class Teams:
    """
    Handles all team related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "teams"

    def get(self, department_id: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves a list of teams from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/teams
        
        Args:
            department_id (str, optional): Filter on department ID. Must contain only digits.
            
        Returns:
            pd.DataFrame: Teams data
            
        Raises:
            ValueError: If parameters are invalid or team data fails validation
            requests.HTTPError: If the API request fails
        """
        # Validate parameters
        if department_id and not re.match(r"^[0-9]+$", department_id):
            raise ValueError("department_id must contain only digits")
        
        # Prepare query parameters
        params = {}
        if department_id:
            params["department_id"] = department_id
            
        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        
        # Extract team data from the response
        teams = []
        for team_data in response_data:
            # Extract team from the potentially nested structure
            team = team_data.get("Team", team_data)
            teams.append(team)
            
        # Convert to DataFrame
        df = pd.DataFrame(teams)
        
        # If no data is returned, return an empty DataFrame
        if df.empty:
            return df
        
        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, TeamSchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid team data: {str(e)}"
            raise ValueError(error_message)
        
    def get_by_id(self, team_id: str) -> Dict:
        """
        Retrieves a specific team by its ID.
        
        Endpoint: GET https://api.shiftbase.com/api/teams/{teamId}
        
        Args:
            team_id (str): The unique identifier of the team
            
        Returns:
            Dict: Team details including associated users
            
        Raises:
            ValueError: If team_id is invalid or team data fails validation
            requests.HTTPError: 
                - 404: Team not found
        """
        # Validate team_id
        if not team_id:
            raise ValueError("team_id cannot be empty")
            
        if not re.match(r"^[0-9]+$", team_id):
            raise ValueError("team_id must contain only digits")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{team_id}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract team data and additional information
            team_data = response_data.get("Team", {})
            
            # Convert to DataFrame for validation
            df = pd.DataFrame([team_data])
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, TeamSchema)
                # Add additional information to the result
                return valid_data
            except Exception as e:
                error_message = f"Invalid team data: {str(e)}"
                raise ValueError(error_message)
                
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"Team with ID {team_id} not found.")
            raise 