from typing import Dict, Optional
import pandas as pd
from .contracts import Contracts
from .time_off_balances import TimeOffBalances
from .absences import Absences

class Employees:
    """
    Handles all employee related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "users/"
        
        # Initialize employee-related classes
        self.contracts = Contracts(shiftbase)
        self.time_off_balances = TimeOffBalances(shiftbase)
        self.absences = Absences(shiftbase)


    def get_time_off_balance_details(self, employee_id: str, year: str) -> pd.DataFrame:
        """
        Returns the time off balances details for the given employee for a specific year.
        
        Will select end of contract OR end of year. Whichever is first for the given year.
        
        Args:
            employee_id (str): The unique identifier of the employee
            year (str): The full year to use
            
        Returns:
            pd.DataFrame: Time off balances details
            
        Raises:
            ValueError: If employee_id is not a valid digit string
            ValueError: If year is not a valid 4-digit year string
            requests.HTTPError: 
                - 403: If the user doesn't have required permissions (View time off balances, View own time off balances)
                - 404: If the employee is not found
                - 426: If the request fails for another reason
        """
        # Validate parameters
        if not employee_id.isdigit():
            raise ValueError("employee_id must contain only digits")
            
        if not (len(year) == 4 and year.isdigit()):
            raise ValueError("year must be a valid 4-digit year string")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}{employee_id}/timeOff/balances/details/{year}"
        
        # Make the request
        response_data = self.shiftbase.get(endpoint)
        
        # Return as DataFrame
        return pd.DataFrame(response_data.get("data", []))
        
    def get_upcoming_time_off_expiries(self, employee_id: str) -> pd.DataFrame:
        """
        Returns a list of upcoming time-off balance expiries within the date range 
        from today to six months in the future for the given employee.
        
        Args:
            employee_id (str): The unique identifier of the employee
            
        Returns:
            pd.DataFrame: Upcoming time off balance expiries
            
        Raises:
            ValueError: If employee_id is not a valid digit string
            requests.HTTPError: 
                - 403: If the user doesn't have required permissions (View time off balances, View own time off balances)
                - 426: If the request fails for another reason
        """
        # Validate employee_id parameter
        if not employee_id.isdigit():
            raise ValueError("employee_id must contain only digits")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}{employee_id}/timeOff/balances/expiries"
        
        # Make the request
        response_data = self.shiftbase.get(endpoint)
        
        # Return as DataFrame
        return pd.DataFrame(response_data.get("data", []))
