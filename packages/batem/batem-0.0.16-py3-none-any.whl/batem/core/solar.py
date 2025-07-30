"""Solar model calculation the radiations on a given unit surface with a specific direction.

Author: stephane.ploix@grenoble-inp.fr
"""
from __future__ import annotations
import configparser
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize  # , differential_evolution
import time
from abc import ABC, abstractmethod
from math import asin, atan2, cos, exp, log, sin, sqrt, floor, radians, degrees, pi, ceil
from .library import SLOPES, DIRECTIONS_SREF
import json
import os.path
import requests
import matplotlib.pyplot as plt
import datetime
import pyexcelerate
from pytz import utc

import random
import logging
from .weather import SiteWeatherData
from . import timemg
import enum
import prettytable
from .utils import day_averager, mkdir_if_not_exist

logging.basicConfig(level=logging.ERROR)


class MOUNT_TYPES(enum.Enum):
    PLAN = 0
    FLAT = 1
    BACK2BACK = 2


class RADIATION_TYPES(enum.Enum):
    DIRECT = 1
    DIFFUSE = 2
    REFLECTED = 3


class EXTRA_DIRECTIONS(enum.Enum):
    PERSO = 10
    BEST = 11


config = configparser.ConfigParser()
config.read('setup.ini')
plot_size: tuple[int, int] = (8, 8)


def _encode4file(string: str, number: float = None):  # type: ignore
    if number is not None:
        string += '='+(str(number).replace('.', ','))
    return string.encode("iso-8859-1")


class SkylineRetriever:
    """
    A class to retrieve and store skylines data based on geographic coordinates.

    This class uses a local JSON file to cache skyline data to reduce the need for
    repeated external API calls for the same coordinates.

    Attributes:
        json_database_name (str): The name of the JSON file used for storing data.
        data (dict[str,tuple[tuple[float, float]]): A dictionary to hold the coordinates (azimuth, altitude)"""

    def __init__(self, json_database_name: str = 'skylines.json') -> None:
        """
        Initializes the Skyline Retriever instance.

        Args:
            json_database_name (str): The name of the file where azimuths and altitudes are saved. Defaults to 'skylines.json'.
        """
        self.json_database_name: str = json_database_name
        self.data: dict[str, tuple[tuple[float, float]]] = self._load_data()

    def _load_data(self) -> dict[str, float]:
        """Load skyline data from the JSON file if it exists, else returns an empty dictionary."""
        if os.path.isfile(self.json_database_name):
            with open(self.json_database_name, 'r') as json_file:
                return json.load(json_file)
        else:
            return {}

    def get(self, latitude: float, longitude: float) -> tuple[tuple[float, float]]:
        """
        Retrieves the skyline for the given latitude (degrees north) and longitude (degrees east) coordinates.
        If the skyline data is not cached, it fetches from an external API and stores it.

        Args:
            longitude_deg_east (float): Longitude in degrees east.
            latitude_deg_north (floatS): Latitude in degrees north.

        Returns:
            tuple[tuple[float, float]]: The skyline.
        """
        coordinate = str((latitude, longitude))
        if coordinate not in self.data:
            skyline = self._fetch_skyline_from_api(latitude, longitude)
            self.data[coordinate] = skyline
            self._save_data()
        else:
            skyline: tuple[tuple[float, float]] = self.data[coordinate]
        return skyline

    def _fetch_skyline_from_api(self, latitude_deg_north: float, longitude_deg_east: float) -> float:
        """
        Fetches elevation data from an external API for given coordinates.

        Args:
            longitude_deg_east (float): East degree longitude.
            latitude_deg_north (float): North degree latitude.

        Returns:
            float: The elevation data in meters.
        """
        response = requests.get(
            f'https://re.jrc.ec.europa.eu/api/v5_2/printhorizon?outputformat=json&lat={latitude_deg_north}&lon={longitude_deg_east}',
            headers={'Accept': 'application/json'}
        )
        data = response.json()
        horizon_profile = data['outputs']['horizon_profile']
        skyline = list()
        for horizon_point in horizon_profile:
            skyline.append((horizon_point['A'], horizon_point['H_hor']))
        return tuple(skyline)

    def _save_data(self) -> None:
        """Saves the current elevation data to the JSON file."""
        with open(self.json_database_name, 'w') as json_file:
            json.dump(self.data, json_file)


class Angle:

    def __init__(self, value: float, rad=False) -> None:
        if not rad:
            self.value_rad: float = self._normalize(radians(value))
        else:
            self.value_rad: float = self._normalize(value)

    @property
    def rad(self) -> float:
        return self._normalize(self.value_rad)

    @property
    def deg(self) -> float:
        return degrees(self._normalize(self.value_rad))

    @staticmethod
    def _normalize(value_rad: float) -> float:
        if -pi <= value_rad <= pi:
            return value_rad
        return (value_rad + pi) % (2 * pi) - pi

    def _diff(self, other_angle: Angle) -> float:
        return (other_angle.value_rad - self.value_rad) * 180/pi

    def __lt__(self, other_angle: Angle) -> bool:
        return self._diff(other_angle) > 0

    def __le__(self, other_angle: Angle) -> bool:
        return self._diff(other_angle) >= 0

    def __gt__(self, other_angle: Angle) -> bool:
        return self._diff(other_angle) < 0

    def __ge__(self, other_angle: Angle) -> bool:
        return self._diff(other_angle) <= 0

    def __eq__(self, other_angle: Angle) -> bool:
        return self._diff(other_angle) == 0

    def __add__(self, other_angle: Angle) -> Angle:
        return Angle(self.value_rad + other_angle.value_rad)

    def __str__(self) -> str:
        return 'Angle:%g°' % self.deg


class SolarPosition:
    """Contain self.azimuths_in_deg[i] and altitude angles of the sun for mask processing."""

    def __init__(self, azimuth: float, altitude: float, rad=False) -> None:
        """Create a solar position with self.azimuths_in_deg[i] (south to west directed) and altitude (south to zenith directed) angles of the sun for mask processing.

        :param azimuth_in_deg: solar angle with the south in degree, counted with trigonometric direction i.e. the self.azimuths_in_deg[i] (0=South, 90=West, 180=North, -90=East)
        :type azimuth_in_deg: float
        :param altitude_in_deg: zenital solar angle with the horizontal in degree i.e. the altitude (0=horizontal, 90=zenith)
        :type altitude_in_deg: float
        """
        if type(azimuth) is not Angle:
            self.azimuth_angle: Angle = Angle(azimuth, rad=rad)
        else:
            self.azimuth_angle = azimuth
        if type(altitude) is not Angle:
            self.altitude_angle: Angle = Angle(altitude, rad=rad)
        else:
            self.altitude_angle: Angle = altitude

    def distance(self, solar_position: SolarPosition) -> float:
        return sqrt((self.azimuth_angle.value_rad-solar_position.azimuth_angle.value_rad)**2 + (self.altitude_angle.value_rad - solar_position.altitude_angle.value_rad)**2)

    def __eq__(self, solar_position: SolarPosition) -> bool:
        return self.altitude_angle == solar_position.altitude_angle and self.azimuth_angle == solar_position.azimuth_angle

    def __lt__(self, solar_position: SolarPosition) -> bool:
        if self.azimuth_angle < solar_position.azimuth_angle:
            return True
        elif self.azimuth_angle == solar_position.azimuth_angle:
            if self.altitude_angle < solar_position.altitude_angle:
                return True
        return False

    def __gt__(self, solar_position: SolarPosition) -> bool:
        if self.azimuth_angle > solar_position.azimuth_angle:
            return True
        elif self.azimuth_angle == solar_position.azimuth_angle:
            if self.altitude_angle > solar_position.altitude_angle:
                return True
        return False

    def __str__(self):
        """Return a description of the solar position.

        :return: string with normalized self.azimuths_in_deg[i] and altitude angles in degree
        :rtype: str
        """
        return '(AZ:%s,AL:%s)' % (self.azimuth_angle.__str__(), self.altitude_angle.__str__())


