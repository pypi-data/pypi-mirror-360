"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0
"""


# configuration of the lambda house
from __future__ import annotations
import core.lambdahouse
import core.weather
import core.library
import core.solar
import configparser
import time
import sys


config = configparser.ConfigParser()
config.read('setup.ini')
weather_file_name = None

# weather_file: str = 'campus_transition.json'
# location: str = 'Forges'
# weather_year = 2019
# latitude_deg_north, longitude_deg_east = 48.419742, 2.962580

weather_file: str = 'Grenoble.json'
location: str = 'Grenoble'
weather_year = 2022
latitude_deg_north, longitude_deg_east = 45.19154994547585, 5.722065312331381

# weather_file: str = 'saint-nazaire.json'
# location: str = 'Saint-Nazaire'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 47.271497, -2.208271

# weather_file: str = 'le_caire.json'
# location: str = 'Le Caire'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 30.088719, 31.235820

# weather_file: str = 'briancon.json'
# location: str = 'Briançon'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 44.901334, 6.644723

# weather_file: str = 'tirana.json'
# location: str = 'Tirana'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 41.330815, 19.819229

# weather_file: str = 'liege.json'
# location: str = 'liege'
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 50.63809597884662, 5.5748852887240945

# weather_file: str = 'coimbra.json'
# location: str = 'Coimbra'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 40.206317, -8.428578

# weather_file: str = 'refuge_des_bans.json'
# location: str = 'Refuge des Bans'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 44.83460591359195, 6.361240519353813

# weather_file: str = 'barcelonnette.json'
# location: str = 'Barcelonnette'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 44.387127, 6.652518

# location: str = 'Crolles'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 45.284790, 5.885759

# location: str = 'Assouan'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 24.02769921861417, 32.87455490478971

# location: str = 'Cayenne'
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 4.924435336591809, -52.31276008988111

# location: str = 'RefugeDeLaPilatte'
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 44.870439591344194, 6.331864347312895

# location: str = 'Giens'
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 43.05173789891146, 6.132881864519103

# location: str = 'AutransMeaudre'
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 45.175560185534195, 5.5427723689148065

# location: str = 'la-cote-saint-andre'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 45.393775, 5.260494

# location: str = 'Meolans'
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 44.399190, 6.497175

# location: str = "Saint-Germain-au-Mont-d'Or"
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 45.884843, 4.801576

# location: str = "Ardennes"
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 49.81357529876085, 4.74266551569724

# location: str = "Liege"
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 50.63809597884662, 5.5748852887240945

# location: str = "Grenoble_campus"
# weather_year = 2022
# latitude_deg_north, longitude_deg_east = 45.191135, 5.764832

# location: str = "Rotterdam"
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 51.932723048945405, 4.469347589348471

# location: str = "Liège"
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 50.63809597884662, 5.5748852887240945

# location: str = "Nagada"
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 25.90082736144239, 32.72443181962625

# location: str = "Novara"
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 45.453333753154936, 8.62274742072009

# location: str = "DahammaMahi"
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 47.777145, 3.169911

# location: str = "Mens"
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 44.816667, 5.750000

# latitude_deg_north, longitude_deg_east = 45.39394199789429, 5.259668832483038
# location: str = "La-cote-saint-andre"
# weather_year = 2022

# latitude_deg_north, longitude_deg_east = 45.216719, 5.577455
# location: str = "projet_vercors"
# weather_year = 2022

# location: str = 'Carqueiranne'
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 43.08933178200723, 6.072235955304281

# location: str = 'Saint-Julien-en-Saint-Alban'
# weather_year = 2023
# latitude_deg_north, longitude_deg_east = 44.71407488275519, 4.633318302898348

#########################################################################

if weather_file_name is None:
    weather_file_name = location

core.library.properties.load('polystyrene2', 'thermal', 170)  # the argument 1 is the local name that should be used in the wall compositions
core.library.properties.load('straw', 'thermal', 261)  # the argument 1 is the local name that should be used in the wall compositions


class MyConfiguration(core.lambdahouse.LambdaParametricData):

    def __init__(self, location: str, latitude: float, longitude: float, weather_year: int, albedo: float = 0.1, pollution: float = 0.1) -> None:
        super().__init__(location, latitude, longitude, weather_year, albedo, pollution)

        self.section('house')
        self(total_living_surface_m2=100)
        self(height_per_floor_m=2.5)
        self(shape_factor=1, parametric=[.25, .5, .75, 1, 1.25, 1.5, 1.75, 2, 3])
        self(number_of_floors=1, parametric=[1, 2, 3])
        self(wall_composition_in_out=[('concrete', 14e-2), ('plaster', 15e-3), ('polystyrene', 20e-2)])
        self(roof_composition_in_out=[('plaster', 30e-3), ('polystyrene', 9e-2), ('concrete', 13e-2)])
        self(glass_composition_in_out=[('glass', 4e-3), ('air', 6e-3), ('glass', 4e-3)])
        self(ground_composition_in_out=[('concrete', 13e-2), ('polystyrene', 30e-2), ('gravels', 20e-2)])
        self.insulation: str = 'polystyrene'  # be careful: no space in the material used for insulation
        self(polystyrene=20e-2, parametric=[0, 5e-2, 10e-2, 15e-2, 20e-2, 25e-2, 30e-2, 35e-2, 40e-2])

        self.section('windows')
        self(offset_exposure_deg=0, parametric=[offset_exposure for offset_exposure in range(-45, 45, 5)])
        self(glazing_percent={'north': 0.1, 'west': 0.1, 'east': 0.1, 'south': 0.1}, parametric=[0.05, .2, .4, .6, .8])
        self(solar_factor=0.8)
        self(south_solar_protection_angle_deg=0, parametric=[0, 15, 30, 35, 40, 45, 50, 55, 60, 65, 70])

        self.section('HVAC and photovoltaic (PV) systems')
        self(heating_setpoint=21, parametric=[18, 19, 20, 22, 23])
        self(delta_temperature_absence_mode=3, parametric=[0, 1, 2, 3, 4])
        self(cooling_setpoint=26, parametric=[23, 24, 25, 27, 28, 29])
        self(winter_hvac_trigger_temperature=20)
        self(summer_hvac_trigger_temperature=26)
        self(hvac_hour_delay_for_trigger=24)
        self(hvac_COP=3)
        self(PV_surface=20, parametric=[2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22])
        self(final_to_primary_energy_coefficient=2.54)
        self(air_renewal_presence_vol_per_h=1, parametric=[.5, 1, 2, 3])  # in vol/h
        self(air_renewal_absence_vol_per_h=.1)
        self(ventilation_heat_recovery_efficiency=0.8, parametric=[0, .25, .5, .7, .9])
        self(pv_efficiency=0.20)

        self.section('inhabitants')
        self(occupancy_schema={(1, 2, 3, 4, 5): {(18, 7): 4, (7, 18): 0}, (6, 7): {(0, 24): 4}})  # days of weeks (1=Monday,...), period (start. hour, end. hour) : avg occupancy
        self(average_occupancy_electric_gain=50)
        self(average_occupancy_metabolic_gain=100)
        self(average_permanent_electric_gain=200)
        self(air_renewal_overheat_threshold=26)
        self(air_renewal_overheat=5)


configuration: MyConfiguration = MyConfiguration(location=location, weather_year=weather_year, latitude=latitude_deg_north, longitude=longitude_deg_east)

on_screen = False
report_generator: core.lambdahouse.ReportGenerator = core.lambdahouse.ReportGenerator(configuration, on_screen=on_screen)
analysis: core.lambdahouse.Analyzes = core.lambdahouse.Analyzes(report_generator)

print(configuration)
tstart: float = time.time()
analysis.climate(report_generator)
analysis.evolution(report_generator)
analysis.solar(report_generator)
analysis.house(report_generator)
analysis.neutrality(report_generator)
print(f'duration {round((time.time() - tstart)/60, 1)} min', file=sys.stderr)
