__author__ = 'stephane.ploix@g-scop.grenoble-inp.fr'
from math import sqrt, exp
import matplotlib.pyplot as plt
from math import log10, ceil, floor
from .utils import Averager
from psychrochart import PsychroChart


def plot_givoni(temperature_deg: list[float], relative_humidity_percent: list[float], chart_name: str = ''):
    chart: PsychroChart = PsychroChart.create()
    plt.figure()
    axes = chart.plot(ax=plt.gca())
    axes.scatter(temperature_deg, [1000*h for h in relative_humidity_percent], marker='o', alpha=.1)
    axes.set_title("Psychrometric diagram: %s" % chart_name)
    plt.show()


class OutdoorTemperatureIndices:

    @staticmethod
    def heat_index(temperature_celsius: float, relative_humidity: float):
        """
        Calculate Heat Index (feels like temperature) based on National Oceanic and Atmospheric Administration equation.

        Heat Index or humiture is an index that combines air-temperature and relative humidity in an attempt to determine the human-perceived equivalent temperature.
        HI is only useful when (temperature > 27 C) & (relative_humidity > 40 %) with temperature_fahrenheit = (temperature_celsius * 9/5) + 32 and temperature_celsius = (temperature_fahrenheit - 32) * 5/9

        See:
        [1] https://en.wikipedia.org/wiki/Heat_index
        [2] http://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
        [3] https://github.com/geanders/weathermetrics/blob/master/R/heat_index.R
        [4] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3801457/
        """

        c1: float = -8.78469475556  # SI units (Celsius)
        c2: float = 1.61139411
        c3: float = 2.33854883889
        c4: float = -0.14611605
        c5: float = -0.012308094
        c6: float = -0.0164248277778
        c7: float = 0.002211732
        c8: float = 0.00072546
        c9: float = -0.000003582

        temperature_fahrenheit: float = (temperature_celsius * 9/5) + 32
        heat_index_fahrenheit: float = 0.5 * (temperature_fahrenheit + 61 + (temperature_fahrenheit - 68) * 1.2 + relative_humidity * 0.094)
        temperature_fahrenheit_avg: float = (heat_index_fahrenheit + temperature_fahrenheit)/2   # Instructions in [3] call for averaging

        if temperature_fahrenheit_avg >= 80:
            # if (temperature > 27°C) & (relative_humidity > 40%), then use the full Rothfusz regression formula
            heat_index: float = sum([c1, c2 * temperature_celsius, c3 * relative_humidity, c4 * temperature_celsius * relative_humidity, c5 * temperature_celsius**2, c6 * relative_humidity**2, c7 * temperature_celsius**2 * relative_humidity, c8 * temperature_celsius * relative_humidity**2, c9 * temperature_celsius**2 * relative_humidity**2])
        else:
            heat_index = (heat_index_fahrenheit - 32) * 5/9

        return heat_index

    @staticmethod
    def wind_chill(temperature_celsius, wind_speed_km_h):
        """
        Calculate Wind Chill (feels like temperature) based on National Oceanic and Atmospheric Administration. Wind-chill or windchill (popularly wind chill factor) is the lowering of body temperature due to the passing-flow of lower-temperature air. Wind chill numbers are always lower than the air temperature for values where the formula is valid. When the apparent temperature is higher than the air temperature, the heat index is used instead.
        Wind Chill Temperature is only defined for temperatures at or below
        10°C and wind speeds above 4.8 Km/h

        [1] https://en.wikipedia.org/wiki/Wind_chill
        [2] https://www.wpc.ncep.noaa.gov/html/windchill.shtml
        """

        if temperature_celsius > 10 or wind_speed_km_h <= 4.8:
            raise ValueError("Wind Chill Temperature is only defined for temperatures at or below 10°C and wind speeds above 4.8 Km/h")
        return 13.12 + (0.6215 * temperature_celsius) - 11.37 * wind_speed_km_h**0.16 + 0.3965 * temperature_celsius * wind_speed_km_h**0.16

    @staticmethod
    def feels_like(temperature_celsius, relative_humidity, wind_speed_km_h) -> float:
        """
        Calculate the "Feels like" temperature based on National Oceanic and Atmospheric Administration logic.
        * Wind Chill:   temperature <= 10°C and wind > 4.8km/h
        * Heat Index:   temperature >= 26.7°C
        * Temperature as is: all other cases
        """

        if temperature_celsius <= 10 and wind_speed_km_h > 4.8:
            # Wind Chill for low temp cases (and wind)
            feels_like: float = OutdoorTemperatureIndices.wind_chill(temperature_celsius, wind_speed_km_h)
        elif temperature_celsius >= 26.7:
            # Heat Index for High temp cases
            feels_like = OutdoorTemperatureIndices.heat_index(temperature_celsius, relative_humidity)
        else:
            feels_like = temperature_celsius

        return round(feels_like, 1)

    @staticmethod
    def apparent_temperature(temperature_celsius, relative_humidity_percent, wind_speed_km_h) -> float:
        """
        The apparent temperature used here is based on a mathematical model of an adult, walking outdoors, in the shade (Steadman 1994). The apparent temperature is defined as; the temperature, at the reference relative_humidity level, producing the same amount of discomfort as that experienced under the current ambient temperature and relative_humidity.
        Practically speaking, this means that you have to adjust the ambient temparature by the apparent temperature. In this function the returned value, is the already adjusted temperature.

        References:
        [1] http://www.bom.gov.au/info/thermal_stress/#atapproximation
        """
        vapor_pressure: float = (relative_humidity_percent/100) * 6.105 * exp((17.27 * temperature_celsius) / (237.7 + temperature_celsius))
        apparent_temperature: float = temperature_celsius + 0.33 * vapor_pressure - 0.7 * wind_speed_km_h - 4
        return round(apparent_temperature, 1)


