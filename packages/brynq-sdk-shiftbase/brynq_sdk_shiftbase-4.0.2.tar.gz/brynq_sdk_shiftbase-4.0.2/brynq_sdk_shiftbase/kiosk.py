from typing import Dict, Optional
import pandas as pd
from .schemas.kiosk import KioskSchema
from brynq_sdk_functions import Functions

class Kiosk:
    """
    Handles all Kiosk related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "timetracking/kiosk"

    def get(self) -> pd.DataFrame:
        """
        Retrieves all kiosks from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/timetracking/kiosk
        
        Returns:
            pd.DataFrame: Kiosks data
            
        Raises:
            ValueError: If kiosk data fails validation
            requests.HTTPError: If the API request fails
        """
        # Make the request
        response_data = self.shiftbase.get(self.uri)
        
        if not response_data:
            return pd.DataFrame()
        
        # Extract kiosk data from response
        kiosks = []
        for item in response_data:
            if "Kiosk" in item:
                kiosks.append(item["Kiosk"])
        
        # Create DataFrame from response
        df = pd.DataFrame(kiosks)
        
        # If no data is returned, return an empty DataFrame
        if df.empty:
            return df
        
        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, KioskSchema)
            return valid_data
        except Exception as e:
            raise ValueError(f"Invalid kiosk data: {str(e)}")
    
    def get_by_id(self, kiosk_id: str) -> pd.DataFrame:
        """
        Retrieves a specific kiosk by its ID.
        
        Endpoint: GET https://api.shiftbase.com/api/timetracking/kiosk/{kioskId}
        
        Args:
            kiosk_id (str): The unique identifier of the kiosk
            
        Returns:
            Dict: Kiosk details
            
        Raises:
            ValueError: If kiosk_id is invalid or kiosk data fails validation
            requests.HTTPError: 
                - 404: Kiosk not found
                - 403: Unauthorized access
        """
        # Validate kiosk_id
        if not kiosk_id:
            raise ValueError("kiosk_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{kiosk_id}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract kiosk data
            if not response_data or not "Kiosk" in response_data:
                raise ValueError(f"Kiosk with ID {kiosk_id} not found or has an invalid format")
                
            kiosk_data = response_data["Kiosk"]
            
            # Validate with KioskSchema
            df = pd.DataFrame([kiosk_data])
            try:
                valid_data, _ = Functions.validate_data(df, KioskSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid kiosk data: {str(e)}")
                
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"Kiosk with ID {kiosk_id} not found.")
            raise 

    def get_pin(self) -> str:
        """
        Retrieves the user's kiosk PIN.
        
        Endpoint: GET https://api.shiftbase.com/api/pin
        
        Notes:
            - Required permissions: None specific
            - Minimum plan: premium
        
        Returns:
            str: A 4-digit PIN used for the kiosk
            
        Raises:
            ValueError: If failed to retrieve PIN
            requests.HTTPError: 
                - 422: Validation error
                - 426: Upgrade required (Premium plan required)
        """
        try:
            # Make the request
            response_data = self.shiftbase.get("pin")
            
            if not response_data or "Pin" not in response_data:
                raise ValueError("Could not retrieve PIN, no data returned")
                
            return response_data["Pin"]
                
        except Exception as e:
            if "426" in str(e):
                raise ValueError("Premium plan required to use PIN functionality")
            if "422" in str(e):
                raise ValueError("Validation error when retrieving PIN")
            raise

    def get_employee_pin(self, employee_id: str) -> str:
        """
        Retrieves the kiosk PIN for an employee with the specified ID.
        
        Endpoint: GET https://api.shiftbase.com/api/pin/{employeeId}
        
        Notes:
            - Required permissions: Clock time
            - Minimum plan: premium
        
        Args:
            employee_id (str): The unique identifier of the employee
            
        Returns:
            str: A 4-digit PIN used for the kiosk
            
        Raises:
            ValueError: If failed to retrieve PIN
            requests.HTTPError: 
                - 403: Unauthorized access
                - 422: Validation error
                - 426: Upgrade required (Premium plan required)
        """
        try:
            # Make the request
            response_data = self.shiftbase.get(f"pin/{employee_id}")
            
            if not response_data or "Pin" not in response_data:
                raise ValueError(f"Could not retrieve PIN for employee {employee_id}, no data returned")
                
            return response_data["Pin"]
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view this employee's PIN")
            if "426" in str(e):
                raise ValueError("Premium plan required to use PIN functionality")
            if "422" in str(e):
                raise ValueError("Validation error when retrieving PIN")
            raise 