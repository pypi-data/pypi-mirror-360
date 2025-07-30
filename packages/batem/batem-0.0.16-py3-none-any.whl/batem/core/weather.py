"""This is a reader for openweathermap (https://openweathermap.org) historical weather files.

Author: stephane.ploix@grenoble-inp.fr
"""
from __future__ import annotations
import json
import requests
from scipy.constants import Stefan_Boltzmann
import configparser
import os
import sys
import glob
import pytz
from datetime import datetime
from math import exp, cos, pi
from batem.core.timemg import REGULAR_DATETIME_FORMAT, datetime_to_epochtimems, datetime_with_day_delta, epochtimems_to_datetime, epochtimems_to_stringdate, stringdate_to_openmeteo_date, stringdate_to_epochtimems
from batem.core.utils import FilePathChecker, TimeSeriesPlotter, FilePathBuilder
from timezonefinder import TimezoneFinder
from typing import Optional

from batem.core.weather_refactored import WeatherDataManager

config = configparser.ConfigParser()
config.read('setup.ini')


def absolute_humidity_kg_per_m3(temperature_deg: float, relative_humidity_percent: float) -> float:
    Rv_J_per_kg_K = 461.5  # J/kg.K
    saturation_vapour_pressure_Pa: float = 611.213 * \
        exp(17.5043 * temperature_deg / (temperature_deg + 241.2)
            )  # empirical formula of Magnus-Tetens
    partial_vapour_pressure_Pa: float = saturation_vapour_pressure_Pa * \
        relative_humidity_percent / 100
    return partial_vapour_pressure_Pa / (Rv_J_per_kg_K * (temperature_deg + 273.15))


def absolute_humidity_kg_per_kg(temperature_deg: float, relative_humidity_percent: float, atmospheric_pressures_hPa: float = 1013.25) -> float:
    Rs_J_per_kg_K = 287.06
    density_kg_per_m3 = (atmospheric_pressures_hPa * 100 - 2.30617*relative_humidity_percent*exp(
        17.5043*temperature_deg/(241.2+temperature_deg)))/Rs_J_per_kg_K/(temperature_deg + 273.15)
    return absolute_humidity_kg_per_m3(temperature_deg, relative_humidity_percent) / density_kg_per_m3


def relative_humidity(temperature_deg, absolute_humidity_kg_per_m3) -> float:
    Rv_J_per_kg_K = 461.5  # J/kg.K
    saturation_vapour_pressure_Pa: float = 611.213 * \
        exp(17.5043 * temperature_deg / (temperature_deg + 241.2)
            )  # empirical formula of Magnus-Tetens
    partial_vapour_pressure_Pa: float = absolute_humidity_kg_per_m3 * \
        Rv_J_per_kg_K * (temperature_deg + 273.15)
    return 100 * partial_vapour_pressure_Pa / saturation_vapour_pressure_Pa


class ElevationRetriever:
    """Class creating or getting elevations from google website corresponding
    to a localization characterized by a longitude and latitude.
    To avoid offline issues with Internet, anytime an elevation is collected,
    it is stored into the localizations.json file in order
    to use it a next time.
    The localizations.json file is stored in the data folder.

    :param json_db_name: name of the file where longitudes,
    latitudes and elevations are saved, defaults to 'localizations.json'
    :type json_db_name: str, optional
    :param data: dictionary containing the longitudes,
    latitudes and elevations, defaults to an empty dictionary
    :type data: dict[str, float], optional
    """

    def __init__(self) -> None:
        """Initializer of the elevation retriever.
        """

        self.json_db_name = FilePathBuilder().get_localizations_file_path()

        if not os.path.isfile(self.json_db_name):
            self.data = dict()
        else:
            with open(self.json_db_name) as json_file:
                self.data: dict[str, float] = json.load(json_file)

    def get(self, longitude_deg_east: float,
            latitude_deg_north: float) -> float:
        """Method returning the complete coordinate with the elevation or
        just the elevation at a given longitude and latitude.

        :param longitude_deg_east: longitude in degree east
        :type longitude_deg_east: float
        :param latitude_deg_north: latitude in degree north
        :type latitude_deg_north: float
        :return: elevation
        :rtype: float
        """
        coordinate = '(%s,%s)' % (longitude_deg_east, latitude_deg_north)
        if coordinate not in self.data:
            elevation = 200
            try:
                elevation = ElevationRetriever._webapi_elevation_meter(
                    longitude_deg_east, latitude_deg_north)
            except Exception:
                elevation = float(input('Enter manually the elevation:'))
            self.data[coordinate] = elevation
            with open(self.json_db_name, 'w') as json_file:
                json.dump(self.data, json_file)
        else:
            elevation: float = self.data[coordinate]
        return elevation

    @staticmethod
    def _webapi_elevation_meter(longitude_deg_east: float,
                                latitude_deg_north: float) -> float:
        """Method searching in local database if the coordinates exists,
        if so it gets the elevation in meters from google
        and add to the database.

        :param latitude_deg_north: north degree latitude
        :type latitude_deg_north: float
        :param longitude_deg_east: east degree longitude
        :type longitude_deg_east: float
        :return: the collected elevation
        :rtype: float
        """

        url = 'https://api.open-elevation.com/api/v1/lookup'

        params = {"locations": [
            {"latitude": latitude_deg_north, "longitude": longitude_deg_east}]}
        response = requests.post(url, json=params)
        try:
            response.raise_for_status()
            for info in response:
                print(info, response)

            data = response.json()
            elevations = [result['elevation'] for result in data['results']]
            return elevations[0]
        except requests.HTTPError as error:
            print(
                "The elevation server does not respond: "
                "horizon mask has to be set manually.", error)
            elevation = int(input('Elevation in m: '))
            return elevation


