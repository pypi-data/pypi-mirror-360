from typing import Dict, Optional, List, Union
import pandas as pd
from datetime import date
import json

from .contract_types import ContractTypes
from .schemas.contracts import ContractSchema, ContractCreateSchema, ContractUpdateSchema
from brynq_sdk_functions import Functions

class Contracts:
    """
    Handles all contract related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "contracts/"
        self.contract_types = ContractTypes(shiftbase)
    def get(self, filters: Optional[Dict] = None,
            max_date: Optional[date] = None,
            min_date: Optional[date] = None,
            user_id: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves the contracts from Shiftbase.

        Args:
            filters (Dict, optional): Additional query parameters
            max_date (Union[str, date], optional): End of the period to filter (YYYY-MM-DD)
            min_date (Union[str, date], optional): Start of the period to filter (YYYY-MM-DD)
            user_id (str, optional): Filter on a user ID.
                Must match pattern: ^[0-9]+$

        Returns:
            pd.DataFrame: Contract data

        Raises:
            ValueError: If the contract data fails validation
        """
        # Prepare query parameters
        params = filters or {}

        # Add date filters if provided
        if max_date:
            if not isinstance(max_date, date):
                raise TypeError("max_date must be a datetime object")
            params["max_date"] = max_date.strftime("%Y-%m-%d")
        if min_date:
            if not isinstance(min_date, date):
                raise TypeError("min_date must be a datetime object")
            params["min_date"] = min_date.strftime("%Y-%m-%d")

        # Add user_id filter if provided
        if user_id:
            if not user_id.isdigit():
                raise ValueError("user_id must contain only digits")
            params["user_id"] = user_id

        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        contracts = [contract.get("Contract") for contract in response_data]

        # Validate the data using brynq_sdk_functions
        valid_data, invalid_data = Functions.validate_pydantic_data(
            contracts,
            ContractSchema
        )
        # Raise error if there are invalid records
        if invalid_data:
            error_message = f"Invalid contract data: {len(invalid_data)} records failed validation"
            raise ValueError(error_message)

        # Convert valid data to DataFrame
        return pd.DataFrame(valid_data)

    def get_by_id(self, contract_id: str) -> pd.DataFrame:
        """
        Retrieves a specific contract by ID from Shiftbase.

        Calls the API endpoint: GET https://api.shiftbase.com/api/contracts/{contractId}

        Args:
            contract_id (str): The unique identifier of a contract.
                Must match pattern: ^[0-9]+$

        Returns:
            pd.DataFrame: Single contract data as a DataFrame with one row.
                Returns an empty DataFrame if the contract wasn't found.

        Raises:
            ValueError: If contract_id doesn't match the required pattern or if the data fails validation
            requests.HTTPError: If the API returns a 403 (Forbidden) or 404 (Not Found) status
                - 403: Missing required permission(s) - Need 'View contracts' and 'View salary'
                - 404: Contract not found
        """
        # Validate contract_id pattern
        if not contract_id.isdigit():
            raise ValueError("contract_id must contain only digits")

        # Get the contract data
        try:
            response_data = self.shiftbase.get(f"{self.uri}{contract_id}")
        except Exception as e:
            raise ValueError(f"Error fetching contract with ID {contract_id}: {str(e)}")

        # Extract the Contract object from the response
        contract = response_data.get("Contract")
        if not contract:
            return pd.DataFrame()

        # Validate the data using brynq_sdk_functions
        valid_data, invalid_data = Functions.validate_pydantic_data(
            [contract],
            ContractSchema
        )

        # Raise error if there are invalid records
        if invalid_data:
            error_message = f"Invalid contract data for ID {contract_id}"
            raise ValueError(error_message)

        # Convert valid data to DataFrame
        return pd.DataFrame(valid_data)

    def create(self, data: Dict) -> Dict:
        """
        Creates a new contract in Shiftbase.

        Calls the API endpoint: POST https://api.shiftbase.com/api/contracts

        Args:
            data (Dict): Dictionary containing the contract data to create.
                Must match the ContractCreateSchema structure.
                Example: {"Contract": {...fields...}}

        Returns:
            Dict: Response from the API containing the created contract details.

        Raises:
            ValueError: If the data fails validation or if the creation fails
            requests.HTTPError: If the API returns a non-successful status
                - 400: Bad request or invalid parameters
                - 403: Missing required permission(s) - Need 'Create contracts'
                - 422: Unprocessable entity (e.g., validation failed)
        """
        # Extract the 'Contract' section if present
        contract_data = data.get("Contract", data)
        # Validate input data against the schema
        try:
            valid_data, invalid_data = Functions.validate_pydantic_data(data=contract_data, schema=ContractCreateSchema)
            if invalid_data:
                raise ValueError(f"Invalid contract data: {invalid_data}")
        except Exception as e:
            raise ValueError(f"Invalid contract data: {str(e)}")
        # Use the first (and only) validated contract
        validated_contract = valid_data[0]
        # Strip None values
        cleaned_contract = {k: v for k, v in validated_contract.items() if v is not None}
        # Build request payload
        request_payload = {"Contract": cleaned_contract}
        # Serialize request body with proper date handling
        request_body_json = json.dumps(request_payload, default=self.shiftbase.datetime_converter)
        # Make POST request
        try:
            response = self.shiftbase.session.post(
                f"{self.shiftbase.base_url}{self.uri}",
                data=request_body_json,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response
        except Exception as e:
            # Attach the response JSON to the exception for downstream logging
            import requests
            if isinstance(e, requests.HTTPError):
                try:
                    e.api_json = response.json()
                    # Extract validation errors and feedback for easier access
                    if e.api_json:
                        meta = e.api_json.get('meta', {})
                        e.api_feedback = meta.get('feedback')
                        e.api_validation_errors = meta.get('validation_errors')
                        # Collect validation error messages
                        validation_error_msgs = []
                        if e.api_validation_errors:
                            for field, msgs in e.api_validation_errors.items():
                                if isinstance(msgs, list):
                                    validation_error_msgs.extend(msgs)
                                else:
                                    validation_error_msgs.append(str(msgs))
                        e.validation_error_messages = validation_error_msgs
                except Exception:
                    e.api_json = None
                    e.api_feedback = None
                    e.api_validation_errors = None
                    e.validation_error_messages = []
            raise

    def update(self, contract_id: str, data: Dict) -> Dict:
        """
        Updates an existing contract in Shiftbase.

        Calls the API endpoint: PUT https://api.shiftbase.com/api/contracts/{contractId}

        Args:
            contract_id (str): The unique identifier of the contract to update.
                Must match pattern: ^[0-9]+$
            data (Dict): Dictionary containing the contract data to update.
                Must match the ContractUpdateSchema structure.
                Example: {"Contract": {...fields...}}

        Returns:
            Dict: Response from the API containing the updated contract details.

        Raises:
            ValueError: If the data fails validation or if the update fails
            requests.HTTPError: If the API returns a non-successful status
                - 400: Bad request or invalid parameters
                - 403: Missing required permission(s) - Need 'Edit contracts'
                - 404: Contract not found
                - 422: Unprocessable entity (e.g., validation failed)
        """
        # Extract the 'Contract' section if present
        contract_data = data.get("Contract", data)
        contract_data["id"] = contract_id
        # Validate input data against the schema
        try:
            valid_data, invalid_data = Functions.validate_pydantic_data(data=contract_data, schema=ContractUpdateSchema)
            if invalid_data:
                raise ValueError(f"Invalid contract data: {invalid_data}")
        except Exception as e:
            raise ValueError(f"Invalid contract data: {str(e)}")
        # Use the first (and only) validated contract
        validated_contract = valid_data[0]
        # Strip None values
        cleaned_contract = {k: v for k, v in validated_contract.items() if v is not None}
        # Build request payload
        request_payload = {"Contract": cleaned_contract}
        # Serialize request body with proper date handling
        request_body_json = json.dumps(request_payload, default=self.shiftbase.datetime_converter)
        # Make PUT request
        try:
            response = self.shiftbase.session.put(
                f"{self.shiftbase.base_url}{self.uri}{contract_id}",
                data=request_body_json,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Attach the response JSON to the exception for downstream logging
            import requests
            if isinstance(e, requests.HTTPError):
                try:
                    e.api_json = response.json()
                    # Extract validation errors and feedback for easier access
                    if e.api_json:
                        meta = e.api_json.get('meta', {})
                        e.api_feedback = meta.get('feedback')
                        e.api_validation_errors = meta.get('validation_errors')
                        # Collect validation error messages
                        validation_error_msgs = []
                        if e.api_validation_errors:
                            for field, msgs in e.api_validation_errors.items():
                                if isinstance(msgs, list):
                                    validation_error_msgs.extend(msgs)
                                else:
                                    validation_error_msgs.append(str(msgs))
                        e.validation_error_messages = validation_error_msgs
                except Exception:
                    e.api_json = None
                    e.api_feedback = None
                    e.api_validation_errors = None
                    e.validation_error_messages = []
            raise

    def delete(self, contract_id: str) -> Dict:
        """
        Deletes a contract in Shiftbase.

        Calls the API endpoint: DELETE https://api.shiftbase.com/api/contracts/{contractId}

        Args:
            contract_id (str): The unique identifier of the contract to delete.
                Must match pattern: ^[0-9]+$

        Returns:
            Dict: Response from the API confirming the deletion.

        Raises:
            ValueError: If contract_id doesn't match the required pattern
            requests.HTTPError: If the API returns a non-successful status
                - 403: Missing required permission(s) - Need 'Delete contracts'
                - 404: Contract not found
                - 422: Unprocessable entity
        """

        # Make DELETE request
        response = self.shiftbase.session.delete(f"{self.shiftbase.base_url}{self.uri}{contract_id}")

        # Raise exception if the request failed
        response.raise_for_status()

        # Return the response JSON
        return response.json()
