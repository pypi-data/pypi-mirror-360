from matplotlib.colorbar import Colorbar
import configparser
import math
import copy
import numpy
import hashlib
import prettytable
import sys
import os
import os.path
import shutil
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import matplotlib.image as mplimg
from psychrochart import PsychroChart
from matplotlib.colors import LinearSegmentedColormap
#from typing import Any, Self
from datetime import datetime
from matplotlib import cm
from matplotlib.ticker import PercentFormatter
from windrose import WindAxes, WindroseAxes
from .weather import SiteWeatherData
from .solar import SolarModel, Collector, PVplant, MOUNT_TYPES, SolarSystem, RectangularMask, InvertedMask
from .components import Composition
from .library import DIRECTIONS_SREF, SLOPES
from .timemg import datetime_to_stringdate
from .comfort import OutdoorTemperatureIndices
from .utils import Averager
from ..ecommunity.indicators import year_autonomy, NEEG_percent, self_consumption, self_sufficiency


class ParametricData:
    """Clonable configuration of the lambda-house"""

    configparser_obj = None

    @staticmethod
    def setup(*references: tuple[str]) -> configparser.ConfigParser:
        """Read a configuration file and give an easy access to the configuration parameters.
        A parameter value can be temporarily masked by another value and restored at any time"""
        if ParametricData.configparser_obj is None:
            _setup = configparser.ConfigParser()
            _setup.read('setup.ini')  # read configuration from the setup.ini file
            ParametricData.configparser_obj: configparser.ConfigParser = _setup
        configparser_obj = copy.copy(ParametricData.configparser_obj)
        for ref in references:  # flatten sections
            configparser_obj: configparser.SectionProxy = configparser_obj[ref]
        return configparser_obj  # returns different ConfigParser related to the elevation

    def __init__(self) -> None:
        """Initialize a parametric data object
        """
        self._sections: dict[str, list[str]] = dict()
        self._current_section: str = 'site'
        self._selected_parametric: str = None
        self._current_parametric_data: dict[str, float] = dict()
        self._nominal_parametric_data: dict[str, float] = dict()
        self._parametric_possible_values: dict[str, tuple[str, list[float]]] = dict()
        self._given_data: dict[str, list[str]] = dict()
        self._functions: dict[str, callable] = dict()
        self._resulting_data = dict()

    @property
    def signature(self) -> int:
        """generate a signature representing the current parameter values

        :return: a hash code
        :rtype: int
        """
        _signature: str = ''
        for v in self._nominal_parametric_data:
            _signature += str(self(v))
        return int.from_bytes(hashlib.sha256(_signature.encode()).digest()[:8], 'big')

    def parametric(self, name: str = None) -> list[float]:
        if name is None:
            return self._parametric_possible_values.keys()
        return self._parametric_possible_values[name]

    def select(self, name: str) -> None:
        if name in self._parametric_possible_values:
            self._selected_parametric = name
        else:
            raise ValueError(f"parametric {name} not found")

    def section(self, name: str) -> None:
        self._current_section = name
        if name not in self._sections:
            self._sections[name] = list()

    def sections(self) -> list[str]:
        return list(self._sections.keys())

    def given(self, name: str, data, *data_value_domain: list[float]) -> None:
        if len(data_value_domain) > 0:  # this is a new parametric value
            if name in self._nominal_parametric_data:
                print('warning: redefinition of value domain for parametric %s' % name)
                data_value_domain.pop(name)
            data_value_domain = list(data_value_domain)
            if data not in data_value_domain:
                data_value_domain.append(data)
            self._parametric_possible_values[name] = sorted(data_value_domain)  # add the value to the list of possible values
            if name not in self._nominal_parametric_data:
                self._nominal_parametric_data[name] = data
                self._current_parametric_data[name] = data
                self._sections[self._current_section].append(name)
        elif name in self._parametric_possible_values:
            self._current_parametric_data[name] = data
        else:  # this is not a parametric value
            if name not in self._given_data:
                self._given_data[name] = data
                if self._current_section not in self._sections:
                    self._sections[self._current_section] = list()
                self._sections[self._current_section].append(name)
            else:
                raise ValueError(f"given data {name} cannot be redefined")

    def function(self, name: str, a_function: callable) -> None:
        if name not in self._functions:
            self._functions[name] = a_function
            self._sections[self._current_section].append(name)
        else:
            raise ValueError(f"function {name} already exists")

    def result(self, name: str, data) -> None:
        self._resulting_data[name] = data
        self._sections[self._current_section].append(name)

    def __eq__(self, other_configuration: "Self") -> bool:
        return self.signature == other_configuration.signature

    def __call__(self, name: str, nominal: bool = False) -> float:
        if name in self._functions:
            return self._functions[name](self)
        elif name in self._nominal_parametric_data:
            if not nominal and name in self._current_parametric_data:
                return self._current_parametric_data[name]
            else:
                return self._nominal_parametric_data[name]
        elif name in self._given_data:
            return self._given_data[name]
        elif name in self._given_data:
            return self._given_data[name]
        elif name in self._resulting_data:
            return self._resulting_data[name]
        elif name.endswith('_kW'):
            alternate_name: str = name[:-3] + '_W'
            value_W: float = self(alternate_name)
            return [_ / 1000 for _ in value_W]
        elif name.endswith('_kWh'):
            alternate_name: str = name[:-4] + '_W'
            value_W = self(alternate_name)
            return sum(value_W) / 1000
        else:
            print(self, sys.stderr)
            raise ValueError(f"data {name} not found")

    def __contains__(self, name) -> bool:
        return name in self._nominal_parametric_data or name in self._functions or name in self._given_data or name in self._resulting_data

    def copy(self) -> "Self":
        """Clone a configuration, including the temporary parameters

        :return: a cloned configuration
        :rtype: Configuration
        """
        site_weather_data: SiteWeatherData = self('site_weather_data')
        lbd_copy = LambdaParametricData(site_weather_data.location, site_weather_data.latitude_deg_north, site_weather_data.longitude_deg_east, self('year'), site_weather_data.albedo, site_weather_data.pollution)
        lbd_copy._current_section = self._current_section
        lbd_copy._selected_parametric = self._selected_parametric
        lbd_copy._nominal_parametric_data = copy.deepcopy(self._nominal_parametric_data)
        lbd_copy._current_parametric_data = copy.deepcopy(self._current_parametric_data)
        lbd_copy._parametric_possible_values = copy.deepcopy(self._parametric_possible_values)
        lbd_copy._functions = copy.deepcopy(self._functions)
        lbd_copy._resulting_data = copy.deepcopy(self._resulting_data)
        return lbd_copy

    def reset(self, parametric: str = None) -> None:
        """restore the nominal value for a parameter

        :param name: the parameter name
        :type name: str
        """
        self._resulting_data.clear()
        if parametric is None:
            self._current_parametric_data.clear()
        else:
            if parametric in self._current_parametric_data:
                self._current_parametric_data.pop(parametric)

    def __iter__(self) -> "Self":
        """Make it possible to iterate over the parametric value of the last selected parameter thanks to the parametric method
        """
        self.n = 0
        return self

    def __next__(self) -> "Any":
        """Skip for first parametric value of the selected parameter to the last one with a for loop. Once the latest value is reached, the nominal value
        is restored

        :raises StopIteration: raised when last value is reached
        :return: the next parametric value if exists
        :rtype: Any
        """
        value_domain: tuple[str, list[float]] = self._parametric_possible_values[self._selected_parametric]
        if self.n < len(value_domain):
            value: str | list[float] = value_domain[self.n]
            self._current_parametric_data[self._selected_parametric] = value
            self.n += 1
            return value
        else:
            self.reset(self._selected_parametric)
            # self._current_parametric = None
            raise StopIteration

    def __data_type(self, name: str) -> str:
        if name in self._given_data:
            return 'given'
        elif name in self._parametric_possible_values:
            return 'parametric'
        elif name in self._functions:
            return 'function'
        elif name in self._resulting_data:
            return 'result'
        else:
            raise ValueError(f"data {name} not found")

    def __given_str(self, name: str) -> str:
        return '- given "%s" = ' % (name) + self.__str_shortener(self._given_data[name])

    def __parametric_str(self, name: str) -> str:
        return '- parametric "%s" = ' % (name) + self.__str_shortener(self(name)) + '[nominal: ' + str(self._nominal_parametric_data[name]) + '] in {' + ', '.join([str(v) for v in self._parametric_possible_values[name]]) + '}'

    def __result_str(self, name: str) -> str:
        return '- result "%s" = ' % (name) + self.__str_shortener(self._resulting_data[name])

    def __function_str(self, name: str) -> str:
        return '- function "%s" = ' % (name) + self.__str_shortener(self._functions[name](self))

    def __str_shortener(self, data: "Any", max_length: int = 100) -> str:
        string: str = str(data)
        if len(string) > max_length:
            return string[0:max_length] + '...'
        else:
            return string

    def __str__(self) -> str:
        string: str = ''
        for section_name in self._sections:
            string += '######### Section %s #########\n' % section_name
            for data_name in self._sections[section_name]:
                if self.__data_type(data_name) == 'given':
                    string += self.__given_str(data_name) + '\n'
                elif self.__data_type(data_name) == 'parametric':
                    string += self.__parametric_str(data_name) + '\n'
                elif self.__data_type(data_name) == 'result':
                    string += self.__result_str(data_name) + '\n'
                elif self.__data_type(data_name) == 'function':
                    string += self.__function_str(data_name) + '\n'
        return string


# set the plotting preferences
plot_size: tuple[int, int] = (int(ParametricData.setup('sizes', 'width')), int(ParametricData.setup('sizes', 'height')))


