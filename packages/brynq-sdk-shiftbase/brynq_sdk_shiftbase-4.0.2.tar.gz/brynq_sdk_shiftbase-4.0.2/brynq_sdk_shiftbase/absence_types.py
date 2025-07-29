from typing import Dict, Optional, Any
import pandas as pd
from .schemas.absence_types import AbsenteeOptionSchema, AbsenteeOptionCreateSchema, AbsenteeOptionUpdateSchema
import logging
from brynq_sdk_functions import Functions

# Setup logging
logger = logging.getLogger(__name__)

class AbsenceTypes:
    """
    Handles all absence type related operations in Shiftbase.
    This class provides methods to interact with the absence types endpoint.
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "absentee_options/"

    def get(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """
        Retrieves all absence types from Shiftbase.
        This endpoint returns a list of all available absence types in the system.
        
        Args:
            filters (Dict, optional): Query parameters
            
        Returns:
            pd.DataFrame: DataFrame containing all absence types with their details.
                Each row represents an AbsenteeOption with its properties.
                
        Raises:
            ValueError: If the absence types data fails validation
        """
        # Process filters parameter
        if filters is None:
            params = {}
        elif isinstance(filters, dict):
            params = filters.copy()
        else:
            params = {}
            
        # Make a GET request with optional filters
        response_data = self.shiftbase.get(self.uri, params)
        absence_types = [absence_type.get("AbsenteeOption") for absence_type in response_data]
        df = pd.DataFrame(absence_types)
        
        # Validate the DataFrame against the schema using brynq_sdk_functions
        valid_df, invalid_df = Functions.validate_data(df, AbsenteeOptionSchema)
        
        # Raise error if there are invalid records
        if not invalid_df.empty:
            error_message = f"Invalid absence type data: {len(invalid_df)} records failed validation"
            raise ValueError(error_message)
            
        return valid_df
        
    def get_by_id(self, absence_type_id: str) -> pd.DataFrame:
        """
        Retrieves a specific absence type by ID from Shiftbase.
        
        Args:
            absence_type_id (str): The unique identifier of an absence type.
                Must match pattern: ^[0-9]+$
                
        Returns:
            pd.DataFrame: DataFrame containing the specific absence type details.
                Each row represents an AbsenteeOption with its properties.
                
        Raises:
            ValueError: If absence_type_id doesn't match the required pattern or if the data fails validation
        """
        # Validate absence_type_id pattern
        if not absence_type_id.isdigit():
            raise ValueError("absence_type_id must contain only digits")
            
        # Get the absence type data
        response_data = self.shiftbase.get(f"{self.uri}{absence_type_id}")
        if response_data:
            # Extract the AbsenteeOption object from the response
            absence_type = response_data.get("AbsenteeOption")
            if not absence_type:
                return pd.DataFrame()  # Return empty DataFrame if no data found

            df = pd.DataFrame([absence_type])

            # Validate the DataFrame against the schema using brynq_sdk_functions
            valid_df, invalid_df = Functions.validate_data(df, AbsenteeOptionSchema)

            # Raise error if there are invalid records
            if not invalid_df.empty:
                error_message = f"Invalid absence type record for ID {absence_type_id}"
                raise ValueError(error_message)

            return valid_df

        else:
            return pd.DataFrame()

    def create(self, data: Dict) -> pd.DataFrame:
        """
        Creates a new absence type in Shiftbase.
        
        Args:
            data (Dict): Dictionary containing the absence type data to create.
                Must match the AbsenteeOptionCreateSchema structure.
                
        Returns:
            pd.DataFrame: DataFrame containing the created absence type details.
                
        Raises:
            ValueError: If the data fails validation or if the creation fails
        """
        # Validate input data against the schema
        try:
            valid_data, _ = Functions.validate_pydantic_data(data, schema=AbsenteeOptionCreateSchema)
        except Exception as e:
            raise ValueError(f"Invalid absence type data: {str(e)}")
            
        # Prepare request body
        group_ids = valid_data[0].pop("group_ids", [])
        request_body = {
            "AbsenteeOption": valid_data[0],
            "Group": group_ids
        }
        
        # Make POST request
        response = self.shiftbase.session.post(f"{self.shiftbase.base_url}{self.uri}", json=request_body)
        return response

    def update(self, absence_type_id: str, data: Dict) -> pd.DataFrame:
        """
        Updates an existing absence type in Shiftbase.
        
        Args:
            absence_type_id (str): The ID of the absence type to update
            data (Dict): Dictionary containing the updated absence type data.
                Must match the AbsenteeOptionUpdateSchema structure.
                
        Returns:
            pd.DataFrame: DataFrame containing the updated absence type details.
                
        Raises:
            ValueError: If absence_type_id is invalid or if the data fails validation
        """
        # Validate absence_type_id
        if not absence_type_id.isdigit():
            raise ValueError("absence_type_id must contain only digits")
            
        # Validate input data against the schema
        try:
            valid_data, _ = Functions.validate_pydantic_data(data=data, schema=AbsenteeOptionUpdateSchema)
        except Exception as e:
            raise ValueError(f"Invalid absence type data: {str(e)}")
            
        # Prepare request body
        group_ids = valid_data[0].pop("group_ids", [])
        request_body = {
            "AbsenteeOption": valid_data[0],
            "Group": group_ids
        }
        
        # Make PUT request
        response = self.shiftbase.session.put(f"{self.shiftbase.base_url}{self.uri}{absence_type_id}", json=request_body)
        
        return response

    def delete(self, absence_type_id: str) -> Dict[str, Any]:
        """
        Deletes a specific absence type from Shiftbase.
        
        Args:
            absence_type_id (str): The unique identifier of an absence type.
                Must contain only digits.
                
        Returns:
            Dict[str, Any]: Response from the API containing status and metadata
            
        Raises:
            ValueError: If absence_type_id is invalid (doesn't contain only digits)
        """
        # Validate absence_type_id
        if not absence_type_id.isdigit():
            raise ValueError("absence_type_id must contain only digits")
        
        # Send DELETE request to the API
        response = self.shiftbase.session.delete(f"{self.shiftbase.base_url}{self.uri}{absence_type_id}")
        return response