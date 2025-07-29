from typing import Dict, Optional
from datetime import date
import pandas as pd
from .schemas.events import EventSchema
from brynq_sdk_functions import Functions
from uuid import UUID

class Events:
    """
    Handles all event related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "events"

    def get(self, 
            department_id: Optional[str] = None,
            max_date: Optional[date] = None,
            min_date: Optional[date] = None,) -> pd.DataFrame:
        """
        Retrieves the list of events from Shiftbase.
        
        Args:
            department_id (str, optional): Filter on passed department ids
            max_date (str, optional): End of the period to filter (YYYY-MM-DD)
            min_date (str, optional): Start of the period to filter (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Events data
            
        Raises:
            ValueError: If the events data fails validation or parameters are invalid
        """
        # Prepare query parameters
        params = {}
        if department_id:
            params["department_id"] = department_id
        if max_date:
            if not isinstance(max_date, date):
                raise TypeError("max_date must be a datetime object")
            params["max_date"] = max_date.strftime("%Y-%m-%d")
        if min_date:
            if not isinstance(min_date, date):
                raise TypeError("min_date must be a datetime object")
            params["min_date"] = min_date.strftime("%Y-%m-%d")
            
        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        # Extract events data
        events = pd.DataFrame(response_data)
        # Validate the data using brynq_sdk_functions
        valid_data, invalid_data = Functions.validate_pydantic_data(
            events, 
            EventSchema
        )
        
        # Raise error if there are invalid records
        if invalid_data:
            error_message = f"Invalid event data: {len(invalid_data)} records failed validation"
            raise ValueError(error_message)
        
        # Return as DataFrame
        return pd.DataFrame(valid_data)
        
    def get_by_id(self, event_id: str) -> Dict:
        """
        Retrieves a specific event by ID.
        
        Args:
            event_id (str): The unique identifier of the event
            
        Returns:
            Dict: Event details
            
        Raises:
            ValueError: If event_id is invalid or event data fails validation
            requests.HTTPError: 
                - 400: If the request is invalid
        """
        # Validate event_id
        if not event_id:
            raise ValueError("event_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{event_id}"
        
        # Make the request
        response_data = self.shiftbase.get(endpoint)
        
        # Extract event data
        event_data = response_data
        
        # Validate event data if present
        if event_data:
            event_list = [event_data]
            valid_data, invalid_data = Functions.validate_pydantic_data(
                event_list,
                EventSchema
            )
            
            if invalid_data:
                error_message = f"Invalid event data: {len(invalid_data)} record failed validation"
                raise ValueError(error_message)
                
            # Update with validated data
            event_data = valid_data[0]
        
        # Return the event data
        return pd.DataFrame(event_data)
        
    def get_by_sequence(self, sequence_id: str, 
                      from_date: Optional[date] = None,
                      to_date: Optional[date] = None) -> pd.DataFrame:
        """
        Retrieves a list of events that are part of a sequence.
        
        When no period is passed, all current events for the sequence will be returned.
        When a period is specified, only events that occur in the given sequence during 
        the requested period are returned.
        
        Args:
            sequence_id (str): Sequence ID to use for fetching a list of events
            from_date (date, optional): Filter for returning only occurrences on/after this date
            to_date (date, optional): Filter for returning only occurrences before/on this date

        Returns:
            pd.DataFrame: Events in the sequence
            
        Raises:
            ValueError: If sequence_id is invalid or events data fails validation
            requests.HTTPError: If the API request fails
        """
        # Validate sequence_id
        if not sequence_id:
            raise ValueError("sequence_id cannot be empty")
            
        try:
            UUID(sequence_id)
        except ValueError:
            raise ValueError(f"Invalid sequence_id format: {sequence_id}. Expected UUID format")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/sequence/{sequence_id}"
        
        # Prepare query parameters
        params = {}
        if from_date:
            if not isinstance(from_date, date):
                raise TypeError("from_date must be a datetime object")
            params["from_date"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            if not isinstance(to_date, date):
                raise TypeError("to_date must be a datetime object")
            params["to_date"] = to_date.strftime("%Y-%m-%d")
        # Make the request
        response_data = self.shiftbase.get(endpoint, params)
        
        # Extract events data
        events = response_data.get("data", [])
        
        # Validate the data using brynq_sdk_functions
        valid_data, invalid_data = Functions.validate_pydantic_data(
            events, 
            EventSchema
        )
        
        # Raise error if there are invalid records
        if invalid_data:
            error_message = f"Invalid event data: {len(invalid_data)} records failed validation"
            raise ValueError(error_message)
        
        # Return as DataFrame
        return pd.DataFrame(valid_data) 