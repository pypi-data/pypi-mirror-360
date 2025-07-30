from batem.core.data import DataProvider
from batem.core.control import ContinuousModePort, DiscreteModePort, OpeningPort, Simulation, TemperatureController, CONTROL_TYPE
from batem.core.inhabitants import Preference
from batem.sites.building_h358 import make_building_state_model_k
from batem.sites.data_h358 import make_data_provider


# #### INITIALIZATION OF THE SIMULATION TYPE ####

# simulation_type = CONTROL_TYPE.NO_CONTROL  # simple simulation without control
# simulation_type = CONTROL_TYPE.POWER_CONTROL  # simulation with power control
simulation_type = CONTROL_TYPE.TEMPERATURE_CONTROL  # simulation with temperature control

with_air_conditioning = True

# In the 3 next functions allowing to introduce control rules, the system object provides different services:
# - system.dp(variable_name, k) to get the value of the variable at the specified hour
# - system.control_ports(port_name)(k, value) to force a specific value to a control port
#                                                (to be used in action_rule to be sure to get an effect)
# - system.hour(k) to get the hour of the day
# - system.weekday(k) to get the weekday of the day
# - system.day_number(k) to get the number of the day from the beginning of the simulation


def action_rule(system, k: int) -> None:
    """function used to force a control action (opening window,...)

    :param system: the system to control, which provide the above services
    :type system: Simulation
    :param k: the number of simulated hours from the beginning of the simulation
    :type k: int
    :param heater_power: the data-based power of the heater
    :type heater_power: float
    :return: the modified power of the heater
    :rtype: float
    """
    # system.control_ports('window_opening')(k, 1)
    pass


def control_rule(system, k: int, zone_heater_power: float) -> float:
    """function used to force power of a zone HVAC system.

    :param system: the system to control, which provide the above services
    :type system: Simulation
    :param k: the number of simulated hours from the beginning of the simulation
    :type k: int
    :param heater_power: the data-based power of the heater
    :type heater_power: float
    :return: the modified power of the heater
    :rtype: float
    """
    # if 8 <= system.hour(k) <= 12:
    #     heater_power = 0
    return zone_heater_power


def setpoint_rule(system, k: int, setpoint: float) -> float:
    """function used to force the temperature setpoint for a zoneHVAC system.

    :param system: the system to control, which provide the above services
    :type system: Simulation
    :param k: the number of simulated hours from the beginning of the simulation
    :type k: int
    :param heater_power: the data-based power of the heater
    :type heater_power: float
    :return: the modified power of the heater
    :rtype: float
    """
    # if 15 <= system.hour(k) <= 19:
    #     setpoint = 24
    return setpoint


# #### INITIALIZATION OF THE DATA PROVIDER AND THE SIMULATION DURATION ####
starting_stringdate, ending_stringdate = '15/02/2015', '15/02/2016'
dp: DataProvider = make_data_provider(starting_stringdate, ending_stringdate, not (simulation_type == CONTROL_TYPE.TEMPERATURE_CONTROL))

# ### GENERATION OF THE SETPOINT AND MODE SIGNALS ####

if not with_air_conditioning:
    print('heating only')
    mode_setpoint_siggen = HeaterModeSetpointSignalGenerator(dp.datetimes, ('15/10', '15/4'), [WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: None, 6: 21, 18: None}, 'mode')
    modes: list[float] = mode_setpoint_siggen.get_modes()
    setpoints = mode_setpoint_siggen.get_setpoints()
else:
    print('heating and cooling')
    mode_setpoint_siggen = ModeSetpointSignalGenerator(dp.datetimes, heating_period=('15/10', '15/4'), cooling_period=('15/6', '15/9'))
    mode_setpoint_siggen.add_daily_setpoints(mode_setpoint_siggen.modes, 1, [WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: None, 6: 21, 18: None})
    mode_setpoint_siggen.add_daily_setpoints(mode_setpoint_siggen.modes, -1, [WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: None, 6: 24, 18: None})
    modes = mode_setpoint_siggen.get_modes()
    setpoints = mode_setpoint_siggen.get_setpoints()