class LambdaParametricData(ParametricData):

    def __init__(self, site_weather_data: SiteWeatherData, year: int) -> None:
        super().__init__()

        self.full_site_weather_data: SiteWeatherData = site_weather_data
        self.given('full_site_weather_data', self.full_site_weather_data)
        print(site_weather_data)
        self.site_weather_data: SiteWeatherData = site_weather_data.excerpt(from_stringdate='1/1/%i' % year, to_stringdate='31/12/%i' % year)
        self.given('site_weather_data', self.site_weather_data)
        self.datetimes: list[datetime] = self.site_weather_data.datetimes
        self.given('cloudiness_percentage', self.site_weather_data.get('cloudiness'))
        self.given('precipitations_mm_per_hour', self.site_weather_data.get('precipitation'))
        self.given('rains_mm_per_hour', self.site_weather_data.get('rain'))
        self.given('snowfalls_mm_per_hour', self.site_weather_data.get('snowfall'))
        self.given('outdoor_temperatures_deg', self.site_weather_data.get('temperature'))
        self.given('pressures_hPa', self.site_weather_data.get('pressure'))
        self.given('humidities_percentage', self.site_weather_data.get('humidity'))
        self.given('wind_directions_deg', self.site_weather_data.get('wind_direction_in_deg'))
        self.given('wind_speeds_m_per_s', self.site_weather_data.get('wind_speed_m_per_s'))
        self.given('absolute_humidity_kg_kg', self.site_weather_data.absolute_humidity_kg_per_kg())
        self.given('winter_hvac_trigger_temperature_deg', 18)
        self.given('summer_hvac_trigger_temperature_deg', 25)
        self.given('year', year)
        self.solar_model = SolarModel(self.site_weather_data)
        self.given('solar_model', self.solar_model)

        self.section('house')
        self.given('total_living_surface_m2', 100)
        self.given('floor_height_m', 2.5)
        self.given('shape_factor', 1, .25, .5, .75, 1, 1.25, 1.5, 1.75, 2, 3)
        self.given('number_of_floors', 1, 2, 3)

        self.given('glass_composition_in_out', [('glass', 4e-3), ('air', 6e-3), ('glass', 4e-3)])
        self.given('thickness_m', 10e-2, 0, 2e-2, 5e-2, 10e-2, 15e-2, 20e-2, 25e-2, 30e-2,)
        self.given('solar_factor', 0.8)

        self.function('floor_surface_m2', lambda configuration: configuration('total_living_surface_m2') / configuration('number_of_floors'))
        self.function('wall_composition_in_out', lambda configuration: [('concrete', 14e-2), ('plaster', 15e-3), ('polystyrene', configuration('thickness_m'))])
        self.function('roof_composition_in_out', lambda configuration: [('plaster', 30e-3), ('polystyrene', configuration('thickness_m')), ('concrete', 13e-2)])
        self.function('ground_composition_in_out', lambda configuration: [('concrete', 13e-2), ('polystyrene', configuration('thickness_m')), ('gravels', 20e-2)])
        self.function('air_volume_m3', lambda configuration: configuration('total_living_surface_m2') * configuration('floor_height_m'))
        self.function('building_height_m', lambda configuration: configuration('number_of_floors') * configuration('floor_height_m'))
        self.function('wall_surface_m2', lambda configuration: configuration('floor_height_m') * ((2 - configuration('glazing_ratio_north') - configuration('glazing_ratio_south')) * math.sqrt(configuration('number_of_floors') * configuration('total_living_surface_m2') * configuration('shape_factor')) + (2 - configuration('glazing_ratio_west') - configuration('glazing_ratio_east')) * math.sqrt(configuration('number_of_floors') * configuration('total_living_surface_m2') / configuration('shape_factor'))))
        self.function('largest_side_length_m', lambda configuration: math.sqrt(configuration('total_living_surface_m2') * configuration('shape_factor') / configuration('number_of_floors')))
        self.function('smallest_side_length_m', lambda configuration: math.sqrt(configuration('total_living_surface_m2') / (configuration('shape_factor') * configuration('number_of_floors'))))

        self.section('windows')
        self.given('offset_exposure_deg', 0, -45, -30, -15, 0, 15, 30, 45)
        self.given('glazing_ratio_north', .1, 0.05, .2, .4, .6, .8)
        self.given('glazing_ratio_west', .1, 0.05, .2, .4, .6, .8)
        self.given('glazing_ratio_east', .1, 0.05, .2, .4, .6, .8)
        self.given('glazing_ratio_south', .1, 0.05, .2, .4, .6, .8)
        
        self.function('glazing_surface_north_m2', lambda configuration: configuration('floor_height_m') * configuration('glazing_ratio_north') * math.sqrt(configuration('number_of_floors') * configuration('total_living_surface_m2') * configuration('shape_factor')))
        self.function('glazing_surface_south_m2', lambda configuration: configuration('floor_height_m') * configuration('glazing_ratio_south') * math.sqrt(configuration('number_of_floors') * configuration('total_living_surface_m2') * configuration('shape_factor')))
        self.function('glazing_surface_west_m2', lambda configuration: configuration('floor_height_m') * configuration('glazing_ratio_west') * math.sqrt(configuration('number_of_floors') * configuration('total_living_surface_m2') / configuration('shape_factor')))
        self.function('glazing_surface_east_m2', lambda configuration: configuration('floor_height_m') * configuration('glazing_ratio_east') * math.sqrt(configuration('number_of_floors') * configuration('total_living_surface_m2') / configuration('shape_factor')))
        self.function('glazing_surface_m2', lambda configuration: configuration('floor_height_m') * ((configuration('glazing_ratio_north') + configuration('glazing_ratio_south')) * math.sqrt(configuration('number_of_floors') * configuration('total_living_surface_m2') * configuration('shape_factor')) + (configuration('glazing_ratio_east') + configuration('glazing_ratio_west')) * math.sqrt(configuration('number_of_floors') * configuration('total_living_surface_m2') / configuration('shape_factor'))))
        self.given('south_solar_protection_angle_deg', 0, 15, 30, 35, 40, 45)

        self.section('HVAC')
        self.given('heating_setpoint_deg', 21, 18, 19, 20, 22, 23)
        self.given('delta_temperature_absence_mode_deg', 3, 0, 1, 2, 3, 4)
        self.given('cooling_setpoint_deg', 24, 23, 24, 25, 27, 28, 29)
        self.given('hvac_hour_delay_for_trigger_h', 24)
        self.given('hvac_COP', 3)
        self.given('final_to_primary_energy_coefficient', 2.54)
        self.given('air_renewal_presence_vol_per_h', 3, .5, 1, 3, 5)
        self.given('air_renewal_absence_vol_per_h', 1)
        self.given('ventilation_heat_recovery_efficiency', 0.6, 0, .25, .5, .75, .9)
        self.section('PV')
        self.given('PV_surface_m2', 20, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22)
        self.given('PV_efficiency', 0.20)
        best_exposure_deg, best_slope_deg = self.solar_model.best_angles()
        self.given('best_exposure_deg', best_exposure_deg)
        self.given('best_slope_deg', best_slope_deg)

        self.section('inhabitants')
        self.given('occupancy_schema', {(1, 2, 3, 4, 5): {(18, 7): 4}, (6, 7): {(0, 24): 4}})  # days of weeks (1=Monday,...), period (start. hour, end. hour) : avg occupancy
        self.given('average_occupancy_electric_gain_w', 50)
        self.given('average_occupancy_metabolic_gain_w', 100)
        self.given('average_permanent_electric_gain_w', 200)
        self.given('air_renewal_overheat_threshold_deg', 26)
        self.given('air_renewal_overheat', 5)

        self.section('weather')
        self.given('datetimes', self.site_weather_data.datetimes)
        self.given('average_wind_speed_m_per_s', sum(self('wind_speeds_m_per_s')) / len(self))
        self.given('average_outdoor_temperature_deg', sum(self.site_weather_data.get('temperature')) / len(self))
        self.given('smooth_outdoor_temperatures_for_hvac_periods_deg', Averager(self.site_weather_data.get('temperature')).inertia_filter())

        no_heating_period = numpy.where(numpy.array(self('smooth_outdoor_temperatures_for_hvac_periods_deg')) > self('winter_hvac_trigger_temperature_deg'))[0]
        # self.given('no_heating_period', no_heating_period)
        if len(self) - self('hvac_hour_delay_for_trigger_h') - len(no_heating_period) > 0:
            if len(no_heating_period) > 0:
                i_end_heating: int = no_heating_period[0]
                i_start_heating: int = no_heating_period[-1]
                if i_start_heating.item() < i_end_heating.item():
                    self.given('heating_period_indices', (i_start_heating.item(), i_end_heating.item()))
                else:
                    self.given('heating_period_indices', (0, i_end_heating.item(), i_start_heating.item(), len(self)))
            else:
                self.given('heating_period_indices', (0, 0))
        if len(self('heating_period_indices')) == 2:
            self.given('heating_period_duration_h', self('heating_period_indices')[1] - self('heating_period_indices')[0])
        else:
            self.given('heating_period_duration_h',  self('heating_period_indices')[1] - self('heating_period_indices')[0] + self('heating_period_indices')[3] - self('heating_period_indices')[2])
        self.heating_period_indices: tuple[int, int] = self('heating_period_indices')
        self.heating_period_duration_h: float = self('heating_period_duration_h')

        no_cooling_period = numpy.where(numpy.array(self('smooth_outdoor_temperatures_for_hvac_periods_deg')) > self('summer_hvac_trigger_temperature_deg'))[0]
        if len(no_cooling_period) > self('hvac_hour_delay_for_trigger_h'):
            i_start_cooling: int = no_cooling_period[0]
            i_end_cooling: int = no_cooling_period[-1]
            # self.given('cooling_period_indices', (i_start_cooling.item(), i_end_cooling.item()))
            if i_start_cooling.item() < i_end_cooling.item():
                self.given('cooling_period_indices', (i_start_cooling.item(), i_end_cooling.item()))
            else:
                self.given('cooling_period_indices', (0, i_end_cooling.item(), i_start_cooling.item(), len(self)))
        else:
            self.given('cooling_period_indices', (0, 0))
        if len(self('cooling_period_indices')) == 2:
            self.given('cooling_period_duration_h', self('cooling_period_indices')[1] - self('cooling_period_indices')[0])
        else:
            self.given('cooling_period_duration_h',  self('cooling_period_indices')[1] - self('cooling_period_indices')[0] + self('cooling_period_indices')[3] - self('cooling_period_indices')[2])
        self.cooling_period_indices: tuple[int, int] = self('cooling_period_indices')
        self.cooling_period_duration_h: float = self('cooling_period_duration_h')

        self.PV_plant = PVplant(self.solar_model, self('best_exposure_deg'), self('best_slope_deg'), mount_type=MOUNT_TYPES.PLAN, number_of_panels_per_array=10, panel_width_m=1, panel_height_m=1, pv_efficiency=self('PV_efficiency'), temperature_coefficient=0.0035, distance_between_arrays_m=1, surface_pv_m2=self('PV_surface_m2'))
        self.given('best_PV_plant_powers_W', self.PV_plant.powers_W())
        self.PV_plant_powers_W: list[float] = self.PV_plant.powers_W()

        self.unit_solar_gain_system = SolarSystem(self.solar_model)
        for direction in DIRECTIONS_SREF:
            Collector(self.unit_solar_gain_system, direction.name, exposure_deg=direction.value, slope_deg=SLOPES.VERTICAL.value, surface_m2=1, solar_factor=1)
        Collector(self.unit_solar_gain_system, 'HORIZONTAL_UP', exposure_deg=DIRECTIONS_SREF.SOUTH.value, slope_deg=SLOPES.HORIZONTAL_UP.value, surface_m2=1, solar_factor=1)
        self.given('unit_canonic_solar_powers_W', self.unit_solar_gain_system.powers_W(gather_collectors=False))
        self.unit_canonic_solar_powers_W: list[float] = self.unit_solar_gain_system.powers_W(gather_collectors=False)

        occupancy_schema: float = self('occupancy_schema')
        occupancy = list()
        for a_datetime in self('datetimes'):
            day_of_week = a_datetime.isoweekday()
            hour_in_day = a_datetime.hour

            for days in occupancy_schema:
                if day_of_week in days:
                    for period in occupancy_schema[days]:
                        if period[0] <= hour_in_day <= period[1]:
                            occupancy.append(occupancy_schema[days][period])
                        elif hour_in_day >= period[0] or hour_in_day <= period[1]:
                            occupancy.append(occupancy_schema[days][period])
                        else:
                            occupancy.append(0)
        self.given('occupancy', occupancy)
        self.occupancy: list[float] = self('occupancy')

    def __len__(self) -> int:
        return len(self.datetimes)

    def __str__(self) -> str:
        string = str(super().__str__())
        string += f'{self.__class__.__name__} with {len(self)} samples\n'
        return string


def sort_values(datetimes, values) -> list[float]:
    """sort the time series defined by the lists datetimes and values according to the values, with descending order.

    :param datetimes: times corresponding to values
    :type datetimes: list[datetime]
    :param values: values to be sorter
    :type values: list[float]
    :return: both input series sorted
    :rtype: list[datetime], list[float]
    """
    values_array = numpy.array(values)
    months_array = numpy.array([datetimes[i].timetuple().tm_yday/30.41666667 + 1 for i in range(len(datetimes))])
    indices = (-values_array).argsort()
    sorted_values_array = values_array[indices]
    sorted_months_array = months_array[indices]
    return sorted_months_array.tolist(), sorted_values_array.tolist()


