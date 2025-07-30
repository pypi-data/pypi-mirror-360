"""
House and appliance creation utilities.

This module provides classes for creating House and Appliance instances
from various data sources (database, CSV files) and managing their
relationships.
"""

import csv
from datetime import datetime
from typing import Optional

import numpy

from batem.core.timemg import epochtimems_to_datetime
from batem.reno.db import execute_query, get_db_connection
from batem.reno.house.model import Appliance, House
import pandas as pd
from batem.reno.constants import APPLIANCES
from batem.reno.utils import FilePathBuilder


class HouseBuilder:
    """
    Builder for creating House instances from various data sources.

    This class provides methods to create House instances from:
    - Database records
    - CSV files
    - Individual house IDs
    """

    def __init__(self):
        """Initialize the HouseBuilder."""
        pass

    def build_all_houses(self, exclude_consumption: bool = False
                         ) -> list[House]:
        """
        Build all houses from the database.

        Args:
            exclude_consumption: Whether to exclude consumption data
                (default: False)

        Returns:
            list[House]: List of created House instances

        Example:
            >>> builder = HouseBuilder()
            >>> houses = builder.build_all_houses()
        """
        query = """
        SELECT ID, ZIPcode, Location, WeatherStationIDREF, \
            StartingEpochTime, EndingEpochTime
        FROM House
        """
        houses_data = execute_query(query)

        houses: list[House] = []

        for house_data in houses_data:
            house = self.build_house(house_data, exclude_consumption)
            if house is not None:
                houses.append(house)
        return houses

    def build_house(self, house_data: tuple[int, str, str, int, int,
                                            int],
                    exclude_consumption: bool = False) -> Optional[House]:
        """
        Build a house from database record.

        Args:
            house_data: Tuple containing house information:
                (ID, ZIPcode, Location, WeatherStationIDREF,
                 StartingEpochTime, EndingEpochTime)
            exclude_consumption: Whether to exclude consumption data
                (default: False)

        Returns:
            Optional[House]: Created House instance or None if no
                appliances found

        Example:
            >>> data = (1, "38000", "Grenoble", 1, 1234567890, 1234567899)
            >>> house = builder.build_house(data)
        """
        ID = house_data[0]
        ZIPcode = house_data[1]
        Location = house_data[2]
        WeatherStationIDREF = house_data[3]
        # Convert to milliseconds, then to UTC
        StartingEpochTime = epochtimems_to_datetime(
            house_data[4] * 1000, timezone_str="UTC")
        EndingEpochTime = epochtimems_to_datetime(
            house_data[5] * 1000, timezone_str="UTC")

        house = House(ID, ZIPcode, Location, WeatherStationIDREF)
        house.start_time = StartingEpochTime
        house.end_time = EndingEpochTime

        # Get the appliances first to check if the house has any appliances
        appliances = ApplianceBuilder().build_all_appliances(house)

        if len(appliances) == 0:
            return None

        if exclude_consumption:
            msg = (f"Built house {ID} from {house.start_time} to "
                   f"{house.end_time} from database, "
                   "but excluded consumption.")
            print(msg)
            return house

        house.appliances = appliances

        house.set_total_consumption()

        msg = (f"Built house {ID} from {house.start_time} to {house.end_time} "
               f"from database.")
        print(msg)
        return house

    def build_house_from_csv(self, house_id: int, path: str) -> House:
        """
        Build a house from a CSV file.

        The CSV file should have the following format:
        - Header: timestamp,total,appliance_1,appliance_2,...
        - Timestamp format: YYYY-MM-DD HH:MM:SS
        - Consumption values in kW

        Args:
            house_id: ID to assign to the house
            path: Path to the CSV file

        Returns:
            House: Created House instance

        Example:
            >>> house = builder.build_house_from_csv(1, "house_1.csv")
        """
        house = House(house_id)
        appliances = ApplianceBuilder().build_appliances_from_csv(
            house, path)
        house.appliances = appliances
        house.set_total_consumption()
        self._set_start_and_end_time(house)

        print(f"House {house_id} built from csv.")

        return house

    def _set_start_and_end_time(self, house: House):
        """
        Set the start and end time of a house from its consumption data.

        Args:
            house: House instance to set times for
        """
        house.start_time = list(house.total_consumption_10min.keys())[0]
        house.end_time = list(house.total_consumption_10min.keys())[-1]

    def build_house_by_id(self, house_id: int) -> Optional[House]:
        """
        Build a house from the database by its ID.

        Args:
            house_id: ID of the house to build

        Returns:
            House: Created House instance

        Raises:
            ValueError: If the house has no appliances

        Example:
            >>> house = builder.build_house_by_id(1)
        """
        query = """
        SELECT ID, ZIPcode, Location, WeatherStationIDREF, \
            StartingEpochTime, EndingEpochTime
        FROM House
        WHERE ID = ?
        """
        house_data = execute_query(query, (house_id,))
        house = self.build_house(house_data[0])
        if house is None:
            print(f"Warning: House {house_id} has no appliances")
            return None
        return house


