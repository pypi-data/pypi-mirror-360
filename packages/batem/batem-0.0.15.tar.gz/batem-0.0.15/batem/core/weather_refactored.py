"""Refactored weather data management system.

This module provides a robust, scalable, and testable weather data management
system with clear separation of concerns and proper class design.

Author: stephane.ploix@grenoble-inp.fr
Refactored for better maintainability and testability
"""
from __future__ import annotations
import json
import requests
from scipy.constants import Stefan_Boltzmann
import os
import sys
import glob
import pytz
from datetime import datetime
from math import exp, cos, pi
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple, Union, Any
from dataclasses import dataclass

from batem.core.timemg import (
    datetime_with_day_delta, epochtimems_to_datetime,
    epochtimems_to_stringdate, stringdate_to_openmeteo_date,
    stringdate_to_epochtimems
)
from batem.core.utils import (
    FilePathChecker, TimeSeriesPlotter, FilePathBuilder)
from timezonefinder import TimezoneFinder


# Constants
AVAILABLE_WEATHER_VARIABLES = [
    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
    "dew_point_2m", "precipitation", "rain", "showers", "snowfall",
    "snow_depth", "surface_pressure", "cloud_cover", "cloud_cover_low",
    "cloud_cover_mid", "cloud_cover_high", "wind_speed_10m",
    "wind_direction_10m", "wind_gusts_10m", "soil_temperature_0cm",
    "shortwave_radiation", "direct_radiation", "diffuse_radiation",
    "direct_normal_irradiance", "shortwave_radiation_instant",
    "direct_radiation_instant", "diffuse_radiation_instant",
    "direct_normal_irradiance_instant", "terrestrial_radiation_instant"
]

EQUIVALENT_OPENMETEO_WEATHER_VARIABLES = {
    'temperature_2m': 'temperature',
    'dew_point_2m': 'dew_point_temperature',
    'wind_speed_10m': 'wind_speed',
    'wind_direction_10m': 'wind_direction_in_deg',
    'apparent_temperature': 'feels_like',
    'relative_humidity_2m': 'humidity',
    'cloud_cover': 'cloudiness',
    'surface_pressure': 'pressure'
}


@dataclass
class WeatherLocation:
    """Represents a weather location with coordinates and metadata."""
    name: str
    latitude_deg_north: float
    longitude_deg_east: float
    elevation_m: float = 0.0
    timezone_str: Optional[str] = None


@dataclass
class WeatherVariable:
    """Represents a weather variable with its data and metadata."""
    name: str
    unit: str
    values: List[float]
    description: str = ""


class HumidityCalculator:
    """Handles humidity-related calculations."""

    @staticmethod
    def absolute_humidity_kg_per_m3(
        temperature_deg: float,
        relative_humidity_percent: float
    ) -> float:
        """Calculate absolute humidity in kg/m³."""
        Rv_J_per_kg_K = 461.5  # J/kg.K
        saturation_vapour_pressure_Pa = 611.213 * exp(
            17.5043 * temperature_deg / (temperature_deg + 241.2)
        )  # empirical formula of Magnus-Tetens
        partial_vapour_pressure_Pa = (
            saturation_vapour_pressure_Pa * relative_humidity_percent / 100
        )
        return partial_vapour_pressure_Pa / (
            Rv_J_per_kg_K * (temperature_deg + 273.15)
        )

    @staticmethod
    def absolute_humidity_kg_per_kg(
        temperature_deg: float,
        relative_humidity_percent: float,
        atmospheric_pressures_hPa: float = 1013.25
    ) -> float:
        """Calculate absolute humidity in kg/kg."""
        Rs_J_per_kg_K = 287.06
        density_kg_per_m3 = (
            atmospheric_pressures_hPa * 100 -
            2.30617 * relative_humidity_percent * exp(
                17.5043 * temperature_deg / (241.2 + temperature_deg)
            )
        ) / Rs_J_per_kg_K / (temperature_deg + 273.15)
        return HumidityCalculator.absolute_humidity_kg_per_m3(
            temperature_deg, relative_humidity_percent
        ) / density_kg_per_m3

    @staticmethod
    def relative_humidity(
        temperature_deg: float,
        absolute_humidity_kg_per_m3: float
    ) -> float:
        """Calculate relative humidity from absolute humidity."""
        Rv_J_per_kg_K = 461.5  # J/kg.K
        saturation_vapour_pressure_Pa = 611.213 * exp(
            17.5043 * temperature_deg / (temperature_deg + 241.2)
        )
        partial_vapour_pressure_Pa = (
            absolute_humidity_kg_per_m3 * Rv_J_per_kg_K *
            (temperature_deg + 273.15)
        )
        return 100 * partial_vapour_pressure_Pa / saturation_vapour_pressure_Pa


