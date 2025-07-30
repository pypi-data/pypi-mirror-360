"""
This code is protected under GNU General Public License v3.0

A helper module dedicated to the design of time-varying state space model approximated by bilinear state space model.

Author: stephane.ploix@grenoble-inp.fr
"""
from __future__ import annotations
import time
from abc import ABC
from typing import Any
import numpy as np
import numpy.linalg as la
from enum import Enum
from datetime import datetime
from batem.core.components import Airflow
from batem.core.statemodel import StateModel
from batem.core.model import BuildingStateModelMaker
from batem.core.data import DataProvider
from batem.core.thermal import bar


class VALUE_DOMAIN_TYPE(Enum):
    """An enum to define the type of the value domain of a control port.

    :cvar CONTINUOUS: Continuous value domain (e.g., [0, 100])
    :cvar DISCRETE: Discrete value domain (e.g., [0, 1, 2, 3])
    """
    CONTINUOUS = 0
    DISCRETE = 1


class CONTROL_TYPE(Enum):
    """An enum to define the type of control strategy.

    :cvar NO_CONTROL: No control applied to the system
    :cvar POWER_CONTROL: Direct power control of HVAC systems
    :cvar TEMPERATURE_CONTROL: Temperature-based control with setpoints
    """
    NO_CONTROL = 0
    POWER_CONTROL = 1
    TEMPERATURE_CONTROL = 2


