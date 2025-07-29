from typing import Dict, List
import pandas as pd
from .schemas.insights import (
    DepartmentInsightSchema,
    TeamInsightSchema,
    ScheduleInsightDaySchema,
    ScheduleInsightTotalSchema
)
from brynq_sdk_functions import Functions
from datetime import date
class Insights:
    """
    Handles all Performance and Schedule Insight operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.insights_uri = "insights"
        
    def get_daily_performance(self, date_field: date,
                             department_ids: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Retrieves daily performance insights for the specified departments and date.
        
        Endpoint: GET https://api.shiftbase.com/api/insights/performance/daily/{date}
        
        Notes:
            - Required permissions: View logs
            - Minimum plan: Premium
            
            Performance insights use department targets to determine status:
            - For Productivity:
              - On: ≥ above target
              - Near: 0-3% below target
              - Off: >3% below target
            - For Average Hourly Wage:
              - On: ≤ below target
              - Near: Up to 2% above target
              - Off: >2% above target
            - For Labor Cost Percentage:
              - On: ≤ below target
              - Near: Up to 10% above target
              - Off: >10% above target
        
        Args:
            date_field (str): The date to retrieve insights for (YYYY-MM-DD)
            department_ids (List[str]): List of department IDs to retrieve insights for
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing two DataFrames:
                - 'departments': Department performance insights
                - 'teams': Team performance insights
            
        Raises:
            ValueError: If parameters are invalid or data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 426: Upgrade required (Premium plan required)
        """
        # Validate date
        if not date_field:
            raise ValueError("date cannot be empty")

        if not isinstance(date_field, date):
            raise TypeError("date_field must be a datetime object")
        date_field = date_field.strftime("%Y-%m-%d")
        # Validate department_ids
        if not department_ids:
            raise ValueError("department_ids cannot be empty")
            
        try:
            # Prepare query parameters
            params = {
                'department_ids': ','.join(department_ids)
            }
                
            # Make the request
            response_data = self.shiftbase.get(f"{self.insights_uri}/performance/daily/{date_field}", params)
            
            if not response_data:
                return {
                    'departments': pd.DataFrame(),
                    'teams': pd.DataFrame()
                }
                
            # Extract departments and teams insights
            departments_data = response_data.get('departments', [])
            teams_data = response_data.get('teams', [])
            
            # Create DataFrames
            df_departments = pd.DataFrame(departments_data) if departments_data else pd.DataFrame()
            df_teams = pd.DataFrame(teams_data) if teams_data else pd.DataFrame()
            
            # If no data is returned, return empty DataFrames
            if df_departments.empty and df_teams.empty:
                return {
                    'departments': pd.DataFrame(),
                    'teams': pd.DataFrame()
                }
                
            # Validate departments data if not empty
            if not df_departments.empty:
                try:
                    valid_departments_data, _ = Functions.validate_data(df_departments, DepartmentInsightSchema)
                    df_departments = valid_departments_data
                except Exception as e:
                    raise ValueError(f"Invalid department insight data: {str(e)}")
            
            # Validate teams data if not empty
            if not df_teams.empty:
                try:
                    valid_teams_data, _ = Functions.validate_data(df_teams, TeamInsightSchema)
                    df_teams = valid_teams_data
                except Exception as e:
                    raise ValueError(f"Invalid team insight data: {str(e)}")
            
            return {
                'departments': df_departments,
                'teams': df_teams
            }
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view performance insights")
            if "426" in str(e):
                raise ValueError("Premium plan required to access performance insights")
            raise
            
    def get_schedule_insights(self, department_ids: List[str], 
                             from_date: date, 
                             to_date: date) -> Dict[str, pd.DataFrame]:
        """
        Retrieves schedule insights for the specified departments and date range.
        
        Endpoint: GET https://api.shiftbase.com/api/insights/schedule
        
        Notes:
            - Required permissions: Create roster, Edit roster
            - Minimum plan: Premium
            
            Schedule insights use department targets to determine status:
            - For Productivity:
              - ±3%: On target
              - 3-6%: Near target
              - Above 6%: Off target
            - For Average Hourly Wage:
              - Below target: On target
              - Up to 10% above target: Near target
              - Above 10%: Off target
            - For Labor Cost Percentage:
              - Below target: On target
              - Up to 2% above target: Near target
              - Above 2%: Off target
        
        Args:
            department_ids (List[str]): List of department IDs to retrieve insights for
            from_date (date): Start date for the period
            to_date (date): End date for the period
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing two DataFrames:
                - 'days': Daily schedule insights
                - 'totals': Total schedule insights
            
        Raises:
            ValueError: If parameters are invalid or data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
                - 426: Upgrade required (Premium plan required)
        """
        # Validate department_ids
        if not department_ids:
            raise ValueError("department_ids cannot be empty")
            
        # Validate from_date
        if not from_date:
            raise ValueError("from_date cannot be empty")
            
        if not isinstance(from_date, date):
            raise TypeError("from_date must be a datetime.date object")
            
        # Validate to_date
        if not to_date:
            raise ValueError("to_date cannot be empty")
            
        if not isinstance(to_date, date):
            raise TypeError("to_date must be a datetime.date object")
            
        try:
            # Prepare query parameters
            params = {
                'department_ids': ','.join(department_ids),
                'from': from_date.strftime("%Y-%m-%d"),
                'to': to_date.strftime("%Y-%m-%d")
            }
                
            # Make the request
            response_data = self.shiftbase.get(f"{self.insights_uri}/schedule", params)
            
            if not response_data:
                return {
                    'days': pd.DataFrame(),
                    'totals': pd.DataFrame()
                }
                
            # Extract days and totals insights
            days_data = response_data.get('days', [])
            totals_data = response_data.get('totals', [])
            
            # Create DataFrames
            df_days = pd.DataFrame(days_data) if days_data else pd.DataFrame()
            df_totals = pd.DataFrame(totals_data) if totals_data else pd.DataFrame()
            
            # If no data is returned, return empty DataFrames
            if df_days.empty and df_totals.empty:
                return {
                    'days': pd.DataFrame(),
                    'totals': pd.DataFrame()
                }
                
            # Validate days data if not empty
            if not df_days.empty:
                try:
                    valid_days_data, _ = Functions.validate_data(df_days, ScheduleInsightDaySchema)
                    df_days = valid_days_data
                except Exception as e:
                    raise ValueError(f"Invalid schedule day insight data: {str(e)}")
            
            # Validate totals data if not empty
            if not df_totals.empty:
                try:
                    valid_totals_data, _ = Functions.validate_data(df_totals, ScheduleInsightTotalSchema)
                    df_totals = valid_totals_data
                except Exception as e:
                    raise ValueError(f"Invalid schedule total insight data: {str(e)}")
            
            return {
                'days': df_days,
                'totals': df_totals
            }
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view schedule insights")
            if "426" in str(e):
                raise ValueError("Premium plan required to access schedule insights")
            raise 