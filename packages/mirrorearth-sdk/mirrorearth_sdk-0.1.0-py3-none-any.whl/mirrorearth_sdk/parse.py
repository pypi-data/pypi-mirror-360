from dataclasses import dataclass

import requests
from .Variable import Variable
from .Aggregation import Aggregation
from .VariableWithValues import VariableWithValues
from .Unit import Unit
from .Model import Model
import numpy as np
import pandas as pd
from .WeatherApiResponse import WeatherApiResponse
from typing import Dict, Any, Optional, List, Union, TypeVar, Generic
from .variable_mapping import variable_name_to_short_name, short_name_to_variable_name

def get_enum_key(enum, value):
    for key, v in enum.__dict__.items():
        if value == v:
            return key
    return None


unit_value_to_symbol = {
    Unit.undefined: "",
    Unit.celsius: "°C",
    Unit.centimetre: "cm",
    Unit.cubic_metre_per_cubic_metre: "m³/m³",
    Unit.cubic_metre_per_second: "m³/s",
    Unit.degree_direction: "°",
    Unit.dimensionless_integer: "",
    Unit.dimensionless: "",
    Unit.european_air_quality_index: "EAQI",
    Unit.fahrenheit: "°F",
    Unit.feet: "ft",
    Unit.fraction: "",
    Unit.gdd_celsius: "GDD(°C)",
    Unit.geopotential_metre: "gpm",
    Unit.grains_per_cubic_metre: "gr/m³",
    Unit.gram_per_kilogram: "g/kg",
    Unit.hectopascal: "hPa",
    Unit.hours: "h",
    Unit.inch: "in",
    Unit.iso8601: "",
    Unit.joule_per_kilogram: "J/kg",
    Unit.kelvin: "K",
    Unit.kilopascal: "kPa",
    Unit.kilogram_per_square_metre: "kg/m²",
    Unit.kilometres_per_hour: "km/h",
    Unit.knots: "kn",
    Unit.megajoule_per_square_metre: "MJ/m²",
    Unit.metre_per_second_not_unit_converted: "m/s",
    Unit.metre_per_second: "m/s",
    Unit.metre: "m",
    Unit.micrograms_per_cubic_metre: "μg/m³",
    Unit.miles_per_hour: "mph",
    Unit.millimetre: "mm",
    Unit.pascal: "Pa",
    Unit.per_second: "/s",
    Unit.percentage: "%",
    Unit.seconds: "s",
    Unit.unix_time: "",
    Unit.us_air_quality_index: "USAQI",
    Unit.watt_per_square_metre: "W/m²",
    Unit.wmo_code: "",
    Unit.parts_per_million: "ppm"
}


def get_unit_symbol(unit_value):
    """
    根据Unit枚举值获取对应的单位符号

    Args:
        unit_value: Unit枚举的值

    Returns:
        str: 对应的单位符号
    """
    return unit_value_to_symbol.get(unit_value, "")


aggregation_short_name = {
    Aggregation.none: "none",
    Aggregation.minimum: "min",
    Aggregation.maximum: "max",
    Aggregation.mean: "mean",
    Aggregation.p10: "p10",
    Aggregation.p25: "p25",
    Aggregation.median: "median",
    Aggregation.p75: "p75",
    Aggregation.p90: "p90",
    Aggregation.dominant: "dominant",
    Aggregation.sum: "sum",
    Aggregation.spread: "spread"
}


@dataclass
class VariableInPython:
    variable_name: str = None
    aggregation_name: str = None
    altitude: int = None
    unit: str = None
    pressure_level: str = None
    depth: int = None
    depth_to: int = None
    ensemble_member: str = None
    previous_day: str = None
    values: np.ndarray = None
    model: str = None
    with_model: bool = False

    def name(self, del_model: bool = False, short_name: bool = False, unit: bool = True):
        x = self.variable_name
        if self.altitude:
            x += f"_{self.altitude}m"

        if self.variable_name == 'shortwave_radiation' and self.altitude:
            if self.altitude == 1:
                x = 'longwave_radiation_downward' 
            elif self.altitude == 2:
                x = 'shortwave_radiation_upward' 
            elif self.altitude == 3:
                x = 'longwave_radiation_upward'

        if self.variable_name == 'surface_pressure' and self.altitude == 80:
            x = 'pressure_80m'

        if self.depth_to and self.depth_to > 0:
            x += f"_{self.depth}_to_{self.depth_to}cm"
        if self.aggregation_name and self.aggregation_name != "none":
            x += f"_{self.aggregation_name}"
        if self.pressure_level:
            x += f"_{self.pressure_level}hPa"
        if not del_model and self.with_model and self.model:
            x += f"_{self.model}"

        if short_name:
            x = variable_name_to_short_name.get(x, x)
        if unit and self.unit:
            x += f"_{self.unit}"    
        return x

    def __repr__(self):
        return self.name()


