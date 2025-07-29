from typing import Dict, Optional, List, Union
import pandas as pd
import re
from .schemas.team_days import TeamDaySchema
from .schemas.teams import TeamSchema
from brynq_sdk_functions import Functions

class TeamDays:
    """
    Handles all team day related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "team_days"

    def get(self) -> pd.DataFrame:
        """
        Retrieves a list of team days from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/team_days
        
        Returns:
            pd.DataFrame: Team days data with associated team information
            
        Raises:
            ValueError: If team day data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
        """
        try:
            # Make the request
            response_data = self.shiftbase.get(self.uri)
            
            # Extract team day data from the response
            team_days = []
            teams = []
            
            for item in response_data:
                # Extract team day data
                team_day = item.get("TeamDay", {})
                if team_day:
                    team_days.append(team_day)
                
                # Extract team data
                team = item.get("Team", {})
                if team:
                    # Add team_day_id to link with team day
                    team["team_day_id"] = team_day.get("id")
                    teams.append(team)
            
            # Convert to DataFrames
            df_team_days = pd.DataFrame(team_days)
            df_teams = pd.DataFrame(teams) if teams else pd.DataFrame()
            
            # If no data is returned, return an empty DataFrame
            if df_team_days.empty:
                return df_team_days
            
            # Validate team day data with Functions.validate_data
            try:
                validated_team_days = Functions.validate_data(df_team_days, TeamDaySchema)
                
                # If we have team data, validate and join it
                if not df_teams.empty:
                    try:
                        validated_teams = Functions.validate_data(df_teams, TeamSchema)
                        
                        # Merge the data to include team information
                        result = pd.merge(
                            validated_team_days, 
                            validated_teams,
                            how="left",
                            left_on="team_id",
                            right_on="id",
                            suffixes=("", "_team")
                        )
                        return result
                    except Exception as e:
                        # If team validation fails, just return the team days
                        print(f"Warning: Invalid team data: {str(e)}. Returning only team days.")
                        return validated_team_days
                else:
                    return validated_team_days
            except Exception as e:
                error_message = f"Invalid team day data: {str(e)}"
                raise ValueError(error_message)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View team notes' or 'View budget' permission.")
            raise
        
    def get_by_id(self, team_day_id: str) -> pd.DataFrame:
        """
        Retrieves a specific team day by its ID.
        
        Endpoint: GET https://api.shiftbase.com/api/team_days/{teamDayId}
        
        Args:
            team_day_id (str): The unique identifier of the team day
            
        Returns:
            Dict: Team day details including associated team information
            
        Raises:
            ValueError: If team_day_id is invalid or team day data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
                - 404: Team day not found
        """
        # Validate team_day_id
        if not team_day_id:
            raise ValueError("team_day_id cannot be empty")
            
        if not re.match(r"^[0-9]+$", team_day_id):
            raise ValueError("team_day_id must contain only digits")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{team_day_id}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # The API may return an array with one item
            if isinstance(response_data, list) and len(response_data) > 0:
                response_item = response_data[0]
            else:
                response_item = response_data
                
            # Extract team day data and team information
            team_day_data = response_item.get("TeamDay", {})
            team_data = response_item.get("Team", {})
            
            # Convert to DataFrame for validation
            df_team_day = pd.DataFrame([team_day_data])
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df_team_day, TeamDaySchema)
                # Convert validated data back to dictionary
                result = valid_data.iloc[0].to_dict()
                
                # If we have team data, validate and add it to the result
                if team_data:
                    try:
                        df_team = pd.DataFrame([team_data])
                        validated_team = Functions.validate_data(df_team, TeamSchema)
                        # Add team information to the result
                        result["team"] = validated_team.iloc[0].to_dict()
                    except Exception as e:
                        # If team validation fails, add the raw team data
                        print(f"Warning: Invalid team data: {str(e)}. Adding unvalidated team data.")
                        result["team"] = team_data
                
                return pd.DataFrame(result)
            except Exception as e:
                error_message = f"Invalid team day data: {str(e)}"
                raise ValueError(error_message)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View team notes' or 'View budget' permission.")
            elif "404" in str(e):
                raise ValueError(f"Team day with ID {team_day_id} not found.")
            raise 