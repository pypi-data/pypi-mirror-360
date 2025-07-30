import os
import plotly.graph_objects as go
from batem.weather.model import OPEN_WEATHER_TO_NAMES_MAP, WEATHER_VARIABLES, WeatherData
from batem.reno.utils import FilePathBuilder
from typing import List, Optional


class WeatherPlotter:
    """Class for plotting weather data using plotly."""

    def __init__(self):
        """Initialize the weather plotter."""
        # Define units for each variable
        self.units = {
            'temperature': '°C',
            'humidity': '%',
            'wind_speed': 'm/s',
            'wind_direction_in_deg': '°',
            'pressure': 'hPa',
            'cloudiness': '%',
            'feels_like': '°C',
            'dew_point_temperature': '°C'
        }

    def plot_variable(self, weather_data: WeatherData,
                      variable: str,
                      title: Optional[str] = None) -> None:
        """Plot any weather variable over time.

        Args:
            weather_data: WeatherData object containing the data to plot
            variable: Name of the variable to plot
            title: Optional custom title for the plot
        """
        found_variable = False
        for owv in WEATHER_VARIABLES:
            if owv in OPEN_WEATHER_TO_NAMES_MAP:
                if variable in OPEN_WEATHER_TO_NAMES_MAP[owv]:
                    found_variable = True
                    break
            else:
                if variable == owv:
                    found_variable = True
                    break
        if not found_variable:
            raise ValueError(
                f"Variable '{variable}' not found. Available variables: "
                f"{WEATHER_VARIABLES}"
            )

        time = list(weather_data.variables_by_time.keys())
        values = [
            data[variable]
            for data in weather_data.variables_by_time.values()
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=time,
                y=values,
                mode='lines',
                name=variable.replace('_', ' ').title(),
            )
        )

        if title is None:
            title = f"{variable.replace('_', ' ').title()} in {weather_data.location}"

        unit = self.units.get(variable, '')
        y_axis_title = f"{variable.replace('_', ' ').title()} [{unit}]"

        fig.update_layout(
            title=title,
            xaxis_title='Time',
            yaxis_title=y_axis_title
        )

        file_path = WeatherPlotBuilder().set_file_path(
            weather_data, variable)
        fig.write_html(file_path, auto_open=True)

    def plot_multiple_variables(self, weather_data: WeatherData,
                                variables: List[str],
                                title: Optional[str] = None) -> None:
        """Plot multiple weather variables on the same graph.

        Args:
            weather_data: WeatherData object containing the data to plot
            variables: List of variable names to plot
            title: Optional custom title for the plot
        """
        time = list(weather_data.variables_by_time.keys())
        fig = go.Figure()

        for variable in variables:
            if variable not in weather_data.variables_by_time[0]:
                available_vars = list(weather_data.variables_by_time[0].keys())
                raise ValueError(
                    f"Variable '{variable}' not found. Available variables: "
                    f"{available_vars}"
                )

            values = [
                data[variable]
                for data in weather_data.variables_by_time.values()
            ]

            fig.add_trace(
                go.Scatter(
                    x=time,
                    y=values,
                    mode='lines',
                    name=variable.replace('_', ' ').title(),
                )
            )

        if title is None:
            title = f"Multiple Variables in {weather_data.location}"

        fig.update_layout(
            title=title,
            xaxis_title='Time',
            yaxis_title='Value'
        )

        file_path = WeatherPlotBuilder().set_file_path(
            weather_data, '_'.join(variables))
        fig.write_html(file_path, auto_open=True)

    def plot_temperature(self, weather_data: WeatherData) -> None:
        """Plot temperature data over time.

        Args:
            weather_data: WeatherData object containing the data to plot
        """
        self.plot_variable(weather_data, 'temperature')

    def plot_humidity(self, weather_data: WeatherData) -> None:
        """Plot humidity data over time.

        Args:
            weather_data: WeatherData object containing the data to plot
        """
        self.plot_variable(weather_data, 'humidity')

    def plot_wind(self, weather_data: WeatherData) -> None:
        """Plot wind speed and direction over time.

        Args:
            weather_data: WeatherData object containing the data to plot
        """
        time = list(weather_data.variables_by_time.keys())
        wind_speed = [
            data['wind_speed']
            for data in weather_data.variables_by_time.values()
        ]
        wind_direction = [
            data['wind_direction_in_deg']
            for data in weather_data.variables_by_time.values()
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=time,
                y=wind_speed,
                mode='lines',
                name='Wind Speed',
            )
        )
        fig.add_trace(
            go.Scatter(
                x=time,
                y=wind_direction,
                mode='lines',
                name='Wind Direction',
                yaxis='y2'
            )
        )

        fig.update_layout(
            title=f'Wind in {weather_data.location}',
            xaxis_title='Time',
            yaxis_title='Wind Speed [m/s]',
            yaxis2=dict(
                title='Wind Direction [°]',
                overlaying='y',
                side='right'
            )
        )

        file_path = WeatherPlotBuilder().set_file_path(
            weather_data, 'wind')
        fig.write_html(file_path, auto_open=True)


class WeatherPlotBuilder:
    """Class for building weather plot file paths."""

    def __init__(self):
        """Initialize the weather plot builder."""
        pass

    def set_file_path(self, weather_data: WeatherData,
                      plot_type: str) -> str:
        """Set the file path for the weather plot.

        Args:
            weather_data: WeatherData object containing the data
            plot_type: Type of plot (temperature, humidity, wind)

        Returns:
            str: Path where the plot will be saved
        """
        start_time = min(weather_data.variables_by_time.keys())
        end_time = max(weather_data.variables_by_time.keys())

        folder = FilePathBuilder().get_plots_folder()
        name = f"weather_{weather_data.location}_{plot_type}"
        name = f"{name}_from_{start_time}_to_{end_time}.html"

        file_path = os.path.join(folder, name)
        return file_path


if __name__ == "__main__":

    # python batem/plot/weather.py

    # Example usage
    from batem.reno.utils import TimeSpaceHandler
    from batem.weather.creation import WeatherDataBuilder

    location = "Grenoble"
    time_space_handler = TimeSpaceHandler(
        location=location,
        start_date="01/01/2023",
        end_date="31/12/2023"
    )

    weather_data = WeatherDataBuilder().build(time_space_handler)

    plotter = WeatherPlotter()

    # Example of plotting a single variable
    plotter.plot_variable(weather_data, 'temperature')

    # Example of plotting multiple variables
    plotter.plot_multiple_variables(
        weather_data,
        ['temperature', 'humidity', 'pressure']
    )