class PMVcalculator:

    @staticmethod
    def __pmv(precision, input_data: dict[str, float]) -> tuple[float]:
        air_temperature_C: float = input_data['air_temperature_C']
        air_temperature_K: float = 273.15 + air_temperature_C
        if input_data['radiant_temperature_C'] is None:
            radiant_temperature_C: float = air_temperature_C
        else:
            radiant_temperature_C = input_data['radiant_temperature_C']
        air_speed_m_s: float = input_data['air_speed_m_s']
        metabolism_MET: float = input_data['metabolism_MET']
        Icl_CLO: float = input_data['Icl_CLO']
        relative_humidity_percent: float = input_data['relative_humidity_percent']
        work_MET = 0

        P_vapor_Pa: float = relative_humidity_percent * 10 * exp(16.6536 - 4030.183 / (air_temperature_C + 235))

        R_clothes: float = 0.155 * Icl_CLO  # thermal insulation of the clothing in M2K/W
        metabolism_W_m2: float = metabolism_MET * 58.15  # metabolic rate in W/M2
        work_W_m2: float = work_MET * 58.15  # external work in W/M2
        base_metabolism_W_m2: float = metabolism_W_m2 - work_W_m2  # internal heat production in the human body
        # calculation of the clothing area factor
        if R_clothes <= 0.078:
            F_cl: float = 1 + (1.29 * R_clothes)  # ratio of surface clothed body over nude body
        else:
            F_cl = 1.05 + (0.645 * R_clothes)

        # heat transfer coefficient by forced convection
        hc_ventilated: float = 12.1 * sqrt(air_speed_m_s)
        hc: float = hc_ventilated  # initialize variable
        air_temperature_K: float = air_temperature_C + 273
        radiant_temperature_K: float = radiant_temperature_C + 273
        T_clothes_last_C: float = air_temperature_K + (35.5 - air_temperature_C) / (3.5 * R_clothes + 0.1)

        xn: float = T_clothes_last_C / 100
        xf: float = T_clothes_last_C / 50
        precision = 0.00015

        n = 0
        while abs(xn - xf) > precision:
            xf = (xf + xn) / 2
            hc_non_ventilated: float = 2.38 * abs(100.0 * xf - air_temperature_K) ** 0.25
            if hc_ventilated > hc_non_ventilated:
                hc = hc_ventilated
            else:
                hc = hc_non_ventilated
            xn = ((308.7 - 0.028 * base_metabolism_W_m2) + (R_clothes * F_cl * 3.96 * (radiant_temperature_K / 100.0) ** 4) + R_clothes * F_cl * air_temperature_K * hc - R_clothes * F_cl * 3.96 * xf**4) / (100 + R_clothes * F_cl * 100 * hc)
            n += 1
            if n > 150:
                raise StopIteration("Max iterations exceeded")

        T_clothes_C: float = 100 * xn - 273

        # heat loss diff. through skin
        P_perspiration_sweat_W_m2: float = 3.05 * 0.001 * (5733 - (6.99 * base_metabolism_W_m2) - P_vapor_Pa)
        # heat loss by sweating
        if base_metabolism_W_m2 > 58.15:
            P_perspiration_diffusion_W_m2: float = 0.42 * (base_metabolism_W_m2 - 58.15)
        else:
            P_perspiration_diffusion_W_m2 = 0
        # latent respiration heat loss
        P_breath_latent_W_m2: float = 1.7 * 0.00001 * metabolism_W_m2 * (5867 - P_vapor_Pa)
        # dry respiration heat loss
        P_breath_sensitive_W_m2: float = 0.0014 * metabolism_W_m2 * (34 - air_temperature_C)
        # heat loss by radiation
        P_rad_W_m2: float = 3.96 * F_cl * (xn**4 - (radiant_temperature_K / 100.0) ** 4)
        # heat loss by convection
        P_conv_W_m2 = F_cl * hc * (T_clothes_C - air_temperature_C)

        ts: float = 0.303 * exp(-0.036 * metabolism_W_m2) + 0.028
        PMV: float = ts * (base_metabolism_W_m2 - P_perspiration_sweat_W_m2 - P_perspiration_diffusion_W_m2 - P_breath_latent_W_m2 - P_breath_sensitive_W_m2 - P_rad_W_m2 - P_conv_W_m2)
        PPD: float = 100 - 95 * exp(-0.03353 * PMV**4 - 0.2179 * PMV**2)

        return {'PMV': PMV, 'P_metabolism_W_m2': metabolism_W_m2, 'P_perspiration_sweat_W_m2': P_perspiration_sweat_W_m2, 'P_perspiration_diffusion_W_m2': P_perspiration_diffusion_W_m2, 'P_breath_latent_W_m2': P_breath_latent_W_m2, 'P_breath_sensitive_W_m2': P_breath_sensitive_W_m2, 'P_rad_W_m2': P_rad_W_m2, 'P_conv_W_m2':  P_conv_W_m2, 'T_clothes_C': T_clothes_C, 'P_vapor_Pa': P_vapor_Pa, 'PPD': PPD}

    class Sampler:

        def __init__(self, bounds: dict[str, tuple[float, float]] = {'air_temperature_C': (17, 27), 'relative_humidity_percent': (0, 100), 'radiant_temperature_C': (14, 37), 'Icl_CLO': (0, 1.5), 'metabolism_MET': (0.8, 4.1), 'air_speed_m_s': (0, 1)}):
            self.bounds: dict[str, tuple[float, float]] = bounds

        @property
        def data_names(self) -> list[str]:
            return list(self.bounds.keys())

        def __call__(self, data_name: str, n_samples: int = 10):
            m, M = self.bounds[data_name]
            delta: float = (M - m) / (n_samples - 1)
            return [m + i * delta for i in range(n_samples)]

    def __init__(self, air_temperature_C=21, relative_humidity_percent=50, radiant_temperature_C=None, Icl_CLO=1, metabolism_MET=1, air_speed_m_s=0.1, precision: float = 1e-5) -> None:
        """
        air_temperature_C: air temperature in celcius
        self.relative_humidity = relative_humidity between 0 and 100
        radiant_temperature: average temperature for radiative effect i.e. average wall surface temperature in celcius, if None use air_temperature
        relative_humidity: relative humidity from 0 to 1 default=0.50
        Icl_CLO: clothing index in CLO
        metabolism_MET: metabolism in MET typ. from 0.8 to 4
        air_speed_m_s: air speed in m/s typ. from 0 to 1 default=0.1
        """
        self.precision: float = precision
        self.__input_data = dict()
        self.__input_data['air_temperature_C'] = air_temperature_C
        self.__input_data['relative_humidity_percent'] = relative_humidity_percent
        self.__input_data['radiant_temperature_C'] = radiant_temperature_C
        self.__input_data['Icl_CLO'] = Icl_CLO
        self.__input_data['metabolism_MET'] = metabolism_MET
        self.__input_data['air_speed_m_s'] = air_speed_m_s

        self._input_names: list = list(self.__input_data.keys())
        self._output_names: list[str] = ['PMV', 'P_metabolism_W_m2', 'P_perspiration_sweat_W_m2', 'P_perspiration_diffusion_W_m2', 'P_breath_latent_W_m2', 'P_breath_sensitive_W_m2', 'P_rad_W_m2', 'P_conv_W_m2', 'T_clothes_C', 'P_vapor_Pa', 'PPD']

    def set_input_data(self, **name_values: dict[str, float]) -> None:
        for name in name_values:
            self.__input_data[name] = name_values[name]

    @property
    def input_names(self) -> list[str]:
        return self._input_names

    @property
    def output_names(self) -> list[str]:
        return self._output_names
    
    def PMV(self, **input_data) -> float:
        return self.output_data('PMV', **input_data)['PMV']

    def PPD(self, **input_data) -> float:
        return self.output_data('PPD', **input_data)['PPD']
    
    def abs_PMV(self, **input_data) -> float:
        return abs(self.PMV(**input_data))

    def output_data(self, *output_names, **input_data) -> dict[str, float]:
        # return tuple: (PMV, Pperspirationsweat, Pperspirationdiffusion, Pbreathlatent, Pbreathsensitive, Pradiative, Pconvection, PPD) with powers in Watts
        my_input_data: dict[str, float] = dict()
        for input_name in self.input_names:
            if input_name in input_data:
                my_input_data[input_name] = input_data[input_name]
            else:
                my_input_data[input_name] = self.__input_data[input_name]
        output_data: dict[str, float] = PMVcalculator.__pmv(self.precision, my_input_data)
        if len(output_names) == 0:
            return output_data
        return {output_name: output_data[output_name] for output_name in output_names}

    def variate(self, input_name: str, input_values: list[float], overloaded_data: dict[str, float] = {}) -> tuple[float]:
        results: dict[str, list[float]] = {output_name: [] for output_name in self.output_names}
        for input_value in input_values:
            data = dict()
            for an_input_name in self._input_names:
                if an_input_name == input_name:
                    data[input_name] = input_value
                elif an_input_name in overloaded_data:
                    data[an_input_name] = overloaded_data[an_input_name]
                else:
                    data[an_input_name] = self.__input_data[an_input_name]
            result: tuple[float] = PMVcalculator.__pmv(self.precision, data)
            for output_name in self.output_names:
                results[output_name].append(result[output_name])
        return results

    def __str__(self) -> str:
        string = '* Input data with default value:\n'
        for v in self._input_names:
            if self.__input_data[v] is not None:
                string += '%s: %g\n' % (v, self.__input_data[v])
            else:
                string += '%s: None\n' % (v)
        string += '\n* Output data with default value:\n'
        output_data: dict[str, float] = self.output_data()
        for v in output_data:
            string += '%s: %g\n' % (v, output_data[v])
        return string + '\n'

    def parametric_plot(self, parameter_name: str, x_variable_name: str, y_variable_name: str = 'PMV'):
        sampler = PMVcalculator.Sampler()
        parameter_samples: list[float] = sampler(parameter_name, n_samples=6)
        for p_val in parameter_samples:
            x_variable_samples: list[float] = sampler(x_variable_name, 16)
            results: tuple[float] = self.variate(x_variable_name, x_variable_samples, overloaded_data={parameter_name: p_val})
            plt.plot(x_variable_samples, results[y_variable_name], label='%s=%g' % (parameter_name, p_val))
        plt.legend()
        plt.xlabel(x_variable_name)
        plt.ylabel(y_variable_name)
        plt.grid()

    def ppd_plot(self):
        PMVs: list[float] = [_/10 for _ in range(-30, 31)]
        PPDs: list[float] = [100 - 95 * exp(-0.03353 * PMV**4 - 0.2179 * PMV**2) for PMV in PMVs]
        plt.plot(PMVs, PPDs)
        plt.xlabel('PMV')
        plt.ylabel('Predicted Percentage of Dissatisfied')
        plt.grid()


