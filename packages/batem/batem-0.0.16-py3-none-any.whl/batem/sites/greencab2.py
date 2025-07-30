import numpy
import time
from core.data import DataProvider, Bindings
from batem.core.siggen import SignalBuilder, Merger
from core.solar import SolarModel, SolarSystem, Collector
from core.model import BuildingStateModelMaker
from core.components import SideFactory
from core.control import ZoneTemperatureSetpointPort, TemperatureController, ControlModel, AirflowPort, ZoneHvacContinuousPowerPort, ControlledZoneManager
from batem.core.siggen import SignalBuilder, Merger
from core.inhabitants import Preference
from core.library import SIDE_TYPES, DIRECTIONS_SREF, SLOPES


solar_protection = 90  # Notice that 90°C ->no protection
solar_factor = 0.56
body_metabolism = 100
occupant_consumption = 200
insulation_thickness = 150e-3

# Consequences
surface_window: float = 2.2*0.9
container_height = 2.29
container_width = 2.44
container_length = 6
toilet_length = 1.18

container_floor_surface: float = container_length*container_width
cabinet_volume: float = container_floor_surface*container_height
toilet_surface: float = toilet_length*container_width
toilet_volume: float = toilet_surface*container_height
cabinet_surface_wall: float = (2 * container_length + container_width) * container_height - surface_window
exposure_window = DIRECTIONS_SREF.NORTH.value
slope_window = SLOPES.VERTICAL.value
q_infiltration: float = cabinet_volume/3600
q_ventilation: float = 6 * cabinet_volume/3600
q_freecooling: float = 15 * cabinet_volume/3600
body_PCO2 = 7


def make_data_and_signals(starting_stringdate="1/1/2022", ending_stringdate="5/1/2023") -> DataProvider:
    bindings = Bindings()
    bindings('TZoutdoor', 'weather_temperature')
    
    dp = DataProvider(location='Saint-Julien-en-Saint-Alban', latitude_deg_north=44.71407488275519, longitude_deg_east=4.633318302898348, starting_stringdate=starting_stringdate, ending_stringdate=ending_stringdate, bindings=bindings, albedo=0.1, pollution=0.1, number_of_levels=4)

    solar_model = SolarModel(dp.weather_data)
    dp.solar_model = solar_model
    solar_system = SolarSystem(solar_model)
    Collector(solar_system, 'main', surface_m2=surface_window, exposure_deg=exposure_window, slope_deg=slope_window, solar_factor=solar_factor)
    solar_gains_with_mask: list[float] = solar_system.solar_gains_W()
    dp.add_external_variable('Psun_window', solar_gains_with_mask)

    occupancy_signal_generator = SignalBuilder(dp.series('datetime'))
    occupancy_signal_generator.build_daily([0, 1, 2, 3, 4], {0: 0, 8: 3, 18: 0})  # 12: 0, 13: 3,
    occupancy: list[float] = occupancy_signal_generator()
    dp.add_external_variable('occupancy', occupancy)
    presence: list[int] = [int(occupancy[k] > 0) for k in range(len(dp))]
    dp.add_external_variable('presence', presence)

    dp.add_external_variable('PZcabinet', [occupancy[k] * (body_metabolism + occupant_consumption) + solar_gains_with_mask[k] for k in dp.ks])
    dp.add_parameter('PZtoilet', 0)

    # Data heating and cooling
    temperature_signal_generator = SignalBuilder(dp.series('datetime'), None)
    temperature_signal_generator.build_daily([0, 1, 2, 3, 4], {0: None, 7: 20, 19: None}, merger=Merger(min, 'r'))
    heating_period: list[int] = temperature_signal_generator.build_seasonal('16/11', '15/3', 1, merger=Merger(max, 'b'))
    summer_temperature_signal_generator = SignalBuilder(dp.series('datetime'), None)
    summer_temperature_signal_generator.build_daily([0, 1, 2, 3, 4], {0: None, 7: 22, 19: None}, merger=Merger(min, 'r'))
    cooling_period: list[int] = summer_temperature_signal_generator.build_seasonal('16/3', '15/11', 1, merger=Merger(max, 'b'))
    temperature_signal_generator.merge(summer_temperature_signal_generator(), merger=Merger(min, 'n'))
    dp.add_external_variable('TZcabinet_setpoint', temperature_signal_generator())

    hvac_modes_signal_generator = SignalBuilder(dp.series('datetime'))
    hvac_modes_signal_generator.merge(heating_period, merger=Merger(max, 'l'))
    hvac_modes_signal_generator.merge(cooling_period, merger=Merger(lambda x, y: x - y, 'n'))
    dp.add_external_variable('mode', hvac_modes_signal_generator())
    # dp.plot()

    dp.add_parameter('CCO2outdoor', 400)
    dp.add_parameter('cabinet:volume', cabinet_volume)
    dp.add_parameter('toilet:volume', toilet_volume)
    dp.add_external_variable('PCO2cabinet', [body_PCO2 * occupancy[k] for k in range(len(dp))])
    dp.add_parameter('PCO2toilet', 0)
    
    ventilation_signal_generator = SignalBuilder(dp.series('datetime'))
    ventilation_signal_generator.build_daily([0, 1, 2, 3, 4], {0: 0, 7: 1, 18: 0})
    ventilation: list[float] = ventilation_signal_generator()

    dp.add_external_variable('ventilation', ventilation)
    dp.add_external_variable('cabinet-outdoor:Q', [q_infiltration + ventilation[k]*q_ventilation for k in range(len(dp))])
    dp.add_external_variable('toilet-outdoor:Q', [q_infiltration + ventilation[k]*q_ventilation for k in range(len(dp))])

    return dp