class WEEKDAYS(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class SignalBuilder:
    """
    A signal generator for creating time-series signals based on datetime sequences.

    This class provides methods to generate various types of signals including
    constant values, seasonal patterns, daily schedules, and more.
    """

    def __init__(self, datetimes: list[datetime.datetime]):
        """
        Initialize the SignalGenerator with a list of datetime objects.

        :param datetimes: List of datetime objects representing the time points
        :type datetimes: list[datetime.datetime]
        """
        self.datetimes: list[datetime.datetime] = datetimes
        self.starting_datetime: datetime.datetime = datetimes[0]
        self.starting_year: int = self.starting_datetime.year
        self.starting_month: int = self.starting_datetime.month
        self.starting_day: int = self.starting_datetime.day
        self.ending_datetime: datetime.datetime = datetimes[-1]
        self.ending_year: int = self.ending_datetime.year
        self.ending_month: int = self.ending_datetime.month
        self.ending_day: int = self.ending_datetime.day
        
    def merge(self, signal1: list[float | None] | float, signal2: list[float | None] | float, operator: callable,  none_dominate: bool = False) -> Any:
        """
        Combine two signals using a specified operator.

        :param signal1: First signal (can be float or list)
        :type signal1: list[float | None] | float
        :param signal2: Second signal (can be float or list)
        :type signal2: list[float | None] | float
        :param operator: Function to combine the signals (e.g., add, multiply)
        :type operator: callable
        :param none_dominate: If True, None values dominate the result
        :type none_dominate: bool
        :return: Combined signal
        :rtype: Any
        """
        signal: list[float | None] = list()
        for k in range(len(self.datetimes)):
            signal.append(self._merge_vals(signal1[k], signal2[k], operator, none_dominate))
        return signal
    
    def filter(self, signal: list[float | None], filter_function: callable) -> list[float | None]:
        """
        Filter a signal using a filter function.
        """
        signal = list(signal)
        for i in range(len(signal)):
            if signal[i] is not None:
                filter_function(signal[i])
        return signal
    
    def filter_replace(self, signal: list[float | None], existing_value: float, replacement_value: float) -> list[float | None]:
        """
        Replace specific values in a signal with replacement values.
        """
        signal = list(signal)
        for i in range(len(signal)):
            if signal[i] == existing_value:
                signal[i] = replacement_value
        return signal
    
    def filter_denonify(self, signal: list[float | None], none_value: int = 0) -> list[float | None]:
        """
        Convert None values in a signal to integer values.

        :param signal: Signal to convert
        :type signal: list[float | None]
        :param none_value: Integer value to use for None values
        :type none_value: int
        :return: Signal with None values converted to integers
        :rtype: list[float | None]
        """
        for k in range(len(self.datetimes)):
            if signal[k] is None:
                signal[k] = none_value
        return signal
    
    def build_constant(self, value: float | None) -> list[float | None]:
        """
        Generate a constant signal with the specified value.

        :param value: The constant value to use for all time points
        :type value: float | None
        :return: List of constant values with same length as datetimes
        :rtype: list[float | None]
        """
        return [value for _ in range(len(self.datetimes))]

    def build_seasonal(self, day_month_start: str, day_month_end: str, seasonal_value: float = 1, out_season_value: float = None, period2_start: str = None, period2_end: str = None, period2_value: float = None) -> list[float | None]:
        """
        Generate a seasonal signal with one or two periods per year.

        :param day_month_start: Start date of first period in format 'DD/MM'
        :type day_month_start: str
        :param day_month_end: End date of first period in format 'DD/MM'
        :type day_month_end: str
        :param seasonal_value: Value during the first period
        :type seasonal_value: float
        :param out_season_value: Value outside the first period (or between periods if second period is specified)
        :type out_season_value: float
        :param period2_start: Start date of second period in format 'DD/MM' (optional)
        :type period2_start: str
        :param period2_end: End date of second period in format 'DD/MM' (optional)
        :type period2_end: str
        :param period2_value: Value during the second period (optional)
        :type period2_value: float
        :return: Seasonal signal with values for each time point
        :rtype: list[float | None]
        """
        year = self.starting_year

        # Parse dates for first period
        day1, month1 = tuple([int(v) for v in day_month_start.split('/')])
        day2, month2 = tuple([int(v) for v in day_month_end.split('/')])

        # Create datetime thresholds for first period
        period1_start_dt = datetime(
            year=year, month=month1, day=day1,
            hour=0, minute=0, second=0, microsecond=0,
            tzinfo=self.starting_datetime.tzinfo
        )
        period1_end_dt = datetime(
            year=year, month=month2, day=day2,
            hour=0, minute=0, second=0, microsecond=0,
            tzinfo=self.starting_datetime.tzinfo
        )

        # Handle year transitions for first period
        if period1_end_dt < period1_start_dt:
            period1_end_dt = period1_end_dt.replace(year=year+1)

        # Check if second period is specified
        has_second_period = period2_start is not None and period2_end is not None and period2_value is not None

        if has_second_period:
            # Parse dates for second period
            day2_start, month2_start = tuple([int(v) for v in period2_start.split('/')])
            day2_end, month2_end = tuple([int(v) for v in period2_end.split('/')])

            # Create datetime thresholds for second period
            period2_start_dt = datetime.datetime(
                year=year, month=month2_start, day=day2_start,
                hour=0, minute=0, second=0, microsecond=0,
                tzinfo=self.starting_datetime.tzinfo
            )
            period2_end_dt = datetime.datetime(
                year=year, month=month2_end, day=day2_end,
                hour=0, minute=0, second=0, microsecond=0,
                tzinfo=self.starting_datetime.tzinfo
            )

            # Handle year transitions for second period
            if period2_end_dt < period2_start_dt:
                period2_end_dt = period2_end_dt.replace(year=year+1)

        signal = list()
        for dt in self.datetimes:
            # Check if current datetime is in first period
            in_period1 = self._is_in_period(dt, period1_start_dt, period1_end_dt, year)

            if has_second_period:
                # Check if current datetime is in second period
                in_period2 = self._is_in_period(dt, period2_start_dt, period2_end_dt, year)

                # Determine the value based on which period the datetime falls into
                if in_period1:
                    signal.append(seasonal_value)
                elif in_period2:
                    signal.append(period2_value)
                else:
                    signal.append(out_season_value)
            else:
                # Original single period logic
                if in_period1:
                    signal.append(seasonal_value)
                else:
                    signal.append(out_season_value)
        return signal

    def build_daily(self, info_signal: list[float | None], info_signal_activation_value: float, weekdays: list[WEEKDAYS], hour_setpoints: dict[int, float]) -> list[float | None]:
        """
        Generate a daily signal based on weekdays and hour setpoints.

        :param info_signal: Input signal to modify (can be None for new signal)
        :type info_signal: list[float | None]
        :param info_signal_activation_value: Value that activates the daily schedule
        :type info_signal_activation_value: float
        :param weekdays: List of weekdays to apply the schedule
        :type weekdays: list[WEEKDAYS]
        :param hour_setpoints: Dictionary mapping hours to setpoint values
        :type hour_setpoints: dict[int, float]
        :return: Modified signal with daily schedule applied
        :rtype: list[float | None]
        """
        # Convert WEEKDAYS enum to integers for comparison
        weekday_ints = [d.value if hasattr(d, 'value') else d for d in weekdays]

        # Build the 24-hour day sequence
        previous_hour, previous_setpoint = None, None
        day_sequence = list()

        if 0 not in hour_setpoints:
            raise ValueError("0 must appear in the trigger dictionary")

        # Sort hours to ensure they are in increasing order
        sorted_hours = sorted(hour_setpoints.keys())

        for hour in sorted_hours:
            if previous_hour is None:
                previous_hour, previous_setpoint = hour, hour_setpoints[hour]
            else:
                # Fill the gap between previous hour and current hour
                for _ in range(previous_hour, hour):
                    day_sequence.append(previous_setpoint)
                previous_hour, previous_setpoint = hour, hour_setpoints[hour]

        # Fill the remaining hours until 24
        for hour in range(previous_hour, 24):
            day_sequence.append(previous_setpoint)

        # Create or modify the signal
        signal = [None] * len(self.datetimes)

        for i, dt in enumerate(self.datetimes):
            if dt.weekday() in weekday_ints:
                if info_signal[i] == info_signal_activation_value:
                    signal[i] = day_sequence[dt.hour]
        return signal

    def build_long_absence(self, presence_signal: list[float], high_setpoint: float, long_absence_setpoint: float, number_of_days: int) -> list[float]:
        """
        Generate a signal that switches to long absence setpoint after a specified number of days of absence.

        :param high_setpoint: Normal setpoint value
        :type high_setpoint: float
        :param long_absence_setpoint: Setpoint value during long absence periods
        :type long_absence_setpoint: float
        :param number_of_days: Number of days of absence before switching to long absence setpoint
        :type number_of_days: int
        :param presence: Presence signal (positive values indicate presence)
        :type presence: list[float]
        :return: Signal with long absence logic applied
        :rtype: list[float]
        """
        long_absence_start = None  # starting index for long absence
        long_absence_counter: int = 0
        signal: list = list()
        for i in range(len(self.datetimes)):
            if presence_signal[i] > 0:  # presence
                if long_absence_start is not None:  # long absence detected and ongoing
                    if long_absence_start + long_absence_counter > number_of_days * 24:  # long absence detected but is over (presence detected)
                        for i in range(long_absence_start, long_absence_counter):  # add long absence.endswith() setpoints
                            signal.append(long_absence_setpoint)
                    else:  # long absence has not been detected
                        for i in range(long_absence_start, long_absence_counter):
                            signal.append(high_setpoint)
                    signal.append(high_setpoint)
                long_absence_counter = 0  # reinitialize the long absence counter
            else:  # absence
                if long_absence_start is None:  # first absence detection
                    long_absence_counter = 1
                    long_absence_start = i
                else:  # new absence detection
                    long_absence_counter += 1
        for i in range(len(signal), len(self.datetimes)):
            signal.append(high_setpoint)
        return signal
    
    def _merge_vals(self, val1: float | None, val2: float | None, operator: callable, none_dominate: bool = False) -> float | None:
        if val1 is None and val2 is None:
            return None
        elif val1 is None and val2 is not None:
            if none_dominate:
                return None
            else:
                return val2
        elif val2 is None and val1 is not None:
            if none_dominate:
                return None
            else:
                return val1
        else:
            return operator(val1, val2)
    
    def _is_in_period(self, dt: datetime.datetime, period_start: datetime.datetime, period_end: datetime.datetime, base_year: int) -> bool:
        """
        Helper method to check if a datetime falls within a period.

        :param dt: Datetime to check
        :type dt: datetime.datetime
        :param period_start: Start of the period
        :type period_start: datetime.datetime
        :param period_end: End of the period
        :type period_end: datetime.datetime
        :param base_year: Base year for the period
        :type base_year: int
        :return: True if datetime is in period, False otherwise
        :rtype: bool
        """
        # Adjust period dates to match the year of the datetime being checked
        dt_year = dt.year

        adjusted_start = period_start.replace(year=dt_year)
        adjusted_end = period_end.replace(year=dt_year)

        # Handle periods that cross year boundary
        if adjusted_end < adjusted_start:
            # Period crosses year boundary
            if dt >= adjusted_start or dt < adjusted_end:
                return True
        else:
            # Period is within the same year
            if adjusted_start <= dt < adjusted_end:
                return True

        return False


class Port(ABC):
    """Abstract base class for control ports that interface with system components.

    A control port manages the communication between the control system and
    physical components, handling value domains and data recording.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param value_domain_type: Type of value domain (continuous or discrete)
    :type value_domain_type: VALUE_DOMAIN_TYPE
    :param value_domain: Allowed values for the port
    :type value_domain: list[float]
    """

    def _intersection(self, *sets) -> tuple[float, float] | None:
        """Compute the intersection of multiple intervals or sets.

        :param sets: Variable number of intervals or sets to intersect
        :type sets: tuple[float, float] | list[float]
        :return: Intersection of the sets, or None if no intersection exists
        :rtype: tuple[float, float] | None
        """
        if sets[0] is None:
            return None
        global_set: tuple[float, float] = sets[0]
        for _set in sets[1:]:
            if _set is None:
                return None
            else:
                if self.value_domain_type == VALUE_DOMAIN_TYPE.CONTINUOUS:
                    bound_inf: float = max(global_set[0], _set[0])
                    bound_sup: float = min(global_set[1], _set[1])
                    if bound_inf <= bound_sup:
                        global_set: tuple[float, float] = (bound_inf, bound_sup)
                    else:
                        return None
                else:
                    global_set: list[int] = list(set(global_set) & set(_set))
        return global_set

    def __union(self, *sets) -> tuple[float, float] | None:
        """Compute the union of multiple intervals or sets.

        :param sets: Variable number of intervals or sets to union
        :type sets: tuple[float, float] | list[float]
        :return: Union of the sets, or None if all sets are None
        :rtype: tuple[float, float] | None
        """
        i = 0
        while i < len(sets) and sets[i] is None:
            i += 1
        if i == len(sets):
            return None
        global_set: tuple[float, float] = sets[i]
        i += 1
        while i < len(sets):
            if sets[i] is not None:
                if self.value_domain_type == VALUE_DOMAIN_TYPE.CONTINUOUS:
                    global_set: tuple[float, float] = (min(global_set[0], sets[i][0]), max(global_set[1], sets[i][-1]))
                else:
                    global_set: list[int] = list(set(global_set) | set(sets[i]))
            i += 1
        return tuple(global_set)

    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str, value_domain_type: VALUE_DOMAIN_TYPE, value_domain: list[float]) -> None:
        """Initialize a control port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param value_domain_type: Type of value domain (continuous or discrete)
        :type value_domain_type: VALUE_DOMAIN_TYPE
        :param value_domain: Allowed values for the port
        :type value_domain: list[float]
        """
        super().__init__()
        self.dp: DataProvider = data_provider
        self.model_variable_name: str = model_variable_name
        self.feeding_variable_name: str = feeding_variable_name
        self.in_provider: bool = self._in_provider(feeding_variable_name)
        if self.in_provider:
            print(f'{feeding_variable_name} is saved automatically by the port')
        else:
            print(f'{feeding_variable_name} must be saved manually via the port at the end of a simulation')
        self.recorded_data: dict[int, float] = dict()
        self.value_domain_type: VALUE_DOMAIN_TYPE = value_domain_type
        self.modes_value_domains: dict[int, list[float]] = dict()
        if value_domain is not None:
            self.modes_value_domains[0] = value_domain

    def _in_provider(self, variable_name: str) -> bool:
        """Check if a variable exists in the data provider.

        :param variable_name: Name of the variable to check
        :type variable_name: str
        :return: True if the variable exists in the data provider
        :rtype: bool
        """
        return self.dp is not None and variable_name in self.dp

    def __call__(self, k: int, port_value: float | None = None) -> list[float] | float | None:
        """Get or set the port value at time step k.

        :param k: Time step index
        :type k: int
        :param port_value: Value to set (None to get current value)
        :type port_value: float | None
        :return: Current value domain or the set value
        :rtype: list[float] | float | None
        """
        if port_value is None:
            if k in self.recorded_data:
                return self.recorded_data[k]
            else:
                return self.modes_value_domains[0]
        else:
            value_domain: list[float] = self._standardize(self.modes_value_domains[0])
            port_value = self._restrict(value_domain, port_value)
            self.recorded_data[k] = port_value
            if self.in_provider:
                self.dp(self.feeding_variable_name, k, port_value)
            return port_value

    def _restrict(self, value_domain: list[float], port_value: float) -> float:
        """Restrict a port value to the allowed domain.

        :param value_domain: Allowed values for the port
        :type value_domain: list[float]
        :param port_value: Value to restrict
        :type port_value: float
        :return: Restricted value within the domain
        :rtype: float
        """
        if self.value_domain_type == VALUE_DOMAIN_TYPE.DISCRETE:
            if port_value not in value_domain:
                distance_to_value = tuple([abs(port_value - v) for v in value_domain])
                port_value = value_domain[distance_to_value.index(min(distance_to_value))]
        else:
            port_value = port_value if port_value <= value_domain[1] else value_domain[1]
            port_value = port_value if port_value >= value_domain[0] else value_domain[0]
        return port_value

    def _standardize(self, value_domain: int | float | tuple | float | list[float]) -> None | tuple[float]:
        """Standardize a value domain to a consistent format.

        :param value_domain: Value domain to standardize
        :type value_domain: int | float | tuple | float | list[float]
        :return: Standardized value domain
        :rtype: None | tuple[float]
        """
        if value_domain is None:
            return None
        else:
            if self.value_domain_type == VALUE_DOMAIN_TYPE.DISCRETE:
                if type(value_domain) is int or type(value_domain) is float:
                    standardized_value_domain: tuple[int | float] = (value_domain,)
                elif len(value_domain) >= 1:
                    standardized_value_domain = tuple(sorted(list(set(value_domain))))
            else:  # VALUE_DOMAIN_TYPE.CONTINUOUS
                if type(value_domain) is not list and type(value_domain) is not tuple:
                    standardized_value_domain: tuple[float, float] = (value_domain, value_domain)
                else:
                    standardized_value_domain: tuple[float, float] = (min(value_domain), max(value_domain))
            return standardized_value_domain

    def save(self) -> None:
        """Save recorded port data to the data provider.

        If the port is not automatically saved, this method manually
        saves all recorded data to the data provider.

        :raises ValueError: If no data provider is available
        """
        if not self.in_provider:
            data = list()
            for k in range(len(self.dp)):
                if k in self.recorded_data:
                    data.append(self.recorded_data[k])
                else:
                    data.append(0)
            self.dp.add_external_variable(self.feeding_variable_name, data)
        else:
            if self.dp is None:
                raise ValueError('No data provider: cannot save the port data')
            else:
                self.dp(self.feeding_variable_name, self.recorded_data)

    def __repr__(self) -> str:
        """Get a string representation of the port.

        :return: String representation of the port
        :rtype: str
        """
        return f"Control port {self.feeding_variable_name}({self.model_variable_name})"

    def __str__(self) -> str:
        """Get a detailed string representation of the port.

        :return: Detailed string representation of the port
        :rtype: str
        """
        if self.value_domain_type == VALUE_DOMAIN_TYPE.DISCRETE:
            string = 'Discrete'
        else:
            string = 'Continuous'
        if self.model_variable_name != self.feeding_variable_name:
            string += f" control port on \"{self.feeding_variable_name}\" related to \"{self.model_variable_name}\""
        else:
            string += f" control port on \"{self.model_variable_name}\""
        if self.in_provider:
            string += f" automatically recorded in data provider as \"{self.feeding_variable_name}\""
        return string


