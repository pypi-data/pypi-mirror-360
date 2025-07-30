"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0

General explanations about Case Base Reasoning for advising can be found in the doc folder ./doc/formalismCBR.md
"""
import time
import matplotlib.pyplot as plt
from batem.core.inhabitants import Preference
from batem.core.data import DataProvider
from batem.sites.simulation_h358 import make_building_state_model
from batem.sites.data_h358 import make_data_provider
from batem.core.cbr import SimpleCaseBaseAdviser, CaseBase


class H358SimpleCaseBaseAdviser(SimpleCaseBaseAdviser):

    def __init__(self, dp: DataProvider, context_variables: tuple[str], action_variables: tuple[str], effect_variables_sensitivities: dict[str, float], first_day_hour: int = 6, last_day_hour: int = 23):
        """The case base handler dedicated to the thermal and CO2 concentration comfort for the H358 office

        :param dp: the data provider containing the measurements and past weather records
        :type dp: DataProvider
        :param context_variables: the names of context variables (uncontrollable causes) to be taken into account
        :type context_variables: tuple[str]
        :param action_variables: the names of action variables (uncontrollable causes) to be taken into account
        :type action_variables: tuple[str]
        :param effect_variables_sensitivities: the sensitive perceivable resolution
        :type effect_variables_sensitivities: dict[str, float]
        :param first_day_hour: the starting hour of each day to 6 (previous hours in the day are ignored)
        :type first_day_hour: int, optional
        :param last_day_hour: the last hour of the day (included) taken into account, defaults to 23
        :type last_day_hour: int, optional
        """
        super(H358SimpleCaseBaseAdviser, self).__init__(dp, context_variables, action_variables, effect_variables_sensitivities, first_day_hour, last_day_hour)

    def performance(self, case: CaseBase.Case) -> float:
        """Evaluate the performance of a case (implemented abstract method)

        :param case: a case
        :type case: CaseBase.Case
        :return: the performance
        :rtype: float
        """
        variable_values = self.case_variable_data(case)
        return Preference().assess(variable_values[self.action_variables[2]],  variable_values[self.effect_variables[0]], variable_values[self.effect_variables[1]], variable_values['occupancy'])


if __name__ == '__main__':

    # hyper-parameters
    period: tuple[str, str] = ('15/02/2015', '15/02/2016')  # '15/02/2016'
    number_of_neighbors: int = 10
    capping: int = 100000
    reoptimize: bool = True
    with_adaptation: bool = True

    # simulation of office temperature and CO2 concentration
    dp_orig: DataProvider = make_data_provider(starting_stringdate=period[0], ending_stringdate=period[1])
    dp_orig.add_external_variable('door_opening_orig', dp_orig.series('door_opening'))  # duplicate door_opening under another name
    dp_orig.add_external_variable('window_opening_orig', dp_orig.series('window_opening'))  # duplicate window_opening under another name
    dp_orig.add_external_variable('Pheater_orig', dp_orig.series('office:Pheater'))  # duplicate PZ under another name
    h358_state_model, nominal_state_model = make_building_state_model(dp_orig, periodic_depth_seconds=60*60, state_model_order_max=5)
    variable_simulated_values: dict[str, list[float]] = h358_state_model.simulate()
    for variable_name in variable_simulated_values:
        dp_orig.add_external_variable(variable_name + '_orig', variable_simulated_values[variable_name])
    datetimes: list[float] = dp_orig.datetimes

    recommended_action_data = dict()  # initialize recommended action with recorded actions
    recommended_action_data['door_opening'] = dp_orig.series('door_opening')
    recommended_action_data['window_opening'] = dp_orig.series('window_opening')
    recommended_action_data['office:Pheater'] = dp_orig.series('office:Pheater')
    print(dp_orig)

    # case base reasoning
    starting_time = time.time()
    cbh1 = H358SimpleCaseBaseAdviser(dp_orig, ('Psun_window', 'occupancy', 'weather_temperature', 'total_electric_power'), ('door_opening', 'window_opening', 'office:Pheater'), {'TZoffice': .5, 'CCO2office': 200}, 6, 23)  # first effect variable must be the office temperature and second the CO2 concentration
    cbh1.weights_optimizer(maxiter=10)
    cbh1.incompleteness(with_plot=True)
    removed_cases: list[CaseBase.Case] = cbh1.cap_cases(capping, reoptimize=reoptimize)
    print('All removed cases (%i):\n' % len(removed_cases) + ',\t'.join([repr(case) for case in sorted(removed_cases)]))
    cbh1.incompleteness(with_plot=True)
    cbh1.statistics(number_of_neighbors=number_of_neighbors)
    for case in cbh1.case_base.cases:
        best_actions: list[float] = cbh1.suggest(case, number_of_neighbors=number_of_neighbors, adaptation=with_adaptation)
        cbh1.set_actions(recommended_action_data, case, best_actions)
    print('cbr time in %i minutes' % round((time.time() - starting_time)/60))

    # make a new data provider for a second simulation using the actions suggested by the case base reasoning approach and load the interesting data series into the initial data provider
    dp_cbr: DataProvider = make_data_provider(starting_stringdate=period[0], ending_stringdate=period[1])
    recommended_door_opening: list[float] = recommended_action_data['door_opening']
    recommended_window_opening: list[float] = recommended_action_data['window_opening']
    recommended_Pheater: list[float] = recommended_action_data['office:Pheater']
    dp_cbr.add_external_variable('door_opening', recommended_door_opening)
    dp_orig.add_external_variable('door_opening_suggest', recommended_door_opening)
    dp_cbr.add_external_variable('window_opening', recommended_window_opening)
    dp_orig.add_external_variable('window_opening_suggest', recommended_window_opening)
    dp_cbr.add_external_variable('office:Pheater', recommended_Pheater)
    dp_orig.add_external_variable('Pheater_suggest', recommended_Pheater)

    h358_state_model, nominal_state_model = make_building_state_model(dp_cbr, periodic_depth_seconds=60*60, state_model_order_max=5)
    variable_simulated_values: dict[str, list[float]] = h358_state_model.simulate()
    for variable_name in variable_simulated_values:
        dp_orig.add_external_variable(variable_name + '_suggest', variable_simulated_values[variable_name])

    # compute the initial performances with the ones obtained with the case base reasoning approach
    preference = Preference()
    print('Without CBR')
    preference.print_assessment(dp_orig.datetimes, dp_orig.series('Pheater_orig'), dp_orig.series('TZoffice_orig'), dp_orig.series('CCO2office_orig'), dp_orig.series('occupancy'), action_sets=())
    # datetimes: datetime, Pheater: list[float], temperatures: list[float], CO2_concentrations: list[float], occupancies: list[float], action_sets: tuple[list[float]],  modes: list[float] = None, list_extreme_hours: bool = False
    print('With CBR')
    preference.print_assessment(dp_orig.datetimes, dp_orig.series('Pheater_suggest'), dp_orig.series('TZoffice_suggest'), dp_orig.series('CCO2office_suggest'), dp_orig.series('occupancy'), action_sets=())

    plt.show()
    dp_orig.plot()