def make_state_model_maker(dp: DataProvider) -> BuildingStateModelMaker:
    state_model_maker = BuildingStateModelMaker('cabinet', 'toilet', data_provider=dp, periodic_depth_seconds=3600, state_model_order_max=5)

    wall = SideFactory(('wood', 3e-3), ('polystyrene', insulation_thickness), ('steel', 5e-3), ('wood', 3e-3))
    floor = SideFactory(('wood', 10e-3), ('polystyrene', insulation_thickness), ('steel', 5e-3))
    ceiling = SideFactory(('wood', 3e-3), ('polystyrene', insulation_thickness), ('steel', 5e-3))
    glazing = SideFactory(('glass', 4e-3), ('air', 10e-3), ('glass', 4e-3), ('air', 10e-3), ('glass', 4e-3))
    internal = SideFactory(('wood', 9e-3), ('air', 20e-3), ('wood', 9e-3))

    # Cabinet
    state_model_maker.make_side(wall('cabinet', 'outdoor', SIDE_TYPES.WALL, cabinet_surface_wall))
    state_model_maker.make_side(floor('cabinet', 'outdoor', SIDE_TYPES.FLOOR, container_floor_surface))
    state_model_maker.make_side(ceiling('cabinet', 'outdoor', SIDE_TYPES.CEILING, container_floor_surface))
    state_model_maker.make_side(glazing('cabinet', 'outdoor', SIDE_TYPES.GLAZING, surface_window))

    # Toilet
    state_model_maker.make_side(internal('cabinet', 'toilet', SIDE_TYPES.WALL, container_width * container_height))
    state_model_maker.make_side(wall('toilet', 'outdoor', SIDE_TYPES.WALL, (toilet_length * 2 + container_width) * container_height))
    state_model_maker.make_side(floor('toilet', 'outdoor', SIDE_TYPES.FLOOR, container_width * toilet_length))
    state_model_maker.make_side(ceiling('toilet', 'outdoor', SIDE_TYPES.CEILING, container_width * toilet_length))

    state_model_maker.simulate_zone('cabinet', 'toilet')
    state_model_maker.connect_airflow('cabinet', 'outdoor', dp('cabinet-outdoor:Q'))  # nominal value
    state_model_maker.connect_airflow('toilet', 'outdoor', dp('toilet-outdoor:Q'))  # nominal value
    print(state_model_maker)
    
    return state_model_maker, state_model_maker.make_k()


