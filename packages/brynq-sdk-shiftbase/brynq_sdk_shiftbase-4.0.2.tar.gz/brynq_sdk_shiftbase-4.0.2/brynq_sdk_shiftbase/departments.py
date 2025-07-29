from typing import Dict, Optional, List, Any
import pandas as pd
from .schemas.departments import DepartmentSchema, DepartmentEmployeeSchema, DepartmentTargetSchema, \
    DepartmentModelSchema
from brynq_sdk_functions import Functions
from datetime import date

class Departments:
    """
    Handles all department related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "departments"

    def get(self, allow_deleted: Optional[bool] = None) -> pd.DataFrame:
        """
        Retrieves the list of all departments from Shiftbase.
        
        Args:
            allow_deleted (bool, optional): Allow deleted departments to be returned
            
        Returns:
            pd.DataFrame: Department data
            
        Raises:
            ValueError: If the department data fails validation
        """
        # Prepare query parameters
        params = {}
        if allow_deleted is not None:
            params["allow_deleted"] = "true" if allow_deleted else "false"
            
        # Make the request
        response_data = self.shiftbase.get(self.uri, params)
        # Extract departments data
        departments = [department.get("Department") for department in response_data]

        # Validate the data using brynq_sdk_functions
        valid_data, invalid_data = Functions.validate_pydantic_data(
            departments,
            DepartmentModelSchema
        )
        
        # Raise error if there are invalid records
        if invalid_data:
            error_message = f"Invalid department data: {len(invalid_data)} records failed validation"
            raise ValueError(error_message)
        
        # Return as DataFrame
        return pd.DataFrame(valid_data)
        
    def get_by_id(self, department_id: str) -> pd.DataFrame:
        """
        Retrieves a specific department by ID.
        
        Args:
            department_id (str): The unique identifier of the department
            
        Returns:
            Dict: Department details including Department, Location, Team and Shift information
            
        Raises:
            ValueError: If department_id is invalid or department data fails validation
            requests.HTTPError: 
                - 400: If the request is invalid
                - 404: If the department is not found
        """
        # Validate department_id
        if not department_id:
            raise ValueError("department_id cannot be empty")
            
        if not isinstance(department_id, str):
            raise ValueError("department_id must be a string")
            
        if not department_id.isdigit():
            raise ValueError("department_id must contain only digits")
            
        # Construct the endpoint URL
        endpoint = f"{self.uri}/{department_id}"
        
        # Make the request
        response_data = self.shiftbase.get(endpoint)

        # Validate Department data if present
        if response_data:
            valid_data, invalid_data = Functions.validate_pydantic_data(
                response_data,
                DepartmentSchema
            )

            if invalid_data:
                error_message = f"Invalid department data: {len(invalid_data)} record failed validation"
                raise ValueError(error_message)


        # Return the complete department data
            return pd.DataFrame(valid_data)
        return pd.DataFrame()
        
    def get_employees(self, department_id: str,
                      max_date: Optional[date] = None,
                      min_date: Optional[date] = None,) -> pd.DataFrame:
        """
        Retrieves a list of all employees that are part of a specific department.
        
        When no period is passed, all current employees for the department will be returned.
        When a period is specified, only employees that occur in the given department 
        during the requested period are returned.
        
        Args:
            department_id (str): The unique identifier of the department
            min_date (str, optional): Start of the period to filter (YYYY-MM-DD)
            max_date (str, optional): End of the period to filter (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Department employees data
            
        Raises:
            ValueError: If department_id is invalid or employee data fails validation
            requests.HTTPError: 
                - 404: If the department is not found
        """
        # Validate department_id
        if not department_id:
            raise ValueError("department_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"hr/{self.uri}/{department_id}/employeeList"
        
        # Prepare query parameters
        params = {}
        if max_date:
            if not isinstance(max_date, date):
                raise TypeError("max_date must be a datetime object")
            params["max_date"] = max_date.strftime("%Y-%m-%d")
        if min_date:
            if not isinstance(min_date, date):
                raise TypeError("min_date must be a datetime object")
            params["min_date"] = min_date.strftime("%Y-%m-%d")
            
        # Make the request
        response_data = self.shiftbase.get(endpoint, params)
        

        # Convert to DataFrame
        df = pd.DataFrame(response_data)
        
        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, DepartmentEmployeeSchema)
            return valid_data
        except Exception as e:
            error_message = f"Invalid department employee data: {str(e)}"
            raise ValueError(error_message) 

    def get_targets(self, department_id: str) -> pd.DataFrame:
        """
        Retrieves targets for a specific department from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/departments/{departmentId}/target
        
        Notes:
            - Required permissions: Manage account
            - Minimum plan: Premium
        
        Args:
            department_id (str): The unique identifier of the department
            
        Returns:
            pd.DataFrame: Department targets data
            
        Raises:
            ValueError: If department_id is invalid or targets data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 404: Department not found
                - 426: Upgrade required (Premium plan required)
        """
        if not department_id:
            raise ValueError("department_id cannot be empty")

        # Make the request
        response_data = self.shiftbase.get(f"departments/{department_id}/target")

        if not response_data:
            return pd.DataFrame()

        # Create DataFrame from response
        df = pd.DataFrame(response_data)

        # If no data is returned, return an empty DataFrame
        if df.empty:
            return df

        # Validate with Functions.validate_data
        try:
            valid_data, _ = Functions.validate_data(df, DepartmentTargetSchema)
            return valid_data
        except Exception as e:
            raise ValueError(f"Invalid department targets data: {str(e)}")