class ContinuousPort(Port):
    """A control port with continuous value domain.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param value_domain: Allowed values for the port (continuous range)
    :type value_domain: list[float]
    """
    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str, value_domain: list[float]) -> None:
        """Initialize a continuous control port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param value_domain: Allowed values for the port (continuous range)
        :type value_domain: list[float]
        """
        super().__init__(data_provider, model_variable_name, feeding_variable_name, VALUE_DOMAIN_TYPE.CONTINUOUS, value_domain)


class DiscretePort(Port):
    """A control port with discrete value domain.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param value_domain: Allowed values for the port (discrete set)
    :type value_domain: list[float]
    """
    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str, value_domain: list[float]) -> None:
        """Initialize a discrete control port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param value_domain: Allowed values for the port (discrete set)
        :type value_domain: list[float]
        """
        super().__init__(data_provider, model_variable_name, feeding_variable_name, VALUE_DOMAIN_TYPE.DISCRETE, value_domain)


class ModePort(Port):
    """A control port that depends on a mode variable: the value domain is different depending on the mode.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param value_domain_type: Type of value domain (continuous or discrete)
    :type value_domain_type: VALUE_DOMAIN_TYPE
    :param modes_value_domains: Dictionary mapping mode values to value domains
    :type modes_value_domains: dict[int, list[float]]
    :param mode_variables: Tuple of mode variable names
    :type mode_variables: tuple[str]
    :raises ValueError: If no mode variables are provided
    """
    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str, value_domain_type: VALUE_DOMAIN_TYPE, modes_value_domains: dict[int, list[float]], mode_variables: tuple[str]) -> None:
        """Initialize a mode-dependent control port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param value_domain_type: Type of value domain (continuous or discrete)
        :type value_domain_type: VALUE_DOMAIN_TYPE
        :param modes_value_domains: Dictionary mapping mode values to value domains
        :type modes_value_domains: dict[int, list[float]]
        :param mode_variables: Tuple of mode variable names
        :type mode_variables: tuple[str]
        :raises ValueError: If no mode variables are provided
        """
        if type(mode_variables) is str:
            mode_variables = (mode_variables,)
        super().__init__(data_provider, model_variable_name, feeding_variable_name, value_domain_type, None)
        self.modes_value_domains = {mode: self._standardize(modes_value_domains[mode]) for mode in modes_value_domains}
        self.mode_variables: tuple[str] = mode_variables
        if len(mode_variables) == 0:
            raise ValueError('ModePort must have mode variables')

    def clean_value(self, value) -> int:
        """Clean a value by converting None or NaN to 0.

        :param value: Value to clean
        :type value: Any
        :return: Cleaned integer value
        :rtype: int
        """
        if value is None or np.isnan(value):
            return 0
        return int(value)

    def _merge_to_mode(self, **mode_variable_values_k: dict[str, float]) -> float:
        """Merge mode variable values into a single mode value.

        :param mode_variable_values_k: Dictionary of mode variable values
        :type mode_variable_values_k: dict[str, float]
        :return: Merged mode value
        :rtype: float
        """
        if len(self.mode_variables) == 1:
            return int(mode_variable_values_k[self.mode_variables[0]])
        return sum(2**i * self.clean_value(mode_variable_values_k[self.mode_variables[i]] > 0) for i in range(len(self.mode_variables)))

    def value_domain(self, k: int, **mode_values: Any) -> list[float]:
        """Get the value domain for a specific mode.

        :param k: Time step index
        :type k: int
        :param mode_values: Mode variable values
        :type mode_values: Any
        :return: Value domain for the current mode
        :rtype: list[float]
        """
        mode: dict[str, float] = self.mode_converter(k, **mode_values)
        return self.modes_value_domains[mode]

    def __call__(self, k: int, port_value: float | None = None, **mode_variable_values: dict[str, float]) -> list[float] | float | None:
        """Get or set the port value at time step k for a specific mode.

        :param k: Time step index
        :type k: int
        :param port_value: Value to set (None to get current value)
        :type port_value: float | None
        :param mode_variable_values: Mode variable values
        :type mode_variable_values: dict[str, float]
        :return: Current value domain or the set value
        :rtype: list[float] | float | None
        """
        mode: dict[str, float] = self._merge_to_mode(**mode_variable_values)
        if port_value is None or np.isnan(port_value):
            return self.modes_value_domains[mode]
        else:
            port_value = self._restrict(self.modes_value_domains[mode], port_value)
            self.recorded_data[k] = port_value
            if self.in_provider:
                self.dp(self.feeding_variable_name, k, port_value)
            return port_value


