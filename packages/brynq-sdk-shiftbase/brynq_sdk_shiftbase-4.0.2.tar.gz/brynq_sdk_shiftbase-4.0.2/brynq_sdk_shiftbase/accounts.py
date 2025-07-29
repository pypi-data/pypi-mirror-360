from typing import Dict
import json
import pandas as pd
from .schemas.accounts import AccountSchema, AccountUpdateSchema
from brynq_sdk_functions import Functions

class Accounts:
    """
    Handles account related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "accounts"

    def get(self) -> pd.DataFrame:
        """
        Retrieves account information from Shiftbase.
        
        Returns:
            pd.DataFrame: Account information data
            
        Raises:
            ValueError: If account data fails validation
            requests.HTTPError: 
                - 501: If the API doesn't support this operation
        """
        # Make the request
        response_data = self.shiftbase.get(self.uri)
        
        # Extract account data
        account_info = response_data.get("Account")
        
        # Convert to DataFrame
        df = pd.DataFrame([account_info])

        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, AccountSchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid account data: {str(e)}"
            raise ValueError(error_message)
        
    def get_by_id(self, account_id: str) -> pd.DataFrame:
        """
        Retrieves account information of a specific account by ID.
        
        Args:
            account_id (str): The unique identifier of the account
            
        Returns:
            pd.Dataframe: Account information data
            
        Raises:
            ValueError: If account_id is invalid
            requests.HTTPError: 
                - 400: If the request is invalid
                - 403: If access is forbidden
                - 404: If the account is not found
        """
        if not account_id or not isinstance(account_id, str):
            raise ValueError("account_id must be a valid string")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{account_id}"
        
        # Make the request
        response_data = self.shiftbase.get(endpoint)
        account_info = response_data.get("Account")
        # Convert to DataFrame

        df = pd.DataFrame([account_info])

        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, AccountSchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid account data: {str(e)}"
            raise ValueError(error_message)

    def update(self, account_id: str, data: Dict) -> Dict:
        """
        Updates an existing account in Shiftbase.
        
        Args:
            account_id (str): The unique identifier of the account to update
            data (Dict): Dictionary containing the account data to update
                Must match the AccountUpdateSchema structure
                
        Returns:
            Dict: Response from the API containing the updated account details
                
        Raises:
            ValueError: If account_id is invalid or if the data fails validation
            requests.HTTPError: 
                - 400: If the request is invalid
                - 403: If access is forbidden
                - 404: If the account is not found
                - 422: If the request contains invalid data
                - 426: If the account needs to be upgraded
        """
        if not account_id or not isinstance(account_id, str):
            raise ValueError("account_id must be a valid string")
            
        # Validate input data against the schema
        try:
            # Make sure the ID is included in the data
            update_data = data.copy()
            update_data["id"] = account_id
            
            valid_data, invalid_data = Functions.validate_pydantic_data(data=update_data, schema=AccountUpdateSchema)
            if invalid_data:
                raise ValueError(f"Invalid account data: {invalid_data}")
        except Exception as e:
            raise ValueError(f"Invalid account data: {str(e)}")
        
        # Prepare request body
        request_body = {"Account": json.dumps(valid_data[0], default=self.shiftbase.datetime_converter)}
        
        # Construct the endpoint URL
        endpoint = f"{self.shiftbase.base_url}{self.uri}/{account_id}"
        
        # Make PUT request
        response = self.shiftbase.session.put(endpoint, json=request_body)
        return response 