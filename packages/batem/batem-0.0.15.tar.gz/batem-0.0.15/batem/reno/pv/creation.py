from datetime import datetime, timedelta
import pandas as pd
import pytz
from batem.core import weather
from batem.core import solar
from batem.core.timemg import datetime_to_stringdate, stringdate_to_datetime
from batem.reno.pv.model import PVPlant
from batem.reno.utils import FilePathBuilder, TimeSpaceHandler


class WeatherDataBuilder:
    def __init__(self):
        pass

    def build(self,
              location: str,
              latitude_north_deg: float,
              longitude_east_deg: float,
              from_datetime_string: str,
              to_datetime_string: str):
        """
        The location is a string like "Paris, France".
        The latitude_north_deg and longitude_east_deg
        are the coordinates of the location.
        The from_datetime_string and to_datetime_string
        are the dates of the data to be fetched.
        The from_datetime_string and to_datetime_string
        are in the format "DD/MM/YYYY HH:MM:SS".
        The from_date and to_date are the dates of the data to be fetched.
        The from_date and to_date are in the format "YYYY-MM-DD".
        """
        # Extract only the date, as per requirements of the openweathermap API
        from_date = from_datetime_string.split(" ")[0]
        to_date = to_datetime_string.split(" ")[0]

        to_datetime_str = self._adapt_end_time(to_date)
        to_date = to_datetime_str.split(" ")[0]

        print(f"From date: {from_date}")
        print(f"To date: {to_date}  ")

        open_weather_map_json_reader = weather.SiteWeatherDataBuilder(
            location=location,
            from_requested_stringdate=from_date,
            to_requested_stringdate=to_date,
            given_latitude_north_deg=latitude_north_deg,
            given_longitude_east_deg=longitude_east_deg)

        return open_weather_map_json_reader.site_weather_data

    def _adapt_end_time(self, end_date: str) -> str:
        """
        Adapt the end date and substract a day because
        weather data includes the next day.
        """
        # Clean up any extra spaces
        end_date = end_date.strip()

        # If the date doesn't have time, add it
        if " " not in end_date:
            end_date = f"{end_date} 00:00:00"

        # Parse the datetime
        end_date_as_datetime = stringdate_to_datetime(
            end_date,
            timezone_str="UTC"
        )

        # Subtract a day and convert back to string
        new_end_date = datetime_to_stringdate(
            end_date_as_datetime - timedelta(days=1)  # type: ignore
        )
        return new_end_date


class PVPlantBuilder:
    def __init__(self):
        pass

    def build(self,
              time_space_handler: TimeSpaceHandler,
              weather_data: weather.SiteWeatherData,
              peak_power_kW: float = 0.5,
              number_of_panels: int = 1,
              panel_height_m: float = 1.7,
              panel_width_m: float = 1,
              pv_efficiency: float = .2,
              PV_inverter_efficiency: float = 0.95,
              temperature_coefficient: float = 0.0035,
              exposure_deg: float = 0,
              slope_deg: float = 160,
              distance_between_arrays_m: float = 1.7,
              mount_type: solar.MOUNT_TYPES = solar.MOUNT_TYPES.FLAT):

        solar_model = solar.SolarModel(weather_data)

        pv_plant = solar.PVplant(
            solar_model,
            peak_power_kW=peak_power_kW,
            number_of_panels=number_of_panels,
            panel_height_m=panel_height_m,
            panel_width_m=panel_width_m,
            pv_efficiency=pv_efficiency * PV_inverter_efficiency,
            temperature_coefficient=temperature_coefficient,
            exposure_deg=exposure_deg,
            slope_deg=slope_deg,
            distance_between_arrays_m=distance_between_arrays_m,
            mount_type=mount_type)

        # Convert the datetimes to UTC
        range = [datetime.replace(tzinfo=pytz.timezone("UTC"))
                 for datetime in weather_data.datetimes]

        # Convert the powers to kW
        power_production = {
            timestamp: float(production)/1000
            for timestamp, production in zip(range, pv_plant.powers_W())}

        self._add_zero_value_for_first_hour(power_production)

        plant = PVPlant(weather_data=weather_data,
                        solar_model=solar_model,
                        exposure_deg=exposure_deg,
                        slope_deg=slope_deg,
                        pv_efficiency=pv_efficiency,
                        panel_height_m=panel_height_m,
                        panel_width_m=panel_width_m,
                        number_of_panels=number_of_panels,
                        peak_power_kW=peak_power_kW,
                        PV_inverter_efficiency=PV_inverter_efficiency,
                        temperature_coefficient=temperature_coefficient,
                        distance_between_arrays_m=distance_between_arrays_m,
                        mount_type=mount_type,
                        power_production_hourly=power_production)

        return plant

    def _add_zero_value_for_first_hour(
            self,
            power_production: dict[datetime, float]):
        """
        Add a zero value for the first hour.
        """
        start_of_range = list(power_production.keys())[0]
        new_start = start_of_range - pd.Timedelta(hours=1)
        power_production[new_start] = 0


if __name__ == "__main__":
    # python batem/reno/pv/creation.py

    time_space_handler = TimeSpaceHandler(location="Grenoble",
                                          start_date="01/02/1998",
                                          end_date="01/02/1999")

    weather_data = WeatherDataBuilder().build(
        location=time_space_handler.location,
        latitude_north_deg=time_space_handler.latitude_north_deg,
        longitude_east_deg=time_space_handler.longitude_east_deg,
        from_datetime_string=time_space_handler.start_date,
        to_datetime_string=time_space_handler.end_date)

    pv_plant = PVPlantBuilder().build(time_space_handler=time_space_handler,
                                      weather_data=weather_data,
                                      peak_power_kW=0.5)

    path = FilePathBuilder().get_pv_plant_path(time_space_handler)
    pv_plant.to_csv(path)