class VariableManager:
    def __init__(self, variables: list[VariableInPython], times: pd.DatetimeIndex):
        self.variables = variables
        self.times = times

    def __getitem__(self, key):
        return self.variables[key]

    def __len__(self):
        return len(self.variables)

    def get_item_by_name(self, name: str):
        return next((v for v in self.variables if v.name(del_model=True) == name), None)

    def __repr__(self):
        return str(self.variables)

    def to_df(self, short_name: bool = False, unit: bool = True) -> pd.DataFrame:
        return pd.DataFrame({i.name(del_model=True, short_name=short_name, unit=unit): i.values for i in self.variables}, index=self.times)

@dataclass
class Metadata:
    """A class that contains weather data metadata."""
    location_id: str
    latitude: float
    longitude: float
    elevation: float
    timezone: str
    timezone_abbreviation: str
    utc_offset_seconds: int
    generation_time_ms: float
    model_value: int  # Raw model value from the API
    
    @property
    def model(self) -> str:
        """Return the model name."""
        return get_enum_key(Model, self.model_value)
    
    def __repr__(self):
        return (f"Metadata(location: {self.location_id}, "
                f"coords: ({self.latitude}, {self.longitude}), "
                f"model: {self.model}, timezone: {self.timezone})")


@dataclass
class WeatherData:
    """A class that organizes weather data with metadata and time series data."""
    metadata: Metadata
    hourly: Optional[VariableManager] = None
    daily: Optional[VariableManager] = None
    monthly: Optional[VariableManager] = None
    
    def __repr__(self):
        components = [f"Metadata: {self.metadata}"]
        if self.hourly and len(self.hourly) > 0:
            components.append(f"Hourly data: {len(self.hourly)} variables")
        if self.daily and len(self.daily) > 0:
            components.append(f"Daily data: {len(self.daily)} variables")
        if self.monthly and len(self.monthly) > 0:
            components.append(f"Monthly data: {len(self.monthly)} variables")
        return ", ".join(components)
    
    def hourly_df(self, short_name: bool = False, unit: bool = True) -> pd.DataFrame:
        return self.hourly.to_df(short_name, unit)
    
    def daily_df(self, short_name: bool = False, unit: bool = True) -> pd.DataFrame:
        return self.daily.to_df(short_name, unit)
    
    def monthly_df(self, short_name: bool = False, unit: bool = True) -> pd.DataFrame:
        return self.monthly.to_df(short_name, unit)
    
    @property
    def model(self) -> str:
        """Return the model name from metadata."""
        return self.metadata.model


class WeatherResponse:
    """A class that manages multiple WeatherData objects, typically from different models."""
    
    def __init__(self, weather_data_list: List[WeatherData]):
        self.data = weather_data_list
        
    def __len__(self) -> int:
        return len(self.data)
        
    def __getitem__(self, key: Union[int, str]) -> WeatherData:
        """Get WeatherData by index or by model name."""
        if isinstance(key, int):
            return self.data[key]
        elif isinstance(key, str):
            for data in self.data:
                if data.model == key:
                    return data
            raise KeyError(f"No weather data for model '{key}'")
        else:
            raise TypeError("Key must be an integer index or a model name string")
    
    def __iter__(self):
        return iter(self.data)
    
    def __repr__(self):
        if not self.data:
            return "WeatherResponse(empty)"
        models = [data.model for data in self.data if data.model]
        return f"WeatherResponse(models: {', '.join(models) if models else 'unknown'})"
    
    @property
    def models(self) -> List[str]:
        """Return a list of available model names."""
        return [data.model for data in self.data if data.model]