def to_markdown_table(pretty_table) -> str:
    """
    Print a pretty table as a markdown table

    :param py:obj:`prettytable.PrettyTable` pt: a pretty table object.  Any customization
      beyond int and float style may have unexpected effects

    :rtype: str
    :returns: A string that adheres to git markdown table rules
    """
    _join = pretty_table.junction_char
    if _join != "|":
        pretty_table.junction_char = "|"
    markdown: list[str] = [row[1:-1] for row in pretty_table.get_string().split("\n")[1:-1]]
    pretty_table.junction_char = _join
    return "\n".join(markdown)


class ReportGenerator:
    def __init__(self, location: str, year: int, on_screen: bool = True) -> None:
        """Initialize the report maker

        :param lpd: House data containing simulation results
        :type lpd: Configuration
        :param on_screen: Whether to display output on screen or save to file
        :type on_screen: bool
        """
        self.on_screen: bool = on_screen
        self.original_stdout = sys.stdout

        self.figure_counter: int = 0
        if not on_screen:
            results_folder: str = LambdaParametricData.setup('folders', 'results')
            if not os.path.exists(results_folder):
                os.mkdir(results_folder)
            self.mmd_filename: str = LambdaParametricData.setup('folders', 'results') + location + "_" + str(year) + ".md"
            self.pdf_filename: str = LambdaParametricData.setup('folders', 'results') + location + "_" + str(year) + ".pdf"
            if os.path.exists(self.mmd_filename):
                os.remove(self.mmd_filename)
            if os.path.exists(self.pdf_filename):
                os.remove(self.pdf_filename)
            figures_folder: str = LambdaParametricData.setup('folders', 'results') + LambdaParametricData.setup('folders', 'figures')
            if os.path.exists(figures_folder):
                shutil.rmtree(figures_folder, ignore_errors=True)
            os.mkdir(figures_folder)
            sys.stdout = open(self.mmd_filename, 'w')
        
        self.add_text(f'# Analysis of the site "{location}" for the year {year} <a name="site"></a>')
        self.add_text('## The $\\lambda$-house principle <a name="principle"></a>')
        self.add_image("lambda.png")

        self.add_text("Pre-design stage is characterized by a known location for the construction but little ideas about the building to design. Nevertheless, this is during this stage that main directions are taken. Because engineers do not have enough data to setup simulations, they use to intervene a little during this stage. However, very impacting decisions like whether it is interesting or not to set large windows for each facade use to be taken, or what is the direction for the building? Or, for a given floor surface, is it more interesting to design a single floor building or a multiple floor one? Moreover, many local phenomena make sense only for a complete building: knowing solar radiation, knowing the albedo, knowing the cloudiness of the site, knowing the solar masks,etc... cannot be appreciated without considering a complete building.")

        self.add_text("The idea of the $\\lambda$-house is to locate a known standard house and to analyze its behavior regarding energy in order to point out the impact of possible choices on energy performances: helping to make decisions for a specific location comparatively to other known locations. By default, the $\\lambda$ house is a $100m^2$ single floor square house equipped with an invertible heat pump and a dual flow ventilation system. If the indoor temperature is passing over a limit and an habitant is present, inhabitants will open the window to preserve their comfort. See the end of the report for the list of parameters characterizing the so-called $\\lambda$-house (\"maison témoin\" in French). When a more specific house is needed, it means that the engineer has more data and can setup a simulation. The lambda house is no longer needed.")

        self.add_text("Three minimum requirements for setting up a lambda-house at a specific location has to be specified:")
        self.add_text("- a name that is used to save the results and to name the weather file")
        self.add_text('- the location of the house in terms of decimal latitude north and longitude east angles, that can be found on Google Maps for instance by right clicking on the map, or on Open Street Map')
        self.add_text("- the year for the analysis")
        self.add_text("The $\\lambda$-house code will download the weather data from 1980 from [open-meteo](https://open-meteo.com), the far solar masks made by surrounding landscape, the elevation of the defined location")
        self.figure_counter = 1

    def close(self, parameters_description: str, pdf: bool = True):
        """Close the report and save it.
        """
        self.add_text('## Features of the $\\lambda$-house <a name="features"></a>')
        self.add_text("The parameters below describe the house context. Although it is not the $\\lambda$-house philosophy, which be the same anywhere for comparison purpose, its parameters can be modified to better match a given context.")

        self.add_text('For each parameter, a list of values defined in "parametric" can be specified. They are used for parametric studies.')
        for data_description in parameters_description.split('\n'):
            self.add_text(data_description)
        sys.stdout.close()
        sys.stdout = self.original_stdout

        if pdf:   # Convert Markdown to PDF with resource path specified
            import pypandoc
            base_dir = os.path.dirname(os.path.abspath(self.mmd_filename))
            print(f"PDF generation: {self.pdf_filename}")
            output: str = pypandoc.convert_file(self.mmd_filename, 'pdf', outputfile=self.pdf_filename, extra_args=['--resource-path', base_dir])
            assert output == "", "Error during conversion"

    def add_image(self, file_name: str):
        if not self.on_screen:
            self.add_text("![](../figs/%s)" % file_name)
        else:
            image = mplimg.imread('./figs/%s' % file_name)
            plt.imshow(image)
            plt.show()

    def add_text(self, text: str, on_screen_only: bool = False, on_mmd_only: bool = False) -> None:
        """Add a text line in the report

        :param text: text to be added
        :type text: str
        """
        if not self.on_screen and (not on_mmd_only and not on_screen_only):
            print(str(text) + '\n')
            if not self.on_screen and not str(text).startswith('!'):
                print(str(text) + '\n', file=sys.stderr)
        else:
            print(str(text) + '\n')

    def add_pretty_table(self, pretty_table: prettytable.PrettyTable, on_screen_only: bool = False, on_mmd_only: bool = False):
        if self.on_screen:
            self.add_text(str(pretty_table), on_screen_only, on_mmd_only)
        else:
            self.add_text(to_markdown_table(pretty_table), on_screen_only, on_mmd_only)

    def add_figure(self, fig=None, on_screen_only: bool = False):
        """Add the last figure to the report

        :param figure_name: name of the figure used for saving, defaults to None
        :type figure_name: str, optional
        """
        if not self.on_screen and not on_screen_only:
            figure_name: str = LambdaParametricData.setup('folders', 'figures') + 'figure%i.png' % self.figure_counter
            self.figure_counter += 1
            if fig is None:
                plt.savefig(LambdaParametricData.setup('folders', 'results') + figure_name, dpi=600)
                plt.close()
            else:
                fig.write_image(LambdaParametricData.setup('folders', 'results') + figure_name, scale=2)
            self.add_text('![](%s)' % figure_name)

    def add_event_plot(self, main_data_name: str, datetimes: list, values: list):
        fig, axes = plt.subplots(figsize=plot_size)
        resolution = 20
        days_with_rain: list[str] = list()
        days: list[str] = list()
        rain_duration_h_quantity_mm_n_events: dict[tuple[float, float], int] = dict()
        rains_months_dict: dict[tuple[float, float], list[str]] = dict()
        rain_duration_h: int = 0
        max_duration = 0
        rain_quantity_mm: float = 0
        max_quantity = 0
        threshold = 0.1
        was_raining = False

        for k, precipitation in enumerate(values):
            month: int = datetimes[k].month
            stringdate: str = datetime_to_stringdate(datetimes[k]).split(' ')[0]
            if stringdate not in days:
                days.append(stringdate)
            if was_raining and precipitation > 0:  # ongoing rain event
                rain_duration_h += 1
                rain_quantity_mm += precipitation
                if stringdate not in days_with_rain:
                    days_with_rain.append(stringdate)
            elif was_raining and precipitation == 0:  # end of rain event
                rain_duration_h_quantity_mm: tuple[int, int] = (rain_duration_h, round(rain_quantity_mm, 0))
                max_duration: int = max(max_duration, rain_duration_h_quantity_mm[0])
                max_quantity: int = max(max_quantity, rain_duration_h_quantity_mm[1])

                if rain_duration_h_quantity_mm in rain_duration_h_quantity_mm_n_events:
                    rain_duration_h_quantity_mm_n_events[rain_duration_h_quantity_mm] += 1
                    if str(month) not in rains_months_dict[rain_duration_h_quantity_mm]:
                        rains_months_dict[rain_duration_h_quantity_mm].append(str(month))
                else:
                    rain_duration_h_quantity_mm_n_events[rain_duration_h_quantity_mm] = 1
                    rains_months_dict[rain_duration_h_quantity_mm] = [str(month)]
                was_raining = False
                rain_duration_h = 0
                rain_quantity_mm = 0
            elif not was_raining and precipitation > threshold:  # beginning of rain event
                if stringdate not in days_with_rain:
                    days_with_rain.append(stringdate)
                rain_duration_h = 1
                rain_quantity_mm = precipitation
                was_raining = True
        rain_duration_scale: list[float] = [_/resolution*max_duration for _ in range(resolution)]
        rain_quantity_scale: list[float] = [_/resolution*max_quantity for _ in range(resolution)]
        rain_duration_quantity_events: list[list[float]] = [[float('NaN') for _ in range(resolution)] for _ in range(resolution)]
        max_number_of_rain_events = 0
        for rain_duration_h_quantity_mm in rain_duration_h_quantity_mm_n_events:
            rain_duration_h, rain_quantity_mm = rain_duration_h_quantity_mm
            n_events = rain_duration_h_quantity_mm_n_events[rain_duration_h_quantity_mm]
            rain_duration_h_index = min(resolution-1, int(rain_duration_h/max_duration*resolution))
            rain_quantity_mm_index = min(resolution-1, int(rain_quantity_mm/max_quantity*resolution))
            rain_duration_quantity_events[rain_duration_h_index][rain_quantity_mm_index] = n_events
            max_number_of_rain_events: int = max(max_number_of_rain_events, rain_duration_h_quantity_mm_n_events[rain_duration_h_quantity_mm])
        cmap: LinearSegmentedColormap = LinearSegmentedColormap.from_list('custom', ['green', 'orange', 'red', 'purple', 'blue'], N=max_number_of_rain_events)
        im: plt.AxesImage = axes.imshow(rain_duration_quantity_events, aspect='auto', origin='lower', extent=[rain_duration_scale[0], rain_duration_scale[-1], rain_quantity_scale[0], rain_quantity_scale[-1]], cmap=cmap)
        color_bar: Colorbar = plt.colorbar(im, ax=axes, orientation='horizontal')
        color_bar.ax.set_ylabel("# events", rotation=-90, va="bottom")
        axes.set_title(main_data_name + ' events: %i raining days out of %i' % (len(days_with_rain), len(days)))
        axes.set_xlabel('duration in hours')
        axes.set_ylabel('quantity in mm/event')
        self.add_figure()

    def add_month_week_averages(self, main_data_name: str, datetimes: list, values: list):
        fig, axis = plt.subplots(figsize=plot_size)

        month_accumulator, month_cumulated_precipitations = list(), list()
        current_month_number: int = datetimes[0].month
        week_accumulator, week_cumulated_precipitations = list(), list()
        week_number: int = datetimes[0].isocalendar().week

        for k, precipitation_mm_per_hour in enumerate(values):

            month: int = datetimes[k].month
            if current_month_number != month or k == len(values)-1:
                month_quantity = sum(month_accumulator)
                month_cumulated_precipitations.extend([month_quantity for _ in range(len(month_accumulator))])
                month_accumulator: list[float] = [precipitation_mm_per_hour]
                current_month_number = month
            else:
                month_accumulator.append(precipitation_mm_per_hour)

            week: int = datetimes[k].isocalendar().week
            if week_number != week or k == len(values)-1:
                week_quantity = sum(week_accumulator)
                week_cumulated_precipitations.extend([week_quantity for _ in range(len(week_accumulator))])
                week_accumulator: list[float] = [precipitation_mm_per_hour]
                week_number = week
            else:
                week_accumulator.append(precipitation_mm_per_hour)

        axis.stairs(month_cumulated_precipitations, datetimes, fill=True, color='cyan')
        axis.stairs(week_cumulated_precipitations, datetimes, fill=True, color='pink')
        axis.set_xlabel('times')
        axis.set_ylabel('quantity')
        axis.set_title(main_data_name)
        self.add_figure()

    def add_time_plot(self, main_data_name: str, datetimes: list, values: list, datetime_marks: list = [], value_marks: list = [], **other_values) -> None:
        _, axis = plt.subplots(figsize=plot_size)
        axis.plot(datetimes, values, alpha=1)
        for series_name in other_values:
            axis.plot(datetimes, other_values[series_name], ':', alpha=.7, linewidth=2)
        min_value, max_value = None, None
        for i in range(len(values)):
            if values[i] is not None:
                if min_value is None:
                    min_value = values[i]
                    max_value = values[i]
                else:
                    min_value = min(min_value, values[i])
                    max_value = max(max_value, values[i])
        for datetime_mark in datetime_marks:
            axis.plot([datetime_mark, datetime_mark], [min_value, max_value], 'r-.', alpha=0.5)
        for value_mark in value_marks:
            axis.plot([datetimes[0], datetimes[-1]], [value_mark, value_mark], 'r-.', alpha=0.5)
        if len(other_values) > 0:
            legends: list[str] = [main_data_name]
            legends.extend([value_name.replace('_', ' ') for value_name in other_values])
            axis.legend(legends)
            axis.grid()
        self.add_figure()

    def add_monotonic(self, title, datetimes, values: list, datetime_marks: list = [], value_marks: list = []) -> None:
        indices: list[float] = [100*i/(len(values)-1) for i in range(len(values))]
        sorted_months, sorted_outdoor_temperatures = sort_values(datetimes, values)
        _, axis = plt.subplots(figsize=plot_size)
        axis.fill_between(indices, sorted_outdoor_temperatures, alpha=1)
        min_value, max_value = min(values), max(values)
        avg_value: float = (sum(values) / len(values))
        for datetime_mark in datetime_marks:
            axis.plot([datetime_mark, datetime_mark], [min_value, max_value], 'r:')
        for value_mark in value_marks:
            axis.plot([0, 100], [value_mark, value_mark], 'r:')
        axis.plot([0, 100], [avg_value, avg_value], 'b')
        axis.set_xlim(left=0, right=100)
        axis.grid(True)
        axis.set_xlabel('% of the year')
        axis.set_ylabel(title)
        for label in axis.get_xticklabels():
            label.set_visible(True)
        ax2 = axis.twinx()
        ax2.plot(indices, sorted_months, '.c')
        ax2.set_ylabel('month number')
        plt.tight_layout()
        self.add_figure()

    def add_windrose(self, wind_directions_deg: list, wind_speeds_m_s, direction_bins: int = 16, speed_bins: int = 20, to_km_h: bool = True):
        if to_km_h:
            wind_speeds_km_h = [speed * 3.6 for speed in wind_speeds_m_s]
        ax = WindroseAxes.from_ax()
        ax.contourf(direction=wind_directions_deg, var=wind_speeds_km_h, bins=speed_bins, normed=True, cmap=cm.hot)
        ax.contour(direction=wind_directions_deg, var=wind_speeds_km_h, bins=speed_bins, normed=True, colors='black', linewidth=.5)
        ax.set_legend()
        ax.set_xlabel('radius stands for number of occurrences')
        ax.set_title('windrose where color stands for wind speed in km/h')
        ax.yaxis.set_major_formatter(PercentFormatter(100))
        self.add_figure()

    def add_histogram(self, title: str | list[str], values: list[float], max_range: float, categories: int | list[str]):
        if type(categories) not in (int, float):
            width = max_range * .8 / len(categories)
            # value_counts, value_bin_edges = numpy.histogram(values, bins, range=(0, max_range))
            categories = len(categories)
        else:
            width = .8
        value_counts, category_bin_edges = numpy.histogram(values, categories, range=(0, max_range))
        ax = WindAxes.from_ax()
        ax.bar(category_bin_edges[:-1], [count/len(values) for count in value_counts], width=width, align='center')
        if type(categories) not in (int, float):
            ax.set_xticks(category_bin_edges[:-1])
            ax.set_xticklabels(categories)
        ax.grid()
        ax.set_xlabel(title)
        ax.set_ylabel('probability')
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        self.add_figure()

    def add_givoni_diagram(self, dry_bulb_temperature_deg: list[float], absolute_humidity_kg_kg: list[float], chart_name: str = ''):
        chart: PsychroChart = PsychroChart.create()
        plt.figure()
        axes = chart.plot(ax=plt.gca())
        axes.scatter(dry_bulb_temperature_deg, [1000*h for h in absolute_humidity_kg_kg], marker='o', alpha=.1)
        axes.set_title("Psychrometric diagram: %s" % chart_name)
        self.add_figure()

    def add_barchart(self, title: str, ylabel: str, **category_series_sets: dict[str, tuple[int, float]]):
        """Add a barchart with a title and a y-axis label.
        Each data belongs to a category defined by a name.
        Each category has a set of series defined by a name.
        Each series has a value and an index.

        :param title: _description_
        :type title: str
        :param ylabel: _description_
        :type ylabel: str
        """
        category_names: list[str] = list(category_series_sets.keys())
        fig, ax = plt.subplots(tight_layout=True, figsize=plot_size)

        if not isinstance(category_series_sets[category_names[0]], (int, float)):
            width = 1/len(category_names)
            bars = list()
            for series_position, series_set_name in enumerate(category_series_sets):
                series = category_series_sets[series_set_name]
                w = width / (len(series)-1)
                for i, series_name in enumerate(series):
                    bars.append(ax.bar(series_position - width + i * w, round(series[series_name], 1), w, label=series_name))
            ax.set_xticks([p - width/2 for p in range(len(category_series_sets))], category_names)
            for bar in bars:
                ax.bar_label(bar, padding=3)
            ax.legend()
        else:
            ax.bar(x=[i for i in range(len(category_names))], height=[round(category_series_sets[category_name], 1) for category_name in category_series_sets], label=[category_name for category_name in category_series_sets])
            ax.set_xticks([p for p in range(len(category_series_sets))], category_names)

        ax.set_ylabel(ylabel)
        ax.set_title(title.replace('_', ' '))
        self.add_figure()

    def add_monthly_trend(self, title, datetimes, values, average: bool = True):
        class YearMonthData:

            def __init__(self) -> None:
                self.month_data = dict()
                self.months = list()

            def add(self, datetime, value):
                month_name = datetime.strftime('%b')
                if month_name not in self.months:
                    self.month_data[month_name] = list()
                    self.months.append(month_name)
                self.month_data[month_name].append(value)

            def data(self) -> tuple[list, list]:
                months_value = dict()
                for month in self.months:
                    if month in self.month_data:
                        try:
                            if average:
                                months_value[month] = sum(self.month_data[month]) / len(self.month_data[month])
                            else:
                                months_value[month] = sum(self.month_data[month])
                        except:  # noqa
                            months_value[month] = None
                return self.months, [months_value[month] for month in self.months]

        year_monthly_values = dict()
        for i, dt in enumerate(datetimes):
            if dt.year not in year_monthly_values:
                year_monthly_values[dt.year] = YearMonthData()
            year_monthly_values[dt.year].add(dt, values[i])

        fig = go.Figure()  # create a figure
        if len(year_monthly_values) > 0:
            colors = ['rgb(%i,%i,%i)' % (255-i*255/len(year_monthly_values), abs(128-i*255/len(year_monthly_values)), i*255/len(year_monthly_values)) for i in range(len(year_monthly_values))]   # Get the colors

            for i, year in enumerate(year_monthly_values):  # Plot each year with a corresponding color
                months, values = year_monthly_values[year].data()
                fig.add_trace(go.Scatterpolar(r=values, theta=months, name=str(year), line_color=colors[i]))
            fig.update_layout(autosize=False, width=1000, height=800, title=title)  # Adjust the size of the figure
        self.add_figure(fig=fig)

    def add_parametric(self, parameter_name: str, parameter_values: list[float], left_indicators: dict[str, list[float]], left_label: str = '', right_indicators: dict[str, list[float]] = None, right_label: str = '') -> None:
        """Add a parametric analysis plot with two y-axes

        Args:
            parameter_name: Name of the parameter being analyzed
            left_indicators: Dictionary of indicator names and values for left y-axis
            right_indicators: Dictionary of indicator names and values for right y-axis
        """
        fig, ax1 = plt.subplots(figsize=plot_size)

        for i, indicator in enumerate(left_indicators):
            color = f'C{i}'
            ax1.plot(parameter_values, left_indicators[indicator], color=color, label=indicator)

        ax1.set_xlabel(parameter_name.replace('_', ' '))
        ax1.set_ylabel(left_label)
        ax1.grid()
        ax1.tick_params(axis='y')
        ax1.legend(loc='upper left')

        # Plot right indicators
        if right_indicators is not None:
            ax2 = ax1.twinx()
            for i, indicator in enumerate(right_indicators):
                color = f'C{i+len(left_indicators)}'
                ax2.plot(parameter_values, right_indicators[indicator], color=color, linestyle='--', label=indicator)

            ax2.set_ylabel(right_label)
            ax2.grid()
            ax2.tick_params(axis='y')
            ax2.legend(loc='upper right')

        fig.tight_layout()
        self.add_figure()  # fig=fig