class AdaptiveComfort:

    @staticmethod
    def comfort_class(Tin: float, Tcomfort: float):
        if Tcomfort - 2 <= Tin <= Tcomfort + 2:
            return 1
        elif Tcomfort - 3 <= Tin <= Tcomfort + 3:
            return 2
        elif Tcomfort - 4 <= Tin <= Tcomfort + 4:
            return 3
        else:
            return 4

    def __init__(self, outdoor_temperatures: list[float], occupancy: list[float], n_hours_averager: int = 7*24) -> None:
        self.Tout_avg: list[float] = Averager(outdoor_temperatures).average(n_hours_averager)
        self.occupancy: list[float] = occupancy

    def Tcomfort(self, level: int = 0) -> list[float]:
        return [0.33 * self.Tout_avg[k] + 18.8 + level for k in range(len(self.Tout_avg))]

    def __call__(self, Tin: list[float]) -> list[int]:
        _Tcomfort: list[float] = self.Tcomfort()
        return [0 if self.occupancy[k] == 0 else AdaptiveComfort.comfort_class(Tin[k], _Tcomfort[k]) for k in range(len(self.Tout_avg))]


def icone(CO2_concentration: list[float], occupancies: list[float]) -> float:
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
    for k in range(len(occupancies)):
        if occupancies[k] > 0:
            n_presence += 1
            if 1000 <= CO2_concentration[k] < 1700:
                n1_medium_containment += 1
            elif CO2_concentration[k] >= 1700:
                n2_high_containment += 1
    f1 = n1_medium_containment / n_presence if n_presence > 0 else 0
    f2 = n2_high_containment / n_presence if n_presence > 0 else 0
    return 8.3 * log10(1 + f1 + 3 * f2)


def extreme_quantiles_during_presence(values: list[float], occupancies: list[float], cut: float = .1):
    values_when_presence = list()
    for i in range(len(occupancies)):
        if occupancies[i] > 0:
            values_when_presence.append(values[i])

    if len(values_when_presence) > 0:
        values_when_presence.sort()
        values_when_presence_lowest = values_when_presence[:ceil(len(values_when_presence) * cut)]
        values_when_presence_highest = values_when_presence[floor(len(values_when_presence) * (1-cut)):]
        return {'average': sum(values_when_presence) / len(values_when_presence), 'cut': cut,
                'lowest': sum(values_when_presence_lowest) / len(values_when_presence_lowest),
                'highest': sum(values_when_presence_highest) / len(values_when_presence_highest)
                }
    else:
        return {'average': None, 'cut': cut, 'lowest': None, 'highest': None}