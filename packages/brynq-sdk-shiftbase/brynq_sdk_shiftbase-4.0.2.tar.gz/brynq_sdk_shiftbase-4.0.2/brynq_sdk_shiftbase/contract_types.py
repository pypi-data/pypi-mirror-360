from typing import Dict, Optional
import pandas as pd
from .schemas.contract_types import ContractTypeSchema
from brynq_sdk_functions import Functions

class ContractTypes:
    """
    Handles all contract type related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "contract_types"

    def get(self) -> pd.DataFrame:
        """
        Retrieves the list of all contract types from Shiftbase.
        
        Returns:
            pd.DataFrame: Contract type data
            
        Raises:
            ValueError: If the contract type data fails validation
        """
        # Make the request
        response_data = self.shiftbase.get(self.uri)
        # Extract contract types data
        contract_types = [contract_type.get("ContractType") for contract_type in response_data]

        # Validate the data using brynq_sdk_functions
        valid_data, invalid_data = Functions.validate_pydantic_data(
            contract_types, 
            ContractTypeSchema
        )
        
        # Raise error if there are invalid records
        if invalid_data:
            error_message = f"Invalid contract type data: {len(invalid_data)} records failed validation"
            raise ValueError(error_message)
        
        # Return as DataFrame
        return pd.DataFrame(valid_data)
        
    def get_by_id(self, contract_type_id: str) -> pd.DataFrame:
        """
        Retrieves a specific contract type by ID.
        
        Args:
            contract_type_id (str): The unique identifier of the contract type
            
        Returns:
            Dict: Contract type details
            
        Raises:
            ValueError: If contract_type_id is invalid or contract type data fails validation
            requests.HTTPError: 
                - 404: If the contract type is not found
        """
        # Validate contract_type_id
        if not contract_type_id:
            raise ValueError("contract_type_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{contract_type_id}"
        
        # Make the request
        response_data = self.shiftbase.get(endpoint)
        contract_type_data = response_data.get("ContractType")
        # Validate contract type data if present
        if contract_type_data:
            valid_data, invalid_data = Functions.validate_pydantic_data(
                contract_type_data,
                ContractTypeSchema
            )
            
            if invalid_data:
                error_message = f"Invalid contract type data: {len(invalid_data)} record failed validation"
                raise ValueError(error_message)
                
            # Update with validated data
            return pd.DataFrame(valid_data)
        # Return the contract type data
        return pd.DataFrame()