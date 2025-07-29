from typing import Optional, List
import pandas as pd
from datetime import date, time
from .schemas.planning_conflicts import PlanningConflictSchema, EmployabilitySchema
from brynq_sdk_functions import Functions

class Planning:
    """
    Handles all Planning related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.conflicts_uri = "planning/conflicts"
        
    def get_conflicts(self, employee_ids: Optional[List[str]] = None,
                      max_date: Optional[date] = None,
                      min_date: Optional[date] = None,) -> pd.DataFrame:
        """
        Retrieves planning conflicts from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/planning/conflicts
        
        Notes:
            - Required permissions: Create roster, Edit roster or Create own roster
            - Minimum plan: free
            
            For availability conflicts:
            - Additional permissions: View availability, Edit availability or Edit own availability
            - Minimum plan: basic
            
            For skills conflicts:
            - Additional permissions: Create roster, Edit roster, View own profile or Edit own profile
            - Minimum plan: premium
            
            For timeoff conflicts:
            - Additional permissions: View absentee or View own absentee
            - Minimum plan: basic
        
        Args:
            employee_ids (List[str], optional): List of employee IDs to filter conflicts by
            min_date (date, optional): The minimum date for returned conflicts (YYYY-MM-DD)
            max_date (date, optional): The maximum date for returned conflicts (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Planning conflicts data
            
        Raises:
            ValueError: If planning conflicts data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 400: Bad request
        """
        try:
            # Prepare query parameters
            params = {}
            if employee_ids:
                params['employee_ids'] = ','.join(employee_ids)
            if max_date:
                if not isinstance(max_date, date):
                    raise TypeError("max_date must be a datetime object")
                params["max_date"] = max_date.strftime("%Y-%m-%d")
            if min_date:
                if not isinstance(min_date, date):
                    raise TypeError("min_date must be a datetime object")
                params["min_date"] = min_date.strftime("%Y-%m-%d")
                
            # Make the request
            response_data = self.shiftbase.get(self.conflicts_uri, params)
            
            if not response_data:
                return pd.DataFrame()
                
            # Create DataFrame from response
            df = pd.DataFrame(response_data)
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, PlanningConflictSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid planning conflict data: {str(e)}")
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view planning conflicts.")
            if "400" in str(e):
                raise ValueError("Bad request: Check your parameters.")
            raise
            
    def get_availability_conflicts(self, employee_ids: Optional[List[str]] = None,
                                   max_date: Optional[date] = None,
                                   min_date: Optional[date] = None,) -> pd.DataFrame:
        """
        Retrieves availability planning conflicts from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/planning/conflicts/availabilities
        
        Notes:
            - Required permissions: Create roster, Edit roster or Create own roster and 
              View availability, Edit availability or Edit own availability
            - Minimum plan: basic
        
        Args:
            employee_ids (List[str], optional): List of employee IDs to filter conflicts by
            min_date (date, optional): The minimum date for returned conflicts (YYYY-MM-DD)
            max_date (date, optional): The maximum date for returned conflicts (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Availability planning conflicts data
            
        Raises:
            ValueError: If planning conflicts data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 400: Bad request
        """
        try:
            # Prepare query parameters
            params = {}
            if employee_ids:
                params['employee_ids'] = ','.join(employee_ids)
            if max_date:
                if not isinstance(max_date, date):
                    raise TypeError("max_date must be a datetime object")
                params["max_date"] = max_date.strftime("%Y-%m-%d")
            if min_date:
                if not isinstance(min_date, date):
                    raise TypeError("min_date must be a datetime object")
                params["min_date"] = min_date.strftime("%Y-%m-%d")
                
            # Make the request
            response_data = self.shiftbase.get(f"{self.conflicts_uri}/availabilities", params)
            
            if not response_data:
                return pd.DataFrame()
                
            # Create DataFrame from response
            df = pd.DataFrame(response_data)
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, PlanningConflictSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid availability conflict data: {str(e)}")
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view availability conflicts.")
            if "400" in str(e):
                raise ValueError("Bad request: Check your parameters.")
            raise
            
    def get_schedule_conflicts(self, employee_ids: Optional[List[str]] = None,
                               max_date: Optional[date] = None,
                               min_date: Optional[date] = None) -> pd.DataFrame:
        """
        Retrieves schedule planning conflicts from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/planning/conflicts/schedules
        
        Notes:
            - Required permissions: Create roster, Edit roster or Create own roster
            - Minimum plan: free
        
        Args:
            employee_ids (List[str], optional): List of employee IDs to filter conflicts by
            min_date (date, optional): The minimum date for returned conflicts (YYYY-MM-DD)
            max_date (date, optional): The maximum date for returned conflicts (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Schedule planning conflicts data
            
        Raises:
            ValueError: If planning conflicts data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 400: Bad request
        """
        try:
            # Prepare query parameters
            params = {}
            if employee_ids:
                params['employee_ids'] = ','.join(employee_ids)
            if max_date:
                if not isinstance(max_date, date):
                    raise TypeError("max_date must be a datetime object")
                params["max_date"] = max_date.strftime("%Y-%m-%d")
            if min_date:
                if not isinstance(min_date, date):
                    raise TypeError("min_date must be a datetime object")
                params["min_date"] = min_date.strftime("%Y-%m-%d")
                
            # Make the request
            response_data = self.shiftbase.get(f"{self.conflicts_uri}/schedules", params)
            
            if not response_data:
                return pd.DataFrame()
                
            # Create DataFrame from response
            df = pd.DataFrame(response_data)
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, PlanningConflictSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid schedule conflict data: {str(e)}")
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view schedule conflicts.")
            if "400" in str(e):
                raise ValueError("Bad request: Check your parameters.")
            raise
            
    def get_skill_conflicts(self, employee_ids: Optional[List[str]] = None,
                            max_date: Optional[date] = None,
                            min_date: Optional[date] = None) -> pd.DataFrame:
        """
        Retrieves skill planning conflicts from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/planning/conflicts/skills
        
        Notes:
            - Required permissions: Create roster or Edit roster, or Create own roster 
              and either View own profile or Edit own profile
            - Minimum plan: early adopter
        
        Args:
            employee_ids (List[str], optional): List of employee IDs to filter conflicts by
            min_date (date, optional): The minimum date for returned conflicts (YYYY-MM-DD)
            max_date (date, optional): The maximum date for returned conflicts (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Skill planning conflicts data
            
        Raises:
            ValueError: If planning conflicts data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 400: Bad request
        """
        try:
            # Prepare query parameters
            params = {}
            if employee_ids:
                params['employee_ids'] = ','.join(employee_ids)
            if max_date:
                if not isinstance(max_date, date):
                    raise TypeError("max_date must be a datetime object")
                params["max_date"] = max_date.strftime("%Y-%m-%d")
            if min_date:
                if not isinstance(min_date, date):
                    raise TypeError("min_date must be a datetime object")
                params["min_date"] = min_date.strftime("%Y-%m-%d")
                
            # Make the request
            response_data = self.shiftbase.get(f"{self.conflicts_uri}/skills", params)
            
            if not response_data:
                return pd.DataFrame()
                
            # Create DataFrame from response
            df = pd.DataFrame(response_data)
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, PlanningConflictSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid skill conflict data: {str(e)}")
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view skill conflicts.")
            if "400" in str(e):
                raise ValueError("Bad request: Check your parameters.")
            raise
            
    def get_timeoff_conflicts(self, employee_ids: Optional[List[str]] = None, 
                            min_date: Optional[date] = None,
                            max_date: Optional[date] = None) -> pd.DataFrame:
        """
        Retrieves time off planning conflicts from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/planning/conflicts/time_off
        
        Notes:
            - Required permissions: Create roster, Edit roster or Create own roster 
              and View absentee or View own absentee
            - Minimum plan: basic
        
        Args:
            employee_ids (List[str], optional): List of employee IDs to filter conflicts by
            min_date (date, optional): The minimum date for returned conflicts (YYYY-MM-DD)
            max_date (date, optional): The maximum date for returned conflicts (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Time off planning conflicts data
            
        Raises:
            ValueError: If planning conflicts data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 400: Bad request
        """
        try:
            # Prepare query parameters
            params = {}
            if employee_ids:
                params['employee_ids'] = ','.join(employee_ids)
            if max_date:
                if not isinstance(max_date, date):
                    raise TypeError("max_date must be a datetime object")
                params["max_date"] = max_date.strftime("%Y-%m-%d")
            if min_date:
                if not isinstance(min_date, date):
                    raise TypeError("min_date must be a datetime object")
                params["min_date"] = min_date.strftime("%Y-%m-%d")
                
            # Make the request
            response_data = self.shiftbase.get(f"{self.conflicts_uri}/time_off", params)
            
            if not response_data:
                return pd.DataFrame()
                
            # Create DataFrame from response
            df = pd.DataFrame(response_data)
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, PlanningConflictSchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid time off conflict data: {str(e)}")
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view time off conflicts.")
            if "400" in str(e):
                raise ValueError("Bad request: Check your parameters.")
            raise

    def get_employability(self, department_id: str, 
                          from_time: time, 
                          to_time: time, 
                          skills: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Retrieves employee employability for a new shift from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/planning/employability
        
        Notes:
            - Required permissions: Add schedules, Edit schedules
            - Minimum plan: free
            - Premium is required for the conflicting skills check
            - Basic is required for the Absence and Availability checks
        
        Args:
            department_id (str): The department identifier for the pool of available employees
            from_time (time): Start of period to check (HH:MM:SS)
            to_time (time): End of period to check (HH:MM:SS)
            skills (List[str], optional): Array of required skills to keep into account for the new shift
            
        Returns:
            pd.DataFrame: Employability data
            
        Raises:
            ValueError: If employability data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 426: Upgrade required
        """
        try:
            # Check parameter types
            if not isinstance(from_time, time):
                raise TypeError("from_time must be a time object")
            if not isinstance(to_time, time):
                raise TypeError("to_time must be a time object")
                
            # Prepare query parameters
            params = {
                'department_id': department_id,
                'from': from_time.strftime("%H:%M:%S"),
                'to': to_time.strftime("%H:%M:%S")
            }
            
            if skills:
                params['skills'] = skills
                
            # Make the request
            response_data = self.shiftbase.get("planning/employability", params)
            
            if not response_data:
                return pd.DataFrame()
                
            # Create DataFrame from response
            df = pd.DataFrame(response_data)
            
            # Validate the basic employability data
            try:
                valid_data, _ = Functions.validate_data(df, EmployabilitySchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid employability data: {str(e)}")
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view employability.")
            if "426" in str(e):
                raise ValueError("Upgrade required: Some features require premium or basic plan.")
            raise
            
    def get_shift_employability(self, shift_id: str, 
                               from_time: Optional[time] = None, 
                               to_time: Optional[time] = None) -> pd.DataFrame:
        """
        Retrieves employee employability for a specific shift from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/planning/shifts/{shiftId}/employability
        
        Notes:
            - Required permissions: Add schedules, Edit schedules
            - Minimum plan: free
            - Premium is required for the conflicting skills check
            - Basic is required for the Absence and Availability checks
        
        Args:
            shift_id (str): Shift ID to use for selecting potential employees and skill requirements
            from_time (time, optional): Start of period to check (HH:MM:SS), defaults to current time
            to_time (time, optional): End of period to check (HH:MM:SS), defaults to current time
            
        Returns:
            pd.DataFrame: Shift employability data
            
        Raises:
            ValueError: If employability data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 426: Upgrade required
        """
        try:
            # Prepare query parameters
            params = {}
            if from_time:
                if not isinstance(from_time, time):
                    raise TypeError("from_time must be a time object")
                params['from'] = from_time.strftime("%H:%M:%S")
            if to_time:
                if not isinstance(to_time, time):
                    raise TypeError("to_time must be a time object")
                params['to'] = to_time.strftime("%H:%M:%S")
                
            # Make the request
            response_data = self.shiftbase.get(f"planning/shifts/{shift_id}/employability", params)
            
            if not response_data:
                return pd.DataFrame()
                
            # Create DataFrame from response
            df = pd.DataFrame(response_data)
            
            # Validate the basic employability data
            try:
                valid_data, _ = Functions.validate_data(df, EmployabilitySchema)
                return valid_data
            except Exception as e:
                raise ValueError(f"Invalid shift employability data: {str(e)}")
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view shift employability.")
            if "426" in str(e):
                raise ValueError("Upgrade required: Some features require premium or basic plan.")
            raise 