class ApplianceBuilder:
    """
    Builder for creating Appliance instances from various data sources.

    This class provides methods to create Appliance instances from:
    - Database records
    - CSV files
    """

    def __init__(self):
        """Initialize the ApplianceBuilder."""
        pass

    def build_appliances_from_csv(self, house: House, path: str
                                  ) -> list[Appliance]:
        """
        Build appliances from a CSV file.

        The CSV file should have the following format:
        - Header: timestamp,total,appliance_1,appliance_2,...
        - Timestamp format: YYYY-MM-DD HH:MM:SS
        - Consumption values in kW

        Args:
            house: Parent House instance
            path: Path to the CSV file

        Returns:
            list[Appliance]: List of created Appliance instances

        Example:
            >>> appliances = builder.build_appliances_from_csv(
            ...     house, "data.csv")
        """
        data_as_dict: dict[datetime, dict[str, float]] = \
            pd.read_csv(path, index_col=0, parse_dates=[
                        0]).to_dict(orient='index')  # type: ignore

        appliances: list[Appliance] = []
        with open(path, "r") as f:
            # Extract the header
            reader = csv.reader(f)
            header = next(reader)
            for key in header:
                if key in ['total', 'timestamp']:
                    continue
                ID, name, type = key.split('_')
                ID = int(ID)
                type = APPLIANCES(type)

                # Extract the consumption data
                consumption_10min = {
                    timestamp: data[key]
                    for timestamp, data in data_as_dict.items()
                }

                appliance = Appliance(ID, house, name, type,
                                      consumption_10min)
                appliances.append(appliance)

        return appliances

    def build_all_appliances(self, house: House) -> list[Appliance]:
        """
        Build all appliances for a house from the database.

        Excludes total site light consumption and site consumption.

        Args:
            house: Parent House instance

        Returns:
            list[Appliance]: List of created Appliance instances

        Example:
            >>> appliances = builder.build_all_appliances(house)
        """
        query = """
        SELECT ID, HouseIDREF, Name
        FROM Appliance
        WHERE HouseIDREF = ?
        """
        appliances_data = execute_query(query, (house.house_id,))

        appliances: list[Appliance] = []
        for appliance_data in appliances_data:
            name = str(appliance_data[2])
            if name in ["Site consumption ()"]:
                continue
            appliance = self.build_appliance(appliance_data, house)
            if appliance is not None:
                appliances.append(appliance)

        return appliances

    def build_appliance(self, appliance_data: tuple[int, int, str, int],
                        house: House) -> Optional[Appliance]:
        """
        Build an appliance from database record.

        Args:
            appliance_data: Tuple containing appliance information:
                (ID, HouseIDREF, Name, TypeIDREF)
            house: Parent House instance

        Returns:
            Optional[Appliance]: Created Appliance instance or None if
                creation fails
        """
        ID = int(appliance_data[0])
        name = str(appliance_data[2])

        appliance_type = self._infer_appliance_type(name)
        consumption_10min = self._get_consumption(house.house_id, ID)
        filtered_consumption = self._filter_outliers(consumption_10min)

        if filtered_consumption == {}:
            return None

        appliance = Appliance(ID=ID,
                              house=house,
                              name=name,
                              type_name=appliance_type,
                              consumption_10min=filtered_consumption)

        return appliance

    def _infer_appliance_type(self, name: str) -> APPLIANCES:
        """
        Infer the type of an appliance from the name.
        """
        inferred_type: APPLIANCES | None = None
        for appliance_type in APPLIANCES:
            if appliance_type.name.lower() in name.lower():
                inferred_type = appliance_type
                break
        if inferred_type is None:
            inferred_type = APPLIANCES.OTHER
        return inferred_type

    def _get_consumption(self, house_id: int, appliance_id: int
                         ) -> dict[datetime, float]:
        """
        Get the consumption data for an appliance with optimized performance.
        The consumption data is stored in 10-minute intervals.
        The data is stored in kW.
        """

        query = """
        SELECT EpochTime, Value
        FROM Consumption
        WHERE ApplianceIDREF = ?
        AND HouseIDREF = ?
        ORDER BY EpochTime
        """

        with get_db_connection() as conn:
            # Enable WAL mode for better read performance
            conn.execute("PRAGMA journal_mode=WAL")
            cursor = conn.cursor()
            cursor.execute(query, (appliance_id, house_id))

            # Use list comprehension for faster data processing
            consumption_data_dict = {
                epochtimems_to_datetime(
                    epoch * 1000,  # convert to milliseconds
                    timezone_str="UTC"): float(value)/1000  # to kW
                for epoch, value in cursor.fetchall()
            }

        return consumption_data_dict

    def _filter_anomalies_basic(self, consumption: dict[datetime, float],
                                threshold: float = 1500
                                ) -> dict[datetime, float]:
        """
        Filter anomalies from the consumption data.
        Any consumption value over a threshold is excluded.
        """
        return {k: 0 if v > threshold else v for k, v in consumption.items()}

    def _filter_outliers(self,
                         consumption: dict[datetime, float],
                         outlier_sensitivity: float = 10.0
                         ) -> dict[datetime, float]:
        """Filter out anomalous values in a time series
        by smoothing spikes and dips.

        Args:
            values: List of numerical values representing time series data
            outlier_sensitivity: Threshold multiplier for standard deviation
                (default: 10.0)

        Returns:
            List of values with outliers smoothed out
        """
        if len(consumption) < 3:
            return consumption.copy()

        # Calculate differences between consecutive values

        consumption_values = list(consumption.values())
        deltas = numpy.diff(consumption_values)
        mean_delta = numpy.mean(deltas)
        std_delta = numpy.std(deltas)

        # Create threshold for outlier detection
        threshold = mean_delta + outlier_sensitivity * std_delta

        # Check each point (except first and last) for outliers
        for i in range(1, len(consumption_values) - 1):
            prev_diff = consumption_values[i] - consumption_values[i - 1]
            next_diff = consumption_values[i + 1] - consumption_values[i]

            # Detect if point is a spike or dip
            is_outlier = (
                abs(prev_diff) > threshold and
                abs(next_diff) > threshold and
                prev_diff * next_diff < 0
            )

            if is_outlier:
                # Smooth the outlier by averaging neighbors
                consumption_values[i] = (consumption_values[i - 1] +
                                         consumption_values[i + 1]) / 2

        return {k: v for k, v in zip(consumption.keys(), consumption_values)}


if __name__ == "__main__":

    # python batem/reno/house/creation.py

    # python -m cProfile -o batem/reno/house/house_creation.prof batem/reno/house/creation.py
    # snakeviz batem/reno/house/house_creation.prof

    house = HouseBuilder().build_house_by_id(2000900)
    if house is None:
        print("Warning: House 2000900 not found")
        exit()
    path = FilePathBuilder().get_house_consumption_path(house.house_id)

    hourly_path = FilePathBuilder().get_house_consumption_path(
        house.house_id, hourly=True)

    house.to_csv(path)
    house.to_csv(hourly_path, hourly=True)

    path = FilePathBuilder().get_house_consumption_path(2000900)
    house = HouseBuilder().build_house_from_csv(2000900, path)
