from typing import Dict, Optional, List, Union
import pandas as pd
import re
from .schemas.time_off_balances import TimeOffBalanceSchema, BalanceCycleSchema
from brynq_sdk_functions import Functions

class TimeOffBalances:
    """
    Handles all Time Off Balance related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "time_off_balances"

    def get(self) -> pd.DataFrame:
        """
        Retrieves all time off balances from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/time_off_balances
        
        Returns:
            pd.DataFrame: Time off balances data
            
        Raises:
            ValueError: If time off balance data fails validation
            requests.HTTPError: If the API request fails
        """
        # Make the request
        response_data = self.shiftbase.get(self.uri)
        
        if not response_data:
            return pd.DataFrame()
            
        # Extract time off balance data from response
        balances = []
        for item in response_data:
            if "TimeOffBalance" in item:
                balances.append(item["TimeOffBalance"])
        
        # Create DataFrame from response
        df = pd.DataFrame(balances)
        
        # If no data is returned, return an empty DataFrame
        if df.empty:
            return df
        
        # Convert expiration_in_months to int if it exists
        if 'expiration_in_months' in df.columns:
            df['expiration_in_months'] = pd.to_numeric(df['expiration_in_months'], errors='coerce').astype('Int64')
        
        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, TimeOffBalanceSchema)
            return valid_data
        except Exception as e:
            raise ValueError(f"Invalid time off balance data: {str(e)}")
            
    def get_by_id(self, balance_id: str) -> pd.DataFrame:
        """
        Retrieves a specific time off balance by its ID.
        
        Endpoint: GET https://api.shiftbase.com/api/time_off_balances/{timeOffBalanceId}
        
        Args:
            balance_id (str): The unique identifier of the time off balance
            
        Returns:
            Dict: Time off balance details
            
        Raises:
            ValueError: If balance_id is invalid or time off balance data fails validation
            requests.HTTPError: 
                - 404: Time off balance not found
        """
        # Validate balance_id
        if not balance_id:
            raise ValueError("balance_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{balance_id}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract time off balance data
            if not response_data or not "TimeOffBalance" in response_data:
                raise ValueError(f"Time off balance with ID {balance_id} not found or has an invalid format")
                
            balance_data = response_data["TimeOffBalance"]
            
            # Validate with TimeOffBalanceSchema
            df = pd.DataFrame([balance_data])
            try:
                valid_data, _ = Functions.validate_data(df, TimeOffBalanceSchema)
                validated_balance = valid_data.iloc[0].to_dict()
                
                # Restore the original structure with validated data
                response_data["TimeOffBalance"] = validated_balance
                
                return pd.DataFrame(response_data)
            except Exception as e:
                raise ValueError(f"Invalid time off balance data: {str(e)}")
                
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"Time off balance with ID {balance_id} not found.")
            raise
            
    def activate(self, balance_id: str) -> Dict:
        """
        Activates a time off balance.
        
        Endpoint: GET https://api.shiftbase.com/api/time_off_balances/{timeOffBalanceId}/activate
        
        Args:
            balance_id (str): The unique identifier of the time off balance
            
        Returns:
            Dict: Updated time off balance details
            
        Raises:
            ValueError: If balance_id is invalid or time off balance data fails validation
            requests.HTTPError: 
                - 404: Time off balance not found
                - 403: Unauthorized access
        """
        # Validate balance_id
        if not balance_id:
            raise ValueError("balance_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{balance_id}/activate"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract time off balance data
            if not response_data or not "TimeOffBalance" in response_data:
                raise ValueError(f"Time off balance with ID {balance_id} not found or has an invalid format")
                
            balance_data = response_data["TimeOffBalance"]
            
            # Validate with TimeOffBalanceSchema
            df = pd.DataFrame([balance_data])
            try:
                valid_data, _ = Functions.validate_data(df, TimeOffBalanceSchema)
                validated_balance = valid_data.iloc[0].to_dict()
                
                # Restore the original structure with validated data
                response_data["TimeOffBalance"] = validated_balance
                
                return response_data
            except Exception as e:
                raise ValueError(f"Invalid time off balance data: {str(e)}")
                
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"Time off balance with ID {balance_id} not found.")
            raise
            
    def deactivate(self, balance_id: str) -> Dict:
        """
        Deactivates a time off balance.
        
        Endpoint: GET https://api.shiftbase.com/api/time_off_balances/{timeOffBalanceId}/deactivate
        
        Args:
            balance_id (str): The unique identifier of the time off balance
            
        Returns:
            Dict: Updated time off balance details
            
        Raises:
            ValueError: If balance_id is invalid or time off balance data fails validation
            requests.HTTPError: 
                - 404: Time off balance not found
                - 403: Unauthorized access
        """
        # Validate balance_id
        if not balance_id:
            raise ValueError("balance_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{balance_id}/deactivate"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract time off balance data
            if not response_data or not "TimeOffBalance" in response_data:
                raise ValueError(f"Time off balance with ID {balance_id} not found or has an invalid format")
                
            balance_data = response_data["TimeOffBalance"]
            
            # Validate with TimeOffBalanceSchema
            df = pd.DataFrame([balance_data])
            try:
                valid_data, _ = Functions.validate_data(df, TimeOffBalanceSchema)
                validated_balance = valid_data.iloc[0].to_dict()
                
                # Restore the original structure with validated data
                response_data["TimeOffBalance"] = validated_balance
                
                return response_data
            except Exception as e:
                raise ValueError(f"Invalid time off balance data: {str(e)}")
                
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"Time off balance with ID {balance_id} not found.")
            raise
            
    def get_employee_balance_cycles(self, employee_id: str) -> pd.DataFrame:
        """
        Returns a list of balances per cycle for an employee.
        
        Endpoint: GET https://api.shiftbase.com/api/employees/{employeeId}/timeOff/balances/cycles
        
        Args:
            employee_id (str): The unique identifier of the employee
            
        Returns:
            pd.DataFrame: Employee's balance cycles data
            
        Raises:
            ValueError: If employee_id is invalid or balance cycle data fails validation
            requests.HTTPError: 
                - 404: Employee not found
                - 403: Unauthorized access
        """
        # Validate employee_id
        if not employee_id:
            raise ValueError("employee_id cannot be empty")
            
        if not re.match(r"^[0-9]+$", employee_id):
            raise ValueError("employee_id must contain only digits")
            
        # Construct the endpoint URL
        endpoint = f"employees/{employee_id}/timeOff/balances/cycles"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract balance cycle data
            if not response_data:
                return pd.DataFrame()
                
            # Create DataFrame from response
            df = pd.DataFrame(response_data)
            
            # If no data is returned, return an empty DataFrame
            if df.empty:
                return df
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, BalanceCycleSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid balance cycle data: {str(e)}")
                
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"Employee with ID {employee_id} not found.")
            raise 