
import pandera as pa
from pandera.typing import Series
from datetime import date as date_type

class WeatherForecastDayTimeBlockSchema(pa.DataFrameModel):
    """
    Validation schema for Weather Forecast Time Block data from Shiftbase API
    """
    time_from: Series[str] = pa.Field(description="Start time for weather forecast time block")
    time_till: Series[str] = pa.Field(description="End time for weather forecast time block")
    temp_celcius: Series[int] = pa.Field(description="Average temperature in celsius")
    temp_min_celcius: Series[int] = pa.Field(description="Minimum temperature in celsius")
    temp_max_celcius: Series[int] = pa.Field(description="Maximum temperature in celsius")
    rain_mm: Series[int] = pa.Field(description="Rain forecast in mm")
    weather_type: Series[str] = pa.Field(description="Weather type of the weather forecast")
    
    @pa.check("time_from", "time_till")
    def check_time_format(cls, series: Series[str]) -> Series[bool]:
        """Validate time is in HH:MM format."""
        valid = series.str.match(r"^\d{2}:\d{2}$") | series.isna()
        return valid

class WeatherForecastDaySchema(pa.DataFrameModel):
    """
    Validation schema for Weather Forecast Day data from Shiftbase API
    """
    id: Series[str] = pa.Field(description="The id is a combination of department_id and date")
    department_id: Series[int] = pa.Field(description="ID of the department")
    date: Series[date_type] = pa.Field(description="Date of the weather forecast")
    temp_celcius: Series[int] = pa.Field(description="Average temperature in celsius")
    temp_min_celcius: Series[int] = pa.Field(description="Minimum temperature in celsius")
    temp_max_celcius: Series[int] = pa.Field(description="Maximum temperature in celsius")
    rain_mm: Series[int] = pa.Field(description="Rain forecast in mm")
    weather_type: Series[str] = pa.Field(description="Weather type of the weather forecast")
    