dp.add_external_variable('TZoffice_setpoint', setpoints)  # add the temperature setpoint signal to the data provider
dp.add_external_variable('mode', modes)  # add the HVAC modes signal to the data provider

# ### INITIALIZATION OF THE CONTROL PORTS ####
window_opening_port = OpeningPort(data_provider=dp, feeding_variable_name='window_opening', presence_variable='presence')
door_opening_port = OpeningPort(data_provider=dp, feeding_variable_name='door_opening', presence_variable='presence')

# #### INITIALIZATION OF THE SIMULATION TYPE-DEPENDENT CONTROL PORTS, AND BUILDING STATE MODEL ####
building_state_model_maker, state_model_nominal = make_building_state_model_k(dp)
if simulation_type == CONTROL_TYPE.NO_CONTROL:
    simulation = Simulation(dp, building_state_model_maker, control_ports=[])
    simulation.add_zone(zone_name='office', heat_gain_name='office:Pheat', CO2production_name='office:PCO2')
    simulation.control = Simulation.HeuristicRule(dp, simulation, None)
else:
    heater_port = ContinuousModePort(dp, 'PZoffice', 'office:Pheater', {0: 0, 1: (0, 2000), -1: (0, -2000)}, 'mode')

    if simulation_type == CONTROL_TYPE.POWER_CONTROL:
        simulation = Simulation(dp, building_state_model_maker, control_ports=[window_opening_port, door_opening_port, heater_port])
        simulation.add_zone(zone_name='office', heat_gain_name='office:Pheat_gain', CO2production_name='office:PCO2', hvac_power_port=heater_port)

    elif simulation_type == CONTROL_TYPE.TEMPERATURE_CONTROL:
        temperature_setpoint_port = DiscreteModePort(dp, 'TZoffice', 'TZoffice_setpoint', {1: (13, 19, 20, 21, 22, 23), 0: None, -1: (24, 25, 26, 28, 29, 32)}, 'mode')
        temperature_controller = TemperatureController(hvac_heat_port=heater_port, temperature_setpoint_port=temperature_setpoint_port, state_model_nominal=state_model_nominal)

        simulation = Simulation(dp, building_state_model_maker, control_ports=[window_opening_port, door_opening_port, heater_port])
        simulation.add_zone(zone_name='office', heat_gain_name='office:Pheat_gain', CO2production_name='office:PCO2', hvac_power_port=heater_port, temperature_controller=temperature_controller)

# #### RUN THE SIMULATION ####
dp.plot('mode', 'TZoffice_setpoint')
simulation.run(suffix='_sim', control_rule=control_rule, setpoint_rule=setpoint_rule, action_rule=action_rule)

# #### PRINT THE SIMULATION RESULTS ####
preference = Preference(preferred_temperatures=(19, 24), extreme_temperatures=(16, 29), preferred_CO2_concentration=(500, 1500), temperature_weight_wrt_CO2=0.5, power_weight_wrt_comfort=0.5, mode_cop={1: 2, -1: 2})

print(simulation)
print(simulation.control_ports)
preference.print_assessment(dp.datetimes, dp.series('office:Pheater'), dp.series('TZoffice_sim'), dp.series('CCO2office_sim'), dp.series('occupancy'), action_sets=(dp.series('window_opening'), dp.series('door_opening')), modes=dp.series('mode'))

if simulation_type != CONTROL_TYPE.NO_CONTROL:
    Pheaters: list[float] = dp.series('office:Pheater')
    Heats: list[float] = dp.series('office:Pheat_gain')
    print('ratio heater power / total heating power: ', round(100 * sum([Pheaters[k] * (modes[k] == 1) for k in range(len(dp))]) / sum([Heats[k] * (modes[k] == 1) for k in range(len(dp))]), 2), '%')

dp.plot('Toffice_reference', 'office:Pheat_gain', 'office:Pheater', 'office:Pheat', 'mode', 'PZoffice', 'TZoffice_sim', 'PZoffice', 'TZoffice_setpoint', 'window_opening', 'door_opening')
# dp.plot()
