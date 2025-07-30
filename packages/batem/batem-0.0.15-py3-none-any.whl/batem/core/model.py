"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0

A helper module dedicated to the design of time-varying state space model approximated by bilinear state space model.

Author: stephane.ploix@grenoble-inp.fr
"""
from __future__ import annotations
import numpy
import networkx
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from .components import SideFactory, Zone, Airflow, LayeredWallSide
from .thermal import ThermalNetworkMaker
from .thermal import ThermalNetwork
from .statemodel import StateModel
from .data import DataProvider
from .library import ZONE_TYPES, properties
import numpy.linalg
import time
import prettytable
import SALib.sample.morris
import SALib.analyze.morris
import plotly.express
from random import randint
from .data import ParameterSet
import configparser


class BuildingStateModelMaker(ThermalNetworkMaker):
    """
    This class complements the class _Building: it contains the API dedicated to the processing into a state model.
    """
    def __init__(self, *zone_names: str, data_provider: DataProvider, periodic_depth_seconds: float = 60*60, state_model_order_max: int = None):
        """
        Initialize a building and help to create it. It generates as state model afterwards thanks to the method 'make_state_model()', that must be called anytime an adjustment multiplicative factor is modified

        :param zone_names: names of the zones except for 'outdoor', which is automatically created
        :type zone_names: tuple[str]
        :param periodic_depth_seconds: the target periodic depth penetration is a wave length, which is defining the decomposition in sublayers, each sublayer is decomposed such that its thickness is attenuating a temperature of this wave length: the smallest, the more precise but also the more computation time.
        :type periodic_depth_seconds:
        :param state_model_order_max: set a maximum order for the final state model. If the value is set to None, there won't be order reduction, default to None
        :type state_model_order_max: int, optional
        :param sample_time_in_secs: sample time for future version (only the default 3600s has been tested), default is 3600s, don't change it
        :type sample_time_in_secs: int, optional
        """
        super().__init__(*zone_names, periodic_depth_seconds=periodic_depth_seconds, data_provider=data_provider)
        self.dp: DataProvider = data_provider
        self.__data_names_in_fingerprint = list()
        self.data_names_in_fingerprint: list[str] = data_provider.parameter_set.adjustable_parameter_names
        self.airflow_network: networkx.Graph = networkx.Graph()
        for zone_name in self.name_zones:
            self.airflow_network.add_node(zone_name)
        self.V_nominal_reduction_matrix: numpy.matrix = None
        self.W_nominal_reduction_matrix: numpy.matrix = None
        self.nominal_fingerprint: int = None
        self.airflows: list[Airflow] = list()
        self.airflow_names: list[str] = list()
        self.CO2_connected_zones = list()
        self.state_model_order_max: int = state_model_order_max

    @property
    def data_names_in_fingerprint(self) -> list[str]:
        return self.__data_names_in_fingerprint

    @data_names_in_fingerprint.setter
    def data_names_in_fingerprint(self, data_names: list[str]) -> None:
        if type(data_names) is str:
            data_names = [data_names]
        for data_name in data_names:
            if data_name not in self.data_names_in_fingerprint:
                self.__data_names_in_fingerprint.append(data_name)
            if data_name not in self.dp.data_names_in_fingerprint:
                self.dp.data_names_in_fingerprint.append(data_name)

    def make_side(self, side_factory: SideFactory) -> None:
        side: LayeredWallSide = self.layered_wall_side(side_factory.zone1_name, side_factory.zone2_name, side_factory.side_type, side_factory.surface)
        for layer in side_factory.layers:
            side.layer(*layer)

    def connect_airflow(self, zone1_name: str, zone2_name: str, nominal_value: float):
        """
        create an airflow exchange between 2 zones

        :param zone1_name: zone name of the origin of the air flow
        :type zone1_name: str
        :param zone2_name: zone name of the destination of the air flow
        :type zone2_name: str
        :param nominal_value: nominal value for air exchange, used if not overloaded
        :type nominal_value: float
        """
        if zone1_name > zone2_name:
            zone1_name, zone2_name = zone2_name, zone1_name
        self.airflow_network.add_edge(zone1_name, zone2_name)
        airflow = Airflow(self.name_zones[zone1_name], self.name_zones[zone2_name], nominal_value)
        self.airflows.append(airflow)
        self.airflow_names.append(airflow.name)
        if self.name_zones[zone1_name].simulated or self.name_zones[zone2_name].simulated:
            dependent_data = self.data_provider.variable_accessor_registry.required_data(airflow.name)
            for data in dependent_data:
                self.data_names_in_fingerprint = data.name

        if self.name_zones[zone1_name] not in self.CO2_connected_zones:
            self.CO2_connected_zones.append(self.name_zones[zone1_name])
        if self.name_zones[zone2_name] not in self.CO2_connected_zones:
            self.CO2_connected_zones.append(self.name_zones[zone2_name])
    
    def make_nominal(self, reset_reduction: bool = False, fingerprint: int = 0) -> StateModel:
        return self.make_k(k=None, reset_reduction=reset_reduction, fingerprint=fingerprint)

    def make_k(self, k: int | None = None, reset_reduction: bool = False, fingerprint: int = 0) -> StateModel:  # current_airflow_values: dict[str, float] = dict(),
        nominal: bool = k is None
        if self.state_model_order_max is not None:
            if reset_reduction:
                self.V_nominal_reduction_matrix = None
                self.W_nominal_reduction_matrix = None
            if nominal:
                self.global_state_model = self.make_no_reduction_k(k=None, fingerprint=fingerprint)
                self.V_nominal_reduction_matrix, self.W_nominal_reduction_matrix = self.global_state_model.reduce(self.state_model_order_max, self.V_nominal_reduction_matrix, self.W_nominal_reduction_matrix)
                return self.global_state_model

        if self.state_model_order_max is not None and self.V_nominal_reduction_matrix is None:
            self.global_state_model = self.make_no_reduction_k(k)
            self.V_nominal_reduction_matrix, self.W_nominal_reduction_matrix = self.global_state_model.reduce(self.state_model_order_max, self.V_nominal_reduction_matrix, self.W_nominal_reduction_matrix)
        self.global_state_model = self.make_no_reduction_k(k, fingerprint=fingerprint)
        if self.state_model_order_max is not None:
            self.V_nominal_reduction_matrix, self.W_nominal_reduction_matrix = self.global_state_model.reduce(self.state_model_order_max, self.V_nominal_reduction_matrix, self.W_nominal_reduction_matrix)
        return self.global_state_model

    def make_no_reduction_k(self, k: int, fingerprint: int = None) -> StateModel:  # nominal: bool = False,
        nominal = k is None

        self.thermal_network: ThermalNetwork = self.make_thermal_network_k()
        air_properties: dict[str, float] = properties.get('air')
        rhoCp_air: float = air_properties['density'] * air_properties['Cp']
        for airflow in self.airflows:
            zone1, zone2 = airflow.connected_zones
            if not nominal:
                self.thermal_network.R(fromT=zone1.air_temperature_name, toT=zone2.air_temperature_name, name='Rv%s_%s' % (zone1.name, zone2.name), val=1/(rhoCp_air*self.data_provider(airflow.name, k)) if airflow.name in self.data_provider else airflow.nominal_value)
            else:
                self.thermal_network.R(fromT=zone1.air_temperature_name, toT=zone2.air_temperature_name, name='Rv%s_%s' % (zone1.name, zone2.name), val=rhoCp_air * airflow.nominal_value)

        full_order_state_model = self.thermal_network.state_model()
        CO2state_matrices = self.make_CO2_k(k)
        A_CO2 = CO2state_matrices['A']
        B_CO2 = numpy.hstack((CO2state_matrices['B_CO2'], CO2state_matrices['B_prod']))
        C_CO2 = CO2state_matrices['C']
        D_CO2 = numpy.hstack((CO2state_matrices['D_CO2'], CO2state_matrices['D_prod']))
        input_names = CO2state_matrices['U_CO2']
        input_names.extend(CO2state_matrices['U_prod'])
        output_names = CO2state_matrices['Y']
        full_order_state_model.extend('CO2', (A_CO2, B_CO2, C_CO2, D_CO2), input_names, output_names)
        full_order_state_model.fingerprint = fingerprint
        return full_order_state_model

    def make_CO2_k(self, k: int = 0, nominal: bool = False) -> dict:  # airflow_values: dict[str, float]
        """
        Generate the state model representing the CO2 evolution

        :param airflow_values: connecting airflows values as a dictionary with the airflow names as keys and the values as airflow values
        :type airflow_values: dict[str, float]
        :param zone_Vfactors: multiplicative adjustment factors for the zone air volumes as a dictionary with zone names as keys and corrective factor as value, default to empty dictionary
        :type zone_Vfactors: dict[str, float], optional
        :return: State space model for the CO2
        :rtype: STATE_MODEL
        """
        simulated_zones = list()
        input_zones = list()
        state_variable_names: list[str] = list()
        input_variable_names: list[str] = list()
        production_names: list[str] = list()
        if k is None:
            k = 0

        for zone_name in self.name_zones:
            zone: Zone = self.name_zones[zone_name]
            if zone.simulated:
                simulated_zones.append(zone)
                state_variable_names.append(zone.CO2_concentration_name)
                production_names.append(zone.CO2_production_name)
            elif len(zone.connected_zones) > 0:
                input_zones.append(zone)
                input_variable_names.append(zone.CO2_concentration_name)

        A_CO2 = numpy.zeros((len(state_variable_names), len(state_variable_names)))
        B_CO2 = numpy.zeros((len(state_variable_names), len(input_variable_names)))
        B_prod = numpy.zeros((len(state_variable_names), len(production_names)))
        C_CO2 = numpy.eye(len(state_variable_names))
        D_CO2 = numpy.zeros((len(state_variable_names), len(input_variable_names)))
        D_prod = numpy.zeros((len(state_variable_names), len(production_names)))

        for i, zone in enumerate(simulated_zones):
            A_CO2[i, i] = 0
            for connecting_airflow in zone.connected_airflows:
                if not nominal and connecting_airflow.name in self.data_provider:
                    A_CO2[i, i] += -self.data_provider(connecting_airflow.name, k) / zone.volume
                else:
                    A_CO2[i, i] += -connecting_airflow.nominal_value / zone.volume
            B_prod[i, 0] = 1/zone.volume
            for connected_zone in zone.connected_zones:
                if connected_zone.simulated:
                    connecting_airflow = zone._airflow(connected_zone)
                    j: int = state_variable_names.index(connected_zone.CO2_concentration_name)
                    if not nominal and connecting_airflow.name in self.data_provider:
                        A_CO2[i, j] = self.data_provider(connecting_airflow.name, k) / zone.volume
                    else:
                        A_CO2[i, j] = connecting_airflow.nominal_value / zone.volume
                else:
                    connecting_airflow = zone._airflow(connected_zone)
                    j = input_variable_names.index(connected_zone.CO2_concentration_name)
                    if not nominal and connecting_airflow.name in self.data_provider:
                        B_CO2[i, j] = self.data_provider(connecting_airflow.name, k) / zone.volume
                    else:
                        B_CO2[i, j] = connecting_airflow.nominal_value / zone.volume

        self.CO2_state_model = StateModel((A_CO2, B_CO2, C_CO2, D_CO2), input_variable_names, state_variable_names, self.sample_time_seconds)
        return {'A': A_CO2, 'B_CO2': B_CO2, 'B_prod': B_prod, 'C': C_CO2, 'D_CO2': D_CO2, 'D_prod': D_prod, 'Y': state_variable_names, 'X': state_variable_names, 'U_CO2': input_variable_names, 'U_prod': production_names, 'type': 'differential'}

    def plot_thermal_net(self):
        """
        draw digraph of the thermal network (use matplotlib.show() to display)
        """
        self.thermal_network.draw()

    def plot_airflow_net(self):
        """
        draw digraph of the airflow network (use matplotlib.show() to display)
        """

        pos = networkx.shell_layout(self.airflow_network)
        node_colors = list()
        for zone_name in self.zones:
            if self.zones[zone_name].is_known:
                node_colors.append('blue')
            elif self.zones[zone_name].simulated:
                node_colors.append('pink')
            else:
                node_colors.append('yellow')
        labels = dict()
        for node in self.airflow_network.nodes:
            label = '\n' + str(self.zones[node]._propagated_airflow)
            labels[node] = label
        plt.figure()
        networkx.draw(self.airflow_network, pos, with_labels=True, edge_color='black', width=1, linewidths=1, node_size=500, font_size='medium', node_color=node_colors, alpha=1)
        networkx.drawing.draw_networkx_labels(self, pos,  font_size='x-small', verticalalignment='top', labels=labels)

    def __str__(self) -> str:
        """
        :return: string depicting the site
        :rtype: str
        """
        string = str(super().__str__())
        string += 'Connected zones:\n'
        for airflow in self.airflows:
            string += '* %s with a nominal value of %.2fm3/h\n' % (str(airflow), 3600 * airflow.nominal_value)
        return string

    def get_twin(self, periodic_depth_seconds: float = None, state_model_order_max: int = None) -> BuildingStateModelMaker:
        if periodic_depth_seconds is None:
            periodic_depth_seconds = self.periodic_depth_seconds
        if state_model_order_max is None:
            self.state_model_order_max = self.state_model_order_max
        twin = BuildingStateModelMaker(*self.zone_names, periodic_depth_seconds=periodic_depth_seconds, state_model_order_max=state_model_order_max, data_provider=self.data_provider)

        twin.layered_wall_sides = self.layered_wall_sides
        twin.block_wall_sides = self.block_wall_sides

        for airflow in self.airflows:
            twin.connect_airflow(airflow.connected_zones[0].name, airflow.connected_zones[1].name, airflow.nominal_value)
        simulated_zone_names: list[str] = list()
        for zone_name in self.name_zones:
            if self.name_zones[zone_name].zone_type == ZONE_TYPES.SIMULATED:
                simulated_zone_names.append(zone_name)
        twin.simulate_zone(*simulated_zone_names)
        return twin


class BuildingStateModel:
    """
    This class gets the state space equation generated from the RC graph model and physics by modules buildings and physics and prepare it for use: generating and discrete time (1 hour) recurrent non-linear state model, identifying and organizing variables by type: inputs or outputs, but also by kind: temperature, heat gain, CO2 concentration, CO2 production for each zone, depending on the information provided by the designer as for example whether a zone has been declared simulated of not.
    """
    def __init__(self, building_state_model_maker: BuildingStateModelMaker) -> None:
        self.building_state_model_maker: BuildingStateModelMaker = building_state_model_maker
        self.dp: DataProvider = building_state_model_maker.data_provider
        if len(self.building_state_model_maker.airflows) > 0:
            self.dp.add_data_names_in_fingerprint(*[airflow.name for airflow in building_state_model_maker.airflows])
        self.nominal_fingerprint = self.dp.fingerprint(0)  # None
        self.nominal_state_model = building_state_model_maker.make_k(k=0, reset_reduction=True, fingerprint=self.nominal_fingerprint)
        self.input_names: list[str] = self.nominal_state_model.input_names
        self.output_names: list[str] = self.nominal_state_model.output_names
        self.state_models_cache: dict[int, StateModel] = {self.nominal_fingerprint: self.nominal_state_model}

    def clear_cache(self):
        self.state_models_cache: dict[int, StateModel] = {self.nominal_fingerprint: self.nominal_state_model}

    def cache_state_models(self):
        print()
        delayed_calls = list()
        for k in range(len(self.dp)):
            fingerprint: list[int] = self.dp.fingerprint(k)
            if fingerprint not in self.state_models_cache:
                delayed_calls.append(delayed(self.building_state_model_maker.make_k)(k, fingerprint=fingerprint))
                print('*', end='')
                self.state_models_cache[fingerprint] = None
        print()
        results_delayed = Parallel(n_jobs=-1)(delayed_calls)
        for state_model in results_delayed:
            self.state_models_cache[state_model.fingerprint] = state_model
        print("\n%i models in cache" % len(self.state_models_cache))

    def simulate(self, pre_cache: bool = True) -> dict[str, list[float]]:
        if pre_cache:
            self.cache_state_models()
        simulated_outputs: dict[str, list[float]] = dict()
        X = None
        for k in range(len(self.dp)):
            current_input_values: dict[str, float] = {input_name: self.dp(input_name, k) for input_name in self.input_names}
            current_fingerprint = self.dp.fingerprint(k)
            if current_fingerprint in self.state_models_cache:
                state_model_k = self.state_models_cache[current_fingerprint]
                print('.', end='')
            else:
                state_model_k: StateModel = self.building_state_model_maker.make_k(k, reset_reduction=(k == 0))
                print('*', end='')
            if X is None:
                X: numpy.matrix = state_model_k.initialize(**current_input_values)
            if state_model_k is None:
                pass
            state_model_k.set_state(X)
            output_values = state_model_k.output(**current_input_values)
            for i, output_name in enumerate(self.output_names):
                if output_name not in simulated_outputs:
                    simulated_outputs[output_name] = list()
                simulated_outputs[output_name].append(output_values[i])
            X = state_model_k.step(**current_input_values)
        return simulated_outputs

    def __str__(self) -> str:
        string: str = 'Model with following variables:\n'
        string += 'regular inputs: \n-%s resp. bounded on %s\n' % (','.join(self.regular_input_names), ','.join([self.bindings[name] for name in self.regular_input_names]))
        string += 'air flows: \n-%s resp. bounded on %s\n' % (','.join([self.bindings[name] for name in self.airflow_names]), ','.join(self.airflow_names))
        string += 'regular outputs:  \n-%s resp. bounded on %s\n' % (','.join(self.regular_output_names), ','.join([self.bindings[name] for name in self.regular_output_names]))
        return string


def setup(*references):
    _setup = configparser.ConfigParser()
    _setup.read('setup.ini')
    configparser_obj = _setup
    for ref in references:
        configparser_obj = configparser_obj[ref]
    return configparser_obj


class ModelFitter:
    """
    Runner is the main class for simulating a site model: it connects measurement data, parameters and models.
    """

    def __init__(self, building_state_model, verbose: bool = True) -> None:
        """
        Initialize a runner i.e. a runnable simulator with the design of the following objects:
        - a parameter set, containing the names og nonlinear inputs (some airflows) with their bounds, to approximate the state model
        - a (state) model, with identified nonlinear input variables
        - a data set, which contains all the data bounded to yield the state
        :param model_data_bindings: connect a model variable to one or several data. If several data are provided, they are summed up. Instead of data, parameterized data can be provided.
        :type model_data_bindings: tuple[str, str | list[str]])
        """

        self.varying_state_model: BuildingStateModel = building_state_model
        self.dp = building_state_model.dp
        self.parameters: ParameterSet = self.dp.parameter_set
        self.verbose = verbose
        self.output_ranges: dict[str, float] = dict()

        self.adjustable_parameter_level_bounds: dict[str, tuple[int, int]] = self.parameters.adjustable_level_bounds
        self.adjustable_parameter_levels: list[int] = self.parameters.adjustable_parameter_levels

    @property
    def training_data_provider(self):
        return self.dp

    def run(self, pre_cache: bool = True, clear_cache: bool = False) -> dict[str, list[float]]:
        self.parameters.set_adjustable_levels([self.adjustable_parameter_levels[p] for p in self.adjustable_parameter_levels])  # self.parameters.levels(self.parameters.adjustable_parameter_names)
        if clear_cache:
            self.varying_state_model.clear_cache()
        return self.varying_state_model.simulate(pre_cache=pre_cache)

    def error(self, output_values: dict[str, list[float]]) -> float:
        total_error: float = 0
        for output_name in output_values:
            if output_name not in self.output_ranges:
                self.output_ranges[output_name] = max(self.dp.series(output_name)) - min(self.dp.series(output_name))
            # output_data_name = self.training_data_provider.model_data_bindings.data_name(output_model_name)
            # data_bounds: tuple[float, float] = self.dp.parameter_set.adjustable_level_bounds[output_name]
            output_error = sum([abs(output_values[output_name][k] - self.dp(output_name, k)) for k in range(len(self.dp))])
            total_error += output_error / len(self.dp) / self.output_ranges[output_name] / len(output_values)  # / abs(data_bounds[1] - data_bounds[0])
        return total_error

    def fit(self, n_iterations: int) -> tuple[dict[str, list[float]], float]:
        iteration: int = 0
        best_error: float = None
        best_outputs: dict[str, list[float]] = None
        parameters_tabu_list: list[tuple[int]] = list()
        number_of_adjustable_parameters: int = len(self.parameters.adjustable_parameter_names)
        adjustable_parameter_levels: tuple[int] = tuple([self.parameters.adjustable_parameter_levels[pname] for pname in self.parameters.adjustable_parameter_names])
        no_progress_counter: int = 0

        while iteration < n_iterations and no_progress_counter < 2 * number_of_adjustable_parameters:
            if self.verbose:
                print('levels: ' + ','.join([str(level) for level in adjustable_parameter_levels]))
            candidate_outputs: dict[str, list[float]] = self.run(clear_cache=True)
            candidate_error: float = self.error(candidate_outputs)
            if self.verbose:
                print('\n-> candidate error:', candidate_error)
                print('* Iteration %i/%i' % (iteration, n_iterations-1))  # time analysis
            parameters_tabu_list.append(adjustable_parameter_levels)
            if best_error is None or candidate_error < best_error:
                if best_error is None:
                    initial_error: float = candidate_error
                    initial_levels: tuple[int] = adjustable_parameter_levels
                best_parameter_levels: tuple[int] = adjustable_parameter_levels
                best_outputs = candidate_outputs
                best_error = candidate_error
                print('\nBest error is: %f' % (best_error,))
                no_progress_counter = 0
            else:
                no_progress_counter += 1
            candidate_found: bool = False
            counter: int = 0
            new_parameter_levels = None
            while not candidate_found and counter < 2 * number_of_adjustable_parameters:
                new_parameter_levels: list[int] = list(best_parameter_levels)
                parameter_to_change = randint(0, number_of_adjustable_parameters-1)
                change = randint(0, 1) * 2 - 1
                if new_parameter_levels[parameter_to_change] + change < 0 or new_parameter_levels[parameter_to_change] + change > number_of_adjustable_parameters - 1:
                    change = - change
                new_parameter_levels[parameter_to_change] = new_parameter_levels[parameter_to_change] + change
                candidate_found = new_parameter_levels not in parameters_tabu_list
                counter += 1
            if counter >= 2 * number_of_adjustable_parameters:
                iteration = n_iterations
            else:
                adjustable_parameter_levels: tuple[int] = tuple(new_parameter_levels)
                self.dp.parameter_set.set_adjustable_levels(new_parameter_levels)
                iteration += 1

        self.dp.parameter_set.set_adjustable_levels(best_parameter_levels)
        self.dp.parameter_set.save('parameters%i' % time.time())

        contact = []
        adjustables_bounds_str: list[str] = ['(%.5f,%.5f)' % self.dp.parameter_set.adjustable_parameter_bounds[name] for name in self.dp.parameter_set.adjustable_parameter_names]
        for parameter_name in self.parameters.adjustable_parameter_names:
            if abs(self.dp.parameter_set(parameter_name)-self.dp.parameter_set.adjustable_parameter_bounds[parameter_name][0]) < 1e-2 * abs(self.dp.parameter_set.adjustable_parameter_bounds[parameter_name][0]):
                contact.append('<')
            elif abs(self.dp.parameter_set(parameter_name)-self.dp.parameter_set.adjustable_parameter_bounds[parameter_name][1]) < 1e-2 * abs(self.dp.parameter_set.adjustable_parameter_bounds[parameter_name][1]):
                contact.append('>')
            else:
                contact.append('-')

        pretty_table = prettytable.PrettyTable(header=True)
        pretty_table.add_column('name', self.dp.parameter_set.adjustable_parameter_names)
        pretty_table.add_column('initial level', initial_levels)
        pretty_table.add_column('final level', best_parameter_levels)
        pretty_table.add_column('final values', self.dp.parameter_set.adjustable_values)
        pretty_table.add_column('bounds', adjustables_bounds_str)
        pretty_table.add_column('contact', contact)
        pretty_table.float_format['final values'] = ".4"

        print(pretty_table)
        print('Learning error from %f to %f ' % (initial_error, best_error))

        return best_parameter_levels, best_outputs, best_error

    def save(self, file_name: str = 'results.csv', selected_variables: list[str] = None):
        """
        save the selected data in a csv file

        :param file_name: name of the csv file, defaults to 'results.csv' saved in the 'results' folder specified in the setup.ini file
        :type file_name: str, optional
        :param selected_variables: list of the variable names to be saved (None for all), defaults to None
        :type selected_variables: list[str], optional
        """
        self.data.save(file_name, selected_variables)

    def sensitivity(self, number_of_trajectories: int, number_of_levels: int = 4) -> dict:
        """Perform a Morris sensitivity analysis for average simulation error both for indoor temperature and CO2 concentration. It returns 2 plots related to each output variable. mu_star axis deals with the simulation variation bias, and sigma for standard deviation of the simulation variations wrt to each parameter.
        :param number_of_trajectories: [description], defaults to 100
        :type number_of_trajectories: int, optional
        :param number_of_levels: [description], defaults to 4
        :type number_of_levels: int, optional
        :return: a dictionary with the output variables as key and another dictionary as values. It admits 'names', 'mu', 'mu_star', 'sigma', 'mu_star_conf' as keys and corresponding values as lists
        :rtype: dict[str,dict[str,list[float|str]]]
        """

        print('number of levels:', number_of_levels)
        print('number of trajectories:', number_of_trajectories)
        problem: dict[str, float] = dict()
        adjustable_parameters: list[str] = self.parameters.adjustable_parameter_names
        problem['num_vars'] = len(adjustable_parameters)
        problem['names'] = []
        problem['bounds'] = []
        for parameter_name in adjustable_parameters:
            parameter_name = self.dp.variable_accessor_registry.reference(parameter_name)  # .name_data.
            problem['names'].append(parameter_name)
            problem['bounds'].append((0, self.parameters.adjustable_level_bounds[parameter_name][1]))

        parameter_value_sets = SALib.sample.morris.sample(problem, number_of_trajectories, num_levels=number_of_levels)

        errors = list()
        for i, parameter_value_set in enumerate(parameter_value_sets):
            parameter_value_set = [round(p) for p in parameter_value_set]
            self.dp.parameter_set.set_adjustable_levels(parameter_value_set)
            print('\nsimulation %i/%i>' % (i+1, len(parameter_value_sets)), '\t', parameter_value_set)
            simulated_output_data: dict[str, list[float]] = self.run(clear_cache=True)
            output_error = self.error(simulated_output_data)
            errors.append(output_error)
        print()
        print('Analyzing simulation results')
        print('\n* estimation errors')
        results: dict = SALib.analyze.morris.analyze(problem, parameter_value_sets, numpy.array(errors, dtype=float), conf_level=0.95, print_to_console=True, num_levels=number_of_levels)
        fig = plotly.express.scatter(results, x='mu_star', y='sigma', text=adjustable_parameters, title='estimation errors')
        fig.show()
        return results