class _SolarModel():
    """Model using the position of the sun and weather data to compute the resulting solar radiations on a directed ground surface."""

    def __init__(self, site_weather_data: SiteWeatherData, horizon_mask: Mask = None, parameters: SolarModel.Parameters = None) -> None:
        """Initialize a new SolarModel instance and compute all the data that are not specific to a collector.
            :param site_weather_data: contains site data like location, altitude, albedo, etc... It is generated by an Weather object, that contains site data like location, altitude,... (see openweather.SiteWeatherData)
            :type site_weather_data: buildingenergy.weather.SiteWeatherData
            :param far_mask: Optional mask for far obstructions. If None, only skyline mask is used.
            :type Mask: Mask
            :param parameters: Optional Parameters object with model coefficients. If None, default parameters are used.

        :param site_weather_data: object generated by an OpenWeatherMapJsonReader, that contains site data like location, altitude,... (see openweather.SiteWeatherData)
        :type site_weather_data: openweather.SiteWeatherData
        """
        # self._use_measurements = False,
        if parameters is None:
            self.parameters = SolarModel.Parameters()
        else:
            self.parameters: SolarModel.Parameters = parameters
        self.site_weather_data: SiteWeatherData = site_weather_data
        self.time_zone: str = site_weather_data.timezone_str
        self.latitude_north_angle: float = Angle(site_weather_data.latitude_deg_north)
        self.longitude_east_angle: float = Angle(site_weather_data.longitude_deg_east)
        self.elevation_m: int = site_weather_data.elevation
        self.albedo: float = site_weather_data.albedo
        self.pollution: float = self.site_weather_data.pollution
        if horizon_mask is None:
            self.horizon_mask = HorizonMask(*SkylineRetriever().get(self.latitude_north_angle.deg, self.longitude_east_angle.deg))
        else:
            self.horizon_mask: Mask = horizon_mask

    def _day_in_year(self, administrative_datetime: datetime.datetime) -> tuple[int, int]:
        """Used by the initializer to calculate the solar time from administrative.

        :param administrative_datetime: the date time
        :type administrative_datetime: datetime.datetime
        :return: elevation_in_rad, azimuth_in_rad, hour_angle_in_rad, latitude_in_rad.?
        :rtype: tuple[float]
        """
        utc_datetime: datetime.datetime = administrative_datetime.astimezone(utc)
        utc_timetuple: time.struct_t.ime = utc_datetime.timetuple()
        return utc_timetuple.tm_yday % 365

    def _daytime_sec(self, administrative_datetime: datetime.datetime) -> float:
        """Used by the initializer to calculate the solar time from administrative.

        :param administrative_datetime: the date time
        :type administrative_datetime: datetime.datetime
        :return: solar daytime in seconds
        :rtype: float
        """
        utc_datetime: datetime.datetime = administrative_datetime.astimezone(utc)
        utc_timetuple: time.struct_time = utc_datetime.timetuple()
        day_in_year: int = utc_timetuple.tm_yday % 365
        hour_in_day: int = utc_timetuple.tm_hour
        minute_in_hour: int = utc_timetuple.tm_min
        seconde_in_minute: int = utc_timetuple.tm_sec
        greenwich_time_in_seconds = hour_in_day * 3600 + minute_in_hour * 60 + seconde_in_minute
        local_solar_time_seconds: float = greenwich_time_in_seconds + self.longitude_east_angle.rad / (2*pi) * 24 * 3600
        time_variation = 2 * pi / 365 * (day_in_year - 81)
        time_correction_equation_seconds = (9.87 * sin(2 * time_variation) - 7.53 * cos(time_variation) - 1.5 * sin(time_variation)) * 60
        return local_solar_time_seconds + time_correction_equation_seconds

    def instant_angles_rad(self, dt: datetime.datetime) -> dict[str, float]:
        """Used by the initializer to calculate of solar angles.
        :param administrative_datetime: administrative time
        :type administrative_datetime: datetime.datetime
        :return: the altitude, in rad, of the sun in the sky from the horizontal plan to the sun altitude,
        the azimuth, in rad, is the angle with south direction in the horizontal plan,
        the declination, in rad, is the angle between the direction of the sun and equatorial plan of Earth
        the solar hour angle, in rad, is the angle between the Greenwich plan at hour 0 and its current angle
        :rtype: tuple[float]
        """
        solar_daytime_sec: float = self._daytime_sec(dt)
        declination_rad: float = 23.45 / 180 * pi * sin(2 * pi * (self._day_in_year(dt) + 284) / 365.25)
        solar_hour_angle_rad: float = 2 * pi * (solar_daytime_sec / 3600 - 12) / 24
        altitude_rad: float = max(0, asin(sin(declination_rad) * sin(self.latitude_north_angle.rad) + cos(declination_rad) * cos(self.latitude_north_angle.rad) * cos(solar_hour_angle_rad)))
        cos_azimuth: float = (cos(declination_rad) * cos(solar_hour_angle_rad) * sin(self.latitude_north_angle.rad) - sin(declination_rad) * cos(self.latitude_north_angle.rad)) / cos(altitude_rad)
        sin_azimuth: float = cos(declination_rad) * sin(solar_hour_angle_rad) / cos(altitude_rad)
        azimuth_rad: float = atan2(sin_azimuth, cos_azimuth)
        return {'altitude_rad': altitude_rad, 'azimuth_rad': azimuth_rad, 'declination_rad': declination_rad}

    def instant_canonic_irradiances_W(self, administrative_datetime: datetime.datetime, nebulosity_percent: float, temperature_celsius: float, humidity_percent: float) -> dict[str, list[float]]:
        """Used by the initializer to compute the solar power on a 1m2 flat surface.

        :param exposure_in_deg: clockwise angle in degrees between the south and the normal of collecting surface. O means south oriented, 90 means West, -90 East and 180 north oriented
        :type exposure_in_deg: float
        :param slope_in_deg: clockwise angle in degrees between the ground and the collecting surface. 0 means horizontal, directed to the sky, and 90 means vertical directed to the specified direction
        :type slope_in_deg: float
        :return: phi_total, phi_direct_collected, phi_diffuse, phi_reflected
        :rtype: list[float]
        """
        solar_angles: dict[str, float] = self.instant_angles_rad(administrative_datetime)
        altitude_rad: float = solar_angles['altitude_rad']
        azimuth_rad: float = solar_angles['azimuth_rad']
        day_in_year: tuple[int, int] = self._day_in_year(administrative_datetime)
        tsi: float = 1327 * (1 + 0.033 * cos(2*pi * (1 + day_in_year) / 365.25))

        # concentration_pm2_5_micrograms_m3 = pollution * 10:
        # 0 -> 12 micrograms per m3: good air quality
        # 12.1 -> 35.4 micrograms per m3: moderate air quality
        # 35.5 -> 55.4 micrograms per m3: unhealthy air quality
        # > 150 micrograms per m3: hazardous conditions

        corrected_total_solar_irradiance: float = (1 - self.parameters('ratio_nebulosity') * (nebulosity_percent/100) ** self.parameters('power_nebulosity')) * tsi
        M0: float = sqrt(1229 + (self.parameters('M0_correct')*sin(altitude_rad))**2) - self.parameters('M0_correct')*sin(altitude_rad)
        Mh: float = (1-self.parameters('Mh_0')/288*self.elevation_m)**self.parameters('Mh_1') * M0
        transmission_coefficient_direct: float = self.parameters('tau_direct') ** Mh  # 0.9
        rhi: float = max(0, self.albedo * corrected_total_solar_irradiance * (self.parameters('rhi_0') + self.parameters('rhi_1') * transmission_coefficient_direct) * sin(altitude_rad))

        if self.horizon_mask.passthrough(SolarPosition(azimuth_rad, altitude_rad, rad=True)):
            rayleigh_length: float = 1 / (self.parameters('tau_direct') * Mh + self.parameters('rayleigh'))
            partial_steam_pressure = humidity_percent * self.parameters('steam_1')*exp(self.parameters('steam_2')*temperature_celsius/(temperature_celsius+self.parameters('steam_3')))
            l_Linke: float = self.parameters('linke_1') + self.parameters('linke_2') * self.pollution + self.parameters('linke_3') * (1 + 2 * self.pollution) * log(partial_steam_pressure)
            dni: float = max(0, transmission_coefficient_direct * corrected_total_solar_irradiance * exp(-Mh * rayleigh_length * l_Linke))
        else:  # stop by mask
            dni = 0
        transmission_coefficient_diffuse: float = self.parameters('tau_diffuse') ** Mh  # 0.66 0.8
        dhi: float = corrected_total_solar_irradiance * (self.parameters('alpha') - self.parameters('beta') * transmission_coefficient_diffuse) * sin(altitude_rad)

        ghi = dni * sin(altitude_rad) + dhi
        # rhi = self.albedo * ghi
        return {'dni': dni, 'dhi': dhi, 'rhi': rhi, 'tsi': tsi, 'ghi': ghi}

    def instant_tilt_irradiances_W(self, administrative_datetime: datetime.datetime, nebulosity_percent: float, temperature_celsius: float, humidity_percent: float, exposure_deg: float, slope_deg: float, scale_factor: float = 1, specific_mask: Mask = None, with_composites: bool = False) -> tuple[float]:
        """Compute the solar power on a 1m2 flat surface.

        :param exposure_in_deg: clockwise angle in degrees between the south and the normal of collecting surface. O means south oriented, 90 means West, -90 East and 180 north oriented
        :type exposure_in_deg: float
        :param slope_in_deg: clockwise angle in degrees between the ground and the collecting surface. 180 means horizontal, directed to the sky, and 90 means vertical directed to the specified direction
        :type slope_in_deg: float
        :return: phi_total, phi_direct_collected, phi_diffuse, phi_reflected
        :rtype: list[float]
        """
        slope_rad = radians(slope_deg)
        exposure_rad = radians(exposure_deg)
        canonical_solar_irradiances: dict[str, list[float]] = self.instant_canonic_irradiances_W(administrative_datetime, nebulosity_percent, temperature_celsius, humidity_percent)
        angles: dict[str, float] = self.instant_angles_rad(administrative_datetime)
        altitude_rad: list[float] = angles['altitude_rad']
        azimuth_rad: list[float] = angles['azimuth_rad']
        dni: float = canonical_solar_irradiances['dni']
        dhi: float = canonical_solar_irradiances['dhi']
        rhi: float = canonical_solar_irradiances['rhi']

        cos_incidence: float = - sin(altitude_rad) * cos(slope_rad) - cos(altitude_rad) * sin(slope_rad) * cos(azimuth_rad + pi - exposure_rad)
        if specific_mask is None:
            mask = self.horizon_mask
        else:
            mask = StackedMask(self.horizon_mask, specific_mask)
        if mask.passthrough(SolarPosition(degrees(azimuth_rad), degrees(altitude_rad))):
            direct_tilt_irradiance: float = max(0, cos_incidence * dni)
        else:
            direct_tilt_irradiance = 0
        diffuse_tilt_solar_irradiance = (1 - cos(slope_rad))/2 * dhi
        reflected_tilt_solar_irradiance = (1 + cos(slope_rad))/2 * rhi
        global_tilt_irradiance: float = direct_tilt_irradiance + diffuse_tilt_solar_irradiance + reflected_tilt_solar_irradiance
        if with_composites:
            return global_tilt_irradiance * scale_factor, {RADIATION_TYPES.DIRECT: direct_tilt_irradiance * scale_factor, RADIATION_TYPES.DIFFUSE: diffuse_tilt_solar_irradiance * scale_factor, RADIATION_TYPES.REFLECTED: reflected_tilt_solar_irradiance * scale_factor}
        else:
            return global_tilt_irradiance * scale_factor