class ContinuousModePort(ModePort):
    """A mode-dependent control port with continuous value domain.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param modes_value_domains: Dictionary mapping mode values to value domains
    :type modes_value_domains: dict[int, list[float]]
    :param mode_variables: Tuple of mode variable names
    :type mode_variables: tuple[str]
    """
    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str,  modes_value_domains: dict[int, list[float]], *mode_variables: tuple[str]) -> None:
        """Initialize a continuous mode-dependent control port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param modes_value_domains: Dictionary mapping mode values to value domains
        :type modes_value_domains: dict[int, list[float]]
        :param mode_variables: Tuple of mode variable names
        :type mode_variables: tuple[str]
        """
        super().__init__(data_provider, model_variable_name, feeding_variable_name, VALUE_DOMAIN_TYPE.CONTINUOUS, modes_value_domains, *mode_variables)


class DiscreteModePort(ModePort):
    """A mode-dependent control port with discrete value domain.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param modes_value_domains: Dictionary mapping mode values to value domains
    :type modes_value_domains: dict[int, list[float]]
    :param mode_variables: Tuple of mode variable names
    :type mode_variables: tuple[str]
    """
    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str, modes_value_domains: dict[int, list[float]], *mode_variables: tuple[str]) -> None:
        """Initialize a discrete mode-dependent control port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param modes_value_domains: Dictionary mapping mode values to value domains
        :type modes_value_domains: dict[int, list[float]]
        :param mode_variables: Tuple of mode variable names
        :type mode_variables: tuple[str]
        """
        super().__init__(data_provider, model_variable_name, feeding_variable_name, VALUE_DOMAIN_TYPE.DISCRETE, modes_value_domains, *mode_variables)


