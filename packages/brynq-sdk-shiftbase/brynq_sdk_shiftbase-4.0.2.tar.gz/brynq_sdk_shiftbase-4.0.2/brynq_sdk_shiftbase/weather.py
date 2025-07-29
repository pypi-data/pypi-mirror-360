from typing import Dict, Optional, List, Union
import pandas as pd
from .schemas.weather import WeatherForecastDaySchema, WeatherForecastDayTimeBlockSchema
from brynq_sdk_functions import Functions
from datetime import date

class Weather:
    """
    Handles all Weather forecast related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.weather_uri = "weather"
        
    def get(self, departments: Optional[List[str]] = None, 
            min_date: Optional[date] = None,
            max_date: Optional[date] = None) -> Dict[str, pd.DataFrame]:
        """
        Retrieves weather forecasts for departments from Shiftbase.
        
        Endpoint: GET https://api.shiftbase.com/api/weather
        
        Notes:
            - Minimum plan: basic
        
        Args:
            departments (List[str], optional): List of department IDs to filter forecasts by
            min_date (date, optional): Start date for period for the weather forecast
            max_date (date, optional): End date for period for the weather forecast
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing two DataFrames:
                - 'days': Weather forecast days data
                - 'time_blocks': Weather forecast time blocks data
            
        Raises:
            ValueError: If weather forecast data fails validation
            requests.HTTPError: 
                - 403: Unauthorized access
        """
        try:
            # Prepare query parameters
            params = {}
            if departments:
                params['departments'] = ','.join(departments)
            if min_date:
                if not isinstance(min_date, date):
                    raise TypeError("min_date must be a date object")
                params['min_date'] = min_date.strftime("%Y-%m-%d")
            if max_date:
                if not isinstance(max_date, date):
                    raise TypeError("max_date must be a date object")
                params['max_date'] = max_date.strftime("%Y-%m-%d")
                
            # Make the request
            response_data = self.shiftbase.get(self.weather_uri, params)
            
            if not response_data:
                return {
                    'days': pd.DataFrame(),
                    'time_blocks': pd.DataFrame()
                }
                
            # Extract days forecasts and time blocks
            days_data = []
            time_blocks_data = []
            
            for day_forecast in response_data:
                # Create a copy of the day forecast data without TimeBlocks
                day_data = {k: v for k, v in day_forecast.items() if k != 'TimeBlocks'}
                days_data.append(day_data)
                
                # Process time blocks if they exist
                if 'TimeBlocks' in day_forecast and day_forecast['TimeBlocks']:
                    for time_block in day_forecast['TimeBlocks']:
                        # Add department_id and date to time block for reference
                        time_block['department_id'] = day_forecast['department_id']
                        time_block['date'] = day_forecast['date']
                        time_blocks_data.append(time_block)
            
            # Create DataFrames
            df_days = pd.DataFrame(days_data)
            df_time_blocks = pd.DataFrame(time_blocks_data) if time_blocks_data else pd.DataFrame()
            
            # If no data is returned, return empty DataFrames
            if df_days.empty:
                return {
                    'days': pd.DataFrame(),
                    'time_blocks': pd.DataFrame()
                }
                
            # Validate days data
            try:
                valid_days_data, _ = Functions.validate_data(df_days, WeatherForecastDaySchema)
                df_days = valid_days_data
            except Exception as e:
                raise ValueError(f"Invalid weather forecast days data: {str(e)}")
                
            # Validate time blocks data if not empty
            if not df_time_blocks.empty:
                try:
                    valid_time_blocks_data, _ = Functions.validate_data(df_time_blocks, WeatherForecastDayTimeBlockSchema)
                    df_time_blocks = valid_time_blocks_data
                except Exception as e:
                    raise ValueError(f"Invalid weather forecast time blocks data: {str(e)}")
            
            return {
                'days': df_days,
                'time_blocks': df_time_blocks
            }
                
        except Exception as e:
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view weather forecasts.")
            raise 