def parse_variable(variable: VariableWithValues, model: str = None, with_model: bool = False) -> VariableInPython:
    """
    flat编码的variable解析为python的variable(str)
    """
    variable_name = get_enum_key(Variable, variable.Variable())
    aggregation_name = aggregation_short_name.get(variable.Aggregation(), "none")
    altitude = variable.Altitude()
    # unit = get_enum_key(Unit, variable.Unit())
    unit = get_unit_symbol(variable.Unit())
    pressure_level = variable.PressureLevel()
    depth = variable.Depth()
    depth_to = variable.DepthTo()
    ensemble_member = variable.EnsembleMember()
    previous_day = variable.PreviousDay()

    return VariableInPython(variable_name, aggregation_name, altitude, unit, pressure_level, depth, depth_to,
                            ensemble_member, previous_day, variable.ValuesAsNumpy(), model, with_model)


def parse_flat_response(response: requests.Response) -> List[WeatherApiResponse]:

    if response.headers.get("Content-Type").startswith("application/json"):
        raise Exception(response.json())

    if response.status_code != 200:
        raise Exception(response.json())

    data = response.content
    messages = []
    total = len(data)
    pos = int(0)
    while pos < total:
        length = int.from_bytes(data[pos: pos + 4], byteorder="little")
        message = WeatherApiResponse.GetRootAs(data, pos + 4)
        messages.append(message)
        pos += length + 4
    return messages


def get_flat_response(response: requests.Response) -> WeatherResponse:
    archive_responses = parse_flat_response(response)
    with_model_suffix = len(archive_responses) > 1
    result = []
    for archive_response in archive_responses:
        # Get the model identifier
        model = get_enum_key(Model, archive_response.Model())
        
        # Process hourly data
        hourly = archive_response.Hourly()
        hourly_data = VariableManager([], [])
        if hourly:
            hourly_variables = list(map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength())))
            vs = list(map(lambda v: parse_variable(v, model, with_model_suffix), hourly_variables))
            hourly_time = pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                periods=len(vs[0].values),
                inclusive="left"
            ) + pd.Timedelta(seconds=archive_response.UtcOffsetSeconds())
            hourly_data = VariableManager(vs, hourly_time)

        # Process daily data
        daily = archive_response.Daily()
        daily_data = VariableManager([], [])
        if daily:
            daily_variables = list(map(lambda i: daily.Variables(i), range(0, daily.VariablesLength())))
            if len(daily_variables) > 0:
                dvs = list(map(lambda v: parse_variable(v, model, with_model_suffix), daily_variables))
                daily_time = pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s"),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    periods=len(dvs[0].values),
                    inclusive="left"
                ) + pd.Timedelta(seconds=archive_response.UtcOffsetSeconds())
                daily_data = VariableManager(dvs, daily_time)

        # Process monthly data
        monthly = archive_response.Monthly()
        monthly_data = VariableManager([], [])
        if monthly:
            delta = archive_response.UtcOffsetSeconds()
            monthly_variables = list(map(lambda i: monthly.Variables(i), range(0, monthly.VariablesLength())))
            if len(monthly_variables) > 0:
                mvs = list(map(lambda v: parse_variable(v, model, with_model_suffix), monthly_variables))
                monthly_time = pd.date_range(
                    start=pd.to_datetime(monthly.Time() + delta, unit="s"),
                    periods=len(mvs[0].values),
                    freq='MS'
                )
                monthly_data = VariableManager(mvs, monthly_time)

        # Create a WeatherData object with Metadata and add it to the result list
        weather_data = WeatherData(
            metadata=Metadata(
                location_id=archive_response.LocationId(),
                latitude=archive_response.Latitude(),
                longitude=archive_response.Longitude(),
                elevation=archive_response.Elevation(),
                timezone=archive_response.Timezone(),
                timezone_abbreviation=archive_response.TimezoneAbbreviation(),
                utc_offset_seconds=archive_response.UtcOffsetSeconds(),
                generation_time_ms=archive_response.GenerationTimeMilliseconds(),
                model_value=archive_response.Model()
            ),
            hourly=hourly_data if len(hourly_data) > 0 else None,
            daily=daily_data if len(daily_data) > 0 else None,
            monthly=monthly_data if len(monthly_data) > 0 else None
        )
        result.append(weather_data)

    # Return a WeatherResponse object containing all the WeatherData objects
    return WeatherResponse(result)


def format_start_hour(start_hour: str):
    date = pd.to_datetime(start_hour)
    return date.strftime('%Y-%m-%dT%H:%M')