class Analyzes:
    """A Lambda analyses contains a set of analyses applied to a lambda house.
    """

    def __init__(self, lpd: LambdaParametricData, on_screen: bool = True) -> None:
        self.report_generator: ReportGenerator = ReportGenerator(location=lpd('site_weather_data').location, year=lpd('year'), on_screen=on_screen)
        self.lpd: LambdaParametricData = lpd
        Simulator.run(self.lpd)  # first simulation is taken as reference (nominal)
        self.datetimes: list[datetime.datetime] = self.lpd('datetimes')

    def close(self, pdf: bool = True):
        self.report_generator.close(str(self.lpd), pdf=pdf)

    def climate(self):
        felt_temperatures_deg: list[float] = [OutdoorTemperatureIndices.feels_like(self.lpd('outdoor_temperatures_deg')[i], self.lpd('humidities_percentage')[i], self.lpd('wind_speeds_m_per_s')[i]) for i in range(len(self.datetimes))]
        self.report_generator.add_text('# Local climate Analysis <a name="climate"></a>')
        self.report_generator.add_text('## Analysis of the local outdoor temperature')
        self.report_generator.add_text('### Evolution of the outdoor and its averaged temperatures with detected heating and cooling periods')
        self.report_generator.add_text(f'The first time the averaged outdoor temperatures pass over the threshold "summer_hvac_trigger_temperature", here equal to {self.lpd("summer_hvac_trigger_temperature_deg")}°C determines the end of the heating period, and the last time it passed under, it determines the start of the heating period. Similarly, the first time the averaged outdoor temperature passes over the "winter_hvac_trigger_temperature" threshold, here equal to {self.lpd("winter_hvac_trigger_temperature_deg")}°C, determines the beginning the cooling period, and last time it passes down, the end.')

        datetime_marks = []

        heating_period_indices: float = self.lpd('heating_period_indices')
        if heating_period_indices is not None:
            if len(heating_period_indices) == 2:
                datetime_marks.append(self.datetimes[heating_period_indices[0]])
                datetime_marks.append(self.datetimes[heating_period_indices[1]])
                self.report_generator.add_text('- The detected heating period lasts from ' + datetime_to_stringdate(self.datetimes[heating_period_indices[0]], date_format='%d %B') + ' to ' + datetime_to_stringdate(self.datetimes[heating_period_indices[1]], date_format='%d %B') + '.\n')
            elif len(heating_period_indices) == 4:
                datetime_marks.append(self.datetimes[heating_period_indices[1]])
                datetime_marks.append(self.datetimes[heating_period_indices[2]])
                self.report_generator.add_text('- The detected heating period is actually composed of 2 periods: one from January 1st until ' + datetime_to_stringdate(self.datetimes[heating_period_indices[1]], date_format='%d %B') + ' and another one from ' + datetime_to_stringdate(self.datetimes[heating_period_indices[2]], date_format='%d %B') + ' to the end of the year.\n')
        self.report_generator.add_text('- The duration of the heating period is %d days.\n' % (round(self.lpd('heating_period_duration_h')/24)))

        cooling_period_indices: float = self.lpd('cooling_period_indices')
        if cooling_period_indices is not None:
            if len(cooling_period_indices) == 2:
                datetime_marks.append(self.datetimes[cooling_period_indices[0]])
                datetime_marks.append(self.datetimes[cooling_period_indices[1]])
                self.report_generator.add_text('- The detected cooling period lasts from ' + datetime_to_stringdate(self.datetimes[cooling_period_indices[0]], date_format='%d %B') + ' to ' + datetime_to_stringdate(self.datetimes[cooling_period_indices[1]], date_format='%d %B') + '.\n')
            elif len(heating_period_indices) == 4:
                datetime_marks.append(self.datetimes[cooling_period_indices[1]])
                datetime_marks.append(self.datetimes[cooling_period_indices[2]])
                self.report_generator.add_text('- The detected cooling period is actually composed of 2 periods: one from January 1st until ' + datetime_to_stringdate(self.datetimes[cooling_period_indices[1]], date_format='%d %B') + ' and another one from ' + datetime_to_stringdate(self.datetimes[heating_period_indices[2]], date_format='%d %B') + ' to the end of the year.\n')
        self.report_generator.add_text('- The duration of the cooling period is %d days.\n' % (round(self.lpd('cooling_period_duration_h')/24)))

        self.report_generator.add_text('This curve shows the local outdoor temperatures along with time during the reference year specified for the analysis. It comes from the [http://open-weather.com](http://open-weather.com) file. The orange curve is the averaged temperature values used to detect the heating and cooling periods. The red lines corresponds to the detection thresholds used to detect the heating and cooling periods.')
        self.report_generator.add_text('### Outdoor temperature and averaged values with heating/cooling periods')
        self.report_generator.add_time_plot('Outdoor temperature and averaged values', self.datetimes, self.lpd('outdoor_temperatures_deg'), datetime_marks=datetime_marks, value_marks=[self.lpd('winter_hvac_trigger_temperature_deg'), self.lpd('summer_hvac_trigger_temperature_deg')], averaged_values=self.lpd('smooth_outdoor_temperatures_for_hvac_periods_deg'))

        self.report_generator.add_text('The following figures are named monotones. The values are not sorted with respect to the time but in a decreasing order: it corresponds to the curve filled with blue, left y-axis scale. The x-axis stands for the percentage of the values higher than the corresponding value given by the curve. It is therefore easy to analyse how values are distributed. On the right y-axis scale, the month number (1=January,..., 12=December) is given and the time where the value has been recorded is marked by a cyan dot.')
        self.report_generator.add_image('monotonic.png')

        self.report_generator.add_text('### Monotone of the outdoor temperatures in Celsius')
        self.report_generator.add_text('The following figure represents the distribution of the outdoor temperatures over the year. The cyan dots represent the date where the related outdoor temperature has been recorded. The red lines represents the detection thresholds for the heating and cooling periods.')
        self.report_generator.add_monotonic('Monotone of the outdoor temperatures in Celsius', self.datetimes, self.lpd('outdoor_temperatures_deg'), value_marks=(self.lpd('winter_hvac_trigger_temperature_deg'), self.lpd('summer_hvac_trigger_temperature_deg')))

        self.report_generator.add_text('## Analysis of the precipitations')
        self.report_generator.add_text('### Monotone of the cloudiness in percentage of the sky covered by clouds')
        self.report_generator.add_text('The following figure represents the distribution of the cloudiness over the year. The cyan dots have the same meaning as in the previous figure.')
        self.report_generator.add_monotonic('Monotone of the cloudiness in percentage of the sky covered by clouds', self.datetimes, self.lpd('cloudiness_percentage'))

        self.report_generator.add_text('### Monotone of the precipitations (rain + hail + snow) along time in mm/h')
        self.report_generator.add_text('It represents the precipitations (rain + hail + snow) along the year in mm/h. The dashed orange curve represents the cumulated snowfalls.')
        self.report_generator.add_time_plot('Precipitations', self.datetimes, self.lpd('precipitations_mm_per_hour'), snowfalls=self.lpd('snowfalls_mm_per_hour')) 
        self.report_generator.add_text('### Rain, hail or snow events: duration, intensity and occurrences')
        self.report_generator.add_text('Here is a heatmap of the rain, hail and snow events: the color intensity represents the number of occurrences of each event situated in a 2D space where the x-axis represents the duration of precipitation events while the y-axis represents the quantity in mm of precipitations fallen during the event.')
        self.report_generator.add_event_plot('Rain, hail or snow', self.datetimes, self.lpd('precipitations_mm_per_hour'))
        self.report_generator.add_text('### Month & week cumulated rain, hail or snow')
        self.report_generator.add_text('It represents the cumulated rain, hail or snow over each month (in cyan) and week (in pink color).')
        self.report_generator.add_month_week_averages('Rain, hail or snow', self.datetimes, self.lpd('precipitations_mm_per_hour'))
        self.report_generator.add_text('## Analysis of the local wind')

        self.report_generator.add_text('The wind speeds and directions over a time period, are usually represented by a wind rose. The colors represent the speed of the wind and a radius stands for the so-called meteorological direction i.e. the direction from where the wind is coming from.')
        self.report_generator.add_windrose(self.lpd('wind_directions_deg'), self.lpd('wind_speeds_m_per_s'))
        
        self.report_generator.add_text('The following histogram represents the wind speed distribution over the year.')
        wind_speeds_km_h = [3.6*_ for _ in self.lpd('wind_speeds_m_per_s')]
        self.report_generator.add_histogram(title='wind speed in km/h', values=wind_speeds_km_h, max_range=max(wind_speeds_km_h), categories=20)
        
        self.report_generator.add_text('The following histogram represents the wind direction distribution over the year. Like for the windrose, the direction is given in degrees and correspond to where the wind is coming from.')
        self.report_generator.add_histogram(title='wind direction in degrees (coming from)', values=self.lpd('wind_directions_deg'), categories=('N', '', 'N-E', '', 'E', '', 'S-E', '', 'S', '', 'S-W', '', 'W', '', 'N-W', ''), max_range=360)

        self.report_generator.add_text('## Analysis of the outdoor comfort')
        self.report_generator.add_text('The following figure represents the Givoni diagram, which is a psychrometric chart. The comfort region is delimited by the [20°C, 25°C] temperature range and the [20%, 80%] relative humidity range.')
        self.report_generator.add_givoni_diagram(self.lpd('outdoor_temperatures_deg'), self.lpd('absolute_humidity_kg_kg'), chart_name='Outdoor comfort')

        min_feel_like_temperatures_deg: list[float] = list()
        max_feel_like_temperatures_deg: list[float] = list()
        for i in range(len(self.datetimes)):
            if i < 72:
                min_feel_like_temperatures_deg.append(felt_temperatures_deg[i])
                max_feel_like_temperatures_deg.append(felt_temperatures_deg[i])
            else:
                min_feel_like_temperatures_deg.append(min(felt_temperatures_deg[i-72:i]))
                max_feel_like_temperatures_deg.append(max(felt_temperatures_deg[i-72:i]))
        last_decile_feel_like_temperature: float = list(numpy.percentile(felt_temperatures_deg, [0, 90]))[-1]
        self.report_generator.add_text('The following figure is based on the felt temperatures along time. The blue curve represents the minimum felt temperature over the last 3 days, the red curve represents the maximum felt temperature over the last 3 days, and the green curve represents the last decile of the felt temperature over the year. It is an indicator for scorching periods: if the 3-days minimum felt temperature is reaching or passing over the horizontal line standing for the last year temperature decile, it reveals a scorching period.')
        self.report_generator.add_time_plot(' 3 days min Felt temperature', self.datetimes, min_feel_like_temperatures_deg, value_marks=[last_decile_feel_like_temperature,], _3_days_max_felt_temperature=max_feel_like_temperatures_deg)

    def evolution(self) -> None:
        self.report_generator.add_text('# Long term climate Evolution <a name="evolution"></a>')
        self.report_generator.add_text('These curves represent the long term evolution of the weather variables. Each radius corresponds to a month. Each curve corresponds to a year with averaged month values. Yellow color stands for oldest years, violet for middle and blue to most recent years.')
        all_years_site_weather_data: SiteWeatherData = self.lpd('full_site_weather_data')
        self.report_generator.add_text('## Outdoor temperature evolution (month average)')
        self.report_generator.add_text('The following figure represents the evolution of the outdoor temperature over the years. The blue curve represents the average temperature over the years, the red curve represents the minimum temperature over the years, and the green curve represents the maximum temperature over the years.')
        self.report_generator.add_text('### Long term outdoor temperature evolution')
        self.report_generator.add_monthly_trend('Outdoor temperature evolution (month average)', all_years_site_weather_data.datetimes, all_years_site_weather_data.series('temperature'))
        self.report_generator.add_text('### Long term outdoor rainfalls evolution (month cumulated)')
        self.report_generator.add_text('The following figure represents the evolution of the monthly cumulated rainfalls over the years.')
        self.report_generator.add_monthly_trend('Outdoor rainfalls evolution (month cumulated)', all_years_site_weather_data.datetimes, all_years_site_weather_data.series('precipitation'))

    def solar(self) -> None:
        self.report_generator.add_text('# Solar radiation analysis <a name="solar"></a>')
        self.report_generator.add_text('An heliodon represents the sun path along the year. The position of the sun is represented by 2 angles: the azimuth, the angle formed by a vertical plan directed to the south and the vertical plan where the sun is i.e. the azimuth angle, and the altitude (or elevation) of the sun formed by the horizontal plan tangent to earth and the horizontal where the sun is with 0° means: directed to the south (for azimuth, east is negative and west positive, and altitude 0° and 90° stand respectively for horizontal and vertical positions). The heliodon plot represents the trajectory of the sun the 21th of each month of the year.')
        self.report_generator.add_image('solar_angles.png')
        self.report_generator.add_text('Additionally, the solar masks coming from the skyline in particular (specified in the configuration file) are also drawn: gray dots represent the angles where the sun is visible.')
        self.report_generator.add_text('- Heliodon at local position, with the azimuth angles on the x-axis and the altitude angle on the y-axis')
        self.lpd('solar_model').plot_heliodon(self.lpd('year'))  # axis: plt.Axes = 
        self.report_generator.add_figure()
        self.report_generator.add_text("The best exposure (horizontal angle of the perpendicular to the PV panel wrt the south) and best tilt angle (vertical angle of the perpendicular to the PV panel wrt to the south), have been computed. An exposure of -90° means the panel is directed to the the east, +90° to the west. A slope of 90° means the panel is facing the south whereas 0° means facing the ground and 180°,facing the sky.")
        self.report_generator.add_image("exposure_tilt.png")
        self.report_generator.add_text("- The best PV exposure angle is: %g°E with a tilt angle of %g° (%g°) with a production of %ikWh/year for %im2" % (self.lpd("best_exposure_deg"), self.lpd('best_slope_deg'), 180-self.lpd('best_slope_deg'), sum(self.lpd('best_PV_plant_powers_W')) / 1000, self.lpd('floor_surface_m2')))
        # CHECK
        self.report_generator.add_text('- The next figure gives the collected solar energy (not PV production) on different ($1m^2$) surface direction')
        self.report_generator.add_barchart('Collected solar energy on different surfaces', 'kWh/m2.year', **{direction: sum(self.lpd('unit_canonic_solar_powers_W')[direction])/1000 for direction in self.lpd('unit_canonic_solar_powers_W')})

    def house(self):
        self.report_generator.add_text('## House Analysis <a name="house"></a>')
        self.report_generator.add_text('### Global results')

        self.report_generator.add_text('- The following time plot represents the evolution along time of the indoor temperatures (blue), the setpoints of the HVAC system (orange) and the outdoor temperatures (green).')
        self.report_generator.add_text('The horizontal dashed red lines point out the values that are used to estimate the inhabitant discomfort. The percentage of the occupancy hours where the temperature is over 29°C stands for summer discomfort and the percentage of the occupancy hours where the temperature is under 18°C stands for winter discomfort. These values may be more important than in reality because the model does not represent the window openings and other reactive actions done by the occupants in reaction to overheating.')
        self.report_generator.add_time_plot('indoor temperatures', self.lpd.datetimes, self.lpd('indoor_temperatures_deg'), value_marks=[18, 29], setpoints=self.lpd('setpoint_temperatures_deg'), outdoor_temperatures_deg=self.lpd('outdoor_temperatures_deg'))

        self.report_generator.add_text('The resulting primary energy needs are given below. In addition to these values, the final energy need taking into account the coefficient of performance of the HVAC system are also given.')

        self.report_generator.add_text('- The primary year heat needed for heating the lambda-house is: %gkWh, with a final energy needs = %.fkWh and a maximum power of %gW' % (sum(self.lpd('heating_needs_W'))/1000, sum(self.lpd('heating_needs_W')) / self.lpd('hvac_COP') / 1000, self.lpd('max_heating_power_W')))

        self.report_generator.add_text('- The primary year heat removal needed for cooling the lambda-house is: %gkWh, with a final energy needs = %gkWh and a maximum power of %gW' % (sum(self.lpd('cooling_needs_W'))/1000, sum(self.lpd('cooling_needs_W')) / 1000 / self.lpd('hvac_COP'), self.lpd('max_cooling_power_W')))
        self.report_generator.add_text('- The primary year heat needs for the HVAC system (heating and cooling) is: %gkWh (with a final energy needs = %gkWh)' % (sum(self.lpd('hvac_needs_W'))/1000, sum(self.lpd('hvac_needs_W')) / 1000 / self.lpd('hvac_COP')))

        # consumption comparison

        self.report_generator.add_text('- The following bar chart represents the final energy from a heat pump (COP=%.1f) needed per square meter of useful living surface.' % (self.lpd('hvac_COP')))
        self.report_generator.add_barchart('Final energy for heating and cooling with a heat pump', 'kWh/m2/year', needed_energy={
            'heating': sum(self.lpd('heating_needs_W'))/1000/self.lpd('total_living_surface_m2')/self.lpd('hvac_COP'),
            'cooling': sum(self.lpd('cooling_needs_W'))/1000/self.lpd('total_living_surface_m2')/self.lpd('hvac_COP')
            })

        self.report_generator.add_text('Monthly electricity needs are plotted below, together with heat needs and the PV production')
        self.report_generator.add_time_plot('monthly electricity needs in kWh', self.lpd.datetimes, self.lpd('monthly_electricity_consumption_kW'), monthly_energy_need_kWh=self.lpd('month_average_needed_energy_kW'), monthly_PV_energy_produced_kWh=self.lpd('month_average_PV_energy_kW'))

        self.report_generator.add_text('- The following bar chart represents the discomfort18 (the ratio of hours of presence where the temperature is lower than 18°C) and discomfort29 (the ratio of hours of presence where the temperature is higher than 29°C).')
        self.report_generator.add_barchart('ratio of hours of presence with discomfort', 'hours in discomfort / hours of occupancy in %', needed_energy={'discomfort18': self.lpd('discomfort18'), 'discomfort29': self.lpd('discomfort29')})

        self.report_generator.add_text("### Parametric analyses")
        self.report_generator.add_text("Different parametric analyses are performed in the next. It consists in modifying one parameter while keeping all the others at their nominal values. The impact is computed in percentage of variation wrt nominal impacts: heating primary energy needs, cooling primary energy needs (and their total), but also indicators dealing with inhabitant comfort: Discomfort18, the frequency of hours with presence where indoor temperature is lower than 18°C. In the same way, Discomfort29 is the frequency of hours where the indoor temperature is higher than 29°C.")
        self.report_generator.add_text("Right hand scale is representing the percentage of variation wrt to nominal value. For instance, 0% means the result is the same than the one of the nominal parameter values. 100% means the value is the double of the case of nominal results, and -50% stands for half of the nominal value. It concerns the variable representing the heating, cooling and total energy needs.")
        self.report_generator.add_text("Left hand scale represents the discomfort indicators: discomfort18 and discomfort29, see above).")
        self.report_generator.add_text("The first parametric analysis focuses on glazing. Variation of the surface of glazing (10% for each house side for nominal) are computed: there are as many plot that the studied direction.")

    def parametric(self) -> None:
        self.report_generator.add_text("- Parametric analysis of the glazing for each side")  # Parametric analysis of the glazing for each side
        for side in ['south', 'west', 'east', 'north']:
            self.lpd.reset()
            parameter_name: str = 'glazing_ratio_%s' % side
            self.lpd.select(parameter_name)
            parameter_values: list[str] = list()
            left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
            right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
            for parameter_value in self.lpd:
                parameter_values.append(parameter_value)
                Simulator.run(self.lpd)
                left_indicators['heating_needs_kWh'].append(self.lpd('heating_needs_kWh'))
                left_indicators['cooling_needs_kWh'].append(self.lpd('cooling_needs_kWh'))
                left_indicators['hvac_needs_kWh'].append(self.lpd('hvac_needs_kWh'))
                right_indicators['discomfort18'].append(self.lpd('discomfort18'))
                right_indicators['discomfort29'].append(self.lpd('discomfort29'))
            self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='primary energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

        self.lpd.reset()
        Simulator.run(self.lpd)
        self.report_generator.add_text('The solar gain / loss balance of South window is:')  # south_heating_windows_global_gains_W
        self.report_generator.add_text('* for heating period:  %g%%' % (self.lpd('south_heating_windows_global_gains_W')))
        self.report_generator.add_text('* for cooling period:  %g%%' % (self.lpd('south_cooling_windows_global_gains_W')))
        self.report_generator.add_text('The solar gain / loss balance of West window is:')
        self.report_generator.add_text('* for heating period:  %g%%' % (self.lpd('west_heating_windows_global_gains_W')))
        self.report_generator.add_text('* for cooling period:  %g%%' % (self.lpd('west_cooling_windows_global_gains_W')))
        self.report_generator.add_text('The solar gain / loss balance of East window is:')
        self.report_generator.add_text('* for heating period:  %g%%' % (self.lpd('east_heating_windows_global_gains_W')))
        self.report_generator.add_text('* for cooling period:  %g%%' % (self.lpd('east_cooling_windows_global_gains_W')))
        self.report_generator.add_text('The solar gain / loss balance of North window is:')
        self.report_generator.add_text('* for heating period:  %g%%' % (self.lpd('north_heating_windows_global_gains_W')))
        self.report_generator.add_text('* for cooling period:  %g%%' % (self.lpd('north_cooling_windows_global_gains_W')))

        self.report_generator.add_text("- Parametric analysis of lambda-house direction (exposure of the south side).")

        self.report_generator.add_text("The house is rotated east/west to analyze the resulting global impacts (remember that the skyline is also impacting the results).")
        self.report_generator.add_text('The best angle of the south wall with the South (0° stands for South wall facing the South, 90° the West and -90° the East.) ')
        self.report_generator.add_image('exposure.png')

        self.report_generator.add_text("- Parametric analysis of the offset exposure")  # Parametric analysis of the glazing for each side

        parameter_name: str = 'offset_exposure_deg'
        self.lpd.select(parameter_name)
        parameter_values: list[str] = list()
        left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
        right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
        for parameter_value in self.lpd:
            parameter_values.append(parameter_value)
            Simulator.run(self.lpd)
            [left_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in left_indicators]
            [right_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in right_indicators]
        self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

        self.report_generator.add_text('- The shape factor parametric analysis')
        self.report_generator.add_text("Changing the shape factor, a square ground print at first, aims at defining the best house shape.")
        self.report_generator.add_text('It keeps the useful building surface constant, 1 yields a square,  and higher than 1 value yields a rectangle with South/North sides bigger than East/West sides and lower than one, the opposite')
        table = prettytable.PrettyTable()
        Sfloor: float = self.lpd('total_living_surface_m2') / self.lpd('number_of_floors')
        table.field_names = ('shape factor', 'south/north side length', 'west/east side length')
        for shape_factor in self.lpd.parametric('shape_factor'):
            Lsouth_north_wall: float = math.sqrt(Sfloor * shape_factor)
            Least_west_wall: float = math.sqrt(Sfloor / shape_factor)
            table.add_row(('%g' % shape_factor, '%g' % Lsouth_north_wall, '%g' % Least_west_wall))
        self.report_generator.add_pretty_table(table)  # delta_temperature_absence_mode

        parameter_name: str = 'shape_factor'
        self.lpd.select(parameter_name)
        parameter_values: list[str] = list()
        left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
        right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
        for parameter_value in self.lpd:
            parameter_values.append(parameter_value)
            Simulator.run(self.lpd)
            [left_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in left_indicators]
            [right_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in right_indicators]
        self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

        self.report_generator.add_text('- The number_of_floors: the useful surface can be distributed over different floors, reducing thus the floor print, and increasing the height of the house.')
        parameter_name: str = 'number_of_floors'
        self.lpd.select(parameter_name)
        parameter_values: list[str] = list()
        left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
        right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
        for parameter_value in self.lpd:
            parameter_values.append(parameter_value)
            Simulator.run(self.lpd)
            [left_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in left_indicators]
            [right_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in right_indicators]
        self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

        self.report_generator.add_text('- Parametric study of the solar protection over the South glazing')
        self.report_generator.add_text('The parameter "south_solar_protection_angle_deg" stands for the maximum altitude angle where the sun is not hidden by the passive solar protection mask over the South glazing.')
        self.report_generator.add_text('The nominal lambda house has a passive solar mask, which is masking the sun at a specified altitude:. This parametric analysis makes it possible to define a relevant compromise for this exposure angle leading to lower energy needs while limiting the inhabitant discomfort.')
        parameter_name: str = 'south_solar_protection_angle_deg'
        self.lpd.select(parameter_name)
        parameter_values: list[str] = list()
        left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
        right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
        for parameter_value in self.lpd:
            parameter_values.append(parameter_value)
            Simulator.run(self.lpd)
            [left_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in left_indicators]
            [right_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in right_indicators]
        self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

        # self.report_generator.add_text('- Parametric study of the air renewal through ventilation in indoor volume per hour in case a presence has been detected')
        # self.parametric_analysis(parameter_name='air_renewal_presence_vol_per_h')

        self.report_generator.add_text('- Parametric study of the ventilation heat recovery efficiency')
        self.report_generator.add_text('The ventilation heat recovery efficiency reduces the heat exchanges between indoor and outdoor. 0% means there is no dual flow ventilation system and 85%, which is the greatest value than can be found on rotating heat exchangers with wheels, means that 85% of the heat from the extracted air is recovered and reinjected into the new air (heat exchange represents 15% of the one of a single flow ventilation system).')
        # self.parametric_analysis(parameter_name='ventilation_heat_recovery_efficiency')
        parameter_name: str = 'ventilation_heat_recovery_efficiency'
        self.lpd.select(parameter_name)
        parameter_values: list[str] = list()
        left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
        right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
        for parameter_value in self.lpd:
            parameter_values.append(parameter_value)
            Simulator.run(self.lpd)
            [left_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in left_indicators]
            [right_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in right_indicators]
        self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

        self.report_generator.add_text('- Parametric study of the HVAC heating temperature setpoint')
        self.report_generator.add_text('This setpoint temperature is applied only during time periods where at least an inhabitant is present.')
        parameter_name: str = 'heating_setpoint_deg'
        self.lpd.select(parameter_name)
        parameter_values: list[str] = list()
        left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
        right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
        for parameter_value in self.lpd:
            parameter_values.append(parameter_value)
            Simulator.run(self.lpd)
            [left_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in left_indicators]
            [right_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in right_indicators]
        self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

        self.report_generator.add_text('- Parametric study of the HVAC cooling temperature setpoint')
        self.report_generator.add_text('This setpoint temperature is applied only during time periods where at least an inhabitant is present.')
        parameter_name: str = 'cooling_setpoint_deg'
        self.lpd.select(parameter_name)
        parameter_values: list[str] = list()
        left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
        right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
        for parameter_value in self.lpd:
            parameter_values.append(parameter_value)
            Simulator.run(self.lpd)
            [left_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in left_indicators]
            [right_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in right_indicators]
        self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

        self.report_generator.add_text('- Parametric study of the insulation thickness')
        self.report_generator.add_text('It modifies the thickness of the chosen material for insulation.')

        parameter_name: str = 'thickness_m'
        self.lpd.select(parameter_name)
        parameter_values: list[str] = list()
        left_indicators: dict[str, list[float]] = {'heating_needs_kWh': list(), 'cooling_needs_kWh': list(), 'hvac_needs_kWh': list()}
        right_indicators: dict[str, list[float]] = {'discomfort18': list(), 'discomfort29': list()}
        for parameter_value in self.lpd:
            parameter_values.append(parameter_value)
            Simulator.run(self.lpd)
            [left_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in left_indicators]
            [right_indicators[indicator_name].append(self.lpd(indicator_name)) for indicator_name in right_indicators]
        self.report_generator.add_parametric(parameter_name=parameter_name, parameter_values=parameter_values, left_indicators=left_indicators, left_label='energy needs in kWh/year', right_indicators=right_indicators, right_label='discomfort in %')

    def neutrality(self) -> None:
        self.lpd.reset()
        Simulator.run(lpd=self.lpd)
        self.report_generator.add_text('# Neutrality analysis <a name="neutrality"></a>')

        self.report_generator.add_text('## Zero energy over the year')
        self.report_generator.add_text('The aim is to appreciate the yearly energy needed by the HVAC system. To do it, the energy neutrality is searched thanks to a certain surface of photovoltaic panels.')

        self.report_generator.add_text('- The required surface of photovoltaic panels for balancing the annual energy consumption of the HVAC system is:')
        table = prettytable.PrettyTable()
        table.field_names = ('PV (efficiency: %g%%)' % (100*self.lpd('PV_efficiency')), 'energy needs (in best eq. PV m2)')
        table.add_row(('1. heater', '%gm2' % (self.lpd('heating_needs_kWh') / self.lpd('hvac_COP') / self.lpd('best_PV_plant_powers_kWh'))))
        table.add_row(('2. air conditioning', '%gm2' % (self.lpd('cooling_needs_kWh') / self.lpd('hvac_COP') / self.lpd('best_PV_plant_powers_kWh'))))
        table.add_row(('1+2. HVAC', '%gm2' % (self.lpd('hvac_needs_kWh') / self.lpd('hvac_COP') / self.lpd('best_PV_plant_powers_kWh'))))
        table.add_row(('1+2+other usages', '%gm2' % (self.lpd('electricity_needs_kWh') / self.lpd('best_PV_plant_powers_kWh'))))
        self.report_generator.add_pretty_table(table)

        self.report_generator.add_text('The electricity hourly consumption and photovoltaic production (surface=%gm2) is plotted below:' % self.lpd('PV_surface_m2'))
        self.report_generator.add_time_plot('electricity needs (kWh/year)', self.lpd('datetimes'), self.lpd('electricity_needs_W'), PV_production_W=self.lpd('best_PV_plant_powers_W'))

        self.report_generator.add_text('Different indicators are used to appreciate the level of autonomy and dependency from the grid:')
        self.report_generator.add_text('- the self-consumption is the part of the PV electricity consumed locally: the more, the lower the electricity bill: %g%%' % (self.lpd('self_consumption')))
        self.report_generator.add_image('self_consumption.png')
        self.report_generator.add_text('- the self-production is the part of the consumption produced locally by PV: it is representing how much the energy needs are covered: %g%%' % (self.lpd('self_production')))
        self.report_generator.add_image('self_production.png')
        self.report_generator.add_text('When self-consumption=self-production it means that all the load is produced locally.')
        self.report_generator.add_text('- the L-NEEG is the net energy exchange with the grid (import + export) normalized by the total load. The less, the more independent of the grid: %g%%' % (self.lpd('neeg')))
        self.report_generator.add_image('L-NEEG.png')
        if self.lpd('max_grid_withdraw_W') <= 0:
            self.report_generator.add_text('- the surface of PV (%gm2) is sufficient to cover the everyday electricity needs' % (self.lpd('PV_surface_m2')))
        else:
            the_date: str = self.lpd('max_grid_withdraw_datetime').strftime('%d/%m/%Y')
            self.report_generator.add_text('- the surface of PV (%gm2) is not sufficient to cover all the daily electricity needs. The worst day of the year is %s: %gm2 of PV should be added' % (self.lpd('PV_surface_m2'), the_date, self.lpd('max_grid_withdraw_PV_covering_m2') - self.lpd('PV_surface_m2')))

        self.report_generator.add_text('- The Net Energy Exchange from or to grid normalized by the total electricity needs is: %.f%%' % (self.lpd('neeg')))
        self.report_generator.add_text('- The year electricity autonomy is: %.f%%' % (self.lpd('year_autonomy')))
        self.report_generator.add_text('- The self consumption, i.e. the part of the production consumed locally, normalized by the total electricity needs is: %.f%%' % (self.lpd('self_consumption')))
        self.report_generator.add_text('- The self production, i.e. the part of the consumption produced locally, normalized by the total electricity needs is: %.f%%' % (self.lpd('self_production')))
        
        # self.report_generator.add_text('- Parametric study of the net energy exchange with the grid, the self consumption and self-production')
        # self.lpd.reset()
        # self.lpd.select('PV_surface_m2')
        # self.parametric()


