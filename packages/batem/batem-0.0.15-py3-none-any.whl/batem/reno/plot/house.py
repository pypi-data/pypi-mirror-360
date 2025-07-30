from datetime import datetime
import os
from typing import Optional
from batem.reno.constants import DATE_FORMAT
from batem.reno.house.creation import HouseBuilder
from batem.reno.house.model import House
from plotly.graph_objects import Scatter, Figure

from batem.reno.pv.creation import PVPlantBuilder
from batem.reno.utils import (
    FilePathBuilder,
    TimeSpaceHandler,
    parse_args
)


class AppliancesPlotter:
    def __init__(self):
        pass

    def plot(self,
             house: House,
             hourly: bool = True,
             production: Optional[dict[datetime, float]] = None,
             show: bool = False):
        # Create a single figure
        fig = Figure()  # type: ignore

        # Add a line for each appliance
        for appliance in house.appliances:
            if hourly:
                time = list(appliance.consumption_hourly.keys())
                consumption = tuple(appliance.consumption_hourly.values())
                label = "consumption hourly"
            else:
                time = list(appliance.consumption_10min.keys())
                consumption = tuple(appliance.consumption_10min.values())
                label = "consumption 10min"

            fig.add_trace(
                Scatter(
                    x=time,
                    y=consumption,
                    name=f"{appliance.name} {label}",
                    mode='lines'
                )  # type: ignore
            )

        # Update layout
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Power [kW]",
            height=800,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            )
        )

        if production:
            x = list(production.keys())
            y = tuple(production.values())
            fig.add_trace(
                Scatter(x=x, y=y, mode='lines',
                        name="Production hourly",
                        )  # type: ignore
            )

        if show:
            fig.show()
        else:
            file_path = HousePlotBuilder().set_file_path(
                house,
                hourly=hourly,
                appliances=True,
                production=production is not None)
            fig.write_html(file_path, auto_open=True)


class HousePlotBuilder:
    def __init__(self):
        pass

    def set_file_path(self,
                      house: House,
                      hourly: bool,
                      appliances: bool = False,
                      production: bool = False) -> str:
        """
        Set the file path for the plot.
        If appliances is True, the file path will be for the appliances plot.
        If appliances is False, the file path will be for the house plot.
        If hourly is True, the file path will be for the hourly plot.
        If hourly is False, the file path will be for the 10min plot.
        """

        folder = FilePathBuilder().get_plots_folder()
        start_time_str = house.start_time.strftime(
            DATE_FORMAT) if house.start_time is not None else "_"
        end_time_str = house.end_time.strftime(
            DATE_FORMAT) if house.end_time is not None else "_"
        suffix = 'hourly' if hourly else '10min'
        prefix = 'appliances' if appliances else 'house'
        if production:
            prefix = f'{prefix}_with_production'
        file_name = (f"{prefix}_{house.house_id}_from_{start_time_str}_to_"
                     f"{end_time_str}_{suffix}.html")
        path = os.path.join(folder, file_name)
        return path


class HousePlotter:

    def __init__(self):
        pass

    def plot_consumption(
            self,
            house: House,
            hourly: bool = True,
            production: Optional[dict[datetime, float]] = None,
            show: bool = False):

        if hourly:
            time = list(house.total_consumption_hourly.keys())
            consumption = tuple(house.total_consumption_hourly.values())
            label = "Consumption hourly"
        else:
            time = list(house.total_consumption_10min.keys())
            consumption = tuple(house.total_consumption_10min.values())
            label = "Consumption 10min"

        fig = Figure()  # type: ignore
        fig.add_trace(
            Scatter(x=time, y=consumption, mode='lines',
                    name=label,
                    )  # type: ignore
        )

        if production is not None:
            time = list(production.keys())
            production_values = tuple(production.values())
            fig.add_trace(
                Scatter(x=time, y=production_values, mode='lines',
                        name="Production hourly",
                        )  # type: ignore
            )

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Power [kW]")

        if show:
            fig.show()
        else:
            file_path = HousePlotBuilder().set_file_path(
                house, hourly=hourly, appliances=False,
                production=production is not None)
            fig.write_html(file_path, auto_open=True)


if __name__ == "__main__":
    # python batem/reno/plot/house.py
    # house_id = 2000901
    house_id = 2000917

    args = parse_args()

    time_space_handler = TimeSpaceHandler(location=args.location,
                                          start_date=args.start_date,
                                          end_date=args.end_date)
    peak_power_kW = 8

    house = HouseBuilder().build_house_by_id(house_id)

    if house is None:
        print(f"Warning: House {house_id} not found")
        exit()

    AppliancesPlotter().plot(house, hourly=True)
    AppliancesPlotter().plot(house, hourly=False)
    HousePlotter().plot_consumption(house, hourly=True)
    HousePlotter().plot_consumption(house, hourly=False)

    pv_plant = PVPlantBuilder().build(time_space_handler=time_space_handler,
                                      exposure_deg=0,
                                      slope_deg=160,
                                      number_of_panels=3,
                                      peak_power_kW=peak_power_kW,
                                      )

    AppliancesPlotter().plot(house,
                             hourly=True,
                             production=pv_plant.power_production_hourly)
    HousePlotter().plot_consumption(
        house,
        hourly=True,
        production=pv_plant.power_production_hourly)
