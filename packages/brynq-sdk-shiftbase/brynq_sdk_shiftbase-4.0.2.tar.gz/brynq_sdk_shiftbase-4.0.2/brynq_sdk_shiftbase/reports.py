from typing import Dict, Optional, List, Union, Any
import pandas as pd
import io

import requests

from .schemas.reports import (
    ReportSchema,
    ReportingFavoriteSchema,
    RecurringReportSchema,
    ReportParameters,
    AbsenteeReportRequestSchema
)
from brynq_sdk_functions import Functions
from datetime import date

class Reports:
    """
    Handles all reporting related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.reports_uri = "reports"
        self.reporting_uri = "reporting"
    
    def get_favorites(self) -> pd.DataFrame:
        """
        Retrieves a list of favorite reports for the authorized user.
        
        Endpoint: GET https://api.shiftbase.com/api/reporting/favorites
        
        Returns:
            pd.DataFrame: Favorite reports data
            
        Raises:
            ValueError: If favorite report data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
        """
        # Construct the endpoint URL
        endpoint = f"{self.reporting_uri}/favorites"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Convert to DataFrame
            if not response_data:
                return pd.DataFrame()
                
            favorites = []
            for favorite in response_data:
                # Validate with Pydantic schema
                try:
                    validated_favorite = ReportingFavoriteSchema.parse_obj(favorite)
                    favorites.append(validated_favorite.dict())
                except Exception as e:
                    print(f"Warning: Invalid favorite report data: {str(e)}. Skipping.")
            
            return pd.DataFrame(favorites)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View reports' permission and a premium plan.")
            raise
    
    def get_favorite_by_id(self, uuid: str) -> Dict:
        """
        Retrieves a specific favorite report by its UUID.
        
        Endpoint: GET https://api.shiftbase.com/api/reporting/favorites/{uuid}
        
        Args:
            uuid (str): The unique identifier of the favorite report
            
        Returns:
            Dict: Favorite report details
            
        Raises:
            ValueError: If uuid is invalid or favorite report data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
                - 404: Favorite report not found
        """
        # Validate uuid
        if not uuid:
            raise ValueError("uuid cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.reporting_uri}/favorites/{uuid}"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Validate with Pydantic schema
            try:
                validated_favorite = ReportingFavoriteSchema.parse_obj(response_data)
                return validated_favorite.dict()
            except Exception as e:
                error_message = f"Invalid favorite report data: {str(e)}"
                raise ValueError(error_message)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View reports' permission.")
            elif "404" in str(e):
                raise ValueError(f"Favorite report with UUID {uuid} not found.")
            raise
    
    def get_recurring(self) -> pd.DataFrame:
        """
        Retrieves a list of recurring reports.
        
        Endpoint: GET https://api.shiftbase.com/api/reporting/recurring
        
        Returns:
            pd.DataFrame: Recurring reports data
            
        Raises:
            ValueError: If recurring report data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
        """
        # Construct the endpoint URL
        endpoint = f"{self.reporting_uri}/recurring"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            
            # Convert to DataFrame
            if not response_data:
                return pd.DataFrame()
                
            recurring_reports = []
            for report in response_data:
                # Validate with Pydantic schema
                try:
                    validated_report = RecurringReportSchema.parse_obj(report)
                    recurring_reports.append(validated_report.dict())
                except Exception as e:
                    print(f"Warning: Invalid recurring report data: {str(e)}. Skipping.")
            
            return pd.DataFrame(recurring_reports)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View reports' permission and a premium plan.")
            raise
    
    def get_requested(self) -> pd.DataFrame:
        """
        Retrieves a list of reports that are requested by the current user.
        
        Endpoint: GET https://api.shiftbase.com/api/reports
        
        Returns:
            pd.DataFrame: Requested reports data
            
        Raises:
            ValueError: If report data fails validation
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
        """
        try:
            # Make the request
            response_data = self.shiftbase.get(self.reports_uri)
            
            # Convert to DataFrame
            df = pd.DataFrame(response_data)
            
            # If no data is returned, return an empty DataFrame
            if df.empty:
                return df
            
            # Validate with Functions.validate_data
            try:
                valid_data, _ = Functions.validate_data(df, ReportSchema)
                return valid_data
            except Exception as e:
                error_message = f"Invalid report data: {str(e)}"
                raise ValueError(error_message)
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View reports' permission.")
            raise
    
    def get_report_status(self, report_id: str) -> Dict:
        """
        Retrieves the status of a specific report.
        
        Endpoint: GET https://api.shiftbase.com/api/reports/{reportId}/status
        
        Args:
            report_id (str): The unique identifier of the report
            
        Returns:
            Dict: Report status details
            
        Raises:
            ValueError: If report_id is invalid
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
                - 404: Report not found
        """
        # Validate report_id
        if not report_id:
            raise ValueError("report_id cannot be empty")
            
        # Construct the endpoint URL
        endpoint = f"{self.reports_uri}/{report_id}/status"
        
        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)
            return response_data
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View reports' permission.")
            elif "404" in str(e):
                raise ValueError(f"Report with ID {report_id} not found.")
            raise
    
    def fetch_report(self, report_id: str, format: str = "json") -> Union[pd.DataFrame, Dict, str, bytes]:
        """
        Fetches the result of a report in the specified format.
        
        Endpoint: GET https://api.shiftbase.com/api/reports/{reportId}/fetch
        
        Args:
            report_id (str): The unique identifier of the report
            format (str): The format of the returned report. 
                         Options: "html", "csv", "xlsx", "json"
            
        Returns:
            Union[pd.DataFrame, Dict, str, bytes]: Report data in the specified format
                - For "json": Returns a DataFrame
                - For "csv": Returns a DataFrame
                - For "xlsx": Returns bytes containing the Excel file
                - For "html": Returns the HTML content as a string
            
        Raises:
            ValueError: If report_id is invalid or format is invalid
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
                - 404: Report not found
        """
        # Validate report_id
        if not report_id:
            raise ValueError("report_id cannot be empty")
            
        # Validate format
        valid_formats = ["html", "csv", "xlsx", "json"]
        if format not in valid_formats:
            raise ValueError(f"Invalid format: {format}. Must be one of {valid_formats}")
            
        # Construct the endpoint URL
        endpoint = f"{self.reports_uri}/{report_id}/fetch"
        
        # Prepare query parameters
        params = {"format": format}
        
        try:
            # For JSON and CSV formats, we can process the response data into a DataFrame
            if format in ["json", "csv"]:
                # Make the request
                response_data = self.shiftbase.get(endpoint, params)
                
                if format == "json":
                    return pd.DataFrame(response_data)
                else:  # CSV format
                    # Process CSV data
                    return pd.read_csv(io.StringIO(response_data))
            else:
                # For XLSX and HTML formats, we need to get the raw response content
                url = f"{self.shiftbase.base_url}{endpoint}"
                response = self.shiftbase.session.get(url, params=params)
                response.raise_for_status()
                
                if format == "xlsx":
                    return response.content  # Return bytes for XLSX
                else:  # HTML format
                    return response.text  # Return text for HTML
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View reports' permission.")
            elif "404" in str(e):
                raise ValueError(f"Report with ID {report_id} not found.")
            raise
            
    def absentee_report(self, from_date: date, to_date: date, 
                        columns: Optional[List[str]] = None,
                        export_format: str = "json",
                        user: Optional[str] = None,
                        absentee_option: Optional[str] = None,
                        contract_type: Optional[List[str]] = None,
                        contract_department: Optional[List[str]] = None,
                        approval_status: Optional[List[str]] = None) -> requests.Response:
        """
        Generates an absentee report from Shiftbase.
        
        Endpoint: POST https://api.shiftbase.com/api/reports/absentee
        
        For more info see: https://help.shiftbase.com/report-employees-absent
        
        Args:
            from_date (date): Start date of the period (YYYY-MM-DD)
            to_date (date): End date of the period (YYYY-MM-DD)
            columns (List[str], optional): Specific columns to include in the report
            export_format (str, optional): Format of the returned report. 
                                         Options: "raw", "json", "csv", "xlsx"
                                         Default: "json"
            user (str, optional): User ID filter
            absentee_option (str, optional): Absentee option filter
            contract_type (List[str], optional): Contract type filter
            contract_department (List[str], optional): Contract department filter
            approval_status (List[str], optional): Approval status filter. 
                                                 Options: "Approved", "Pending", "Declined"
            
        Returns:
            Response: requests.Response object
            
        Raises:
            ValueError: If parameters are invalid
            requests.HTTPError: 
                - 403: Forbidden access (insufficient permissions)
        """
        # Validate date parameters
        if not isinstance(from_date, date):
            raise TypeError("from_date must be a date object")
        if not isinstance(to_date, date):
            raise TypeError("to_date must be a date object")
            
        # Prepare request data
        request_data = {
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "export": export_format
        }
        
        # Add optional parameters if provided
        if columns:
            request_data["columns"] = columns
        if user:
            request_data["user"] = user
        if absentee_option:
            request_data["absenteeOption"] = absentee_option
        if contract_type:
            request_data["contractType"] = contract_type
        if contract_department:
            request_data["contractDepartment"] = contract_department
        if approval_status:
            request_data["approvalStatus"] = approval_status
            
        # Validate the request data against the schema
        try:
            valid_data, invalid_data = Functions.validate_pydantic_data(
                data=request_data, 
                schema=AbsenteeReportRequestSchema
            )

            if invalid_data:
                raise ValueError(f"Invalid request data: {invalid_data}")
        except Exception as e:
            raise ValueError(f"Invalid request data: {str(e)}")
        
        # Prepare the request body
        request_body = valid_data[0]
        request_body["from"] = request_body.pop("from_date")
        request_body["to"] = request_body.pop("to_date")
        request_body["columns"] = []
        
        # Construct the endpoint URL
        endpoint = f"{self.reports_uri}/absentee"
        
        try:
            # For JSON and CSV formats
            if export_format in ["json", "csv"]:
                # Make the request
                url = f"{self.shiftbase.base_url}{endpoint}"
                response = self.shiftbase.session.post(url, json=request_body)
                response.raise_for_status()
                return response
            elif export_format == "xlsx":
                # For XLSX format, we need to get the raw response content
                url = f"{self.shiftbase.base_url}{endpoint}"
                response = self.shiftbase.session.post(url, json=request_body)
                response.raise_for_status()
                return response  # Return bytes for XLSX
            else:  # Raw format
                # Make the request and return the raw data
                url = f"{self.shiftbase.base_url}{endpoint}"
                response = self.shiftbase.session.post(url, json=request_body)
                response.raise_for_status()
                return response
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Access forbidden. Check if you have 'View reports' and 'View absentee' permissions.")
            raise 