class HeaterContinuousModePort(ContinuousModePort):
    """A continuous mode port specifically for heater control.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param max_power: Maximum heater power
    :type max_power: float
    :param mode_variable: Mode variable name
    :type mode_variable: str
    """
    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str,  max_power: float, mode_variable: str) -> None:
        """Initialize a heater continuous mode port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param max_power: Maximum heater power
        :type max_power: float
        :param mode_variable: Mode variable name
        :type mode_variable: str
        """
        super().__init__(data_provider, model_variable_name, feeding_variable_name, {0: 0, 1: (0, max_power)}, *(mode_variable,))


class HVACcontinuousModePort(ContinuousModePort):
    """A continuous mode port specifically for HVAC control.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param max_heating_power: Maximum heating power
    :type max_heating_power: float
    :param max_cooling_power: Maximum cooling power
    :type max_cooling_power: float
    :param mode_variable: Mode variable name
    :type mode_variable: str
    """
    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str,  max_heating_power: float, max_cooling_power: float, mode_variable: str) -> None:
        """Initialize an HVAC continuous mode port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param max_heating_power: Maximum heating power
        :type max_heating_power: float
        :param max_cooling_power: Maximum cooling power
        :type max_cooling_power: float
        :param mode_variable: Mode variable name
        :type mode_variable: str
        """
        super().__init__(data_provider, model_variable_name, feeding_variable_name, {0: 0, 1: max_heating_power, -1: max_cooling_power}, *(mode_variable,))


class OpeningPort(ModePort):
    """A mode port specifically for opening control based on presence.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param presence_variable: Name of the presence variable
    :type presence_variable: str
    """
    def __init__(self, data_provider: DataProvider, feeding_variable_name: str, presence_variable: str) -> None:
        """Initialize an opening port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param presence_variable: Name of the presence variable
        :type presence_variable: str
        """
        super().__init__(data_provider, feeding_variable_name, feeding_variable_name, VALUE_DOMAIN_TYPE.DISCRETE, {0: 0, 1: (0, 1)}, 'presence_variable')


class TemperatureSetpointPort(DiscreteModePort):
    """A discrete mode port specifically for temperature setpoint control.

    :param data_provider: Provider for time series data
    :type data_provider: DataProvider
    :param model_variable_name: Name of the variable in the system model
    :type model_variable_name: str
    :param feeding_variable_name: Name of the variable in the data provider
    :type feeding_variable_name: str
    :param heating_levels: List of heating temperature levels
    :type heating_levels: list[float]
    :param cooling_levels: List of cooling temperature levels
    :type cooling_levels: list[float]
    :param mode_variable: Mode variable name
    :type mode_variable: str
    """
    def __init__(self, data_provider: DataProvider, model_variable_name: str, feeding_variable_name: str, heating_levels: list[float], cooling_levels: list[float], mode_variable: str) -> None:
        """Initialize a temperature setpoint port.

        :param data_provider: Provider for time series data
        :type data_provider: DataProvider
        :param model_variable_name: Name of the variable in the system model
        :type model_variable_name: str
        :param feeding_variable_name: Name of the variable in the data provider
        :type feeding_variable_name: str
        :param heating_levels: List of heating temperature levels
        :type heating_levels: list[float]
        :param cooling_levels: List of cooling temperature levels
        :type cooling_levels: list[float]
        :param mode_variable: Mode variable name
        :type mode_variable: str
        """
        super().__init__(data_provider, model_variable_name, feeding_variable_name, VALUE_DOMAIN_TYPE.DISCRETE, {1: heating_levels, 0: 0, -1: cooling_levels}, *(mode_variable,))


class TemperatureController:
    """A controller that manages HVAC power to reach temperature setpoints.

    The controller adjusts HVAC power output to maintain desired temperature
    setpoints. It can operate with immediate effect (delay=0) or with a
    one-time-step delay (delay=1).

    :param hvac_heat_port: Port controlling HVAC heating power
    :type hvac_heat_port: Port
    :param temperature_setpoint_port: Port providing temperature setpoints
    :type temperature_setpoint_port: Port
    :param state_model_nominal: Nominal state model for control calculations
    :type state_model_nominal: StateModel
    :raises ValueError: If power or temperature variables are not found in the model
    """

    def __init__(self, hvac_heat_port: Port, temperature_setpoint_port: Port,  state_model_nominal: StateModel) -> None:
        """Initialize the temperature controller.

        :param hvac_heat_port: Port controlling HVAC heating power
        :type hvac_heat_port: Port
        :param temperature_setpoint_port: Port providing temperature setpoints
        :type temperature_setpoint_port: Port
        :param state_model_nominal: Nominal state model for control calculations
        :type state_model_nominal: StateModel
        :raises ValueError: If power or temperature variables are not found in the model
        """
        self.hvac_heat_port: Port = hvac_heat_port
        self.temperature_setpoint_port: Port = temperature_setpoint_port

        self.temperature_setpoint_name: str = temperature_setpoint_port.feeding_variable_name
        self.model_power_name: str = hvac_heat_port.model_variable_name
        self.model_temperature_name: str = temperature_setpoint_port.model_variable_name
        self.temperature_setpoint_name: str = self.temperature_setpoint_port.model_variable_name

        self.power_index: int = state_model_nominal.input_names.index(self.model_power_name)
        self.temperature_index: int = state_model_nominal.output_names.index(self.model_temperature_name)
        self.n_inputs: int = state_model_nominal.n_inputs
        self.n_states: int = state_model_nominal.n_states
        self.n_outputs: int = state_model_nominal.n_outputs

        self.T = np.zeros((1, self.n_outputs))
        self.T[0, self.temperature_index] = 1
        self.S = np.zeros((1, self.n_inputs))

        self.S[0, self.power_index] = 1
        self.S_bar = bar(self.S)

        self.controller_delay: int = -1
        if self.model_power_name not in state_model_nominal.input_names:
            raise ValueError(f'{self.model_power_name} is not an input of the state model: {state_model_nominal.input_names}')
        if self.model_temperature_name not in state_model_nominal.output_names:
            raise ValueError(f'{self.model_temperature_name} is not an output of the state model: {str(state_model_nominal.output_names)}')

        if not np.all(self.T * state_model_nominal.D * self.S.transpose() == 0):
            self.controller_delay = 0
        elif not np.all(self.T*state_model_nominal.C*state_model_nominal.B*self.S.transpose() == 0):
            self.controller_delay = 1
        else:
            raise ValueError(f'{self.temperature_name} cannot be controlled by {self.model_power_name} thanks to the setpoint {self.temperature_setpoint_name} adding power to {self.heat_gain_name}')

    def control_ports(self) -> list[Port]:
        """Get the list of control ports managed by this controller.

        :return: List of control ports (hvac_heat_port and temperature_setpoint_port)
        :rtype: list[Port]
        """
        return [self.hvac_heat_port, self.temperature_setpoint_port]

    def hvac_power_k(self, k: int, temperature_setpoint: float, state_model_k: StateModel, state_k: np.matrix, name_inputs_k: np.matrix, name_inputs_kp1: np.matrix = None) -> tuple[np.matrix, float]:
        """Calculate required HVAC power to reach temperature setpoint.

        :param k: Time step index
        :type k: int
        :param temperature_setpoint: Target temperature setpoint
        :type temperature_setpoint: float
        :param state_model_k: State model at time step k
        :type state_model_k: StateModel
        :param state_k: Current state vector
        :type state_k: np.matrix
        :param name_inputs_k: Input vector at time step k
        :type name_inputs_k: np.matrix
        :param name_inputs_kp1: Input vector at time step k+1 (for delay=1)
        :type name_inputs_kp1: np.matrix
        :return: Required HVAC power to reach setpoint
        :rtype: tuple[np.matrix, float]
        """

        inputs_k: np.matrix = np.matrix([[name_inputs_k[_]] for _ in name_inputs_k])

        if temperature_setpoint is None or np.isnan(temperature_setpoint) or type(temperature_setpoint) is float('nan'):
            return 0
        if self.controller_delay == 0:
            hvac_power_k: float = la.inv(self.T * state_model_k.D * self.S.transpose()) * (temperature_setpoint - self.T * state_model_k.C * state_k - self.T * state_model_k.D * self.S_bar.transpose() * inputs_k)

        elif self.controller_delay == 1:

            inputs_kp1: np.matrix = np.matrix([[name_inputs_kp1[_]] for _ in name_inputs_kp1])

            hvac_power_k: float = la.inv(self.T * state_model_k.C * state_model_k.B * self.S.transpose()) * (temperature_setpoint - self.T * state_model_k.C * state_model_k.A * state_k - self.T * state_model_k.C * state_model_k.B * self.S_bar.transpose() * self.S_bar * inputs_k - self.T * state_model_k.D * self.S_bar.transpose() * self.S_bar * inputs_kp1)

        return hvac_power_k[0, 0]

    def delay(self) -> int:
        """Get the delay of the controller.

        0 means that the controller reaches the setpoint immediately,
        1 means that the controller reaches the setpoint with a delay
        of one time slot.

        :return: The delay of the controller (0 or 1)
        :rtype: int
        """
        return self.controller_delay

    def __repr__(self) -> str:
        """Get a string representation of the controller.

        :return: String representation of the controller
        :rtype: str
        """
        return self.temperature_setpoint_port.model_variable_name + ' > ' + self.hvac_heat_port.model_variable_name

    def __str__(self) -> str:
        """Get a detailed string representation of the controller.

        :return: Detailed string representation of the controller
        :rtype: str
        """
        string: str = f'\n{self.hvac_heat_port.model_variable_name} is controlled by the setpoint {self.temperature_setpoint_port.feeding_variable_name}\n  with a delay of {self.controller_delay} hour(s)'
        return string