class ElevationService:
    """Service for retrieving elevation data."""

    def __init__(self, json_db_name: Optional[str] = None) -> None:
        """Initialize the elevation service."""
        self.json_db_name = (
            json_db_name or FilePathBuilder().get_localizations_file_path()
        )
        self.data = self._load_elevation_data()

    def _load_elevation_data(self) -> Dict[str, float]:
        """Load elevation data from JSON file."""
        if not os.path.isfile(self.json_db_name):
            return {}

        with open(self.json_db_name) as json_file:
            return json.load(json_file)

    def _save_elevation_data(self) -> None:
        """Save elevation data to JSON file."""
        with open(self.json_db_name, 'w') as json_file:
            json.dump(self.data, json_file)

    def get_elevation(
        self,
        longitude_deg_east: float,
        latitude_deg_north: float
    ) -> float:
        """Get elevation for given coordinates."""
        coordinate = f'({longitude_deg_east},{latitude_deg_north})'

        if coordinate not in self.data:
            elevation = self._fetch_elevation_from_api(
                longitude_deg_east, latitude_deg_north
            )
            self.data[coordinate] = elevation
            self._save_elevation_data()

        return self.data[coordinate]

    def _fetch_elevation_from_api(
        self,
        longitude_deg_east: float,
        latitude_deg_north: float
    ) -> float:
        """Fetch elevation from web API."""
        url = 'https://api.open-elevation.com/api/v1/lookup'
        params = {
            "locations": [{
                "latitude": latitude_deg_north,
                "longitude": longitude_deg_east
            }]
        }

        try:
            response = requests.post(url, json=params)
            response.raise_for_status()
            data = response.json()
            elevations = [result['elevation'] for result in data['results']]
            return elevations[0]
        except requests.HTTPError as error:
            print(
                "The elevation server does not respond: "
                "horizon mask has to be set manually.", error
            )
            return float(input('Elevation in m: '))


class WeatherFormatChecker:
    """Checks weather data format."""

    @staticmethod
    def is_open_meteo_file(json_content: Dict[str, Any]) -> bool:
        """Check if JSON content is from Open-Meteo."""
        return 'generationtime_ms' in json_content


class WeatherDataParser(ABC):
    """Abstract base class for weather data parsers."""

    @abstractmethod
    def parse(self, data: Dict[str, Any]) -> Tuple[
        List[int], Dict[str, List[float]], Dict[str, str]
    ]:
        """Parse weather data and return timestamps, values, and units."""
        pass


class OpenMeteoDataParser(WeatherDataParser):
    """Parser for Open-Meteo weather data format."""

    def __init__(self, timezone_str: str) -> None:
        """Initialize the parser with timezone."""
        self.timezone_str = timezone_str

    def parse(
        self,
        data: Dict[str, Any]
    ) -> Tuple[List[int], Dict[str, List[float]], Dict[str, str]]:
        """Parse Open-Meteo data format."""
        timestamps = []
        values = {}
        units = {}

        hourly_data = data['hourly']
        epochtimems = hourly_data['epochtimems']

        # Get variable names excluding timestamps
        variable_names = [
            name for name in hourly_data.keys()
            if name != 'epochtimems'
        ]

        # Initialize data structures
        for var_name in variable_names:
            weather_var_name = (
                EQUIVALENT_OPENMETEO_WEATHER_VARIABLES.get(var_name, var_name)
            )
            values[weather_var_name] = []
            units[weather_var_name] = data['hourly_units'][var_name]

        # Parse data
        for i, timestamp in enumerate(epochtimems):
            timestamps.append(timestamp)

            for var_name in variable_names:
                weather_var_name = (
                    EQUIVALENT_OPENMETEO_WEATHER_VARIABLES.get(
                        var_name, var_name)
                )
                values[weather_var_name].append(hourly_data[var_name][i])

        return timestamps, values, units


