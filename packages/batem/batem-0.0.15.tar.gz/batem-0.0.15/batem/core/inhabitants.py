import math
from datetime import datetime
from .timemg import datetime_to_stringdate
from .comfort import icone


class Contiguous:
    """Display datetimes series from """

    def __init__(self, name: str, datetimes: list[datetime]):
        self.name: str = name
        self.datetimes: list[datetime] = datetimes
        self.time_slots: list[int] = list()

    def add(self, k: int) -> None:
        self.time_slots.append(k)

    def __str__(self) -> None:
        string: str = f"Period of {self.name}: "
        if len(self.time_slots) == 0:
            return string + "\nempty"
        k_start: int = self.time_slots[0]
        counter: int = 1
        for i in range(1, len(self.time_slots)):
            if self.time_slots[i] != k_start + counter:
                string += "\n%s (k=%i): %i hours, " % (datetime_to_stringdate(self.datetimes[k_start]), k_start, counter)
                counter = 1
                k_start = self.time_slots[i]
            else:
                counter += 1
        return string


class Preference:
    """Provide de a model of the occupants'preferences. It deals with thermal comfort, air quality, number of home configuration changes, energy cost, icone,..."""

    def __init__(self, preferred_temperatures=(21, 23), extreme_temperatures=(16, 28), preferred_CO2_concentration=(500, 1500), temperature_weight_wrt_CO2: float = 0.5, power_weight_wrt_comfort: float = 0.5, mode_cop: dict[int, float] = {}):
        """Definition of comfort regarding  number of required actions by occupants, temperature and CO2 concentration, but also weights between cost and comfort, and between thermal and air quality comfort.

        :param preferred_temperatures: preferred temperature range, defaults to (21, 23)
        :type preferred_temperatures: tuple, optional
        :param extreme_temperatures: limits of acceptable temperatures, defaults to (18, 26)
        :type extreme_temperatures: tuple, optional
        :param preferred_CO2_concentration: preferred CO2 concentration range, defaults to (500, 1500)
        :type preferred_CO2_concentration: tuple, optional
        :param temperature_weight_wrt_CO2: relative importance of thermal comfort wrt air quality (1 means only temperature is considered), defaults to 0.5
        :type temperature_weight_wrt_CO2: float, optional
        :param power_weight_wrt_comfort: relative importance of energy cost wrt comfort (1 means only energy cost is considered), defaults to 0.5e-3
        :type power_weight_wrt_comfort: float, optional
        :param mode_cop: coefficient of performance for the HVAC system per mode (corresponding for instance to heating and cooling periods), defaults to an empty dictionary which corresponds to a COP=1
        :type mode_cop: dict[int, float]
        """
        self.preferred_temperatures = preferred_temperatures
        self.extreme_temperatures = extreme_temperatures
        self.preferred_CO2_concentration = preferred_CO2_concentration
        self.temperature_weight_wrt_CO2 = temperature_weight_wrt_CO2
        self.power_weight_wrt_comfort = power_weight_wrt_comfort
        self.mode_cop = mode_cop

    def change_dissatisfaction(self, occupancy, action_set):
        """Compute the ratio of the number of hours where occupants have to change their home configuration divided by the number of hours with presence.

        :param occupancy: a vector of occupancies
        :type occupancy: list[float]
        :param action_set: different vectors of actions
        :type action_set: tuple[list[float]]
        :return: the number of hours where occupants have to change their home configuration divided by the number of hours with presence
        :rtype: float
        """
        number_of_changes = 0
        number_of_presences = 0
        previous_actions = [actions[0] for actions in action_set]
        for k in range(len(occupancy)):
            if occupancy[k] > 0:
                number_of_presences += 1
                for i in range(len(action_set)):
                    actions = action_set[i]
                    if actions[k] != previous_actions[i]:
                        number_of_changes += 1
                        previous_actions[i] = actions[k]
        return number_of_changes / number_of_presences if number_of_presences > 0 else 0

    def thermal_comfort_dissatisfaction(self, temperatures, occupancies):
        """Compute average dissatisfaction regarding thermal comfort: 0 means perfect and greater than 1 means not acceptable. Note that thermal comfort is only taken into account if occupancy > 0, i.e. in case of presence.

        :param temperatures: vector of temperatures
        :type temperatures: list[float]
        :param occupancies: vector of occupancies (number of people per time slot)
        :type occupancies: list[float]
        :return: average dissatisfaction regarding thermal comfort
        :rtype: float
        """
        if type(temperatures) is not list:
            temperatures = [temperatures]
            occupancies = [occupancies]
        dissatisfaction = 0
        for i in range(len(temperatures)):
            if occupancies[i] != 0:
                if temperatures[i] < self.preferred_temperatures[0]:
                    dissatisfaction += (self.preferred_temperatures[0] - temperatures[i]) / (self.preferred_temperatures[0] - self.extreme_temperatures[0])
                elif temperatures[i] > self.preferred_temperatures[1]:
                    dissatisfaction += (temperatures[i] - self.preferred_temperatures[1]) / (self.extreme_temperatures[1] - self.preferred_temperatures[1])
        return dissatisfaction / len(temperatures)

    def air_quality_dissatisfaction(self, CO2_concentrations, occupancies):
        """Compute average dissatisfaction regarding air quality comfort: 0 means perfect and greater than 1 means not acceptable. Note that air quality comfort is only taken into account if occupancy > 0, i.e. in case of presence.

        :param CO2_concentrations: vector of CO2 concentrations
        :type CO2_concentrations: list[float]
        :param occupancies: vector of occupancies (number of people per time slot)
        :type occupancies: list[float]
        :return: average dissatisfaction regarding air quality comfort
        :rtype: float
        """
        if type(CO2_concentrations) is not list:
            CO2_concentrations = [CO2_concentrations]
            occupancies = [occupancies]
        dissatisfaction = 0
        for i in range(len(CO2_concentrations)):
            if occupancies[i] != 0:
                dissatisfaction += max(0., (CO2_concentrations[i] - self.preferred_CO2_concentration[0]) /
                                       (self.preferred_CO2_concentration[1] - self.preferred_CO2_concentration[0]))
        return dissatisfaction / len(CO2_concentrations)

    def comfort_dissatisfaction(self, temperatures: list[float], CO2_concentrations: list[float], occupancies: list[float]):
        """Compute the comfort weighted dissatisfaction that combines thermal and air quality dissatisfactions: it uses the thermal_dissatisfaction and air_quality_dissatisfaction methods.

        :param temperatures: list of temperatures
        :type temperatures: list[float]
        :param CO2_concentrations: list of CO2 concentrations
        :type CO2_concentrations: list[float]
        :param occupancies: list of occupancies
        :type occupancies: list[float]
        :return: the global comfort dissatisfaction
        :rtype: float
        """
        return self.temperature_weight_wrt_CO2 * self.thermal_comfort_dissatisfaction(temperatures, occupancies) + (1 - self.temperature_weight_wrt_CO2) * self.air_quality_dissatisfaction(CO2_concentrations, occupancies)

    def daily_cost_euros(self, Pheat: list[float], modes: list[int] = None, kWh_price: float = 0.13) -> float:
        """Compute the heating cost.

        :param Pheat: list of heating power consumptions
        :type Pheat: list[float]
        :param kWh_price: tariff per kWh, defaults to .13
        :type kWh_price: float, optional
        :return: energy cost
        :rtype: float
        """
        needed_energy_Wh = 0
        for k in range(len(Pheat)):
            if modes is not None and modes[k] != 0 and modes[k] in self.mode_cop:
                needed_energy_Wh += abs(Pheat[k]) / self.mode_cop[modes[k]]
            else:  # consider a COP = 1
                needed_energy_Wh += abs(Pheat[k])
            # else:
            #     cost_Wh = sum(Pheat)
        return 24 * needed_energy_Wh / len(Pheat) / 1000 * kWh_price

    def icone(self, CO2_concentration, occupancy) -> float:
        """Compute the ICONE indicator dealing with confinement regarding air quality.

        :param CO2_concentration: list of CO2 concentrations
        :type CO2_concentration: list[float]
        :param occupancy: list of occupancies
        :type occupancy: list[float]
        :return: value between 0 and 5
        :rtype: float
        """
        n_presence = 0
        n1_medium_containment = 0
        n2_high_containment = 0
        for k in range(len(occupancy)):
            if occupancy[k] > 0:
                n_presence += 1
                if 1000 <= CO2_concentration[k] < 1700:
                    n1_medium_containment += 1
                elif CO2_concentration[k] >= 1700:
                    n2_high_containment += 1
        f1 = n1_medium_containment / n_presence if n_presence > 0 else 0
        f2 = n2_high_containment / n_presence if n_presence > 0 else 0
        return 8.3 * math.log10(1 + f1 + 3 * f2)

    def assess(self, Pheater: list[float], temperatures: list[float], CO2_concentrations: list[float], occupancies: tuple[list[float]], modes: list[float] = None) -> float:
        """Compute the global objective to minimize including both comforts and energy cost for heating.

        :param Pheater: list of heating powers
        :type Pheater: list[float]
        :param temperatures: list of temperatures
        :type temperatures: list[float]
        :param CO2_concentrations: list of CO2 concentrations
        :type CO2_concentrations: list[float]
        :param occupancies: list of occupancies
        :type occupancies: list[float]
        :return: objective value
        :rtype: float
        """
        return self.daily_cost_euros(Pheater, modes) * self.power_weight_wrt_comfort + (1 - self.power_weight_wrt_comfort) * self.comfort_dissatisfaction(temperatures, CO2_concentrations, occupancies)

    def print_assessment(self, datetimes: datetime, Pheater: list[float], temperatures: list[float], CO2_concentrations: list[float], occupancies: list[float], action_sets: tuple[list[float]],  modes: list[float] = None, list_extreme_hours: bool = False):
        """Print different indicators to appreciate the impact of a series of actions.

        :param Pheat: list of heating powers
        :type Pheat: list[float]
        :param temperatures: list of temperatures
        :type temperatures: list[float]
        :param CO2_concentrations: list of CO2 concentrations
        :type CO2_concentrations: list[float]
        :param occupancies: list of occupancies
        :type occupancies: list[float]
        :param actions: list of actions
        :type actions: tuple[list[float]]
        """
        hour_quality_counters: dict[str, int] = {'extreme cold': 0, 'cold': 0, 'perfect': 0, 'warm': 0, 'extreme warm': 0}
        n_hours_with_presence = 0
        extreme_cold_contiguous = Contiguous('Extreme cold', datetimes)
        extreme_warm_contiguous = Contiguous('Extreme warm', datetimes)

        for k, temperature in enumerate(temperatures):
            if occupancies[k] > 0:
                n_hours_with_presence += 1
                if temperature < self.extreme_temperatures[0]:
                    hour_quality_counters['extreme cold'] += 1
                    extreme_cold_contiguous.add(k)
                elif temperature < self.preferred_temperatures[0]:
                    hour_quality_counters['cold'] += 1
                elif temperature > self.extreme_temperatures[1]:
                    hour_quality_counters['extreme warm'] += 1
                    extreme_warm_contiguous.add(k)
                elif temperature > self.preferred_temperatures[1]:
                    hour_quality_counters['warm'] += 1
                else:
                    hour_quality_counters['perfect'] += 1
        print(f'\nThe assessed period covers {round(len(temperatures)/24)} days with a total HVAC energy of {int(round(sum([abs(P) / 1000 for P in Pheater])))}kWh (heating: {int(round(sum([P / 1000 if P > 0 else 0 for P in Pheater])))}kWh / cooling: {int(round(sum([-P / 1000 if P < 0 else 0 for P in Pheater])))}kWh):')
        print('- global objective: %s' % self.assess(Pheater, temperatures, CO2_concentrations, occupancies, modes))
        print('- average thermal dissatisfaction: %.2f%%' % (self.thermal_comfort_dissatisfaction(temperatures, occupancies) * 100))
        for hour_quality_counter in hour_quality_counters:
            print('- %% of %s hours: %.2f' % (hour_quality_counter, 100 * hour_quality_counters[hour_quality_counter] / n_hours_with_presence))
        print('- average CO2 dissatisfaction: %.2f%%' % (self.air_quality_dissatisfaction(CO2_concentrations, occupancies) * 100))
        print('- ICONE: %.2f' % (icone(CO2_concentrations, occupancies)))
        print('- average comfort dissatisfaction: %.2f%%' % (self.comfort_dissatisfaction(temperatures, CO2_concentrations, occupancies) * 100))
        print('- change dissatisfaction (number of changes / number of time slots with presence): %.2f%%' % (self.change_dissatisfaction(occupancies, action_sets) * 100))
        print('- heating cost: %.2f euros/day' % self.daily_cost_euros(Pheater, modes))

        temperatures_when_presence = list()
        CO2_concentrations_when_presence = list()
        for i in range(len(occupancies)):
            if occupancies[i] > 0:
                temperatures_when_presence.append(temperatures[i])
                CO2_concentrations_when_presence.append(CO2_concentrations[i])
        if len(temperatures_when_presence) > 0:
            temperatures_when_presence.sort()
            CO2_concentrations_when_presence.sort()
            office_temperatures_estimated_presence_lowest = temperatures_when_presence[:math.ceil(len(temperatures_when_presence) * 0.1)]
            office_temperatures_estimated_presence_highest = temperatures_when_presence[math.floor(len(temperatures_when_presence) * 0.9):]
            office_co2_concentrations_estimated_presence_lowest = CO2_concentrations_when_presence[:math.ceil(len(CO2_concentrations_when_presence) * 0.1)]
            office_co2_concentrations_estimated_presence_highest = CO2_concentrations_when_presence[math.floor(len(CO2_concentrations_when_presence) * 0.9):]
            print('- average temperature during presence: %.1f' % (sum(temperatures_when_presence) / len(temperatures_when_presence)))
            print('- average 10%% lowest temperature during presence: %.1f' % (sum(office_temperatures_estimated_presence_lowest) / len(office_temperatures_estimated_presence_lowest)))
            print('- average 10%% highest temperature during presence: %.1f' % (sum(office_temperatures_estimated_presence_highest) / len(office_temperatures_estimated_presence_highest)))
            print('- average CO2 concentration during presence: %.0f' % (sum(CO2_concentrations_when_presence) / len(CO2_concentrations_when_presence)))
            print('- average 10%% lowest CO2 concentration during presence: %.0f' % (sum(office_co2_concentrations_estimated_presence_lowest) / len(office_co2_concentrations_estimated_presence_lowest)))
            print('- average 10%% highest CO2 concentration during presence: %.0f' %
                  (sum(office_co2_concentrations_estimated_presence_highest) / len(office_co2_concentrations_estimated_presence_highest)))
        if list_extreme_hours:
            print('Contiguous periods:')
            print(extreme_cold_contiguous)
            print(extreme_warm_contiguous)

    def __str__(self):
        """Return a description of the defined preferences.

        :return: a descriptive string of characters.
        :rtype: str
        """
        string = 'Preference:\ntemperature in %f<%f..%f>%f\n concentrationCO2 %f..%f\n' % (
            self.extreme_temperatures[0], self.preferred_temperatures[0], self.preferred_temperatures[1], self.extreme_temperatures[1], self.preferred_CO2_concentration[0], self.preferred_CO2_concentration[1])
        string += 'overall: %.3f * cost + %.3f disT + %.3f disCO2' % (self.power_weight_wrt_comfort, (1-self.power_weight_wrt_comfort) * self.temperature_weight_wrt_CO2, (1-self.power_weight_wrt_comfort) * (1-self.temperature_weight_wrt_CO2))
        return string
