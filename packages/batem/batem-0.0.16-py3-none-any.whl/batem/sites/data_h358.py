"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0

"""
from __future__ import annotations
from batem.core.solar import SolarModel, SolarSystem, RectangularMask, InvertedMask, Collector
from batem.core.data import DataProvider, Bindings


def make_data_provider(starting_stringdate: str = '15/02/2015', ending_stringdate: str = '15/02/2016', control: bool = False) -> DataProvider:

    deleted_variables: tuple[str] = ('Tyanis', 'zetaW7', 'zetaW9', 'wind_direction_in_deg', 'feels_like', 'occupancy', 'temp_min', 'temp_max', 'description', 'power_heater', 'temperature_2m', 'relativehumidity_2m', 'dewpoint_2m', 'apparent_temperature', 'weathercode', 'cloudcover_low', 'cloudcover_mid', 'cloudcover_high', 'et0_fao_evapotranspiration', 'vapor_pressure_deficit', 'windspeed_10m', 'windspeed_100m', 'winddirection_10m', 'winddirection_100m', 'windgusts_10m', 'soil_temperature_0_to_7cm', 'soil_temperature_7_to_28cm', 'soil_temperature_28_to_100cm', 'soil_temperature_100_to_255cm', 'soil_moisture_0_to_7cm', 'soil_moisture_7_to_28cm', 'soil_moisture_28_to_100cm', 'soil_moisture_100_to_255cm', 'is_day', 'shortwave_radiation', 'direct_radiation', 'diffuse_radiation', 'direct_normal_irradiance')  # 'pressure_msl', 'surface_pressure', 

    latitude_deg_north = 45.19154994547585
    longitude_deg_east = 5.722065312331381
    bindings = Bindings()
    bindings.link_model_data('TZoffice', 'Toffice_reference')
    bindings.link_model_data('TZcorridor', 'Tcorridor')
    bindings.link_model_data('TZdownstairs', 'downstairs:Temperature')
    bindings.link_model_data('TZoutdoor', 'weather_temperature')
    bindings.link_model_data('PZoffice', 'office:Pheat')
    bindings.link_model_data('CCO2corridor', 'corridor_CO2_concentration')
    bindings.link_model_data('PCO2office', 'office:PCO2')
    bindings.link_model_data('CCO2outdoor', 'outdoor:CCO2')
    bindings.link_model_data('CCO2office', 'office_CO2_concentration')
    bindings.link_model_data('office-outdoor:z_window', 'window_opening')
    bindings.link_model_data('office-corridor:z_door', 'door_opening')
    bindings.link_model_data('indoor:occupancy', 'occupancy')

    dp = DataProvider(location='Grenoble', latitude_deg_north=latitude_deg_north, longitude_deg_east=longitude_deg_east, csv_measurement_filename='h358data_2015-2016.csv', starting_stringdate=starting_stringdate, ending_stringdate=ending_stringdate, bindings=bindings, albedo=0.1, pollution=0.1, number_of_levels=4, deleted_variables=deleted_variables)

    dp.add_parameter('body_metabolism', 130, (80, 400, 10))
    dp.add_parameter('body_PCO2', 7, (5, 15, 1))
    dp.add_parameter('office:volume', 56)
    dp.add_parameter('office:permanent_power', 100, (0, 500, 25))
    dp.add_parameter('office-outdoor:Q_0', 10/3600, (1/3600, 15/3600, 1/3600))
    dp.add_parameter('office-outdoor:Q_window', 5500/3600, (1000/3600, 10000/3600, 10/3600))
    dp.add_parameter('office-outdoor:Q_door', 1000/3600, (500/3600, 2000/3600, 10/3600))
    dp.add_parameter('office-corridor:Q_0', 30/3600, (1/3600, 50/3600, 1/3600))
    dp.add_parameter('corridor-office:Q_window', 5500/3600, (10/3600, 10000/3600, 10/3600))
    dp.add_parameter('corridor-office:Q_door', 1000/3600, (500/3600, 2000/3600, 10/3600))
    dp.add_parameter('downstairs-office:slab_surface_correction', 1)  # , (1, 3, .1)
    dp.add_parameter('office:heater_power_per_delta_surface_temperature', 50, (30, 200, 10))
    dp.add_parameter('office-outdoor:psi_bridge', 0.5 * 0.99)  # , (0.0 * 0.99, 0.5 * 5, 0.1)
    dp.add_parameter('office-outdoor:foam_thickness', 34e-3)  # , (10e-3, 50e-3, 10e-3)
    dp.add_parameter('office-outdoor:solar_factor', 0.8, (0, 1, .1))
    dp.add_parameter('TZdownstairs', 20, (16, 25, 1))
    dp.add_parameter('CCO2outdoor', 450, (250, 650, 50))
    dp.add_parameter('office-outdoor:Rfactor', 1, (.5, 2, .1))
    dp.add_parameter('corridor-office:Rfactor', 1, (.5, 2, .1))
    dp.add_parameter('downstairs-office:Rfactor', 1, (.5, 2, .1))
    dp.add_parameter('office-outdoor:Cfactor', 1, (.1, 10, .1))
    dp.add_parameter('corridor-office:Cfactor', 1, (.1, 10, .1))
    dp.add_parameter('downstairs-office:Cfactor', 1, (.1, 10, .1))

    window_mask = InvertedMask(RectangularMask((-86, 60), (20, 68)))
    solar_model = SolarModel(dp.weather_data)
    solar_system = SolarSystem(solar_model)
    
    Collector(solar_system, 'main', surface_m2=2, exposure_deg=-13, slope_deg=90, solar_factor=1, mask=window_mask)
    solar_gains_with_mask = solar_system.powers_W(gather_collectors=True)
    dp.add_external_variable('Psun_hitting_window', solar_gains_with_mask)

    # build invariant variables
    detected_motions: list[int] = [int(d > 1) for d in dp.series('detected_motions')]
    power_stephane: list[float] = dp.series('power_stephane')
    power_khadija: list[float] = dp.series('power_khadija')
    power_audrey: list[float] = dp.series('power_audrey')
    power_stagiaire: list[float] = dp.series('power_stagiaire')

    occupancy: list[int] = [max(detected_motions[k], int(power_stephane[k] > 17) + int(power_khadija[k] > 17) + int(power_stagiaire[k] > 17) + int(power_audrey[k] > 17)) for k in range(len(dp))]
    presence: list[int] = [int(occupancy[k] > 0) for k in range(len(dp))]
    dp.add_external_variable('occupancy', occupancy)
    dp.add_external_variable('presence', presence)

    dp.add_parameterized('office:Pmetabolism', lambda k: dp('body_metabolism') * dp('occupancy', k), default=0, resolution=10)
    
    dp.add_parameterized('office:Pwindow', lambda k: dp('office-outdoor:solar_factor') * dp('Psun_hitting_window', k), default=0, resolution=10)

    if control:
        dp.add_parameterized('office:Pheat', lambda k: dp('total_electric_power', k) + dp('occupancy', k) * dp('body_metabolism') + dp('office-outdoor:solar_factor') * dp('Psun_hitting_window', k) + dp('office:permanent_power'), default=0, resolution=10)
        dp.add_parameterized('office:Pheater', lambda k: dp('office:heater_power_per_delta_surface_temperature') * dp('dT_heat', k), default=0, resolution=10)
    else:
        dp.add_parameterized('office:Pheat', lambda k: dp('office:heater_power_per_delta_surface_temperature') * dp('dT_heat', k) + dp('total_electric_power', k) + dp('occupancy', k) * dp('body_metabolism') + dp('office-outdoor:solar_factor') * dp('Psun_hitting_window', k) + dp('office:permanent_power'), default=0, resolution=10)

    dp.add_parameterized('office:Pheat_gain', lambda k: dp('total_electric_power', k) + dp('occupancy', k) * dp('body_metabolism') + dp('office-outdoor:solar_factor') * dp('Psun_hitting_window', k) + dp('office:permanent_power'), default=0, resolution=10)
    dp.add_parameterized('office:PCO2', lambda k: dp('body_PCO2') * dp('occupancy', k), default=0, resolution=100)
    dp.add_parameterized('office-outdoor:Q', lambda k: dp('office-outdoor:Q_0') + dp('office-outdoor:Q_window') * dp('window_opening', k) + dp('office-corridor:Q_door') * dp('door_opening', k), default=0, resolution=15/3600)
    dp.add_parameterized('office-corridor:Q', lambda k: dp('office-corridor:Q_0') + dp('office-corridor:Q_window') * dp('window_opening', k) + dp('office-corridor:Q_door') * dp('door_opening', k), default=0, resolution=15/3600)
    return dp


if __name__ == '__main__':
    # print(h358_data_provider('datetime', all=True))
    dp_full: DataProvider = make_data_provider()
    print('full:', dp_full)
    dp: DataProvider = dp_full.excerpt(starting_stringdate='1/03/2015', ending_stringdate='20/03/2015')
    # print(dp('office-corridor:Q_door', 3))
    # dp('office-corridor:Q_door', value=18, k=3)
    # print(dp('office-corridor:Q_door', k=3))
    # print(dp('TZcorridor', 3))
    # print(dp('Tcorridor'))
    # # print(dp('corridor:Temperature', k=None))
    # print(dp('office:Pmetabolism', 3))
    # print(dp('office:Pmetabolism'))
    # print(dp('office-corridor:Q', 30))
    # print(dp('corridor-office:Q', 30))
    # print()

    # for k in range(len(dp)):
    #     print(dp.fingerprint(k), dp('door_opening', k), dp('window_opening', k))

    print('excerpt:', dp.fingerprint(None))
    dp_full.plot()