class WeatherDataProvider:
    """Provides weather data from various sources."""

    def __init__(self, elevation_service: Optional[ElevationService] = None) -> None:
        """Initialize the weather data provider."""
        self.elevation_service = elevation_service or ElevationService()

    def create_open_meteo_database(
        self,
        file_path: str,
        latitude_deg_north: float,
        longitude_deg_east: float,
        weather_data: List[str] = AVAILABLE_WEATHER_VARIABLES,
        timezone: Optional[pytz.timezone] = None
    ) -> None:
        """Create Open-Meteo weather database."""
        server_url = 'https://archive-api.open-meteo.com/v1/archive'

        # Calculate date range
        date_time_now = datetime.now(timezone)
        to_openmeteo_string_date = datetime_with_day_delta(
            date_time_now, number_of_days=-7, date_format='%d/%m/%Y'
        )
        from_openmeteo_string_date = stringdate_to_openmeteo_date('1/1/1980')
        to_openmeteo_string_date = stringdate_to_openmeteo_date(
            to_openmeteo_string_date, timezone
        )

        # Fetch data from API
        response = requests.get(
            server_url,
            params={
                "latitude": latitude_deg_north,
                "longitude": longitude_deg_east,
                "start_date": from_openmeteo_string_date,
                "end_date": to_openmeteo_string_date,
                "hourly": weather_data
            },
            headers={'Accept': 'application/json'},
            timeout=300,
            stream=True
        )

        data = response.json()
        if 'error' in data:
            raise ValueError(data['reason'])

        # Add metadata
        data['site_latitude'] = latitude_deg_north
        data['site_longitude'] = longitude_deg_east
        data['timezone'] = timezone

        # Process data
        self._remove_extra_times(data)
        self._add_epochtimems(data, timezone)
        del data['hourly']['time']

        # Save to file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)

    def _remove_extra_times(self, data: Dict[str, Any]) -> None:
        """Remove extra times with None values."""
        number_of_data_to_remove = 0
        for k in range(len(data['hourly']['time']) - 1, -1, -1):
            if data['hourly']['temperature_2m'][k] is None:
                number_of_data_to_remove += 1
            else:
                break

        for v in data['hourly']:
            for i in range(number_of_data_to_remove):
                data['hourly'][v].pop(-1)

    def _add_epochtimems(
        self,
        data: Dict[str, Any],
        timezone: Optional[pytz.timezone]
    ) -> None:
        """Add epoch timestamps to data."""
        epochtimems_list = []
        data['hourly']['epochtimems'] = epochtimems_list

        for openmeteo_stringtime in data['hourly']['time']:
            epochtimems = stringdate_to_epochtimems(
                openmeteo_stringtime,
                date_format='%Y-%m-%dT%H:%M',
                timezone_str=timezone
            )
            data['hourly']['epochtimems'].append(epochtimems)