class Simulator:

    @staticmethod
    def cumsum(list_of_floats: list[float]) -> list[float]:
        cumulated_list_of_floats = []
        total = 0
        for x in list_of_floats:
            total: float = total + x
            cumulated_list_of_floats.append(total)
        return cumulated_list_of_floats

    @staticmethod
    def __compute_thermal_features(lpd: LambdaParametricData) -> None:
        wall_composition = Composition(first_layer_indoor=True, last_layer_indoor=False, position='vertical', indoor_average_temperature_in_celsius=21, outdoor_average_temperature_in_celsius=lpd('average_outdoor_temperature_deg'), wind_speed_is_m_per_sec=lpd('average_wind_speed_m_per_s'), heating_floor=False)
        for material, thickness_m in lpd('wall_composition_in_out'):
            wall_composition.layer(material, thickness_m)

        glass_composition = Composition(first_layer_indoor=True, last_layer_indoor=False, position='vertical', indoor_average_temperature_in_celsius=21, outdoor_average_temperature_in_celsius=lpd('average_outdoor_temperature_deg'), wind_speed_is_m_per_sec=lpd('average_wind_speed_m_per_s'), heating_floor=False)
        for material, thickness_m in lpd('glass_composition_in_out'):
            glass_composition.layer(material, thickness_m)

        roof_composition = Composition(first_layer_indoor=True, last_layer_indoor=False, position='horizontal', indoor_average_temperature_in_celsius=21, outdoor_average_temperature_in_celsius=lpd('average_outdoor_temperature_deg'), wind_speed_is_m_per_sec=lpd('average_wind_speed_m_per_s'), heating_floor=False)
        for material, thickness_m in lpd('roof_composition_in_out'):
            roof_composition.layer(material, thickness_m)

        ground_composition = Composition(first_layer_indoor=True, last_layer_indoor=False, position='horizontal', indoor_average_temperature_in_celsius=21, outdoor_average_temperature_in_celsius=lpd('average_outdoor_temperature_deg'), wind_speed_is_m_per_sec=lpd('average_wind_speed_m_per_s'), heating_floor=False)
        for material, thickness_m in lpd('ground_composition_in_out'):
            ground_composition.layer(material, thickness_m)

        lpd.section('thermal')
        lpd.result('U_glass', glass_composition.U)
        lpd.result('US_wall', wall_composition.U * lpd('wall_surface_m2'))
        lpd.result('US_glass', glass_composition.U * lpd('glazing_surface_m2'))
        lpd.result('US_roof', roof_composition.U * lpd('floor_surface_m2'))
        lpd.result('US_ground', ground_composition.U * lpd('floor_surface_m2'))

    @staticmethod
    def __compute_solar_gain(lpd: LambdaParametricData) -> None:
        solar_building_system = SolarSystem(lpd('solar_model'))
        lpd.result('solar_building_system', solar_building_system)
        for direction in DIRECTIONS_SREF:
            direction_name: str = direction.name.lower()
            mask: RectangularMask = InvertedMask(RectangularMask((-90+direction.value, 90+direction.value), (0, 90-lpd('south_solar_protection_angle_deg')) if direction == DIRECTIONS_SREF.SOUTH else (0, 90)))
            Collector(solar_building_system, direction_name, exposure_deg=direction.value + lpd('offset_exposure_deg'), slope_deg=SLOPES.VERTICAL.value, surface_m2=lpd('glazing_surface_%s_m2' % direction_name), scale_factor=lpd('solar_factor'), mask=mask)

        collectors_window_solar_gains_W = solar_building_system.powers_W(gather_collectors=False)
        for collector_name in collectors_window_solar_gains_W:
            lpd.result(collector_name + '_window_solar_gains_W', collectors_window_solar_gains_W[collector_name])
        lpd.result('windows_solar_gains_W', solar_building_system.powers_W(gather_collectors=True))

    @staticmethod
    def hvac_on(indices: tuple[int, int] | tuple[int, int, int, int], i: int) -> bool:
        if indices is not None and (indices[0] <= i <= indices[1]):
            return True
        elif indices is not None and len(indices) == 4:
            return indices[2] <= i <= indices[3]
        else:
            return False

    @staticmethod
    def __step(lpd: LambdaParametricData, i: int, over_ventilation=False) -> tuple[float, float, float, float]:
        occupancy: float = lpd('occupancy')[i]
        presence: bool = occupancy > 0
        air_volume_m3: float = lpd('air_volume_m3')
        if over_ventilation and presence:
            UQ_ventilation: float = 1.204 * 1005 * air_volume_m3 * lpd('air_renewal_overheat')/3600
        elif not presence:
            UQ_ventilation: float = 0
        else:
            UQ_ventilation = (1 - lpd('ventilation_heat_recovery_efficiency')) * 1.204 * 1005 * air_volume_m3 * lpd('air_renewal_presence_vol_per_h')/3600

        free_gain_W: float = lpd('windows_solar_gains_W')[i] + occupancy * (lpd('average_occupancy_electric_gain_w') + lpd('average_occupancy_metabolic_gain_w')) + lpd('average_permanent_electric_gain_w')

        US_outdoor: float = lpd('US_wall') + lpd('US_glass') + lpd('US_roof') + UQ_ventilation

        free_indoor_temperature: float = (free_gain_W + US_outdoor * lpd('smooth_outdoor_temperatures_for_hvac_periods_deg')[i] + lpd('US_ground') * lpd('average_outdoor_temperature_deg')) / (US_outdoor + lpd('US_ground'))

        heating_period_indices: tuple[int, int] = lpd('heating_period_indices')
        cooling_period_indices: tuple[int, int] = lpd('cooling_period_indices')

        if Simulator.hvac_on(heating_period_indices, i):
            if presence:
                setpoint_temperature_deg: float = lpd('heating_setpoint_deg')
            else:
                setpoint_temperature_deg: float = lpd('heating_setpoint_deg') - lpd('delta_temperature_absence_mode_deg')

            heating_need_W = max(0, (US_outdoor + lpd('US_ground')) * (setpoint_temperature_deg - free_indoor_temperature))
            cooling_need_W = 0

        elif Simulator.hvac_on(cooling_period_indices, i):  # cooling period
            if presence:
                setpoint_temperature_deg = lpd('cooling_setpoint_deg')
            else:
                setpoint_temperature_deg = lpd('cooling_setpoint_deg') + lpd('delta_temperature_absence_mode_deg')
            cooling_need_W = max(0, (US_outdoor + lpd('US_ground')) * (free_indoor_temperature - setpoint_temperature_deg))
            heating_need_W = 0
        else:
            heating_need_W = 0
            cooling_need_W = 0
            setpoint_temperature_deg = None

        indoor_temperature = float(free_indoor_temperature + (heating_need_W - cooling_need_W) / (US_outdoor + lpd('US_ground')))
        return indoor_temperature, heating_need_W, cooling_need_W, setpoint_temperature_deg

    @staticmethod
    def run(lpd: LambdaParametricData) -> None:
        
        # def get_cached_solar_data(key):
        #     if key not in solar_cache:
        #         solar_building_system = SolarSystem(lpd('solar_model'))
        #         powers = solar_building_system.powers_W(gather_collectors=True)
        #         solar_cache[key] = powers
        #     return solar_cache[key]
        
        Simulator.__compute_thermal_features(lpd)
        Simulator.__compute_solar_gain(lpd)
        
        heating_needs_W = list()
        cooling_needs_W = list()
        hvac_needs_W = list()
        max_heating_power_W, max_cooling_power_W = 0, 0
        setpoint_temperatures_deg = list()
        indoor_temperatures_deg = list()
        over_ventilation_indices = list()

        for i in range(len(lpd)):
            indoor_temperature_deg, heating_need_W, cooling_need_W, setpoint_temperature_deg = Simulator.__step(lpd, i, over_ventilation=False)
            if lpd('occupancy')[i] and indoor_temperature_deg >= lpd('air_renewal_overheat_threshold_deg'):
                indoor_temperature_deg, heating_need_W, cooling_need_W, setpoint_temperature_deg = Simulator.__step(lpd, i, over_ventilation=True)
                over_ventilation_indices.append(True)
            else:
                over_ventilation_indices.append(False)
            indoor_temperatures_deg.append(indoor_temperature_deg)
            heating_needs_W.append(float(heating_need_W))
            cooling_needs_W.append(float(cooling_need_W))
            hvac_needs_W.append(float(heating_need_W + cooling_need_W))

            if setpoint_temperature_deg is not None:
                setpoint_temperatures_deg.append(float(setpoint_temperature_deg))
            else:
                setpoint_temperatures_deg.append(None)
            if heating_need_W is not None:
                max_heating_power_W: float = max(float(heating_need_W), max_heating_power_W)
            if cooling_need_W is not None:
                max_cooling_power_W: float = max(float(cooling_need_W), max_cooling_power_W)

        lpd.result('indoor_temperatures_deg', indoor_temperatures_deg)
        lpd.result('avg_indoor_temperatures_deg', sum(indoor_temperatures_deg) / len(lpd))
        lpd.result('setpoint_temperatures_deg', setpoint_temperatures_deg)
        lpd.result('cooling_needs_W', cooling_needs_W)
        lpd.result('heating_needs_W', heating_needs_W)
        lpd.result('hvac_needs_W', hvac_needs_W)
        lpd.result('max_heating_power_W', max_heating_power_W)
        lpd.result('max_cooling_power_W', max_cooling_power_W)

        windows_global_gains_W: dict[str, float] = {}
        solar_building_system: SolarSystem = lpd('solar_building_system')
        for collector_name in solar_building_system.collectors:
            collector_windows_solar_gains_W: list[float] = lpd(collector_name + '_window_solar_gains_W')
            smooth_outdoor_temperatures_for_hvac_periods_deg: list[float] = lpd('smooth_outdoor_temperatures_for_hvac_periods_deg')
            glazing_surface_m2: float = lpd('glazing_surface_%s_m2' % collector_name)

            windows_global_gains_W[collector_name] = [collector_windows_solar_gains_W[i] - lpd('U_glass') * glazing_surface_m2 * (indoor_temperatures_deg[i] - smooth_outdoor_temperatures_for_hvac_periods_deg[i]) for i in range(len(lpd))]

        for collector_name in solar_building_system.collectors:
            if lpd('heating_period_indices') is not None and len(lpd('heating_period_indices')) == 2:
                lpd.result(collector_name + '_heating_windows_global_gains_W', sum([windows_global_gains_W[collector_name][i] for i in range(len(lpd)) if lpd('heating_period_indices')[0] <= i <= lpd('heating_period_indices')[1]]) / lpd('heating_period_duration_h'))
            else:
                lpd.result(collector_name + '_heating_windows_global_gains_W', sum([windows_global_gains_W[collector_name][i] for i in range(len(lpd)) if lpd('heating_period_indices')[0] <= i <= lpd('heating_period_indices')[1] or lpd('heating_period_indices')[2] <= i <= lpd('heating_period_indices')[3]]) / lpd('heating_period_duration_h'))

            if lpd('cooling_period_indices') is not None and len(lpd('cooling_period_indices')) == 2:
                lpd.result(collector_name + '_cooling_windows_global_gains_W', sum([windows_global_gains_W[collector_name][i] for i in range(len(lpd)) if lpd('cooling_period_indices')[0] <= i <= lpd('cooling_period_indices')[1]]) / lpd('cooling_period_duration_h'))
            else:
                lpd.result(collector_name + '_cooling_windows_global_gains_W', sum([windows_global_gains_W[collector_name][i] for i in range(len(lpd)) if lpd('cooling_period_indices')[0] <= i <= lpd('cooling_period_indices')[1] or lpd('cooling_period_indices')[2] <= i <= lpd('cooling_period_indices')[3]]) / lpd('cooling_period_duration_h'))

        discomfort18_29: list[int] = [0, 0]
        occupancy_counter = 0
        for k, temperature in enumerate(indoor_temperatures_deg):
            if lpd('occupancy')[k] > 0:
                occupancy_counter += 1
                if temperature < 18:
                    discomfort18_29[0] += 1
                if temperature > 29:
                    discomfort18_29[1] += 1

        lpd.result('discomfort18', round(100*discomfort18_29[0]/occupancy_counter, 0) if occupancy_counter != 0 else 0)
        lpd.result('discomfort29', round(100*discomfort18_29[1]/occupancy_counter, 0) if occupancy_counter != 0 else 0)

        lpd.section('electricity')
        lpd.result('electricity_needs_W', [(lpd('heating_needs_W')[i] + lpd('cooling_needs_W')[i]) / lpd('hvac_COP') + (lpd('average_permanent_electric_gain_w') + lpd('occupancy')[i] * lpd('average_occupancy_electric_gain_w')) for i in range(len(lpd))])

        lpd.result('electricity_grid_exchange_W', [lpd('best_PV_plant_powers_W')[i] - lpd('electricity_needs_W')[i] for i in range(len(lpd))])
        filter: Averager = Averager(lpd('electricity_grid_exchange_W'))
        daily_grid_exchange_W, day_numbers = filter.day_month_average(lpd('datetimes'))
        lpd.result('daily_electricity_grid_exchange_W', [-p*24 for p in daily_grid_exchange_W])

        max_grid_withdraw_W: float = max(lpd('daily_electricity_grid_exchange_W'))
        starting_day_hour_index: int = lpd('daily_electricity_grid_exchange_W').index(max_grid_withdraw_W)
        ending_day_hour_index: int = starting_day_hour_index + 1
        if ending_day_hour_index < len(day_numbers):
            while ending_day_hour_index < len(day_numbers) and day_numbers[ending_day_hour_index] == day_numbers[starting_day_hour_index]:
                ending_day_hour_index += 1
            max_grid_withdraw_datetime: datetime = lpd('datetimes')[round((starting_day_hour_index+ending_day_hour_index)/2)]
            max_grid_withdraw_PV_covering_m2: float = max_grid_withdraw_W / sum(lpd('best_PV_plant_powers_W')[starting_day_hour_index: ending_day_hour_index])

            lpd.result('max_grid_withdraw_datetime', max_grid_withdraw_datetime)
            lpd.result('max_grid_withdraw_W', max_grid_withdraw_W)
            lpd.result('max_grid_withdraw_PV_covering_m2', max_grid_withdraw_PV_covering_m2)

        lpd.result('year_autonomy', 100 * year_autonomy(lpd('electricity_needs_W'), lpd('best_PV_plant_powers_W')))
        lpd.result('neeg', 100 * NEEG_percent(lpd('electricity_needs_W'), lpd('best_PV_plant_powers_W')))

        lpd.result('self_consumption', 100 * self_consumption(lpd('electricity_needs_W'), lpd('best_PV_plant_powers_W')))
        lpd.result('self_production', 100 * self_sufficiency(lpd('electricity_needs_W'), lpd('best_PV_plant_powers_W')))

        _month_average_needed_energy_W, days = Averager(lpd('hvac_needs_W')).day_month_average(lpd('datetimes'), month=True, sum_up=True)
        _month_average_PV_energy_W, days = Averager(lpd('best_PV_plant_powers_W')).day_month_average(lpd('datetimes'), month=True, sum_up=True)
        lpd.result('month_average_needed_energy_W', _month_average_needed_energy_W)
        lpd.result('month_average_PV_energy_W', _month_average_PV_energy_W)
        _monthly_electricity_consumption_W, days = Averager(lpd('electricity_needs_W')).day_month_average(lpd('datetimes'), month=True, sum_up=True)
        lpd.result('monthly_electricity_consumption_W', _monthly_electricity_consumption_W)