class SolarModel(_SolarModel):

    def __init__(self, site_weather_data: SiteWeatherData, horizon_mask: Mask = None, parameters: SolarModel.Parameters = None):
        super().__init__(site_weather_data, horizon_mask, parameters)

        self.datetimes: list[datetime.datetime] = self.site_weather_data.get('datetime')
        self.temperatures: list[float] = self.site_weather_data.get('temperature')
        self.humidities: list[float] = self.site_weather_data.get('humidity')
        self.nebulosities_percent: list[int] = self.site_weather_data.get('cloudiness')
        self.pressures_Pa: list[int] = [p * 100 if p is not None else 101325 for p in self.site_weather_data.get('pressure')]

        self.altitudes_rad = list()
        self.altitudes_deg = list()
        self.azimuths_rad = list()
        self.azimuths_deg = list()
        self.declinations_rad = list()
        self.solar_hour_angles_rad = list()
        self.total_solar_irradiances = list()
        self.direct_normal_irradiances = list()
        self.diffuse_horizontal_irradiances = list()
        self.reflected_horizontal_irradiances = list()
        self.global_horizontal_irradiances = list()
        self.global_direct_irradiances = list()

        for k, dt in enumerate(self.datetimes):
            instant_angles_rad: dict[str, float] = self.instant_angles_rad(dt)
            self.altitudes_rad.append(instant_angles_rad['altitude_rad'])
            self.azimuths_rad.append(instant_angles_rad['azimuth_rad'])
            self.declinations_rad.append(instant_angles_rad['declination_rad'])
            self.altitudes_deg.append(instant_angles_rad['altitude_rad']/pi*180)
            self.azimuths_deg.append(instant_angles_rad['azimuth_rad']/pi*180)
            canonic_irradiances: dict[str, float] = self.instant_canonic_irradiances_W(dt, nebulosity_percent=self.nebulosities_percent[k], temperature_celsius=self.temperatures[k], humidity_percent=self.humidities[k])
            self.direct_normal_irradiances.append(canonic_irradiances['dni'])
            self.diffuse_horizontal_irradiances.append(canonic_irradiances['dhi'])
            self.reflected_horizontal_irradiances.append(canonic_irradiances['rhi'])
            self.total_solar_irradiances.append(canonic_irradiances['tsi'])
            self.global_horizontal_irradiances.append(canonic_irradiances['ghi'])
            self.global_direct_irradiances.append(canonic_irradiances['dni'] + canonic_irradiances['dhi'])

    @property
    def dni(self) -> list[float]:
        return self.direct_normal_irradiances

    @property
    def gni(self) -> list[float]:
        return self.global_direct_irradiances

    @property
    def dhi(self) -> list[float]:
        return self.diffuse_horizontal_irradiances

    @property
    def rhi(self) -> list[float]:
        return self.reflected_horizontal_irradiances

    @property
    def ghi(self) -> list[float]:
        return self.global_horizontal_irradiances

    @property
    def tsi(self) -> list[float]:
        return self.total_solar_irradiances

    def irradiances_W(self, exposure_deg: float, slope_deg: float, scale_factor: float = 1, specific_mask: Mask = None, with_composites: bool = False) -> tuple[list[float], dict[RADIATION_TYPES, list[float]]] | list[float]:
        tilt_global_irradiances_W = list()
        tilt_direct_irradiances_W = list()
        tilt_diffuse_irradiances_W = list()
        tilt_reflected_irradiances_W = list()
        cloudiness_percent: list[float] = self.site_weather_data('cloudiness')
        temperature_celsius: list[float] = self.site_weather_data('temperature')
        humidity_percent: list[float] = self.site_weather_data('humidity')
        for k, dt in enumerate(self.datetimes):
            if with_composites:
                tilt_global_irradiances_W, irradiance_composites_W = self.instant_tilt_irradiances_W(dt, nebulosity_percent=cloudiness_percent[k], temperature_celsius=temperature_celsius[k], humidity_percent=humidity_percent[k],  exposure_deg=exposure_deg, slope_deg=slope_deg, specific_mask=specific_mask, scale_factor=scale_factor, with_composites=with_composites)

                tilt_direct_irradiances_W.append(irradiance_composites_W[RADIATION_TYPES.DIRECT])
                tilt_diffuse_irradiances_W.append(irradiance_composites_W[RADIATION_TYPES.DIFFUSE])
                tilt_reflected_irradiances_W.append(irradiance_composites_W[RADIATION_TYPES.REFLECTED])
            else:
                tilt_global_irradiances_W.append(self.instant_tilt_irradiances_W(dt, nebulosity_percent=cloudiness_percent[k], temperature_celsius=temperature_celsius[k], humidity_percent=humidity_percent[k],  exposure_deg=exposure_deg, slope_deg=slope_deg, specific_mask=specific_mask, scale_factor=scale_factor, with_composites=with_composites))
        if with_composites:
            return tilt_global_irradiances_W, {RADIATION_TYPES.DIRECT: tilt_direct_irradiances_W, RADIATION_TYPES.DIFFUSE: tilt_diffuse_irradiances_W, RADIATION_TYPES.REFLECTED: tilt_reflected_irradiances_W}
        else:
            return tilt_global_irradiances_W

    def best_angles(self, initial_slope_deg: float = 180, initial_exposure_deg: float = 0, with_complements: bool = False) -> dict[str, float]:
        neighborhood: list[tuple[float, float]] = [(-1, 0), (-1, 1), (-1, -1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        taboo = list()
        exposure_slope_in_deg_candidate: tuple[float, float] = (initial_exposure_deg, initial_slope_deg)
        best_exposure_slope_in_deg = tuple(exposure_slope_in_deg_candidate)
        best_total_energy_in_Wh = sum(self.irradiances_W(exposure_slope_in_deg_candidate[0], exposure_slope_in_deg_candidate[1], scale_factor=1))
        initial_production_Wh: float = best_total_energy_in_Wh
        taboo.append(exposure_slope_in_deg_candidate)

        improvement = True
        while improvement:
            improvement = False
            for neighbor in neighborhood:
                exposure_slope_in_deg_candidate = (best_exposure_slope_in_deg[0] + neighbor[0], best_exposure_slope_in_deg[1] + neighbor[1])
                exposure_in_deg: float = exposure_slope_in_deg_candidate[0]
                slope_in_deg: float = exposure_slope_in_deg_candidate[1]
                if -180 <= exposure_in_deg <= 180 and 0 <= slope_in_deg <= 180 and exposure_slope_in_deg_candidate not in taboo:
                    taboo.append(exposure_slope_in_deg_candidate)
                    solar_energy_in_Wh: list[float] = sum(self.irradiances_W(exposure_in_deg, slope_in_deg, scale_factor=1))
                    if solar_energy_in_Wh > best_total_energy_in_Wh:
                        improvement = True
                        best_exposure_slope_in_deg: tuple[float, float] = exposure_slope_in_deg_candidate
                        best_total_energy_in_Wh: float = solar_energy_in_Wh
        if with_complements:
            return best_exposure_slope_in_deg[0], best_exposure_slope_in_deg[1], {'best_energy_kWh': best_total_energy_in_Wh / 1000, 'initial_slope_deg': initial_slope_deg, 'initial_slope_deg': initial_slope_deg, 'initial_production_kWh': initial_production_Wh / 1000, 'complementary_slope_deg': 180 - best_exposure_slope_in_deg[1]}
        else:
            return best_exposure_slope_in_deg[0], best_exposure_slope_in_deg[1]

    @property
    def cardinal_irradiances_W(self) -> dict[SLOPES | DIRECTIONS_SREF, list[float]]:
        _cardinal_irradiances_W = dict()
        _cardinal_irradiances_W[SLOPES.HORIZONTAL_DOWN] = self.irradiances_W(exposure_deg=DIRECTIONS_SREF.SOUTH.value, slope_deg=SLOPES.HORIZONTAL_DOWN.value)
        _cardinal_irradiances_W[SLOPES.HORIZONTAL_UP] = self.irradiances_W(exposure_deg=DIRECTIONS_SREF.SOUTH.value, slope_deg=SLOPES.HORIZONTAL_UP.value)
        _cardinal_irradiances_W[DIRECTIONS_SREF.SOUTH] = self.irradiances_W(exposure_deg=DIRECTIONS_SREF.SOUTH.value, slope_deg=SLOPES.VERTICAL.value)
        _cardinal_irradiances_W[DIRECTIONS_SREF.WEST] = self.irradiances_W(exposure_deg=DIRECTIONS_SREF.WEST.value, slope_deg=SLOPES.VERTICAL.value)
        _cardinal_irradiances_W[DIRECTIONS_SREF.EAST] = self.irradiances_W(exposure_deg=DIRECTIONS_SREF.EAST.value, slope_deg=SLOPES.VERTICAL.value)
        _cardinal_irradiances_W[DIRECTIONS_SREF.NORTH] = self.irradiances_W(exposure_deg=DIRECTIONS_SREF.NORTH.value, slope_deg=SLOPES.VERTICAL.value)
        return _cardinal_irradiances_W

    def try_export(self) -> None:
        """Export a TRY weather files for IZUBA Pleiades software. It generates 2 files per full year:
        - site_location + '_' + 'year' + '.INI'
        - site_location + '_' + 'year' + '.TRY'
        The station ID will correspond to the 3 first characters of the site_location in upper case
        """
        site_location: str = self.site_weather_data.location
        location_id: str = site_location[0:3].upper()
        temperatures: list[float] = self.site_weather_data.get('temperature')
        TempSol: float = round(sum(temperatures) / len(temperatures))
        temperature_tenth: list[float] = [10 * t for t in temperatures]
        humidities: list[float] = self.site_weather_data.get('humidity')
        wind_speeds: list[float] = self.site_weather_data.get('wind_speed')
        wind_directions_in_deg: list[float] = self.site_weather_data.get('wind_direction_in_deg')
        global_horizontal_irradiances: list[float] = self.ghi
        direct_normal_irradiances: list[float] = self.dni
        diffuse_horizontal_irradiances: list[float] = self.ghi
        ini_file = None
        try_file = None
        for i, dt in enumerate(self.datetimes):
            year, month, day, hour = dt.year, dt.month, dt.day, dt.hour+1
            if month == 1 and day == 1 and hour == 1:
                if ini_file is not None:
                    ini_file.close()
                    try_file.close()
                file_name: str = config['folders']['results'] + site_location + '_' + str(year)
                new_line = '\r\n'
                ini_file = open(file_name + '.ini', "w")
                ini_file.write('[Station]' + new_line)
                ini_file.write('Nom=' + site_location + new_line)
                ini_file.write('Altitude=%i%s' % (int(self.elevation_m), new_line))
                ini_file.write('Lattitude=%s%s' % (en2fr(self.latitude_north_angle.deg), new_line))
                ini_file.write('Longitude=%s%s' % (en2fr(self.longitude_east_angle.deg), new_line))
                ini_file.write('NomFichier=' + site_location + '_' + str(year) + '.try' + new_line)
                ini_file.write('TempSol=%i%s' % (round(TempSol), new_line))
                ini_file.write('TypeFichier=xx' + new_line)
                ini_file.write('Heure solaire=0' + new_line)
                ini_file.write('Meridien=%i%s' % (int(floor(self.latitude_north_angle.rad/pi*12)), new_line))
                ini_file.write('LectureSeule=1' + new_line)
                ini_file.write('Categorie=OpenMeteo' + new_line)
                ini_file.close()
                try_file = open(file_name + '.try', "bw")
            irradiance_coefficient = 3600 / 10000
            if try_file is not None:
                row: str = f"{location_id}{round(temperature_tenth[i]):4d}{round(global_horizontal_irradiances[i]*irradiance_coefficient):4d}{round(diffuse_horizontal_irradiances[i]*irradiance_coefficient):4d}{round(direct_normal_irradiances[i]*irradiance_coefficient):4d}   E{round(humidities[i]):3d}{round(wind_speeds[i]):3d}{month:2d}{day:2d}{hour:2d}{round(wind_directions_in_deg[i]):4d} 130     E{self.altitudes_deg[i]:6.2f}{self.azimuths_deg[i]+180:7.2f}\r\n"
                row = row.replace('.', ',')
                try_file.write(_encode4file(row))
        try:
            try_file.close()
        except:  # noqa
            pass

    def plot_heliodon(self, year: int, name: str = '', new_figure: bool = True) -> plt.Axes:
        """Plot heliodon at current location.

        :param year: year to be displayed in figure
        :type year: int
        :param name: file_name to be displayed in figure, default to ''
        :type name: str
        """
        stringdates: list[str] = ['21/%i/%i' % (i, int(year)) for i in range(1, 13, 1)]
        legends: list[str] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.rcParams['font.size'] = 12
        if new_figure:
            _, axis = plt.subplots(figsize=plot_size)
        else:
            plt.gcf()
            axis = plt.gca()
        for day_index, stringdate in enumerate(stringdates):
            altitudes_in_deg, azimuths_in_deg = [], []
            for hour_in_day in range(0, 24, 1):
                for minutes in range(0, 60, 1):
                    instant_angles_rad = self.instant_angles_rad(timemg.stringdate_to_datetime(stringdate + ' %i:%i:0' % (hour_in_day, minutes)))
                    altitude_deg = instant_angles_rad['altitude_rad']/pi*180
                    azimuth_deg = instant_angles_rad['azimuth_rad']/pi*180
                    if altitude_deg > 0:
                        altitudes_in_deg.append(altitude_deg)
                        azimuths_in_deg.append(azimuth_deg)
                axis.plot(azimuths_in_deg, altitudes_in_deg)
            i_position = (day_index % 6)*len(altitudes_in_deg)//6 + random.randint(0, len(altitudes_in_deg)//6)
            axis.legend(legends)
            axis.annotate(legends[day_index], (azimuths_in_deg[i_position], altitudes_in_deg[i_position]), )
        axis.set_title('heliodon %s (21th of each month)' % name)
        for hour_in_day in range(0, 24):
            altitudes_deg, azimuths_deg = list(), list()
            for day_in_year in range(0, 365):
                a_datetime = datetime.datetime(int(year), 1, 1, hour=hour_in_day)
                a_datetime += datetime.timedelta(days=int(day_in_year) - 1)
                instant_angles_rad = self.instant_angles_rad(a_datetime)
                altitude_rad = instant_angles_rad['altitude_rad']
                azimuth_rad = instant_angles_rad['azimuth_rad']
                if altitude_rad > 0:
                    altitudes_deg.append(altitude_rad/pi*180)
                    azimuths_deg.append(azimuth_rad/pi*180)
            axis.plot(azimuths_deg, altitudes_deg, '.c')
            if len(altitudes_deg) > 0 and max(altitudes_deg) > 0:
                i: int = len(azimuths_deg) // 2
                axis.annotate(hour_in_day, (azimuths_deg[i], altitudes_deg[i]))
        self.horizon_mask.plot(axis=axis)
        axis.axis('tight')
        axis.grid()
        return axis

    def plot_angles(self, with_matplotlib: bool = True, title: str = ''):
        """Plot solar angles for the dates corresponding to dates in site_weather_data."""
        if with_matplotlib:
            plt.figure()
            plt.plot(self.datetimes, self.altitudes_deg, self.datetimes, self.azimuths_deg)
            plt.legend(('altitude in deg', 'azimuth in deg'))
            plt.title(title)
            plt.axis('tight')
            plt.grid()
        else:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
            fig.add_trace(go.Scatter(x=self.datetimes, y=self.altitudes_deg, name='sun altitude in °', line_shape='hv'), row=1, col=1)
            # azimuths_deg = [az if az >= -180 else 360+az for az in self.azimuths_deg]
            fig.add_trace(go.Scatter(x=self.datetimes, y=self.azimuths_deg, name='sun azimuth in °', line_shape='hv'), row=2, col=1)
            fig.update_layout(title=title)
            fig.show()

    def plot_cardinal_irradiances(self, with_matplotlib: bool = True, my_exp_slope_angles: tuple[float, float] = None) -> None:
        """Plot total solar irradiation on all cardinal direction and an horizontal one, for the dates corresponding to dates in site_weather_data."""

        irradiances_W = self.cardinal_irradiances_W
        best_exposure, best_slope = self.best_angles()
        print(f'Best exposure: {best_exposure}°, best slope: {best_slope}°')
        irradiances_W[EXTRA_DIRECTIONS.BEST] = self.irradiances_W(best_exposure, best_slope)
        if my_exp_slope_angles is not None:
            print(f'Best exposure: {my_exp_slope_angles[0]}°, best slope: {my_exp_slope_angles[1]}°')
            irradiances_W[EXTRA_DIRECTIONS.PERSO] = self.irradiances_W(exposure_deg=my_exp_slope_angles[0], slope_deg=my_exp_slope_angles[1])

        for d in irradiances_W:
            print('energy', d.name, ':', sum(irradiances_W[d])/1000, 'kWh')

        if with_matplotlib:
            plt.figure()
            for d in irradiances_W:
                plt.plot(self.datetimes, irradiances_W[d], label=d.name)
            plt.legend()
            plt.ylabel('Watt')
            plt.axis('tight')
            plt.grid()
        else:
            fig: go.Figure = make_subplots(rows=1, cols=1, shared_xaxes=True)
            for d in irradiances_W:
                fig.add_trace(go.Scatter(x=self.datetimes, y=irradiances_W[d], name=d.name, line_shape='hv'), row=1, col=1)
            fig.show()

    class Parameters:

        def __init__(self, vals: tuple[str] = None) -> None:
            self.parameters = dict()
            self.parameters['tau_direct'] = [0.305944, (0, 1)]  # 0.9
            self.parameters['tau_diffuse'] = [0.955966, (0, 1)]  # 0.9
            self.parameters['power_nebulosity'] = [1.72593, (0, 20)]   # 3.4
            self.parameters['M0_correct'] = [1365.54, (400, 4000)]  # 614
            self.parameters['ratio_nebulosity'] = [0.778399, (0, 1)]  # 0.75
            self.parameters['alpha'] = [0.224016, (0, 2)]  # 0.271
            self.parameters['beta'] = [0.0276831, (0, 1)]  # 0.294
            self.parameters['Mh_0'] = [0.0627782, (0, .1)]  # 0.0065
            self.parameters['Mh_1'] = [9.88566, (0, 10)]  # 5.256
            self.parameters['rhi_0'] = [0.480556, (0, 1)]  # 0.271
            self.parameters['rhi_1'] = [0.0200125, (0, 2)]  # 0.706
            self.parameters['rayleigh'] = [5.13063, (0, 20)]  # 9.4
            self.parameters['steam_1'] = [7.07651, (1, 10)]  # 6.112
            self.parameters['steam_2'] = [13.4154, (10, 30)]  # 17.67
            self.parameters['steam_3'] = [476.208, (100, 500)]  # 243.5
            self.parameters['linke_1'] = [1.75851, (.5, 5)]  # 2.4
            self.parameters['linke_2'] = [23.7116, (1, 30)]  # 14.6
            self.parameters['linke_3'] = [1.79987, (0, 2)]  # 0.4
            if vals is not None:
                self(value=vals)

        def bounds(self, pname: str = None):
            if pname is not None:
                return self.parameters[pname][1]
            else:
                return [self.parameters[pname][1] for pname in self.parameters]

        def __call__(self, pname: str | list[str] = None, value: float | list[float] = None):
            if value is None:
                if type(pname) is str:
                    return self.parameters[pname][0]
                else:
                    return [self.parameters[_][0] for _ in self.parameters]
            else:
                if type(pname) is str:
                    self.parameters[pname][0] = value
                else:
                    pnames = self.names()
                    for _ in range(len(self.parameters)):
                        self.parameters[pnames[_]][0] = value[_]

        def names(self):
            return tuple(self.parameters.keys())

        def __str__(self):
            return '\n'.join(['%s: %g in (%g, %g)' % (pname, self.parameters[pname][0], *self.parameters[pname][1]) for pname in self.parameters])

    @staticmethod
    def matching_error(vals: list[float], site_weather_data: SiteWeatherData, solar_model: SolarModel):
        parameters = SolarModel.Parameters(vals)
        solar_model = SolarModel(solar_model.site_weather_data, horizon_mask=solar_model.horizon_mask, parameters=parameters)
        # dhi: list[float] = solar_model.ghi
        gni: list[float] = solar_model.gni
        normal = site_weather_data('direct_radiation')
        # diffuse: list[float] = site_weather_data('diffuse_radiation')
        # return sum([abs(dhi[i] - diffuse[i]) + abs(gni[i] - normal[i]) for i in range(len(site_weather_data))]) / len(site_weather_data) / 2
        return sum([abs(gni[i] - normal[i]) for i in range(len(site_weather_data))]) / len(site_weather_data)

    def match_measurements(self, plot: bool = False):
        dts_optim: list[datetime.datetime] = self.site_weather_data.datetimes
        direct_radiation = self.site_weather_data('direct_radiation')
        diffuse_radiation = self.site_weather_data('diffuse_radiation')
        direct_normal_irradiance = self.site_weather_data('direct_normal_irradiance')
        shortwave_radiation = self.site_weather_data('shortwave_radiation')
        print("initial error:", SolarModel.matching_error(self.parameters(), self.site_weather_data, self))

        if plot:
            fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
            fig.add_trace(go.Scatter(x=dts_optim, y=self.dni, name='dni', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=self.gni, name='gni', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=self.ghi, name='ghi', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=self.dhi, name='dhi', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=self.rhi, name='rhi', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=direct_radiation, name='direct_radiation', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=diffuse_radiation, name='diffuse_radiation', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=direct_normal_irradiance, name='direct_normal_irradiance', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=shortwave_radiation, name='shortwave_radiation', line_shape='hv'), row=1, col=1)
            fig.update_layout(title='before parameter adjustment')
            fig.show()

        optim_result = minimize(SolarModel.matching_error, self.parameters(), args=(self.site_weather_data, self), method='NELDER-MEAD', bounds=self.parameters.bounds(), options={'disp': True})
        # optim_result = differential_evolution(SolarModel.matching_error, bounds=self.parameters.bounds(), args=(self.site_weather_data, self), disp=True, polish=True, workers=-1)
        print(optim_result)
        parameters = SolarModel.Parameters(optim_result.x)
        print(parameters)
        solar_model = SolarModel(self.site_weather_data, horizon_mask=self.horizon_mask, parameters=parameters)

        if plot:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
            fig.add_trace(go.Scatter(x=dts_optim, y=solar_model.gni, name='gni', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=direct_radiation, name='direct_radiation', line_shape='hv'), row=1, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=solar_model.dhi, name='dhi', line_shape='hv'), row=2, col=1)
            fig.add_trace(go.Scatter(x=dts_optim, y=diffuse_radiation, name='diffuse_radiation', line_shape='hv'), row=2, col=1)
            fig.show()
        return solar_model


def regular_angle_to_decimal_angle_converter(decimals, minutes, seconds):
    """Convert decimals, minutes, seconds to float value.

    :param decimals: number of degrees as an integer
    :type decimals: int
    :param minutes: number of minutes
    :type minutes: int
    :param seconds: number of seconds
    :type seconds: int
    :return: angle in decimal format
    :rtype: float
    """
    return decimals + minutes/60 + seconds/3600


def en2fr(val: float) -> str:
    val = str(val)
    if '.' in val:
        return val.replace('.', ',')
    return str(val)


class SolarSystem:
    """A class used to obtain the solar gains through the windows of a building."""

    def __init__(self, solar_model: SolarModel):
        """Create a set of solar collectors with masks to estimate the global solar gain.

        :param site_weather_data: weather data
        :type site_weather_data: SiteWeatherData
        :param solar_mask: distant solar mask used for the whole building. None means no global solar masks
        :type solar_mask: ComplexZone
        """
        self.datetimes: list[datetime.datetime] = solar_model.site_weather_data.get('datetime')
        self.stringdates: list[str] = solar_model.site_weather_data.get('stringdate')
        self.temperatures: list[float] = solar_model.site_weather_data.get('temperature')
        self.nebulosities_in_percent: list[float] = solar_model.site_weather_data.get('cloudiness')
        self.humidities: list[float] = solar_model.site_weather_data.get('humidity')
        self.pollution: float = solar_model.site_weather_data.pollution
        self.albedo: float = solar_model.site_weather_data.albedo
        self.solar_model: SolarModel = solar_model
        self.collectors: dict[str, Collector] = dict()

    @property
    def collector_names(self) -> tuple[str]:
        return tuple(self.collectors.keys())

    def collector(self, name: str) -> Collector:
        return self.collectors[name]

    def mask(self, collector_name: str = None) -> Mask:
        if collector_name is None:
            return self.solar_model.horizon_mask
        elif collector_name in self.collectors:
            if collector_name in self.collectors:
                return StackedMask(self.solar_model.horizon_mask, self.collectors[collector_name].collector_mask)
            else:
                return self.solar_model.horizon_mask
        else:
            raise ValueError('unknown collector name: %s' % collector_name)

    def plot_mask(self, collector_name: str = None, **kwargs):
        self.mask(collector_name).plot(**kwargs)

    def clear_collectors(self, collector_name: str = None):
        if collector_name is None:
            self.collectors.clear()
        elif collector_name in self.collector_names:
            del self.collectors[collector_name]

    def powers_W(self, gather_collectors: bool = False) -> list[float] | dict[str, dict[str, list[float]]]:
        """Return hourly solar gains coming through the collectors and with the type of radiation (RADIATION_TYPE.TOTAL, RADIATION_TYPE.DIRECT, RADIATION_TYPE.DIFFUSE, RADIATION_TYPE.REFLECTED).

        :return: a dictionary with collectors as keys and a dictionary with types of radiations as values
        :rtype: dict[str, dict[str, list[float]]]
        """
        collectors_powers = dict()
        for collector_name in self.collectors:
            collectors_powers[collector_name] = self.collectors[collector_name].powers_W()

        if not gather_collectors:
            return collectors_powers
        else:
            powers_W = None
            for collector_name in self.collector_names:
                if powers_W is None:
                    powers_W = collectors_powers[collector_name]
                else:
                    for k in range(len(self.datetimes)):
                        powers_W[k] += collectors_powers[collector_name][k]
            return powers_W

    def __len__(self):
        """Return the number of hours in the weather data.

        :return: number of hours in the weather data
        :rtype: int
        """
        return len(self.stringdates)

    def day_degrees_solar_gain_xls(self, file_name='calculations', heat_temperature_reference=18,  cool_temperature_reference=26):
        """Save day degrees and solar gains per window for each day in an xls file.

        :param file_name: file name without extension, default to 'calculation'
        :type file_name: str
        :param temperature_reference: reference temperature for heating day degrees
        :type heat_temperature_reference: float
        :param cool_temperature_reference: reference temperature for cooling day degrees
        :type cool_temperature_reference: float
        """
        print('Heating day degrees')
        stringdate_days, average_temperature_days, min_temperature_days, max_temperature_days, dju_heat_days = self.solar_model.site_weather_data.day_degrees(temperature_reference=heat_temperature_reference, heat=True)
        print('Cooling day degrees')
        _, _, _, _, dju_cool_days = self.solar_model.site_weather_data.day_degrees(temperature_reference=cool_temperature_reference, heat=False)

        data: list[list[str]] = [['date'], ['Tout'], ['Tout_min'], ['Tout_max'], ['dju_heat'], ['dju_cool']]
        data[0].extend(stringdate_days)
        data[1].extend(average_temperature_days)
        data[2].extend(min_temperature_days)
        data[3].extend(max_temperature_days)
        data[4].extend(dju_heat_days)
        data[5].extend(dju_cool_days)

        collectors_solar_gains_in_kWh: dict[str, list[float]] = self.powers_W()
        i = 6
        for collector_name in self.collector_names:
            data.append([collector_name+'(Wh)'])
            if len(self.collector_names) > 1:
                data[i].extend(day_averager(self.datetimes, collectors_solar_gains_in_kWh[collector_name], average=False))
            else:
                data[i].extend(day_averager(self.datetimes, collectors_solar_gains_in_kWh[collector_name], average=False))
            i += 1

        excel_workbook = pyexcelerate.Workbook()
        excel_workbook.new_sheet(file_name, data=list(map(list, zip(*data))))
        config = configparser.ConfigParser()
        config.read('setup.ini')
        result_folder = config['folders']['results']
        excel_workbook.save(mkdir_if_not_exist(result_folder + file_name + '.xlsx'))


class Mask(ABC):
    """Abstract class standing for a single zone building. It can be used once specialized."""

    _azimuth_min_max_in_rad: tuple = (-pi, pi)
    _altitude_min_max_in_rad: tuple = (0, pi / 2)

    @abstractmethod
    def passthrough(self, solar_position: SolarPosition) -> bool:
        """Determine whether a solar position of the sun in the sky defined by azimuth and altitude angles is passing through the mask (True) or not (False).

        :param solar_position: solar solar_position in the sky
        :type solar_position: SolarPosition
        :return: True if the solar position is blocked by the mask, False otherwise
        :rtype: bool
        """
        raise NotImplementedError

    def plot(self, name: str = '', axis=None, resolution: int = 40):
        """Plot the mask according to the specified max_plot_resolution and print a description of the zone.

        :param name: file_name of the plot, default to ''
        :return: the zone
        """
        azimuths_in_rad: list[float] = [Mask._azimuth_min_max_in_rad[0] + i *
                                        (Mask._azimuth_min_max_in_rad[1] - Mask._azimuth_min_max_in_rad[0]) / (resolution - 1) for i in range(resolution)]
        altitudes_in_rad = [-Mask._altitude_min_max_in_rad[0] + i *
                            (Mask._altitude_min_max_in_rad[1] - Mask._altitude_min_max_in_rad[0]) / (resolution - 1) for i in range(resolution)]
        if axis is None:
            figure, axis = plt.subplots(figsize=plot_size)
            axis.set_xlim((180 / pi * Mask._azimuth_min_max_in_rad[0], 180 / pi * Mask._azimuth_min_max_in_rad[1]))
            axis.set_ylim((-180 / pi * Mask._altitude_min_max_in_rad[0], 180 / pi * Mask._altitude_min_max_in_rad[1]))
        else:
            plt.gcf()
            axis = plt.gca()
        for azimuth_in_rad in azimuths_in_rad:
            for altitude_in_rad in altitudes_in_rad:
                if not self.passthrough(SolarPosition(azimuth_in_rad * 180 / pi, altitude_in_rad * 180 / pi)):
                    axis.scatter(180 / pi * azimuth_in_rad, 180 / pi * altitude_in_rad, c='grey', marker='.')
        axis.set_xlabel('Azimuth in degrees (0° = South)')
        axis.set_ylabel('Altitude in degrees')
        axis.set_title(name)

    @abstractmethod
    def __repr__(self) -> str:
        pass


class RectangularMask(Mask):

    def __init__(self, minmax_azimuths_deg: tuple[float, float] = None, minmax_altitudes_deg: tuple[float, float] = None) -> None:
        super().__init__()

        if minmax_azimuths_deg is None:
            self.minmax_azimuth_angles = None
        else:
            self.minmax_azimuth_angles: float = (Angle(minmax_azimuths_deg[0]), Angle(minmax_azimuths_deg[1]))

        if minmax_altitudes_deg is None:
            self.minmax_altitude_angles = None
        else:
            self.minmax_altitude_angles: float | Angle = (Angle(minmax_altitudes_deg[0]), Angle(minmax_altitudes_deg[1]))

    def passthrough(self, solar_position: SolarPosition) -> bool:
        if self.minmax_azimuth_angles is not None:
            if not (self.minmax_azimuth_angles[0] < solar_position.azimuth_angle < self.minmax_azimuth_angles[1]):
                return True
        if self.minmax_altitude_angles is not None:
            if not (self.minmax_altitude_angles[0] < solar_position.altitude_angle < self.minmax_altitude_angles[1]):
                return True
        return False

    def __repr__(self) -> str:
        return f'RectangularMask[AZ({self.minmax_azimuth_angles[0]},{self.minmax_azimuth_angles[1]}):AL({self.minmax_altitude_angles[0]},{self.minmax_altitude_angles[1]})]'


class EllipsoidalMask(Mask):

    def __init__(self, center_azimuth_altitude_in_deg1: tuple[float | Angle, float | Angle], center_azimuth_altitude_in_deg2: tuple[float | Angle, float | Angle], perimeter_azimuth_altitude_in_deg: tuple[float | Angle, float | Angle]) -> None:
        super().__init__()
        self.center_solar_position1: SolarPosition = SolarPosition(center_azimuth_altitude_in_deg1[0], center_azimuth_altitude_in_deg1[1])
        self.center_solar_position2: SolarPosition = SolarPosition(center_azimuth_altitude_in_deg2[0], center_azimuth_altitude_in_deg2[1])
        self.perimeter_solar_position: SolarPosition = SolarPosition(perimeter_azimuth_altitude_in_deg[0], perimeter_azimuth_altitude_in_deg[1])
        self.length: float | Angle = self._three_positions_length(self.perimeter_solar_position)

    def _three_positions_length(self, solar_position: SolarPosition) -> float | Angle:
        return self.center_solar_position1.distance(self.center_solar_position2) + self.center_solar_position2.distance(solar_position) + solar_position.distance(self.center_solar_position1)

    def passthrough(self, solar_position: SolarPosition) -> bool:
        return self.length > self._three_positions_length(solar_position)

    def __repr__(self) -> str:
        return f'EllipsoidalMask[centre({str(self.center_solar_position1)}),centre({str(self.center_solar_position1)}),perimeter({str(self.perimeter_solar_position)}]'


class HorizonMask(Mask):

    def __init__(self, *azimuths_altitudes_in_deg: tuple[tuple[float | Angle, float | Angle]]) -> None:
        super().__init__()
        azimuths_altitudes_in_deg = list(azimuths_altitudes_in_deg)
        if azimuths_altitudes_in_deg[0][0] != -180:
            azimuths_altitudes_in_deg.insert(0, (-180, 0))
        if azimuths_altitudes_in_deg[-1][0] != 180:
            azimuths_altitudes_in_deg.append((180, azimuths_altitudes_in_deg[0][1]))

        for i in range(1, len(azimuths_altitudes_in_deg)):
            if azimuths_altitudes_in_deg[i-1][0] > azimuths_altitudes_in_deg[i][0]:
                raise ValueError('Skyline is not increasing in azimuth at index %i' % i)
        self.solar_positions: list[SolarPosition] = [SolarPosition(Angle(azimuth_in_deg), Angle(altitude_in_deg)) for azimuth_in_deg, altitude_in_deg in azimuths_altitudes_in_deg]

    def passthrough(self, solar_position: SolarPosition) -> bool:
        index: int = None
        for i in range(1, len(self.solar_positions)):
            index = i - 1
            if self.solar_positions[i-1].azimuth_angle <= solar_position.azimuth_angle <= self.solar_positions[i].azimuth_angle:
                break
        azimuth_angle0, azimuth_angle1 = self.solar_positions[index].azimuth_angle, self.solar_positions[index+1].azimuth_angle
        altitude_angle0, altitude_angle1 = self.solar_positions[index].altitude_angle, self.solar_positions[index+1].altitude_angle
        if azimuth_angle0 == azimuth_angle1:
            return solar_position.altitude_angle > Angle(max(altitude_angle0.deg, altitude_angle1.deg))
        altitude_segment: float | Angle = Angle((altitude_angle1.deg-altitude_angle0.deg)/(azimuth_angle1.deg-azimuth_angle0.deg) * solar_position.azimuth_angle.deg + (
            altitude_angle0.deg*azimuth_angle1.deg-altitude_angle1.deg*azimuth_angle0.deg)/(azimuth_angle1.deg-azimuth_angle0.deg))
        return solar_position.altitude_angle > altitude_segment

    def __repr__(self) -> str:
        return 'HorizonMask[%s]' % (','.join([str(p) for p in self.solar_positions]))


class StackedMask(Mask):

    def __init__(self, *masks: list[Mask]) -> None:
        super().__init__()
        self.masks: list[Mask] = list(masks)

    def add(self, mask: Mask):
        if mask is not None:
            self.masks.append(mask)

    def passthrough(self, solar_position: SolarPosition) -> bool:
        for mask in self.masks:
            if mask is not None and not mask.passthrough(solar_position):
                return False
        return True

    def __repr__(self) -> str:
        return '[' + ' + '.join([str(m) for m in self.masks]) + ']'


class InvertedMask(Mask):
    def __init__(self, mask: Mask) -> None:
        super().__init__()
        self.mask: Mask = mask

    def passthrough(self, solar_position: SolarPosition) -> bool:
        if self.mask is None:
            return True
        return not self.mask.passthrough(solar_position)

    def __repr__(self) -> str:
        return f'Invert[{str(self.mask)}]'


class Collector:

    def __init__(self, solar_system: SolarSystem, name: str, exposure_deg: float, slope_deg: float, surface_m2: float, solar_factor: float = 1, min_incidence_deg: float = 0, scale_factor: int = 1, mask: Mask = None, temperature_coefficient: float = 0) -> None:
        # if not (-180 <= exposure_deg <= 180):
        #     raise ValueError(f'Incorrect exposure value: {exposure_deg}')
        # if not (0 <= slope_deg <= 180):
        #     raise ValueError(f'Incorrect slope value: {slope_deg}')
        self.solar_system: SolarSystem = solar_system
        self.solar_model: SolarModel = solar_system.solar_model
        self.datetimes: list[datetime.datetime] = self.solar_model.datetimes
        self.outdoor_temperatures: list[float] = self.solar_model.temperatures
        self.name: str = name
        if name in self.solar_system.collector_names:
            raise ValueError('Solar collector "%s" still exists' % name)
        self.exposure_deg: float = exposure_deg
        self.slope_deg: float = slope_deg
        self.surface_m2: float = surface_m2
        self.solar_factor: float = solar_factor
        self.scale_factor: float = scale_factor
        self.collector_mask: Mask = InvertedMask(RectangularMask((exposure_deg-90+min_incidence_deg, exposure_deg+90+min_incidence_deg), (max(0, slope_deg-180+min_incidence_deg), min(180, slope_deg+min_incidence_deg))))
        if mask is not None:
            self.collector_mask = StackedMask(self.collector_mask, mask)
        self.temperature_coefficient: float = temperature_coefficient
        if name in self.solar_system.collectors:
            raise ValueError(f'Collector {name} is already existing')
        self.solar_system.collectors[name] = self

    def powers_W(self, with_composites: bool = False) -> dict[RADIATION_TYPES, list[float]] | list[float]:
        powers_W: list[float] = list()

        if not with_composites:
            irradiances_W_per_m2: list[float] = self.solar_model.irradiances_W(exposure_deg=self.exposure_deg, slope_deg=self.slope_deg, scale_factor=1, specific_mask=self.collector_mask)
            irradiances_composites_W = dict()
        else:
            irradiances_W_per_m2, irradiances_composites_W = self.solar_model.irradiances_W(exposure_deg=self.exposure_deg, slope_deg=self.slope_deg, scale_factor=1, specific_mask=self.collector_mask)
            powers_components_W: dict[RADIATION_TYPES, list[float]] = {radiation_type: list() for radiation_type in irradiances_composites_W}

        for k in range(len(self.datetimes)):
            if self.temperature_coefficient > 0:
                temperature_factor: float = Collector.temperature_factor(irradiances_W_per_m2[k], self.outdoor_temperatures[k], self.temperature_coefficient)
            else:
                temperature_factor = 1
            powers_W.append(irradiances_W_per_m2[k] * self.surface_m2 * self.scale_factor * self.solar_factor * temperature_factor)
            for radiation_type in irradiances_composites_W:
                powers_components_W[radiation_type].append(irradiances_W_per_m2[k] * self.surface_m2 * self.scale_factor * self.solar_factor * temperature_factor)
        if not with_composites:
            return powers_W
        else:
            return powers_W, powers_components_W

    @staticmethod
    def temperature_factor(irradiance_W_per_m2: float, outdoor_temperature: float, temperature_coefficient: float):
        TaNOCT: float = 46  # in °Celsius
        cell_temperature: float = outdoor_temperature + irradiance_W_per_m2 / 800 * (TaNOCT - 20)
        if cell_temperature > 25:
            return 1 - temperature_coefficient * max(cell_temperature - 25, 0)
        else:
            return 1

    def __str__(self):
        string: str = 'Collector "%s" (EXP:%g°, SLO:%g°) with a surface = %ix%gm2 and a solar factor = %g' % (
            self.name, self.exposure_deg, self.slope_deg, self.scale_factor, self.surface_m2, self.solar_factor)
        if self.collector_mask is not None:
            string += ', has a specific mask: ' + str(self.collector_mask)
        if self.temperature_coefficient != 0:
            string += ' (PV collector with a temperature coefficient = %g%%)' % (100*self.temperature_coefficient)
        return string


class PVplant:

    def __init__(self, solar_model: SolarModel, exposure_deg: float, slope_deg: float, mount_type: MOUNT_TYPES, distance_between_arrays_m: float = None, number_of_panels: int = None, peak_power_kW: float = None, surface_pv_m2: float = None, number_of_panels_per_array: float = None, panel_width_m: float = 1, panel_height_m: float = 1.7, pv_efficiency: float = 0.2, number_of_cell_rows: float = 10, temperature_coefficient: float = 0.0035) -> None:

        self.solar_model: SolarModel = solar_model
        self.solar_system: SolarSystem = SolarSystem(self.solar_model)

        if exposure_deg is None or slope_deg is None:
            print('Compute best angle')
            exposure_deg, slope_deg = solar_model.best_angles()
        self.exposure_deg: float = exposure_deg
        self.exposure_rad: float = radians(exposure_deg)
        self.slope_deg: float = slope_deg
        self.slope_rad: float = radians(slope_deg)

        self.panel_width_m: float = panel_width_m
        self.panel_height_m: float = panel_height_m
        self.panel_surface_m2: float = panel_width_m * panel_height_m
        self.pv_efficiency: float = pv_efficiency

        self.mount_type: MOUNT_TYPES = mount_type

        if mount_type == MOUNT_TYPES.PLAN:
            if distance_between_arrays_m is None:
                self.distance_between_arrays_m: float = panel_height_m
            else:
                self.distance_between_arrays_m: float = max(distance_between_arrays_m, panel_height_m)
        else:
            if distance_between_arrays_m is None:
                self.distance_between_arrays_m: float = panel_height_m
            else:
                self.distance_between_arrays_m = distance_between_arrays_m

        if peak_power_kW is None and surface_pv_m2 is None and number_of_panels is None:
            raise ValueError('At one among number of panels, peak power or total surface of photovoltaic panels must be provided')
        if number_of_panels is not None:
            self.number_of_panels: int = number_of_panels
        elif surface_pv_m2 is not None:
            self.number_of_panels: int = ceil(surface_pv_m2 / self.panel_surface_m2)
            self.surface_pv_m2 = self.number_of_panels * self.panel_surface_m2
        else:
            self.number_of_panels: int = round(peak_power_kW / self.pv_efficiency / self.panel_surface_m2)
        self.peak_power_kW: float = self.number_of_panels * self.panel_surface_m2 * self.pv_efficiency
        self.surface_pv_m2: float = self.number_of_panels * self.panel_surface_m2

        if number_of_panels_per_array is None:
            self.number_of_panels_per_array = round(sqrt(self.number_of_panels))
        else:
            self.number_of_panels_per_array = number_of_panels_per_array
        self.array_width_m: float = self.number_of_panels_per_array * self.panel_width_m
        self.array_surface_in_m2 = self.array_width_m * self.panel_height_m

        self.number_of_cell_rows = number_of_cell_rows
        self.temperature_coefficient = temperature_coefficient

        self.number_of_panels_per_array: int = floor(self.array_width_m / self.panel_width_m)
        self.array_surface_in_m2: float = self.number_of_panels_per_array * self.panel_surface_m2

        self.n_panels: dict[str, int] = {'front_clear': 0, 'front_shadow': 0, 'rear_clear': 0, 'rear_shadow': 0}
        if self.mount_type == MOUNT_TYPES.PLAN:
            self.n_panels['front_clear'] = self.number_of_panels
            self.ground_surface_m2 = self.number_of_panels * self.panel_surface_m2 * abs(cos(self.slope_rad))

        elif self.mount_type == MOUNT_TYPES.FLAT:
            number_of_complete_arrays: int = floor(self.number_of_panels / self.number_of_panels_per_array)
            if number_of_complete_arrays == 0:
                self.n_panels['front_clear'] += self.number_of_panels
            else:
                self.n_panels['front_clear'] += self.number_of_panels_per_array
                self.n_panels['front_shadow'] += self.number_of_panels_per_array * (number_of_complete_arrays-1)
                self.n_panels['front_shadow'] += self.number_of_panels - self.number_of_panels_per_array * number_of_complete_arrays

        elif self.mount_type == MOUNT_TYPES.BACK2BACK:
            if distance_between_arrays_m < abs(self.panel_height_m * cos(self.slope_rad)) and self.number_of_panels > 1:
                print('The distance between arrays is too short')
                self.number_of_panels = 0
            is_an_unpaired_panel: int = self.number_of_panels % 2
            number_of_panel_pairs: int = self.number_of_panels // 2

            number_of_complete_panel_paired_arrays: int = number_of_panel_pairs // self.number_of_panels_per_array
            number_of_incomplete_paired_panels: int = number_of_panel_pairs % self.number_of_panels_per_array
            if number_of_complete_panel_paired_arrays > 0:  # there are several arrays of paired panels
                self.n_panels['front_clear'] += self.number_of_panels_per_array
                self.n_panels['rear_clear'] += self.number_of_panels_per_array
                self.n_panels['front_shadow'] += is_an_unpaired_panel
            else:  # there is only one array of paired panels
                self.n_panels['front_clear'] += number_of_incomplete_paired_panels
                self.n_panels['rear_clear'] += number_of_incomplete_paired_panels
                self.n_panels['front_clear'] += is_an_unpaired_panel
            remaining_panels_paired: int = (self.number_of_panels - self.number_of_panels_per_array*2 - is_an_unpaired_panel) / 2
            if remaining_panels_paired > 0:  # there are incomplete pairs of panels at the back
                self.n_panels['rear_shadow'] += remaining_panels_paired
                self.n_panels['front_shadow'] += remaining_panels_paired

        self.outdoor_temperatures: list[float] = self.solar_model.temperatures
        self.temperature_coefficient: float = temperature_coefficient
        self.number_of_cell_rows: float | Angle = number_of_cell_rows
        self.datetimes: list[datetime.datetime] = self.solar_model.datetimes
            
        self.cell_row_surface_in_m2: float = self.panel_surface_m2 / self.number_of_cell_rows
        if self.n_panels['front_clear'] > 0:
            Collector(self.solar_system, 'front_clear', exposure_deg=self.exposure_deg, slope_deg=slope_deg, surface_m2=self.cell_row_surface_in_m2, solar_factor=self.pv_efficiency, scale_factor=self.number_of_cell_rows * self.n_panels['front_clear'], temperature_coefficient=self.temperature_coefficient)
        if self.n_panels['rear_clear'] > 0:
            Collector(self.solar_system, 'rear_clear', exposure_deg=self.exposure_deg+180, slope_deg=slope_deg, surface_m2=self.cell_row_surface_in_m2, solar_factor=self.pv_efficiency, scale_factor=self.number_of_cell_rows * self.n_panels['rear_clear'], temperature_coefficient=self.temperature_coefficient)
        if self.n_panels['front_shadow'] > 0:
            for k in range(self.number_of_cell_rows):
                hi: float = (2*k+1)/(2*self.number_of_cell_rows) * self.panel_height_m
                minimum_sun_visible_altitude_in_deg: float = degrees(atan2(sin(self.slope_rad), (self.distance_between_arrays_m/(self.panel_height_m-hi)+cos(self.slope_rad))))
                row_mask = InvertedMask(RectangularMask(minmax_azimuths_deg=(self.exposure_deg-90, self.exposure_deg+90), minmax_altitudes_deg=(minimum_sun_visible_altitude_in_deg, 180)))
                Collector(self.solar_system, 'front_shadow%i' % k, exposure_deg=self.exposure_deg, slope_deg=self.slope_deg, surface_m2=self.cell_row_surface_in_m2, solar_factor=self.pv_efficiency, scale_factor=self.n_panels['front_shadow'], mask=row_mask, temperature_coefficient=self.temperature_coefficient)
        if self.n_panels['rear_shadow'] > 0:
            for k in range(self.number_of_cell_rows):
                hi: float = (2*k+1)/(2*self.number_of_cell_rows) * self.panel_height_m
                minimum_sun_visible_altitude_in_deg: float = degrees(atan2(sin(self.slope_rad), (self.distance_between_arrays_m/(self.panel_height_m-hi)+cos(self.slope_rad))))
                row_mask = InvertedMask(RectangularMask(minmax_azimuths_deg=(self.exposure_deg+180-90, self.exposure_deg+180+90), minmax_altitudes_deg=(minimum_sun_visible_altitude_in_deg, 180)))
                Collector(self.solar_system, 'rear_shadow%i' % k, exposure_deg=self.exposure_deg+180, slope_deg=self.slope_deg, surface_m2=self.cell_row_surface_in_m2, solar_factor=self.pv_efficiency, scale_factor=self.n_panels['rear_shadow'], mask=row_mask, temperature_coefficient=self.temperature_coefficient)

    def powers_W(self, gather_collectors: bool = True) -> list[float] | dict[str, dict[str, list[float]]]:
        return self.solar_system.powers_W(gather_collectors=gather_collectors)

    def __str__(self) -> str:
        string = 'The PV system is composed of %i panels for a total PV surface = %gm2\n' % (self.number_of_panels, self.surface_pv_m2)
        string += 'A PV panel (EXP: %g°, SLO: %g°)' % (self.exposure_deg, self.slope_deg)
        string += ' is W:%gm x H:%gm (%gm2) with an efficiency of %g%% and cells distributed in %i rows\n' % (self.panel_width_m, self.panel_height_m, self.panel_surface_m2, 100 * self.pv_efficiency, self.number_of_cell_rows)
        string += 'The mount type is %s with a peak power of %gkW with a distance between arrays of %gm\n' % (
            self.mount_type.name, self.peak_power_kW, self.distance_between_arrays_m)
        string += 'There are:\n - %i front facing panels not shadowed\n' % self.n_panels['front_clear']
        if self.n_panels['front_shadow'] > 0:
            string += ' - %i front facing panels shadowed\n' % self.n_panels['front_shadow']
        if self.n_panels['rear_shadow'] > 0:
            string += ' - %i rear facing panels shadowed\n' % self.n_panels['rear_shadow']
        if self.n_panels['rear_clear'] > 0:
            string += ' - %i rear facing panels not shadowed\n' % self.n_panels['rear_clear']
        return string

    def best_angles(self, distance_between_arrays_m: float = None, mount_type: MOUNT_TYPES = MOUNT_TYPES.PLAN, error_message: bool = False, initial_exposure_deg: float = 0, initial_slope_deg: float = 180) -> dict[str, float]:
        neighborhood: list[tuple[float, float]] = [(-1, 0), (-1, 1), (-1, -1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        taboo = list()
        exposure_slope_in_deg_candidate: tuple[float, float] = (initial_exposure_deg, initial_slope_deg)
        best_exposure_slope_in_deg = tuple(exposure_slope_in_deg_candidate)
        best_total_production_in_Wh = sum(self.powers_W(
            exposure_slope_in_deg_candidate[0], exposure_slope_in_deg_candidate[1], distance_between_arrays_m, mount_type, error_message))
        initial_production_Wh = best_total_production_in_Wh
        taboo.append(exposure_slope_in_deg_candidate)

        improvement = True
        while improvement:
            improvement = False
            for neighbor in neighborhood:
                exposure_slope_in_deg_candidate = (best_exposure_slope_in_deg[0] + neighbor[0], best_exposure_slope_in_deg[1] + neighbor[1])
                exposure_in_deg: float = exposure_slope_in_deg_candidate[0]
                slope_in_deg: float = exposure_slope_in_deg_candidate[1]
                if -180 <= exposure_in_deg <= 180 and 0 <= slope_in_deg <= 180 and exposure_slope_in_deg_candidate not in taboo:
                    taboo.append(exposure_slope_in_deg_candidate)
                    productions_in_Wh = sum(self.powers_W(
                        exposure_slope_in_deg_candidate[0], exposure_slope_in_deg_candidate[1], distance_between_arrays_m, mount_type, error_message))
                    if productions_in_Wh > best_total_production_in_Wh:
                        improvement = True
                        best_exposure_slope_in_deg: tuple[float, float] = exposure_slope_in_deg_candidate
                        best_total_production_in_Wh: float = productions_in_Wh
        return {'exposure_deg': best_exposure_slope_in_deg[0], 'slope_deg': best_exposure_slope_in_deg[1], 'best_production_kWh': best_total_production_in_Wh / 1000, 'initial_slope_deg': initial_slope_deg, 'initial_slope_deg': initial_slope_deg, 'initial_production_kWh': initial_production_Wh / 1000, 'mount_type': mount_type.name, 'distance_between_arrays_m': distance_between_arrays_m}

    def print_month_hour_power_W(self):
        powers_W = self.powers_W()
        print('total electricity production: %.0fkWh' % (sum(powers_W)/1000))

        month_hour_occurrences: dict[int, dict[int, int]] = [[0 for j in range(24)] for i in range(12)]
        month_hour_productions_in_Wh: dict[int, dict[int, float]] = [[0 for j in range(24)] for i in range(12)]
        table = prettytable.PrettyTable()
        table.set_style(prettytable.TableStyle.MSWORD_FRIENDLY)
        labels: list[str] = ["month#", "cumul"]
        labels.extend(['%i:00' % i for i in range(24)])
        table.field_names = labels
        for i, dt in enumerate(self.datetimes):
            month_hour_occurrences[dt.month-1][dt.hour] += 1
            month_hour_productions_in_Wh[dt.month-1][dt.hour] += powers_W[i]
        for month in range(12):
            number_of_month_occurrences: int = sum(month_hour_occurrences[month-1])
            if number_of_month_occurrences != 0:
                total: str = '%.fkWh' % round(sum(month_hour_productions_in_Wh[month-1]))
            else:
                total: str = '0'
            month_row = [month, total]
            for hour in range(24):
                if month_hour_occurrences[month][hour] != 0:
                    month_row.append('%g' % round(month_hour_productions_in_Wh[month][hour] / month_hour_occurrences[month][hour]))
                else:
                    month_row.append('0.')
            table.add_row(month_row)
        print('Following PV productions are in Wh:')
        print(table)