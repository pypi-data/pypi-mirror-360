from typing import Dict, Optional, List, Union, Any
import pandas as pd
import re
from .schemas.timesheets import TimesheetSchema, ClockBreakSchema, CreateTimeSheetSchema, CreateTimeSheetPydanticSchema,ClockSchema
from brynq_sdk_functions import Functions
from datetime import date

class Timesheets:
    """
    Handles all timesheet related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "timesheets"

    def get(self,
            department_id: Optional[List[str]] = None,
            include: Optional[str] = None,
            max_date: Optional[date] = None,
            min_date: Optional[date] = None,
            rates: Optional[str] = None,
            status: Optional[str] = None,
            user_id: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves a list of timesheets from Shiftbase.

        Args:
            department_id (List[str], optional): Filter on department IDs. Each ID must contain only digits.
            include (str, optional): Include additional related data in the response.
            max_date (date, optional): The maximum date for the returned timesheets.
            min_date (date, optional): The minimum date for the returned timesheets.
            rates (str, optional): Include rates in the response.
            status (str, optional): Filter on a status. Allowed values: Approved, Declined, Pending.
            user_id (str, optional): Filter on a User ID. Must contain only digits.

        Returns:
            pd.DataFrame: Timesheets data
        """
        # Validate parameters
        if user_id and not re.match(r"^[0-9]+$", user_id):
            raise ValueError("user_id must contain only digits")

        if status and status not in ["Approved", "Declined", "Pending"]:
            raise ValueError("status must be one of: Approved, Declined, Pending")

        # Prepare query parameters
        params = {}
        if department_id:
            params["department_id"] = department_id
        if include:
            params["include"] = include
        if max_date:
            if not isinstance(max_date, date):
                raise TypeError("max_date must be a datetime object")
            params["max_date"] = max_date.strftime("%Y-%m-%d")
        if min_date:
            if not isinstance(min_date, date):
                raise TypeError("min_date must be a datetime object")
            params["min_date"] = min_date.strftime("%Y-%m-%d")
        if rates:
            params["rates"] = rates
        if status:
            params["status"] = status
        if user_id:
            params["user_id"] = user_id

        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        if not response_data:
            return pd.DataFrame()

        timesheet_data = []
        for data in response_data:
            timesheet_data.append({
                "Timesheet": data.get("Timesheet"),
                "ClockBreak": data.get("ClockBreak")}
            )

        try:
            valid_data, _ = Functions.validate_pydantic_data(timesheet_data, TimesheetSchema)
            return pd.DataFrame(valid_data)
        except Exception as e:
            raise ValueError(f"Invalid timesheet data: {str(e)}")


    def create(self, data: Dict) -> Dict:
        """
        Creates a new timesheet in Shiftbase.

        Endpoint: POST https://api.shiftbase.com/api/timesheets

        Args:
            data (Dict): Timesheet data to create. Must contain:
                CreateTimeSheetPydanticSchema
        Returns:
            Dict: Created timesheet data

        Raises:
            ValueError: If parameters are invalid or timesheet data fails validation
            requests.HTTPError: If the API request fails
        """
        # Create a copy of data and rename 'break' to 'break_time' if it exists
        data_copy = data.copy()
        if 'break' in data_copy:
            data_copy['break_time'] = data_copy.pop('break')

        # Validate input data against the pydantic schema
        try:
            valid_data, invalid_data = Functions.validate_pydantic_data(data=data_copy,schema=CreateTimeSheetPydanticSchema)
            if invalid_data:
                raise ValueError(f"Invalid timesheet data: {invalid_data}")
        except Exception as e:
            raise ValueError(f"Invalid timesheet data: {str(e)}")

        # Prepare request body - convert validated pydantic model to dict with proper field conversion
        request_body = valid_data[0]

        # Make the request
        response = self.shiftbase.session.post(f"{self.shiftbase.base_url}{self.uri}", json=request_body)
        response.raise_for_status()
        return response

    def update(self, timesheet_id: str, data: Dict) -> Dict:
        """
        Updates an existing timesheet in Shiftbase.

        Endpoint: PUT https://api.shiftbase.com/api/timesheets/{timesheetId}

        Args:
            timesheet_id (str): The unique identifier of the timesheet to update
            data (Dict): Timesheet data to update. May contain:
                CreateTimeSheetPydanticSchema
        Returns:
            Dict: Updated timesheet data

        Raises:
            ValueError: If parameters are invalid or timesheet data fails validation
        """
        # Validate timesheet_id
        if not timesheet_id:
            raise ValueError("timesheet_id cannot be empty")

        if not re.match(r"^[0-9]+$", timesheet_id):
            raise ValueError("timesheet_id must contain only digits")

        # Create a copy of data and rename 'break' to 'break_time' if it exists
        data_copy = data.copy()
        if 'break' in data_copy:
            data_copy['break_time'] = data_copy.pop('break')

        # Validate input data against the pydantic schema
        try:
            valid_data, invalid_data = Functions.validate_pydantic_data(data=data_copy,
                                                                        schema=CreateTimeSheetPydanticSchema)
            if invalid_data:
                raise ValueError(f"Invalid timesheet data: {invalid_data}")
        except Exception as e:
            raise ValueError(f"Invalid timesheet data: {str(e)}")

        # Prepare request body - convert validated pydantic model to dict
        request_body = valid_data[0]

        # Construct the endpoint URL
        endpoint = f"{self.uri}/{timesheet_id}"

        try:
            # Make the request
            response = self.shiftbase.session.put(f"{self.shiftbase.base_url}{endpoint}", json=request_body)
            response.raise_for_status()
            return response

        except Exception as e:
            raise Exception(e)

    def check_clock_status(self, user_id: str, date: Optional[str] = None, time: Optional[str] = None) -> pd.DataFrame:
        """
        Check if an employee is currently clocked in.

        Endpoint: GET https://api.shiftbase.com/api/timesheets/clock/{userId}

        Args:
            user_id (str): The ID of the user to check the clock status for. Must contain only digits.
            date (str, optional): The date to check (YYYY-MM-DD). If not supplied it checks for today.
            time (str, optional): The time to check (HH:MM:SS). If not supplied it checks the current time.

        Returns:
            Dict: Clock status information, including timesheet details if clocked in

        Raises:
            ValueError: If parameters are invalid
            requests.HTTPError: If the API request fails
        """
        # Validate user_id
        if not user_id or not re.match(r"^[0-9]+$", user_id):
            raise ValueError("user_id must contain only digits")

        # Construct the endpoint URL
        endpoint = f"{self.uri}/clock/{user_id}"

        # Prepare query parameters
        params = {}
        if date:
            params["date"] = date
        if time:
            params["time"] = time

        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint, params)

            # Process any timesheet data in the response
            if response_data and "nearest" in response_data:
                nearest_clock = response_data["nearest"]

                # Rename 'break' to 'break_time' if present
                if "break" in nearest_clock:
                    nearest_clock["break_time"] = nearest_clock.pop("break")
                df = pd.DataFrame([nearest_clock])
                try:
                    valid_data, _ = Functions.validate_data(df, ClockSchema)
                    # Update the timesheet in the response with validated data
                    return pd.DataFrame(valid_data)
                except Exception as e:
                    # Log the error but don't raise, as we still want to return the clock status
                    print(f"Error: Validating timesheet data in clock status response: {str(e)}")

        except Exception as e:
            raise

    def get_by_id(self, timesheet_id: str) -> pd.DataFrame:
        """
        Retrieves a specific timesheet by its ID.
        
        Endpoint: GET https://api.shiftbase.com/api/timesheets/{timesheetId}
        
        Args:
            timesheet_id (str): The unique identifier of the timesheet
            
        Returns:
            Dict: Timesheet details
            
        Raises:
            ValueError: If timesheet_id is invalid or timesheet data fails validation
        """
        # Validate timesheet_id
        if not timesheet_id:
            raise ValueError("timesheet_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{timesheet_id}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Extract timesheet data
            if not response_data or "Timesheet" not in response_data:
                raise ValueError(f"Timesheet with ID {timesheet_id} not found or has an invalid format")
                
            timesheet_data = {
                    "Timesheet": response_data.get("Timesheet"),
                    "ClockBreak": response_data.get("ClockBreak")}

            if "break" in timesheet_data["Timesheet"]:
                timesheet_data["Timesheet"]["break_time"] = timesheet_data["Timesheet"].pop("break")

            # Rename 'break' to 'break_time' if present

            
            # Validate with TimeSheetSchema
            try:
                valid_data, _ = Functions.validate_pydantic_data(timesheet_data, TimesheetSchema)
                return pd.DataFrame(valid_data)
            except Exception as e:
                raise ValueError(f"Invalid timesheet data: {str(e)}")
                
        except Exception as e:
            raise Exception(e)

    def create_batch(self, data_list: List[Dict]) -> Dict:
        """
        Creates multiple timesheets in a batch operation.
        
        Endpoint: POST https://api.shiftbase.com/api/timesheets/batch
        
        Args:
            data_list (List[Dict]): List of timesheet data to create. Each dict must contain:
                CreateTimeSheetPydanticSchema
                And may contain the same optional fields as in create method.
                
        Returns:
            Dict: API response containing created timesheet data
            
        Raises:
            ValueError: If parameters are invalid or timesheet data fails validation
            requests.HTTPError: If the API request fails
        """
        # Validate each timesheet in the batch
        validated_batch = []
        
        for i, data in enumerate(data_list):
            # Create a copy of data and rename 'break' to 'break_time' if it exists
            data_copy = data.copy()
            if 'break' in data_copy:
                data_copy['break_time'] = data_copy.pop('break')
            
            # Validate input data against the pydantic schema
            try:
                valid_data, invalid_data = Functions.validate_pydantic_data(data=data_copy, schema=CreateTimeSheetPydanticSchema)
                if invalid_data:
                    raise ValueError(f"Invalid timesheet data at index {i}: {invalid_data}")
                    
                # Add validated data to the batch
                validated_batch.append(valid_data[0])
            except Exception as e:
                raise ValueError(f"Invalid timesheet data at index {i}: {str(e)}")
        
        # Make the request
        endpoint = f"{self.uri}/batch"
        response = self.shiftbase.session.post(f"{self.shiftbase.base_url}{endpoint}", json=validated_batch)
        response.raise_for_status()
        return response