class WeatherJsonCharacteristicsPrinter:
    """Class printing the characteristics of available weather jsons files
    in the data folder.
    """

    def __init__(self) -> None:
        pass

    def print(self) -> None:
        print("Available weather files:\n")
        for json_filename in self.get_exisiting_json_filenames():
            weather_locations: list[str] = list()
            with open(json_filename) as json_file:
                json_content = json.load(json_file)
                # openmeteo file
                if WeatherFormatChecker().is_open_meteo_file(json_content):

                    location = json_filename.split(
                        '.json')[0].split('/')[-1]
                    weather_locations.append(location)

                    latitude = float(json_content['latitude'])
                    longitude = float(json_content['longitude'])

                    from_stringdate, to_stringdate = \
                        self._parse_dates_to_openmeteo(
                            json_content)

                    self._print_weather_coordinates(
                        location, 'open-meteo',
                        latitude, longitude,
                        from_stringdate, to_stringdate)

                else:  # openweathtermap file
                    locations = \
                        self._get_weather_locations_openweathermap(
                            json_content)
                    weather_locations.extend(locations)

                    latitude = float(json_content[0]['lat'])
                    longitude = float(json_content[0]['lon'])

                    from_stringdate, to_stringdate = \
                        self._parse_dates_to_openweathermap(
                            json_content)

                    for city_name in weather_locations:
                        self._print_weather_coordinates(
                            city_name, 'openweathermap',
                            latitude, longitude,
                            from_stringdate, to_stringdate)

    def _print_weather_coordinates(self, location: str,
                                   weather_format: str,
                                   latitude: float,
                                   longitude: float,
                                   from_stringdate: str,
                                   to_stringdate: str) -> None:
        """Method printing the weather coordinates.
        """
        print('\t- [%s] "%s" latitude,longitude=(%f,%f) from %s to %s' %
              (weather_format, location,
               latitude, longitude,
               from_stringdate, to_stringdate))

    def _parse_dates_to_openmeteo(self, json_content: dict) -> tuple[str, str]:
        """Method parsing the dates from the json content.
        Returns the dates in openmeteo format.
        """

        from_stringdate = epochtimems_to_stringdate(
            json_content['hourly']['epochtimems'][0], date_format='%d/%m/%Y')
        to_stringdate = epochtimems_to_stringdate(
            json_content['hourly']['epochtimems'][-1], date_format='%d/%m/%Y')

        print(from_stringdate, to_stringdate)

        from_openmeteo_string_date = stringdate_to_openmeteo_date(
            from_stringdate)
        to_openmeteo_string_date = stringdate_to_openmeteo_date(
            to_stringdate)

        return from_openmeteo_string_date, to_openmeteo_string_date

    def _parse_dates_to_openweathermap(self,
                                       json_content: dict) -> tuple[str, str]:
        """Method parsing the dates from the json content.
        Returns the dates in openweathermap format.
        """
        from_epochtimems = int(json_content['dt'][0])*1000
        from_stringdate = epochtimems_to_stringdate(from_epochtimems)
        to_epochtimems = int(json_content['dt'][-1])*1000
        to_stringdate = epochtimems_to_stringdate(to_epochtimems)
        return from_stringdate, to_stringdate

    def _get_weather_locations_openweathermap(self,
                                              json_content: dict) -> list[str]:
        """Method returning the list of weather locations
        from the json content of an openweathermap file.

        :param json_content: json content of the file
        :type json_content: dict
        :return: list of weather locations
        :rtype: str
        """
        weather_locations: list[str] = list()
        for i in range(len(json_content)):
            weather_location: str = json_content[i]['city_name']
            if len(weather_locations) == 0 or weather_locations[-1] != weather_location:
                weather_locations.append(weather_location)
        return weather_locations

    def get_exisiting_json_filenames(self) -> list[str]:
        """Method returning the list of existing json filenames in the data folder,
        except the localizations.json file.

        :return: list of existing json filenames
        :rtype: list[str]
        """
        data_folder = FilePathBuilder().get_data_folder()
        json_filenames: list[str] = glob.glob(data_folder + '*.json')
        file_names_with_localizations: list[str] = [
            json_filename for json_filename in json_filenames
            if not json_filename.endswith('localizations.json')]
        return file_names_with_localizations


class WeatherFormatChecker:
    """Class checking the format of a weather json file.
    """

    def __init__(self) -> None:
        pass

    def is_open_meteo_file(self, json_content: dict) -> bool:
        """Method checking if the json content is an open-meteo file.

        :param json_content: json content of the file
        :type json_content: dict
        :return: True if the json content is an open-meteo file, False otherwise
        :rtype: bool
        """
        return 'generationtime_ms' in json_content


AVAILABLE_WEATHER_VARIABLES = [
    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
    "dew_point_2m", "precipitation", "rain",
    "showers", "snowfall", "snow_depth",
    "surface_pressure", "cloud_cover", "cloud_cover_low",
    "cloud_cover_mid", "cloud_cover_high", "wind_speed_10m",
    "wind_direction_10m", "wind_gusts_10m", "soil_temperature_0cm",
    "shortwave_radiation", "direct_radiation", "diffuse_radiation",
    "direct_normal_irradiance", "shortwave_radiation_instant", "direct_radiation_instant",
    "diffuse_radiation_instant", "direct_normal_irradiance_instant", "terrestrial_radiation_instant"
]

EQUIVALENT_OPENMETEO_WEATHER_VARIABLES = {
    'temperature_2m': 'temperature',
    'dew_point_2m': 'dew_point_temperature',
    'wind_speed_10m': 'wind_speed',
    'wind_direction_10m': 'wind_direction_in_deg',
    'apparent_temperature': 'feels_like',
    'relative_humidity_2m': 'humidity',
    'cloud_cover': 'cloudiness',
    'surface_pressure': 'pressure'}