class Simulation:
    """Main simulation manager for building energy systems.

    The Simulation class orchestrates the entire simulation process, managing
    zones, control ports, state models, and heuristic control rules.

    :param dp: Data provider containing time series data
    :type dp: DataProvider
    :param state_model_maker: Factory for creating state models
    :type state_model_maker: BuildingStateModelMaker
    :param control_ports: List of control ports for the simulation
    :type control_ports: list[Port]
    """

    class HeuristicRule:
        """Container for heuristic control rules applied during simulation.

        This inner class manages the application of user-defined control rules
        for actions, power control, and setpoint modifications.

        :param dp: Data provider for time series data
        :type dp: DataProvider
        :param simulation: Parent simulation instance
        :type simulation: Simulation
        :param action_rule: Function for executing actions at each time step
        :type action_rule: callable | None
        :param control_rule: Function for modifying control values
        :type control_rule: callable | None
        :param setpoint_rule: Function for modifying setpoint values
        :type setpoint_rule: callable | None
        """

        def __init__(self, dp: DataProvider, simulation: Simulation, action_rule: callable = None, control_rule: callable = None, setpoint_rule: callable = None) -> None:
            """Initialize heuristic rule container.

            :param dp: Data provider for time series data
            :type dp: DataProvider
            :param simulation: Parent simulation instance
            :type simulation: Simulation
            :param action_rule: Function for executing actions at each time step
            :type action_rule: callable | None
            :param control_rule: Function for modifying control values
            :type control_rule: callable | None
            :param setpoint_rule: Function for modifying setpoint values
            :type setpoint_rule: callable | None
            """
            self.dp: DataProvider = dp
            self.simulation: Simulation = simulation
            self.ports: list[Port] = simulation.control_ports
            self.day_number_0: int = self.dp.datetimes[0]
            self.action_rule: callable = action_rule
            self.control_rule: callable = control_rule
            self.setpoint_rule: callable = setpoint_rule

        def hour(self, k: int) -> int:
            """Get the hour of day for time step k.

            :param k: Time step index
            :type k: int
            :return: Hour of day (0-23)
            :rtype: int
            """
            return self.simulation.datetimes[k].hour

        def weekday(self, k: int) -> int:
            """Get the day of week for time step k.

            :param k: Time step index
            :type k: int
            :return: Day of week (0=Monday, 6=Sunday)
            :rtype: int
            """
            return self.simulation.datetimes[k].weekday()

        def day_number(self, k: int) -> int:
            """Get the day number since simulation start for time step k.

            :param k: Time step index
            :type k: int
            :return: Number of days since simulation start
            :rtype: int
            """
            return (self.dp.datetimes[k] - self.dp.datetimes[0]).days

        def control_ports(self, feeding_variable_name: str = None) -> Port | list[Port]:
            """Get control ports by name or all control ports.

            :param feeding_variable_name: Name of specific control port to retrieve
            :type feeding_variable_name: str | None
            :return: Control port(s) matching the criteria
            :rtype: Port | list[Port]
            :raises ValueError: If specified control port is not found
            """
            if feeding_variable_name is None:
                return {port.feeding_variable_name: port for port in self.simulation.control_ports}
            for control_port in self.simulation.control_ports:
                if control_port.feeding_variable_name == feeding_variable_name:
                    return control_port
            raise ValueError(f'No control port found for {feeding_variable_name}, available control ports are: {", ".join([p.feeding_variable_name for p in self.simulation.control_ports])}')

        def action(self, k: int) -> None:
            """Execute action rule at time step k.

            :param k: Time step index
            :type k: int
            """
            if self.action_rule is not None:
                self.action_rule(self, k)

        def control(self, k: int, heater_power: float) -> float:
            """Apply control rule to heater power at time step k.

            :param k: Time step index
            :type k: int
            :param heater_power: Original heater power value
            :type heater_power: float
            :return: Modified heater power value
            :rtype: float
            """
            if self.control_rule is not None or not np.isnan(heater_power):
                heater_power = self.control_rule(self, k, heater_power)
            return heater_power

        def setpoint(self, k: int, setpoint: float) -> float:
            """Apply setpoint rule to temperature setpoint at time step k.

            :param k: Time step index
            :type k: int
            :param setpoint: Original setpoint value
            :type setpoint: float
            :return: Modified setpoint value
            :rtype: float
            """
            if self.setpoint_rule is not None or not np.isnan(setpoint):
                setpoint = self.setpoint_rule(self, k, setpoint)
            return setpoint

    class DataZone:
        """Container for zone-specific data and control configuration.

        This inner class manages zone-specific information including heat gains,
        CO2 production, HVAC control, and temperature control.

        :param simulation: Parent simulation instance
        :type simulation: Simulation
        :param zone_name: Name of the zone
        :type zone_name: str
        :param heat_gain_name: Name of the heat gain variable
        :type heat_gain_name: str
        :param CO2production_name: Name of the CO2 production variable
        :type CO2production_name: str
        :param hvac_power_port: Port for controlling HVAC power
        :type hvac_power_port: Port | None
        :param temperature_controller: Temperature controller for the zone
        :type temperature_controller: TemperatureController | None
        :raises ValueError: If heat gain or CO2 production variables are not found
        """

        def __init__(self, simulation: Simulation, zone_name: str,  heat_gain_name: str, CO2production_name: str, hvac_power_port: Port = None, temperature_controller: TemperatureController = None) -> None:
            """Initialize the data zone.

            :param simulation: Simulation instance
            :type simulation: Simulation
            :param zone_name: Name of the zone
            :type zone_name: str
            :param heat_gain_name: Name of the heat gain variable
            :type heat_gain_name: str
            :param CO2production_name: Name of the CO2 production variable
            :type CO2production_name: str
            :param hvac_power_port: Port for controlling HVAC power
            :type hvac_power_port: Port | None
            :param temperature_controller: Temperature controller for the zone
            :type temperature_controller: TemperatureController | None
            :raises ValueError: If heat gain or CO2 production variables are not found
            """
            self.simulation: Simulation = simulation
            self.zone_name: str = zone_name
            self.hvac_power_port: Port = hvac_power_port
            self.temperature_controller: TemperatureController = temperature_controller

            self.heat_gain_name: str = heat_gain_name
            if heat_gain_name not in self.simulation.dp:
                raise ValueError(f'heat gain {heat_gain_name} must be defined in the data provider')
            self.model_temperature_name: str = 'TZ' + zone_name
            self.model_temperature_index: int = self.simulation.nominal_state_model.output_names.index(self.model_temperature_name)
            self.model_power_name: str = 'PZ' + zone_name
            self.model_power_index: int = self.simulation.nominal_state_model.input_names.index(self.model_power_name)

            self.CO2production_name: str = CO2production_name
            if CO2production_name not in self.simulation.dp:
                raise ValueError(f'CO2 production {CO2production_name} must be defined in the data provider')
            self.model_CCO2_name: str = 'CCO2' + zone_name
            self.model_CO2concentration_index: int = self.simulation.nominal_state_model.output_names.index(self.model_CCO2_name)
            self.model_CO2production_name: str = 'PCO2' + self.zone_name
            self.model_CO2production_index: int = self.simulation.nominal_state_model.input_names.index(self.model_CO2production_name)
            # determine the type of control
            if temperature_controller is None and hvac_power_port is None:
                self.control_type: CONTROL_TYPE = CONTROL_TYPE.NO_CONTROL
            elif temperature_controller is not None:
                self.control_type: CONTROL_TYPE = CONTROL_TYPE.TEMPERATURE_CONTROL
                self.temperature_controller: TemperatureController = temperature_controller
            else:
                self.control_type: CONTROL_TYPE = CONTROL_TYPE.POWER_CONTROL
                if hvac_power_port.model_variable_name != self.model_power_name:
                    raise ValueError(f'hvac_power_port.model_variable_name {hvac_power_port.model_variable_name} must be {self.model_power_name} for power control')

        def __repr__(self) -> str:
            """Get a string representation of the zone.

            :return: String representation of the zone
            :rtype: str
            """
            return f"ZONE \"{self.zone_name}\""

        def __str__(self) -> str:
            """Get a detailed string representation of the zone.

            :return: Detailed string representation of the zone
            :rtype: str
            """
            string: str = "___________________________________________________________\n"
            string += f"ZONE \"{self.zone_name}\" defined by temperature \"{self.model_temperature_name}\" and power \"{self.model_power_name}\""
            string
            if self.control_type == CONTROL_TYPE.NO_CONTROL:
                string += f" without control and fed by heat gains {self.heat_gain_name}"
            elif self.control_type == CONTROL_TYPE.POWER_CONTROL:
                string += f"with power control and fed by port \"{self.hvac_power_port.model_variable_name}\" and heat gain \"{self.heat_gain_name}\""
            elif self.control_type == CONTROL_TYPE.TEMPERATURE_CONTROL:
                string += str(self.temperature_controller)
                string += f" with heat gain: \"{self.heat_gain_name}\""
            return string

    def __init__(self, dp: DataProvider, state_model_maker: BuildingStateModelMaker, control_ports: list[Port]) -> None:
        """Initialize the simulation.

        :param dp: Data provider for time series data
        :type dp: DataProvider
        :param state_model_maker: Factory for creating state models
        :type state_model_maker: BuildingStateModelMaker
        :param control_ports: List of control ports for the simulation
        :type control_ports: list[Port]
        """
        self.dp: DataProvider = dp
        self.state_model_maker: BuildingStateModelMaker = state_model_maker
        self.control_ports: list[Port] = control_ports
        self.airflows: list[Airflow] = state_model_maker.airflows
        self.fingerprint_0: list[int] = self.dp.fingerprint(0)
        self.state_models_cache: dict[int, StateModel] = dict()

        self.name_zones: dict[str, Simulation.DataZone] = dict()
        self.nominal_state_model: StateModel = self.state_model_maker.make_nominal(reset_reduction=True)
        self.model_input_names: list[str] = self.nominal_state_model.input_names
        self.model_output_names: list[str] = self.nominal_state_model.output_names
        self.datetimes: list[datetime] = self.dp.series('datetime')
        self.day_of_week: list[int] = self.dp('day_of_week')   

    def add_zone(self, zone_name: str, heat_gain_name: str, CO2production_name: str, hvac_power_port: Port = None, temperature_controller: TemperatureController = None) -> None:
        """Add a zone to the simulation.

        :param zone_name: Name of the zone
        :type zone_name: str
        :param heat_gain_name: Name of the heat gain variable
        :type heat_gain_name: str
        :param CO2production_name: Name of the CO2 production variable
        :type CO2production_name: str
        :param hvac_power_port: Port for controlling HVAC power
        :type hvac_power_port: Port | None
        :param temperature_controller: Temperature controller for the zone
        :type temperature_controller: TemperatureController | None
        """
        self.name_zones[zone_name] = Simulation.DataZone(self, zone_name, heat_gain_name, CO2production_name, hvac_power_port=hvac_power_port, temperature_controller=temperature_controller)

    def run(self, suffix: str = '_sim', action_rule: callable = None, control_rule: callable = None, setpoint_rule: callable = None) -> None:
        """Run the simulation.

        :param suffix: Suffix for the output variables
        :type suffix: str
        :param action_rule: Function for executing actions at each time step
        :type action_rule: callable | None
        :param control_rule: Function for modifying control values
        :type control_rule: callable | None
        :param setpoint_rule: Function for modifying setpoint values
        :type setpoint_rule: callable | None
        """
        print("simulation running...")
        counter: int = 0
        # create a container for the control rule
        self.heuristic_rules: Simulation.HeuristicRule = Simulation.HeuristicRule(self.dp, self, action_rule, control_rule, setpoint_rule)
        # simulation starts here
        start: float = time.time()
        state_k: np.matrix = None
        simulated_outputs: dict[str, list[float]] = {output_name: list() for output_name in self.model_output_names}

        for k in range(len(self.dp)):
            # compute the current state model
            if action_rule is not None:
                self.heuristic_rules.action_rule(self, k)
            current_fingerprint: list[int] = self.dp.fingerprint(k)
            if current_fingerprint in self.state_models_cache:
                state_model_k = self.state_models_cache[current_fingerprint]
                counter += 1
                if counter % 100 == 0:
                    print('.', end='')
            else:
                state_model_k: StateModel = self.state_model_maker.make_k(k, reset_reduction=False)
                self.state_models_cache[self.dp.fingerprint(k)] = state_model_k
                print('*', end='')
                counter = 0
            # compute inputs and state vector
            name_inputs_k: dict[str, float] = {input_name: float(self.dp(input_name, k)) for input_name in self.model_input_names}
            for zone_name in self.name_zones:
                zone = self.name_zones[zone_name]
                zone_control_type: CONTROL_TYPE = zone.control_type
            if state_k is None:
                state_k: np.matrix = state_model_k.initialize(**name_inputs_k)
            # compute the output before change
            output_values: list[float] = state_model_k.output(**name_inputs_k)

            current_fingerprint: list[int] = self.dp.fingerprint(k)
            if current_fingerprint in self.state_models_cache:
                state_model_k = self.state_models_cache[current_fingerprint]
                counter += 1
                if counter % 100 == 0:
                    print('.', end='')
            else:
                state_model_k: StateModel = self.state_model_maker.make_k(k, reset_reduction=False)
                self.state_models_cache[self.dp.fingerprint(k)] = state_model_k
                print('*', end='')
                counter = 0

            for zone_name in self.name_zones:  # zone processing
                zone: Simulation.DataZone = self.name_zones[zone_name]
                zone_heat_gain_name: str = zone.heat_gain_name
                zone_heat_gain_k: str = self.dp(zone_heat_gain_name, k)
                zone_control_type: CONTROL_TYPE = zone.control_type

                if zone_control_type == CONTROL_TYPE.POWER_CONTROL:
                    control_k: float = zone.hvac_power_port(k, self.dp(zone.hvac_power_port.feeding_variable_name, k), **{v: self.dp(v, k) for v in zone.hvac_power_port.mode_variables})

                elif zone_control_type == CONTROL_TYPE.TEMPERATURE_CONTROL:
                    temperature_controller: TemperatureController = zone.temperature_controller
                    setpoint_k = self.dp(temperature_controller.temperature_setpoint_port.feeding_variable_name, k)
                    if setpoint_k is None or np.isnan(setpoint_k):
                        control_k = 0
                    else:
                        if k < len(self.dp) - 1:
                            name_inputs_kp1: dict[str, float] = {input_name: float(self.dp(input_name, k+1)) for input_name in self.model_input_names}
                        else:
                            name_inputs_kp1 = name_inputs_k
                        if self.heuristic_rules.setpoint_rule is not None:
                            setpoint_k = self.heuristic_rules.setpoint_rule(self, k, setpoint_k)
                        setpoint_k = temperature_controller.temperature_setpoint_port(k, setpoint_k, mode=self.dp('mode', k))
                        control_k = temperature_controller.hvac_power_k(k, setpoint_k, state_model_k, state_k, name_inputs_k, name_inputs_kp1) - zone_heat_gain_k

                if zone_control_type in (CONTROL_TYPE.POWER_CONTROL, CONTROL_TYPE.TEMPERATURE_CONTROL):
                    if self.heuristic_rules.control_rule is not None:
                        control_k = self.heuristic_rules.control_rule(self, k, control_k)
                    control_k = zone.hvac_power_port(k, control_k, mode=self.dp('mode', k))
                    self.dp(zone.hvac_power_port.feeding_variable_name, k, control_k)
                    zone_heat_gain_k: float = zone_heat_gain_k + control_k
                    name_inputs_k[zone.model_power_name] = zone_heat_gain_k
                    self.dp(zone.model_power_name, k, zone_heat_gain_k)

            state_model_k.set_state(state_k)
            output_values = state_model_k.output(**name_inputs_k)
            for i, model_output_name in enumerate(self.model_output_names):
                simulated_outputs[model_output_name].append(output_values[i])
            state_k = state_model_k.step(**name_inputs_k)
        print(f"\nDuration in seconds {time.time() - start} with a state model cache size={len(self.state_models_cache)}")
        string = "Simulation results have been stored in "
        for model_output_name in self.model_output_names:
            string += model_output_name + suffix + ','
            self.dp.add_external_variable(model_output_name + suffix, simulated_outputs[model_output_name])

    def __repr__(self) -> str:
        """Get a string representation of the simulation.

        :return: String representation of the simulation
        :rtype: str
        """
        return f"Simulation of zone(s): {', '.join(self.name_zones.keys())}"

    def __str__(self) -> str:
        """Get a detailed string representation of the simulation.

        :return: Detailed string representation of the simulation
        :rtype: str
        """
        string: str = "___________________________________________________________\n"
        string += self.__repr__()
        for zone_name in self.name_zones:
            string += f"\n{self.name_zones[zone_name]}"
        string += "\nControl ports are:\n"
        for control_port in self.control_ports:
            string += f"\n{control_port}"
        string += f"\n{self.nominal_state_model}"
        string += f"\n{self.airflows}"
        return string + "\n"