class DirectManager(ControlledZoneManager):

    def __init__(self, dp: DataProvider, building_state_model_maker: BuildingStateModelMaker) -> None:
        super().__init__(dp, building_state_model_maker)

    def make_ports(self) -> None:
        
        self.cabinet_airflow_control_port = AirflowPort(self.dp, 'cabinet-outdoor:Q', 'ventilation', 'presence', q_infiltration, q_ventilation, q_freecooling)
        
        self.toilet_airflow_control_port = AirflowPort(self.dp, 'toilet-outdoor:Q', 'ventilation', 'presence', q_infiltration, q_ventilation, q_freecooling)

        self.temperature_setpoint_port = ZoneTemperatureSetpointPort(self.dp, 'TZcabinet_setpoint', mode_name='mode', mode_value_domains={1: (13, 19, 20, 21, 22, 23), 0: None, -1: (24, 25, 26, 28, 29, 32)})

        self.mode_power_control_port = ZoneHvacContinuousPowerPort(self.dp, 'Pheater', max_heating_power=3000, max_cooling_power=3000, hvac_mode='mode', full_range=False)

    def zone_temperature_controllers(self) -> dict[TemperatureController, float]:
        return {self.make_zone_temperature_controller('TZcabinet', self.temperature_setpoint_port, 'PZcabinet', self.mode_power_control_port): 20}

    def controls(self, k: int, X_k: numpy.matrix, current_output_dict: dict[str, float]) -> None:
        pass
        # Tin: float = current_output_dict['TZcabinet']
        # Tout: float = self.dp('weather_temperature', k)
        # if self.dp('presence', k) == 1:
        #     if 20 <= Tout <= 23 or self.dp('CCO2cabinet', k) > 3000:
        #         self.cabinet_airflow_control_port(k, q_freecooling)
        #     elif Tin > 23 and Tout < 20:
        #         self.cabinet_airflow_control_port(k, q_freecooling)


def make_simulation(dp: DataProvider, building_state_model_maker: BuildingStateModelMaker) -> None:

    manager = DirectManager(dp, building_state_model_maker)
    preference = Preference(preferred_temperatures=(19, 24), extreme_temperatures=(16, 29), preferred_CO2_concentration=(500, 1500), temperature_weight_wrt_CO2=0.5, power_weight_wrt_comfort=0.5, mode_cop={1: 2, -1: 2})

    control_model = ControlModel(building_state_model_maker, manager)
    print(control_model)
    start: float = time.time()
    control_model.simulate()
    print('\nmodel simulation duration: %f secondes' % (time.time() - start))

    Pheater: list[float] = dp.series('Pheater')
    occupancy = dp.series('occupancy')
    preference.print_assessment(dp.series('datetime'), Pheater=Pheater, temperatures=dp.series('TZcabinet'), CO2_concentrations=dp.series('CCO2cabinet'), occupancies=dp.series('occupancy'), action_sets=(), modes=dp.series('mode'), list_extreme_hours=True)
    electricity_needs = [abs(Pheater[k])/2 + occupancy[k] * occupant_consumption for k in dp.ks]
    dp.add_external_variable('electricity needs', electricity_needs)

    exposure_in_deg = 0
    slope_in_deg = 180
    solar_factor = .2
    surface = 7
    solar_system = SolarSystem(dp.solar_model)
    Collector(solar_system, 'PVpanel', surface_m2=surface, exposure_deg=exposure_in_deg, slope_deg=slope_in_deg, solar_factor=solar_factor)
    global_productions_in_Wh = solar_system.solar_gains_W()
    print('PV production in kWh:', round(sum(global_productions_in_Wh) / 1000))
    dp.add_external_variable('productionPV', global_productions_in_Wh)
    dp.plot()