class SiteWeatherDataBuilder:
    """Extract the content of a json openweather data file.

    :param json_filename: openweather data file in json format
    :param from_stringdate: initial date in format DD/MM/YYYY hh:mm:ss
    :param to_stringdate: final date in format DD/MM/YYYY hh:mm:ss
    :return: a tuple containing
        - city file_name
        - latitude in decimal north degree
        - longitude in decimal east degree
        - hourly time data variables as a dictionary with variable file_name as a key
        - units as a dictionary with variable file_name as a key
        - initial date as a string
        - final date as a string
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def create_open_meteoDB(
            file_path: str,
            latitude_deg_north: float,
            longitude_deg_east: float,
            weather_data: list[str] = AVAILABLE_WEATHER_VARIABLES,
            timezone: Optional[pytz.timezone] = None) -> None:

        server_url = 'https://archive-api.open-meteo.com/v1/archive'

        date_time_now = datetime.now(timezone)
        to_openmeteo_string_date = datetime_with_day_delta(
            date_time_now, number_of_days=-7, date_format='%d/%m/%Y')
        from_openmeteo_string_date = stringdate_to_openmeteo_date(
            '1/1/1980')
        to_openmeteo_string_date = stringdate_to_openmeteo_date(
            to_openmeteo_string_date, timezone)

        response = requests.get(
            server_url,
            params={"latitude": latitude_deg_north,
                    "longitude": longitude_deg_east,
                    "start_date": from_openmeteo_string_date,
                    "end_date": to_openmeteo_string_date,
                    "hourly": weather_data},
            headers={'Accept': 'application/json'},
            timeout=300,
            stream=True)

        data = response.json()
        if 'error' in data:
            raise ValueError(data['reason'])

        data['site_latitude'] = latitude_deg_north
        data['site_longitude'] = longitude_deg_east
        data['timezone'] = timezone

        SiteWeatherDataBuilder._remove_extra_times(data)

        SiteWeatherDataBuilder._add_epochtimems(data, timezone)

        del data['hourly']['time']

        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)

    @staticmethod
    def _remove_extra_times(data: dict) -> None:
        number_of_data_to_removed = 0
        for k in range(len(data['hourly']['time'])-1, -1, -1):
            if data['hourly']['temperature_2m'][k] is None:
                number_of_data_to_removed += 1
            else:
                break
        for v in data['hourly']:
            for i in range(number_of_data_to_removed):
                data['hourly'][v].pop(-1)

    @staticmethod
    def _add_epochtimems(data: dict, timezone: pytz.timezone) -> None:
        """Add epochtimems to the data.

        :param data: data to add epochtimems to
        :type data: dict
        """
        epochtimems_list: list[int] = list()
        data['hourly']['epochtimems'] = epochtimems_list
        for openmeteo_stringtime in data['hourly']['time']:
            epochtimems = stringdate_to_epochtimems(
                openmeteo_stringtime,
                date_format='%Y-%m-%dT%H:%M',
                timezone_str=timezone)
            data['hourly']['epochtimems'].append(epochtimems)

    def build(
            self, location: str,
            albedo: float = .1,
            pollution: float = 0.1,
            given_latitude_north_deg: Optional[float] = None,
            given_longitude_east_deg: Optional[float] = None,
            from_requested_stringdate: Optional[str] = None,
            to_requested_stringdate: Optional[str] = None) -> SiteWeatherData:
        """Read data from an openweather map json file.
        The user should either provide the location or the latitude and longitude, or both.
        If the location is provided, the latitude and longitude are retrieved from the localizations.json file.
        If the latitude and longitude are provided, the location is retrieved from the localizations.json file.
        If none of the above is provided, the method will raise an error.

        :param json_filename: name of the openweathermap historical weather file
        :type json_filename: str
        :param from_stringdate: starting date for the data collection, defaults to None
        :type from_stringdate: str: dd/mm/YY, optional
        :param to_stringdate: ending date for the data collection, defaults to None
        :type to_stringdate: str: dd/mm/YY, optional
        :param altitude: sea level in meter of the site location, defaults to 290
        :type altitude: float, optional
        :param albedo: albedo at current site location (see https://en.wikipedia.org/wiki/Albedo), defaults to .1
        :type albedo: float, optional
        :param pollution: turbidity coefficient to model the air pollution at the current site location, defaults to 0.1
        :type pollution: float, optional
        :param location: name of the location to select, if None, the first location name is selected
        :type location: str, defaults to None
        :param solar_model: True to use the solar model, False to use the weather data, defaults to False
        :type solar_model: bool, optional
        """
        check_location_and_latitude_longitude(
            location, given_latitude_north_deg, given_longitude_east_deg)

        file_path = self._get_weather_file_path(
            location, given_latitude_north_deg, given_longitude_east_deg)

        with open(file_path) as json_file:
            weather_records = json.load(json_file)

            if 'error' in weather_records:
                msg = f'Delete file {file_path} and try because {weather_records["reason"]}'
                raise ValueError(msg)

            elif WeatherFormatChecker().is_open_meteo_file(weather_records):

                print('Open-Meteo format selected', file=sys.stderr)

                latitude_north_deg, longitude_east_deg = \
                    self._get_latitude_and_longitude(
                        given_latitude_north_deg, given_longitude_east_deg, weather_records)

                self.timezone_str = self._get_timezone(
                    latitude_north_deg, longitude_east_deg)

                self.requested_from_epochtimems, self.requested_to_epochtimems = \
                    self.get_from_stringdate_to_stringdate(
                        from_requested_stringdate,
                        to_requested_stringdate,
                        weather_records['hourly']['epochtimems'])

                self._check_from_epochtimems_to_epochtimems(
                    self.requested_from_epochtimems,
                    self.requested_to_epochtimems,
                    weather_records['hourly']['epochtimems'])

                weather_variables_values, weather_variables_units, weather_epochtimems = \
                    self._parse_weather_records(weather_records)

                site_weather_data = SiteWeatherData(
                    location=location,
                    latitude_deg_north=latitude_north_deg,
                    longitude_deg_east=longitude_east_deg,
                    albedo=albedo,
                    pollution=pollution,
                    weather_epoch_timems=weather_epochtimems,
                    _direct_call=False)

                for var_name in weather_variables_values:
                    site_weather_data.add_variable(
                        var_name,
                        weather_variables_units[var_name],
                        weather_variables_values[var_name])

                # if 'humidity_mass' in self.site_weather_data.variable_names:
                site_weather_data.add_variable(
                    'absolute_humidity', 'kg water/kg air', site_weather_data.absolute_humidity_kg_per_kg())
                site_weather_data.add_variable(
                    'precipitation_mass', 'kg/m2/s', [p/1000/60 for p in site_weather_data.get('precipitation')])
                site_weather_data.add_variable(
                    'snowfall_mass', 'kg/m2/s', [p/1000/60 for p in site_weather_data.get('snowfall')])
                site_weather_data.add_variable(
                    'wind_speed_m_per_s', 'm/s', [p/3.6 for p in site_weather_data.get('wind_speed')])
                site_weather_data.add_variable(
                    'longwave_radiation_sky', 'W/m2', site_weather_data.long_wave_radiation_sky())

                site_weather_data.origin = "openmeteo"

        return site_weather_data

    def _in_time_range(self, epochtimems: int) -> bool:
        """Check if the epochtimems is in the time range.
        """
        return self.requested_from_epochtimems <= epochtimems <= self.requested_to_epochtimems

    def _parse_weather_records(self,
                               weather_records: dict
                               ) -> tuple[dict[str,
                                               list[float]],
                                          dict[str, str],
                                          list[int]]:
        """Parse the weather records 
        and build the weather_variables_values
        and weather_variables_units dictionaries.

        :param weather_records: weather records in the openmeteo format
        :type weather_records: dict
        """

        weather_variables_values: dict[str, list[float]] = dict()
        weather_variables_units: dict[str, str] = {}
        weather_epochtimems: list[int] = list()
        openmeteo_epochtimems = weather_records['hourly']['epochtimems']
        openmeteo_variable_names = list(
            weather_records['hourly'].keys())
        openmeteo_variable_names.remove('epochtimems')

        for k in range(len(openmeteo_epochtimems)):
            if not self._in_time_range(openmeteo_epochtimems[k]):
                continue

            if len(weather_epochtimems) == 0:  # first data read
                weather_epochtimems.append(
                    openmeteo_epochtimems[k])
                self._parse_variables(
                    openmeteo_variable_names,
                    weather_variables_values,
                    weather_variables_units,
                    weather_records,
                    k)
            else:
                delta_ms: float = (
                    openmeteo_epochtimems[k] - openmeteo_epochtimems[k-1])
                if delta_ms > 0:
                    shift_1hr_ms = 3600 * 1000
                    if delta_ms == 2 * shift_1hr_ms:  # autumn time shift
                        weather_epochtimems.append(
                            openmeteo_epochtimems[k-1] +
                            shift_1hr_ms)
                    else:
                        weather_epochtimems.append(
                            openmeteo_epochtimems[k])
                    self._duplicate_time_change_record(
                        openmeteo_variable_names,
                        weather_variables_values,
                        weather_records,
                        k)
        return weather_variables_values, weather_variables_units, weather_epochtimems

    def _parse_variables(self,
                         openmeteo_variable_names: list[str],
                         weather_variables_values: dict[str, list[float]],
                         weather_variables_units: dict[str, str],
                         weather_records: dict,
                         k: int
                         ) -> None:
        """Parse the variables from the weather records.
        The variables are parsed from the weather records
        and added to the weather_variables_values
        and weather_variables_units dictionaries.
        The openmeteo_variable_names are the names of the variables
        in the openmeteo format.
        The weather_variables_values are the values of the variables
        in the weather format.
        The weather_variables_units are the units of the variables
        in the weather format.
        The weather_records are the weather records in the openmeteo format.

        :param openmeteo_variable_names: names of the variables in the openmeteo format
        :type openmeteo_variable_names: list[str]
        """
        for variable_name in openmeteo_variable_names:

            weather_variable_name = (
                EQUIVALENT_OPENMETEO_WEATHER_VARIABLES[variable_name]
                if variable_name in EQUIVALENT_OPENMETEO_WEATHER_VARIABLES
                else variable_name)

            weather_variables_units[weather_variable_name] = weather_records[
                'hourly_units'][variable_name]
            weather_variables_values[weather_variable_name] = [
                weather_records['hourly'][variable_name][k]]

    def _duplicate_time_change_record(
            self, openmeteo_variable_names: list[str],
            weather_variables_values: dict[str, list[float]],
            weather_records: dict,
            k: int) -> None:
        """Dublicate the time change record.
        """
        for var_name in openmeteo_variable_names:
            weather_variable_name = (
                EQUIVALENT_OPENMETEO_WEATHER_VARIABLES[
                    var_name] if var_name in EQUIVALENT_OPENMETEO_WEATHER_VARIABLES
                else var_name)
            weather_variables_values[weather_variable_name].append(
                weather_records['hourly'][var_name][k-1])

    def _get_weather_file_path(
            self, location: str,
            given_latitude_north_deg: Optional[float],
            given_longitude_east_deg: Optional[float]) -> str:
        """Get the weather file path.
        If the weather file does not exist, it is created.
        If the weather file exists, it is not created.
        Eventually, the file path is returned.

        :param location: location of the weather file
        :type location: str
        :param given_latitude_north_deg: latitude of the weather file
        """
        file_path = FilePathBuilder().get_weather_file_path(location)
        if not FilePathChecker().is_file_exists(file_path):
            if given_latitude_north_deg is None or given_longitude_east_deg is None:
                raise ValueError(
                    "Latitude and longitude must be provided to create the weather file")
            print(f"Weather file {file_path} not found, creating it")
            SiteWeatherDataBuilder.create_open_meteoDB(
                file_path, given_latitude_north_deg, given_longitude_east_deg)
            print(f"Weather file {file_path} created")
        else:
            print(f"Weather file {file_path} already exists")
        return file_path

    def _get_latitude_and_longitude(self,
                                    given_latitude_north_deg: Optional[float],
                                    given_longitude_east_deg: Optional[float],
                                    weather_records: dict) -> tuple[float, float]:
        """Get the latitude and longitude.
        If the latitude and longitude are provided, they are returned.
        If the latitude and longitude are not provided,
        they are retrieved from the weather records.

        :param given_latitude_north_deg: latitude of the weather file
        :type given_latitude_north_deg: Optional[float]
        :param given_longitude_east_deg: longitude of the weather file
        :type given_longitude_east_deg: Optional[float]
        """
        if given_latitude_north_deg is None:
            latitude_north_deg = float(
                weather_records['site_latitude'])
        else:
            latitude_north_deg = given_latitude_north_deg
        if given_longitude_east_deg is None:
            longitude_east_deg = float(
                weather_records['site_longitude'])
        else:
            longitude_east_deg = given_longitude_east_deg
        return latitude_north_deg, longitude_east_deg

    def _get_timezone(self, latitude_north_deg: float,
                      longitude_east_deg: float) -> str:
        """Get the timezone based on the latitude and longitude.
        If the timezone is not found, an error is raised.

        :param latitude_north_deg: latitude of the weather file
        :type latitude_north_deg: float
        :param longitude_east_deg: longitude of the weather file
        :type longitude_east_deg: float
        """
        timezone_finder = TimezoneFinder()

        potential_timezone_str = timezone_finder.timezone_at(
            lat=latitude_north_deg, lng=longitude_east_deg)
        if potential_timezone_str is None:
            raise ValueError(
                f"No timezone found for latitude {latitude_north_deg} and longitude {longitude_east_deg}")
        return potential_timezone_str

    def get_from_stringdate_to_stringdate(
        self, given_from_stringdate: Optional[str],
        given_to_stringdate: Optional[str],
        openmeteo_epochtimems: list[float]
    ) -> tuple[int, int]:
        """Get the from and to epochtimems based on the
        from and to stringdates.
        If the from and to stringdates are not provided, the from
        and to epochtimems are the first and last epochtimems
        of the openmeteo_epochtimems list.
        Otherwise, the from and to epochtimems are the epochtimems 
        corresponding to the from and to stringdates.

        :param given_from_stringdate: from stringdate
        :type given_from_stringdate: Optional[str]
        :param given_to_stringdate: to stringdate
        :type given_to_stringdate: Optional[str]
        :param openmeteo_epochtimems: list of epochtimems
        """
        if given_from_stringdate is None:
            from_epochtimems = int(openmeteo_epochtimems[0])
        else:
            from_epochtimems = stringdate_to_epochtimems(
                given_from_stringdate + ' 0:00:00',
                date_format=REGULAR_DATETIME_FORMAT,
                timezone_str=self.timezone_str)
        if given_to_stringdate is None:
            to_epochtimems = int(openmeteo_epochtimems[-1])
        else:
            to_epochtimems = stringdate_to_epochtimems(
                given_to_stringdate + ' 23:00:00',
                date_format=REGULAR_DATETIME_FORMAT,
                timezone_str=self.timezone_str)

        return from_epochtimems, to_epochtimems

    def _check_from_epochtimems_to_epochtimems(
            self, from_epochtimems: int,
            to_epochtimems: int,
            openmeteo_epochtimems: list[float]) -> None:
        """Check if the from and to epochtimems are valid.
        If the to epochtimems is less than the from epochtimems,
        an error is raised.
        If the from epochtimems is greater than the last epochtimems,
        an error is raised.

        :param from_epochtimems: from epochtimems
        :type from_epochtimems: int
        :param to_epochtimems: to epochtimems
        """
        first_epochtimems = int(openmeteo_epochtimems[0])
        last_epochtimems = int(openmeteo_epochtimems[-1])
        if from_epochtimems < first_epochtimems:
            msg = (f"From epochtimems {from_epochtimems} is less than the first epochtimems {first_epochtimems}"
                   f"in the openmeteo_epochtimems list")
            raise ValueError(msg)
        if to_epochtimems > last_epochtimems:
            msg = (f"To epochtimems {to_epochtimems} is greater than the last epochtimems {last_epochtimems}"
                   f"in the openmeteo_epochtimems list")
            raise ValueError(msg)


def check_location_and_latitude_longitude(location: Optional[str],
                                          latitude_north_deg: Optional[float],
                                          longitude_east_deg: Optional[float]
                                          ) -> None:
    """Check if the location and the latitude and longitude are provided.
    """
    if location is None and (latitude_north_deg is None
                             or longitude_east_deg is None):
        raise ValueError(
            "Either the location or the latitude and longitude must be provided")


class SiteWeatherData:
    """Gathers all the data related to a site dealing with location, albedo, pollution, timezone but also weather time data coming from an openweather json file."""

    def __init__(self, location: str, latitude_deg_north: float,
                 longitude_deg_east: float,
                 weather_epoch_timems: list[int],
                 albedo: float = .1,
                 pollution: float = .1,
                 timezone_str: Optional[str] = None,
                 _direct_call: bool = True) -> None:
        """Create object containing data dealing with a specific site,
        including the weather data.

        :param location: name of the site
        :type location: str
        :param latitude_deg_north: latitude in East degree
        :type latitude_deg_north: float
        :param longitude_deg_east: longitude in North degree
        :type longitude_deg_east: float
        :param variable_names: name of the weather variables
        :type variable_names: tuple[str]
        :param variable_units: units of the weather variables
        :type variable_units: tuple[str]
        :param altitude: altitude of the site in meter from sea level, defaults to 290
        :type altitude: float, optional
        :param albedo: albedo of the site, defaults to .1
        :type albedo: float, optional
        :param timezone: timezone of the site, defaults to 'Europe/Paris'
        :type timezone: str, optional
        :param pollution: pollution coefficient between 0 and 1, defaults to 0.1
        :type pollution: float, optional
        :param _direct_call: internal use to prohibit direct calls of the initializer, defaults to True
        :type _direct_call: bool, optional
        :raises PermissionError: raised in case of direct use, the object must be created by OpenWeatherMapJsonReader
        """
        if _direct_call:
            raise PermissionError('SiteWeatherData cannot be called directly')
        self.origin: str = 'undefined'
        self.location: str = location
        self.latitude_deg_north: float = latitude_deg_north
        self.longitude_deg_east: float = longitude_deg_east
        if timezone_str is None:
            timezone_finder = TimezoneFinder()
            self.timezone_str = timezone_finder.timezone_at(
                lat=latitude_deg_north, lng=longitude_deg_east)
        else:
            self.timezone_str = timezone_str

        self.elevation = ElevationRetriever().get(
            latitude_deg_north, longitude_deg_east)
        self.albedo = albedo
        self.pollution = pollution
        self._epochtimems = list()
        self._datetimes = list()
        self._stringdates = list()
        self._variable_data = dict()
        self.variable_units = dict()

        self.epochtimems = weather_epoch_timems

    def remove(self, variable_name: str) -> bool:
        if variable_name in self._variable_data:
            del self._variable_data[variable_name]
            del self.variable_units[variable_name]

    def __contains__(self, variable_name: str) -> bool:
        return variable_name in self._variable_data

    @property
    def variable_names(self) -> list[str]:
        return list(self._variable_data.keys())

    @property
    def variable_names_without_time(self) -> list[str]:
        variable_names_without_time = list()
        for v in self._variable_data:
            if v not in ('datetime', 'stringdate', 'epochtimems'):
                variable_names_without_time.append(v)
        return variable_names_without_time

    def check(self) -> None:
        length = None
        if len(self._epochtimems) > 0:
            length = len(self._epochtimems)
        for variable in self._variable_data:
            if length is not None:
                if len(self._variable_data[variable]) != length:
                    raise ValueError('Variable %s has not a correct length (%i instead of %i)' % (
                        variable, len(self._variable_data[variable]), length))
            else:
                length = len(self._variable_data[variable])

    def __len__(self) -> int:
        return len(self._epochtimems)

    def excerpt(self, from_stringdate: str, to_stringdate: str) -> "SiteWeatherData":
        excerpt_site_weather_data = SiteWeatherData(self.location, self.latitude_deg_north, self.longitude_deg_east,
                                                    # self.variable_names, self._variable_units,
                                                    self.albedo, self.pollution, self.timezone_str,  _direct_call=False)
        excerpt_site_weather_data.origin = self.origin
        indices: list[int] = list()
        from_epochtimems: float = stringdate_to_epochtimems(
            from_stringdate + ' 0:00:00', timezone_str=self.timezone_str)
        if from_epochtimems < self._epochtimems[0]:
            raise ValueError(
                'to stringdate (%s: 0:00:00) is greater than the one of the existing dataset')
        to_epochtimems: float = stringdate_to_epochtimems(
            to_stringdate + ' 23:00:00', timezone_str=self.timezone_str)
        if to_epochtimems > self._epochtimems[-1]:
            raise ValueError(
                'from stringdate (%s: 0:00:00) is lower than the one of the existing dataset')

        excerpt_epochtimems = list()
        for i, t in enumerate(self._epochtimems):
            if from_epochtimems <= t <= to_epochtimems:
                indices.append(i)
                excerpt_epochtimems.append(t)
        excerpt_site_weather_data.epochtimems = excerpt_epochtimems
        for variable_name in self._variable_data:
            excerpt_site_weather_data.add_variable(variable_name, self.variable_units[variable_name], [
                                                   self._variable_data[variable_name][i] for i in indices])
        return excerpt_site_weather_data

    def excerpt_year(self, year: int) -> "SiteWeatherData":
        return self.excerpt('1/1/%i' % year, '31/12/%i' % year)

    def __str__(self) -> str:
        string: str = "site is %s (lat:%f,lon:%f) " % (
            self.location, self.latitude_deg_north, self.longitude_deg_east)
        if self._epochtimems is not None:
            string += "with data from %s to %s\nweather variables are:\n" % (epochtimems_to_stringdate(
                self._epochtimems[0]), epochtimems_to_stringdate(self._epochtimems[-1]))
        else:
            string += "without data loaded yet\nweather variables are:\n"
        for v in self._variable_data:
            string += '- %s (%s)\n' % (v, self.variable_units[v])
        return string

    def units(self, variable_name: str = None):
        """Return the unit of a variable.

        :param variable_name: file_name of the variable
        :type variable_name: str
        :return: unit of this variable
        :rtype: str
        """
        if variable_name is None:
            return self.variable_units
        return self.variable_units[variable_name]

    @property
    def from_stringdate(self) -> str:
        """Return the starting data of the data collection.

        :return: first date where data are available in epoch time (ms)
        :rtype: int
        """
        return self._stringdates[0]

    @property
    def to_stringdate(self):
        """Return the ending date of the data collection.

        :return: last date where data are available
        :rtype: str
        """
        return self._stringdates[-1]

    @property
    def epochtimems(self) -> list[int]:
        return self._epochtimems

    @property
    def datetimes(self) -> list[datetime]:
        return self._datetimes

    @property
    def stringdates(self) -> list[str]:
        return self._stringdates

    @epochtimems.setter
    def epochtimems(self, the_epochtimems: list[int]):
        if type(the_epochtimems) is not list and type(the_epochtimems) is not tuple:
            raise ValueError("epochtimems must be a list or a tuple")
        self._epochtimems: list[int] = the_epochtimems
        self._stringdates: list[str] = [epochtimems_to_stringdate(
            t, timezone_str=self.timezone_str) for t in self._epochtimems]
        self._datetimes: list[datetime] = [epochtimems_to_datetime(
            t, timezone_str=self.timezone_str) for t in self._epochtimems]

    @datetimes.setter
    def datetimes(self, the_datetimes):
        if type(the_datetimes) is not list and type(the_datetimes) is not tuple:
            raise ValueError("datetimes must be a list or a tuple")
        self._datetimes: list[datetime] = the_datetimes
        self._epochtimems: list[float] = [
            datetime_to_epochtimems(dt) for dt in the_datetimes]
        self._datetimes: list[datetime] = [epochtimems_to_datetime(
            t, timezone_str=self.timezone_str) for t in self._epochtimems]

    def add_variable(self, variable_name: str, variable_unit: str, values: list[float | datetime]):
        if variable_name == 'epochtimems':
            self._epochtimems = [
                v - self.timezone_str / 3600000 for v in values]
        elif variable_name == 'stringdate':
            raise ValueError(
                'string dates cannot be added directly: add epochtimems or datetimes instead')
        elif variable_name == 'datetime':
            self._epochtimems = [v.tz_convert(
                self.timezone_str) for v in values]
        else:
            self.variable_units[variable_name] = variable_unit
            self._variable_data[variable_name] = values

    def series(self, variable_name: str = None) -> list[float] | dict[str, list[float]]:
        if variable_name is not None:
            return self.get(variable_name)
        else:
            variable_values = dict()
            for variable_name in self.variable_names:
                if variable_name not in ('datetime', 'epochtimems', 'stringdate'):
                    variable_values[variable_name] = self.get(variable_name)
            return variable_values

    def __call__(self, variable_name: str) -> list[float | datetime.datetime]:
        return self.get(variable_name)

    def get(self, variable_name: str) -> list[float | datetime.datetime]:
        """Return the data collection related to one variable.

        :param variable_name: variable file_name
        :type variable_name: str
        :return: list of float or str values corresponding to common dates for the specified variable
        :rtype: list[float or str]
        """
        if variable_name == 'stringdate':
            return self._stringdates
        elif variable_name == 'datetime':
            return self._datetimes
        elif variable_name == 'epochtimems':
            return self._epochtimems
        elif variable_name in self._variable_data:
            return self._variable_data[variable_name]
        else:
            print(self)
            raise ValueError('Unknown variable: %s' % variable_name)

    def long_wave_radiation_sky(self) -> list[float]:
        """Compute the long wave radiation from the sky.

        :return: list of long wave radiation from the sky in W/m2
        :rtype: list[float]
        """
        _long_wave_radiation_sky_W_per_m2: list[float] = list()
        dew_point_temperatures_deg: list[float] = self.get(
            'dew_point_temperature')
        ground_temperatures_deg: list[float] = self.get('temperature')
        cloudiness_percent: list[float] = self.get('cloudiness')
        for k in range(len(dew_point_temperatures_deg)):
            E_clear_W_per_m2: float = 0.711+.56 * \
                (dew_point_temperatures_deg[k]/100) + \
                0.73 * (dew_point_temperatures_deg[k]/100)**2
            E_cloud_W_m2: float = 0.96 * Stefan_Boltzmann * \
                (ground_temperatures_deg[k]+273.15 - 5)**4
            _long_wave_radiation_sky_W_per_m2.append(
                (1-cloudiness_percent[k]/100) * E_clear_W_per_m2 + cloudiness_percent[k]/100*E_cloud_W_m2)
        return _long_wave_radiation_sky_W_per_m2

    def surface_out_radiative_exchange(self, slope_deg: float, surface_temperature_deg: list[float], ground_temperature_deg: list[float], surface_m2: float = 1) -> tuple[float, float]:
        dew_point_temperatures_deg: list[float] = self.get(
            'dew_point_temperature')
        outdoor_temperatures_deg: list[float] = self.get('temperature')
        cloudiness_percent: list[float] = self.get('cloudiness')
        beta_deg = (slope_deg - 180) / 180 * pi

        phis_surface_sky_W_per_m2, phis_surface_ground_W_per_m2 = list(), list()
        for k in range(len(self._epochtimems)):
            wall_emissivity_W_per_m2 = 0.96 * Stefan_Boltzmann * \
                (surface_temperature_deg[k] + 273.15)**4
            ground_irradiance_W_per_m2 = 0.96 * Stefan_Boltzmann * \
                (ground_temperature_deg[k] + 273.15)**4
            clear_sky_irradiance_W_per_m2 = 0.711+.56 * \
                dew_point_temperatures_deg[k]/100 + 0.73 * \
                (dew_point_temperatures_deg[k]/100)**2
            cloud_irradiance_W_per_m2 = 0.96 * Stefan_Boltzmann * \
                (outdoor_temperatures_deg[k] + 273.15 - 5)**4
            sky_irradiance_W_per_m2 = (
                1-cloudiness_percent[k]/100) * clear_sky_irradiance_W_per_m2 + cloudiness_percent[k]/100*cloud_irradiance_W_per_m2
            phis_surface_ground_W_per_m2.append(
                (wall_emissivity_W_per_m2 - ground_irradiance_W_per_m2)*(1-cos(beta_deg))/2 * surface_m2)
            phis_surface_sky_W_per_m2.append(
                (wall_emissivity_W_per_m2 - sky_irradiance_W_per_m2)*(1+cos(beta_deg))/2 * surface_m2)
        return phis_surface_sky_W_per_m2, phis_surface_ground_W_per_m2

    def absolute_humidity_kg_per_kg(self) -> list[float]:
        Rs_J_per_kg_K = 287.06
        temperatures_deg: list[float] = self.get('temperature')
        relative_humidities_percent: list[float] = self.get('humidity')
        atmospheric_pressures_hPa: list[float] = self.get('pressure')
        _absolute_humidities_kg_per_kg: list[float] = list()
        for k in range(len(temperatures_deg)):
            density_kg_per_m3 = (atmospheric_pressures_hPa[k]*100 - 2.30617*relative_humidities_percent[k]*exp(
                17.5043*temperatures_deg[k]/(241.2+temperatures_deg[k])))/Rs_J_per_kg_K/(temperatures_deg[k] + 273.15)
            _absolute_humidities_kg_per_kg.append(absolute_humidity_kg_per_m3(
                temperatures_deg[k], relative_humidities_percent[k])/density_kg_per_m3)
        return _absolute_humidities_kg_per_kg

    def day_degrees(self, temperature_reference=18, heat=True):
        """Compute heating or cooling day degrees and print in terminal the sum of day degrees per month.

        :param temperature_reference: reference temperature (default is 18°C)
        :param heat: True if heating, False if cooling
        :return: list of day dates as string, list of day average, min and max outdoor temperature and day degrees per day
        :rtype: [list[str], list[float], list[float], list[float], list[float]]
        """
        datetimes: list[datetime] = self._datetimes
        stringdates: list[str] = self._stringdates
        temperatures: list[float] = self.get('temperature')
        dd_months: list[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        month_names: list[str] = ['January', 'February', 'March', 'April', 'May',
                                  'June', 'July', 'August', 'September', 'October', 'November', 'December']
        day_stringdate_days = list()
        average_temperature_days = list()
        min_temperature_days = list()
        max_temperature_days = list()
        day_degrees = list()
        day_temperature = list()
        current_day = datetimes[0].day
        for k in range(len(datetimes)):
            if current_day == datetimes[k].day:
                day_temperature.append(temperatures[k])
            else:
                day_stringdate_days.append(stringdates[k-1].split(' ')[0])
                average_day_temperature: float = sum(
                    day_temperature)/len(day_temperature)
                average_temperature_days.append(average_day_temperature)
                min_temperature_days.append(min(day_temperature))
                max_temperature_days.append(max(day_temperature))
                hdd = 0
                if heat:
                    if average_day_temperature < temperature_reference:
                        hdd = temperature_reference - average_day_temperature
                elif not heat:
                    if average_day_temperature > temperature_reference:
                        hdd = average_day_temperature - temperature_reference
                day_degrees.append(hdd)
                dd_months[datetimes[k].month-1] += hdd
                day_temperature = list()
            current_day = datetimes[k].day
        for i in range(len(dd_months)):
            print('day degrees', month_names[i], ': ', dd_months[i])
        return day_stringdate_days, average_temperature_days, min_temperature_days, max_temperature_days, day_degrees

    def data_datetimes_names(self) -> tuple[dict[str, list[float]], list[datetime], dict]:
        return self._variable_data, self._datetimes, self.variable_units

    def plot(self):
        TimeSeriesPlotter(self._variable_data,
                          self._datetimes, self.variable_units)


# Alias for backward compatibility
class WeatherJsonReader:
    """Alias for SiteWeatherDataBuilder for backward compatibility."""
    
    def __init__(self, location: str, latitude_north_deg: float = None, longitude_east_deg: float = None, 
                 from_requested_stringdate: str = None, to_requested_stringdate: str = None,
                 albedo: float = 0.1, pollution: float = 0.1):
        self.builder = SiteWeatherDataBuilder()
        self.location = location
        self.latitude_north_deg = latitude_north_deg
        self.longitude_east_deg = longitude_east_deg
        self.from_requested_stringdate = from_requested_stringdate
        self.to_requested_stringdate = to_requested_stringdate
        self.albedo = albedo
        self.pollution = pollution
        
        # Build the weather data immediately
        self._site_weather_data = self.builder.build(
            location=location,
            albedo=albedo,
            pollution=pollution,
            given_latitude_north_deg=latitude_north_deg,
            given_longitude_east_deg=longitude_east_deg,
            from_requested_stringdate=from_requested_stringdate,
            to_requested_stringdate=to_requested_stringdate
        )
    
    @property
    def site_weather_data(self):
        return self._site_weather_data


if __name__ == '__main__':

    # python batem/core/weather.py

    location: str = 'Cayenne'
    latitude_deg_north, longitude_deg_east = 4.924435336591809, -52.31276008988111

    WeatherJsonCharacteristicsPrinter().print()

    site_weather_data = WeatherDataManager().get_weather_data(
        location, latitude_deg_north=latitude_deg_north,
        longitude_deg_east=longitude_deg_east)

    print(site_weather_data)

    exit()
    weather_json_reader = SiteWeatherDataBuilder(
        location, given_latitude_north_deg=latitude_deg_north, given_longitude_east_deg=longitude_deg_east)
    site_weather_data: SiteWeatherData = weather_json_reader.site_weather_data
    print(site_weather_data)
    excerpt_site_weather_data: SiteWeatherData = site_weather_data.excerpt(
        '1/1/2023', '31/12/2023')
    print(excerpt_site_weather_data)