class WeatherDataBuilder:
    """Builds weather data objects from various sources."""

    def __init__(self, data_provider: Optional[WeatherDataProvider] = None) -> None:
        """Initialize the weather data builder."""
        self.data_provider = data_provider or WeatherDataProvider()

    def build(
        self,
        location: str,
        albedo: float = 0.1,
        pollution: float = 0.1,
        given_latitude_north_deg: Optional[float] = None,
        given_longitude_east_deg: Optional[float] = None,
        from_requested_stringdate: Optional[str] = None,
        to_requested_stringdate: Optional[str] = None
    ) -> WeatherData:
        """Build weather data object."""
        self._validate_parameters(
            location, given_latitude_north_deg, given_longitude_east_deg
        )

        file_path = self._get_weather_file_path(
            location, given_latitude_north_deg, given_longitude_east_deg
        )

        weather_records = self._load_weather_records(file_path)

        if WeatherFormatChecker().is_open_meteo_file(weather_records):
            return self._build_from_open_meteo(
                location, weather_records, albedo, pollution,
                given_latitude_north_deg, given_longitude_east_deg
            )
        else:
            raise ValueError("Unsupported weather data format")

    def _validate_parameters(
        self,
        location: Optional[str],
        latitude_north_deg: Optional[float],
        longitude_east_deg: Optional[float]
    ) -> None:
        """Validate input parameters."""
        if (location is None
            and latitude_north_deg is None
                and longitude_east_deg is None):
            raise ValueError(
                "Either the location or the latitude and longitude "
                "must be provided"
            )
        elif location is None and (latitude_north_deg is None or
                                   longitude_east_deg is None):
            raise ValueError(
                "Either the location or the latitude and longitude "
                "must be provided"
            )

    def _get_weather_file_path(
        self,
        location: str,
        given_latitude_north_deg: Optional[float],
        given_longitude_east_deg: Optional[float]
    ) -> str:
        """Get weather file path, creating it if necessary."""
        file_path = FilePathBuilder().get_weather_file_path(location)

        if not FilePathChecker().is_file_exists(file_path):
            if (given_latitude_north_deg is None or
                    given_longitude_east_deg is None):
                raise ValueError(
                    "Latitude and longitude must be provided to "
                    "create the weather file"
                )

            print(f"Weather file {file_path} not found, creating it")
            self.data_provider.create_open_meteo_database(
                file_path, given_latitude_north_deg, given_longitude_east_deg
            )
            print(f"Weather file {file_path} created")
        else:
            print(f"Weather file {file_path} already exists")

        return file_path

    def _load_weather_records(self, file_path: str) -> Dict[str, Any]:
        """Load weather records from file."""
        with open(file_path) as json_file:
            weather_records = json.load(json_file)

            if 'error' in weather_records:
                msg = (f'Delete file {file_path} and try because '
                       f'{weather_records["reason"]}')
                raise ValueError(msg)

            return weather_records

    def _build_from_open_meteo(
        self,
        location: str,
        weather_records: Dict[str, Any],
        albedo: float,
        pollution: float,
        given_latitude_north_deg: Optional[float],
        given_longitude_east_deg: Optional[float],
    ) -> WeatherData:
        """Build weather data from Open-Meteo format."""
        print('Open-Meteo format selected', file=sys.stderr)

        # Get coordinates
        latitude_north_deg, longitude_east_deg = self._get_coordinates(
            given_latitude_north_deg, given_longitude_east_deg,
            weather_records
        )

        # Get timezone
        timezone_str = self._get_timezone(
            latitude_north_deg, longitude_east_deg)

        # Parse weather data
        parser = OpenMeteoDataParser(timezone_str)
        timestamps, values, units = parser.parse(weather_records)

        # Create weather data object
        weather_data = WeatherData(
            location=location,
            latitude_deg_north=latitude_north_deg,
            longitude_deg_east=longitude_east_deg,
            timestamps=timestamps,
            albedo=albedo,
            pollution=pollution,
            timezone_str=timezone_str
        )

        # Add variables
        for var_name, var_values in values.items():
            weather_data.add_variable(var_name, units[var_name], var_values)

        # Add derived variables
        self._add_derived_variables(weather_data)

        weather_data.origin = "openmeteo"
        return weather_data

    def _get_coordinates(
        self,
        given_latitude_north_deg: Optional[float],
        given_longitude_east_deg: Optional[float],
        weather_records: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Get latitude and longitude coordinates."""
        latitude_north_deg = (
            given_latitude_north_deg or
            float(weather_records['site_latitude'])
        )
        longitude_east_deg = (
            given_longitude_east_deg or
            float(weather_records['site_longitude'])
        )
        return latitude_north_deg, longitude_east_deg

    def _get_timezone(
        self,
        latitude_north_deg: float,
        longitude_east_deg: float
    ) -> str:
        """Get timezone for coordinates."""
        timezone_finder = TimezoneFinder()
        potential_timezone_str = timezone_finder.timezone_at(
            lat=latitude_north_deg, lng=longitude_east_deg
        )

        if potential_timezone_str is None:
            raise ValueError(
                f"No timezone found for latitude {latitude_north_deg} "
                f"and longitude {longitude_east_deg}"
            )

        return potential_timezone_str

    def _add_derived_variables(self, weather_data: WeatherData) -> None:
        """Add derived weather variables."""
        # Absolute humidity
        weather_data.add_variable(
            'absolute_humidity',
            'kg water/kg air',
            weather_data.absolute_humidity_kg_per_kg()
        )

        # Precipitation mass
        precipitation_values = [
            p/1000/60 for p in weather_data.get('precipitation')
        ]
        weather_data.add_variable(
            'precipitation_mass', 'kg/m2/s', precipitation_values
        )

        # Snowfall mass
        snowfall_values = [
            p/1000/60 for p in weather_data.get('snowfall')
        ]
        weather_data.add_variable(
            'snowfall_mass', 'kg/m2/s', snowfall_values
        )

        # Wind speed in m/s
        wind_speed_values = [p/3.6 for p in weather_data.get('wind_speed')]
        weather_data.add_variable(
            'wind_speed_m_per_s', 'm/s', wind_speed_values
        )

        # Longwave radiation
        weather_data.add_variable(
            'longwave_radiation_sky',
            'W/m2',
            weather_data.long_wave_radiation_sky()
        )


class WeatherData:
    """Main weather data container with comprehensive functionality."""

    def __init__(
        self,
        location: str,
        latitude_deg_north: float,
        longitude_deg_east: float,
        timestamps: List[int],
        albedo: float = 0.1,
        pollution: float = 0.1,
        timezone_str: Optional[str] = None,
        elevation_service: Optional[ElevationService] = None
    ) -> None:
        """Initialize weather data object."""
        self.location = location
        self.latitude_deg_north = latitude_deg_north
        self.longitude_deg_east = longitude_deg_east
        self.albedo = albedo
        self.pollution = pollution
        self.origin = 'undefined'

        # Initialize services
        self.elevation_service = elevation_service or ElevationService()
        self.timezone_str = timezone_str or self._get_timezone()
        self.elevation = self.elevation_service.get_elevation(
            longitude_deg_east, latitude_deg_north
        )

        # Initialize data storage
        self._timestamps = timestamps
        self._datetimes = []
        self._stringdates = []
        self._variable_data = {}
        self._variable_units = {}

        # Update time representations
        self._update_time_representations()

    def _get_timezone(self) -> str:
        """Get timezone for the location."""
        timezone_finder = TimezoneFinder()
        timezone_str = timezone_finder.timezone_at(
            lat=self.latitude_deg_north, lng=self.longitude_deg_east
        )

        if timezone_str is None:
            raise ValueError(
                f"No timezone found for latitude {self.latitude_deg_north} "
                f"and longitude {self.longitude_deg_east}"
            )

        return timezone_str

    def _update_time_representations(self) -> None:
        """Update datetime and stringdate representations."""
        self._datetimes = [
            epochtimems_to_datetime(t, timezone_str=self.timezone_str)
            for t in self._timestamps
        ]
        self._stringdates = [
            epochtimems_to_stringdate(t, timezone_str=self.timezone_str)
            for t in self._timestamps
        ]

    @property
    def timestamps(self) -> List[int]:
        """Get timestamps."""
        return self._timestamps

    @property
    def datetimes(self) -> List[datetime]:
        """Get datetimes."""
        return self._datetimes

    @property
    def stringdates(self) -> List[str]:
        """Get string dates."""
        return self._stringdates

    @property
    def variable_names(self) -> List[str]:
        """Get variable names."""
        return list(self._variable_data.keys())

    @property
    def variable_names_without_time(self) -> List[str]:
        """Get variable names excluding time variables."""
        return [
            v for v in self._variable_data
            if v not in ('datetime', 'stringdate', 'epochtimems')
        ]

    def add_variable(
        self,
        variable_name: str,
        variable_unit: str,
        values: List[float]
    ) -> None:
        """Add a weather variable."""
        if variable_name in ('epochtimems', 'stringdate', 'datetime'):
            raise ValueError(
                f'{variable_name} cannot be added directly: '
                'use timestamps instead'
            )

        self._variable_units[variable_name] = variable_unit
        self._variable_data[variable_name] = values

    def remove_variable(self, variable_name: str) -> bool:
        """Remove a weather variable."""
        if variable_name in self._variable_data:
            del self._variable_data[variable_name]
            del self._variable_units[variable_name]
            return True
        return False

    def get(self, variable_name: str) -> List[float]:
        """Get values for a variable."""
        if variable_name == 'stringdate':
            return self._stringdates
        elif variable_name == 'datetime':
            return self._datetimes
        elif variable_name == 'epochtimems':
            return self._timestamps
        elif variable_name in self._variable_data:
            return self._variable_data[variable_name]
        else:
            raise ValueError(f'Unknown variable: {variable_name}')

    def units(self, variable_name: Optional[str] = None) -> Union[str, Dict[str, str]]:
        """Get units for variable(s)."""
        if variable_name is None:
            return self._variable_units
        return self._variable_units.get(variable_name, '')

    def __len__(self) -> int:
        """Get number of data points."""
        return len(self._timestamps)

    def __contains__(self, variable_name: str) -> bool:
        """Check if variable exists."""
        return variable_name in self._variable_data

    def __str__(self) -> str:
        """String representation."""
        string = (f"site is {self.location} "
                  f"(lat:{self.latitude_deg_north},lon:{self.longitude_deg_east}) ")

        if self._timestamps:
            string += (f"with data from {self._stringdates[0]} to "
                       f"{self._stringdates[-1]}\nweather variables are:\n")
        else:
            string += "without data loaded yet\nweather variables are:\n"

        for v in self._variable_data:
            string += f'- {v} ({self._variable_units[v]})\n'

        return string

    def excerpt(
        self,
        from_stringdate: str,
        to_stringdate: str
    ) -> WeatherData:
        """Create excerpt of weather data for date range.
        The format of the date is dd/mm/yyyy"""
        from_epochtimems = stringdate_to_epochtimems(
            from_stringdate + ' 0:00:00',
            timezone_str=self.timezone_str
        )
        to_epochtimems = stringdate_to_epochtimems(
            to_stringdate + ' 23:00:00',
            timezone_str=self.timezone_str
        )

        # Validate date range
        if from_epochtimems < self._timestamps[0]:
            raise ValueError(
                f'From date ({from_stringdate}) is before available data'
            )
        if to_epochtimems > self._timestamps[-1]:
            raise ValueError(
                f'To date ({to_stringdate}) is after available data'
            )

        # Find indices
        indices = []
        excerpt_timestamps = []
        for i, timestamp in enumerate(self._timestamps):
            if from_epochtimems <= timestamp <= to_epochtimems:
                indices.append(i)
                excerpt_timestamps.append(timestamp)

        # Create excerpt
        excerpt_data = WeatherData(
            location=self.location,
            latitude_deg_north=self.latitude_deg_north,
            longitude_deg_east=self.longitude_deg_east,
            timestamps=excerpt_timestamps,
            albedo=self.albedo,
            pollution=self.pollution,
            timezone_str=self.timezone_str,
            elevation_service=self.elevation_service
        )

        # Copy variables
        for variable_name in self._variable_data:
            excerpt_values = [
                self._variable_data[variable_name][i] for i in indices
            ]
            excerpt_data.add_variable(
                variable_name,
                self._variable_units[variable_name],
                excerpt_values
            )

        excerpt_data.origin = self.origin
        return excerpt_data

    def excerpt_year(self, year: int) -> WeatherData:
        """Create excerpt for a specific year."""
        return self.excerpt(f'1/1/{year}', f'31/12/{year}')

    def absolute_humidity_kg_per_kg(self) -> List[float]:
        """Calculate absolute humidity in kg/kg."""
        temperatures_deg = self.get('temperature')
        relative_humidities_percent = self.get('humidity')
        atmospheric_pressures_hPa = self.get('pressure')

        absolute_humidities = []
        for i in range(len(temperatures_deg)):
            humidity = HumidityCalculator.absolute_humidity_kg_per_kg(
                temperatures_deg[i],
                relative_humidities_percent[i],
                atmospheric_pressures_hPa[i]
            )
            absolute_humidities.append(humidity)

        return absolute_humidities

    def long_wave_radiation_sky(self) -> List[float]:
        """Calculate long wave radiation from sky."""
        dew_point_temperatures_deg = self.get('dew_point_temperature')
        ground_temperatures_deg = self.get('temperature')
        cloudiness_percent = self.get('cloudiness')

        long_wave_radiation = []
        for i in range(len(dew_point_temperatures_deg)):
            E_clear_W_per_m2 = (
                0.711 + 0.56 * (dew_point_temperatures_deg[i]/100) +
                0.73 * (dew_point_temperatures_deg[i]/100)**2
            )
            E_cloud_W_m2 = 0.96 * Stefan_Boltzmann * (
                ground_temperatures_deg[i] + 273.15 - 5
            )**4

            radiation = (
                (1 - cloudiness_percent[i]/100) * E_clear_W_per_m2 +
                cloudiness_percent[i]/100 * E_cloud_W_m2
            )
            long_wave_radiation.append(radiation)

        return long_wave_radiation

    def surface_out_radiative_exchange(
        self,
        slope_deg: float,
        surface_temperature_deg: List[float],
        ground_temperature_deg: List[float],
        surface_m2: float = 1
    ) -> Tuple[List[float], List[float]]:
        """Calculate surface radiative exchange."""
        dew_point_temperatures_deg = self.get('dew_point_temperature')
        outdoor_temperatures_deg = self.get('temperature')
        cloudiness_percent = self.get('cloudiness')
        beta_deg = (slope_deg - 180) / 180 * pi

        phis_surface_sky = []
        phis_surface_ground = []

        for i in range(len(self._timestamps)):
            wall_emissivity_W_per_m2 = 0.96 * Stefan_Boltzmann * (
                surface_temperature_deg[i] + 273.15
            )**4
            ground_irradiance_W_per_m2 = 0.96 * Stefan_Boltzmann * (
                ground_temperature_deg[i] + 273.15
            )**4

            clear_sky_irradiance_W_per_m2 = (
                0.711 + 0.56 * dew_point_temperatures_deg[i]/100 +
                0.73 * (dew_point_temperatures_deg[i]/100)**2
            )
            cloud_irradiance_W_per_m2 = 0.96 * Stefan_Boltzmann * (
                outdoor_temperatures_deg[i] + 273.15 - 5
            )**4

            sky_irradiance_W_per_m2 = (
                (1 - cloudiness_percent[i]/100) * clear_sky_irradiance_W_per_m2 +
                cloudiness_percent[i]/100 * cloud_irradiance_W_per_m2
            )

            phis_surface_ground.append(
                (wall_emissivity_W_per_m2 - ground_irradiance_W_per_m2) *
                (1 - cos(beta_deg))/2 * surface_m2
            )
            phis_surface_sky.append(
                (wall_emissivity_W_per_m2 - sky_irradiance_W_per_m2) *
                (1 + cos(beta_deg))/2 * surface_m2
            )

        return phis_surface_sky, phis_surface_ground

    def day_degrees(
        self,
        temperature_reference: float = 18,
        heat: bool = True
    ) -> Tuple[List[str], List[float], List[float], List[float], List[float]]:
        """Calculate heating or cooling day degrees."""
        temperatures = self.get('temperature')
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        dd_months = [0] * 12
        day_stringdate_days = []
        average_temperature_days = []
        min_temperature_days = []
        max_temperature_days = []
        day_degrees = []
        day_temperature = []
        current_day = self._datetimes[0].day

        for i, dt in enumerate(self._datetimes):
            if current_day == dt.day:
                day_temperature.append(temperatures[i])
            else:
                day_stringdate_days.append(
                    self._stringdates[i-1].split(' ')[0])
                average_day_temperature = sum(
                    day_temperature) / len(day_temperature)
                average_temperature_days.append(average_day_temperature)
                min_temperature_days.append(min(day_temperature))
                max_temperature_days.append(max(day_temperature))

                hdd = 0
                if heat and average_day_temperature < temperature_reference:
                    hdd = temperature_reference - average_day_temperature
                elif not heat and average_day_temperature > temperature_reference:
                    hdd = average_day_temperature - temperature_reference

                day_degrees.append(hdd)
                dd_months[dt.month - 1] += hdd
                day_temperature = []

            current_day = dt.day

        # Print monthly summary
        for i, month in enumerate(month_names):
            print(f'day degrees {month}: {dd_months[i]}')

        return (day_stringdate_days, average_temperature_days,
                min_temperature_days, max_temperature_days, day_degrees)

    def plot(self) -> None:
        """Plot weather data."""
        TimeSeriesPlotter(
            self._variable_data, self._datetimes, self._variable_units
        )


class WeatherDataManager:
    """High-level manager for weather data operations."""

    def __init__(self) -> None:
        """Initialize the weather data manager."""
        self.builder = WeatherDataBuilder()
        self.elevation_service = ElevationService()

    def get_weather_data(
        self,
        location: str,
        albedo: float = 0.1,
        pollution: float = 0.1,
        latitude_deg_north: Optional[float] = None,
        longitude_deg_east: Optional[float] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> WeatherData:
        """Get weather data for a location."""
        return self.builder.build(
            location=location,
            albedo=albedo,
            pollution=pollution,
            given_latitude_north_deg=latitude_deg_north,
            given_longitude_east_deg=longitude_deg_east,
            from_requested_stringdate=from_date,
            to_requested_stringdate=to_date
        )

    def list_available_weather_files(self) -> List[str]:
        """List available weather files."""
        data_folder = FilePathBuilder().get_data_folder()
        json_filenames = glob.glob(data_folder + '*.json')
        return [
            filename for filename in json_filenames
            if not filename.endswith('localizations.json')
        ]


# Convenience functions for backward compatibility
def absolute_humidity_kg_per_m3(
    temperature_deg: float,
    relative_humidity_percent: float
) -> float:
    """Calculate absolute humidity in kg/m³."""
    return HumidityCalculator.absolute_humidity_kg_per_m3(
        temperature_deg, relative_humidity_percent
    )


def absolute_humidity_kg_per_kg(
    temperature_deg: float,
    relative_humidity_percent: float,
    atmospheric_pressures_hPa: float = 1013.25
) -> float:
    """Calculate absolute humidity in kg/kg."""
    return HumidityCalculator.absolute_humidity_kg_per_kg(
        temperature_deg, relative_humidity_percent, atmospheric_pressures_hPa
    )


def relative_humidity(
    temperature_deg: float,
    absolute_humidity_kg_per_m3: float
) -> float:
    """Calculate relative humidity from absolute humidity."""
    return HumidityCalculator.relative_humidity(
        temperature_deg, absolute_humidity_kg_per_m3
    )


if __name__ == '__main__':
    # Example usage
    location = 'Cayenne'
    latitude_deg_north = 4.924435336591809
    longitude_deg_east = -52.31276008988111

    manager = WeatherDataManager()
    weather_data = manager.get_weather_data(
        location=location,
        latitude_deg_north=latitude_deg_north,
        longitude_deg_east=longitude_deg_east
    )

    print(weather_data)
