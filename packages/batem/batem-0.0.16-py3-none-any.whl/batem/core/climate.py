"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0
"""
from __future__ import annotations
import configparser
import time as tm
from datetime import datetime, date, time, timedelta
from statistics import mean
from pytz import timezone
from abc import ABC
import re
import os
import pickle
from hashlib import shake_128
from .data import TimeSeriesPlotter
from .weather import SiteWeatherData
from collections import defaultdict
from .timemg import stringdate_to_date, date_to_stringdate
import plotly.graph_objects as go

config = configparser.ConfigParser()
config.read('setup.ini')


class Merger(ABC):

    def __init__(self, variable_name: str, operation_name: str, operation: callable):
        if operation_name == '':
            self.feature_name = variable_name
        else:
            self.feature_name = variable_name + '_' + operation_name
        self.variable_name = variable_name
        self.operation_name = operation_name
        self.operation: callable = operation

    def __call__(self, variable_values: list[float]) -> float:
        return self.operation([variable_values[i] for i in range(len(variable_values))])


class AvgMerger(Merger):

    def __init__(self, variable_name: str):
        super().__init__(variable_name, '', mean)


class SumMerger(Merger):

    def __init__(self, variable_name: str):
        super().__init__(variable_name, '', sum)


class MinMerger(Merger):

    def __init__(self, variable_name: str):
        super().__init__(variable_name, 'min', min)


class MaxMerger(Merger):

    def __init__(self, variable_name: str):
        super().__init__(variable_name, 'max', max)


class HistoricalDatabase:

    def __init__(self, site_weather_data: SiteWeatherData, feature_merger_weights: dict[Merger, float]) -> None:
        self.site_weather_data: SiteWeatherData = site_weather_data
        self.feature_merger_weights: dict[Merger, float] = feature_merger_weights
        self.feature_names: list[str] = [merger.feature_name for merger in feature_merger_weights]
        self.feature_name_mergers: dict[str, Merger] = {merger.feature_name: merger for merger in feature_merger_weights}
        self.feature_variable_names: list[str] = list({merger.variable_name for merger in feature_merger_weights})
        self.site_date_datetimes: dict[SiteWeatherData, dict[date, list[datetime]]] = dict()
        self.site_date_variable_values: dict[SiteWeatherData, dict[date, dict[str, list[float]]]] = dict()
        self.site_date_feature_values: dict[SiteWeatherData, dict[date, dict[str, float]]] = dict()
        self.features_min_max: dict[str, list[float, float]] = dict()
        self.add_site_weather_data(site_weather_data)
        self.variable_names: list[str] = site_weather_data.variable_names_without_time

    def add_site_weather_data(self, site_weather_data: SiteWeatherData):
        print('building historical database')
        date_datetimes: dict[date, list[datetime]] = defaultdict(list)
        date_variable_values: dict[date, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        variable_data = {v: site_weather_data.get(v) for v in site_weather_data.variable_names_without_time}

        for i, dt in enumerate(site_weather_data.datetimes):
            d: date = dt.date()
            date_datetimes[d].append(dt)
            for v in site_weather_data.variable_names_without_time:
                date_variable_values[d][v].append(variable_data[v][i])

        date_to_be_removed = list()
        feature_names_values: dict[str, list[float]] = {fname: list() for fname in self.feature_names}
        date_feature_values: dict[date, dict[str, float]] = dict()
        for d in date_datetimes:
            if len(date_datetimes[d]) != 24:
                date_to_be_removed.append(d)
            else:
                date_feature_values[d] = dict()
                for merger in self.feature_merger_weights:
                    date_feature_values[d][merger.feature_name] = merger(date_variable_values[d][merger.variable_name])
                    feature_names_values[merger.feature_name].append(date_feature_values[d][merger.feature_name])
        for d in date_to_be_removed:
            del date_datetimes[d]
            del date_variable_values[d]

        for fname in self.feature_names:
            min_max: list[float, float] = [min(feature_names_values[fname]), max(feature_names_values[fname])]
            if fname not in self.features_min_max:
                self.features_min_max[fname] = min_max
            else:
                self.features_min_max[fname][0] = min(self.features_min_max[fname][0], min_max[0])
                self.features_min_max[fname][1] = max(self.features_min_max[fname][1], min_max[1])
        self.site_date_datetimes[site_weather_data] = date_datetimes
        self.site_date_variable_values[site_weather_data] = date_variable_values
        self.site_date_feature_values[site_weather_data] = date_feature_values

    @property
    def sites(self):
        return tuple(self.site_date_feature_values.keys())

    @property
    def earliest_datetime(self):
        return min([site.datetimes[0] for site in self.sites])

    @property
    def latest_datetime(self):
        return max([site.datetimes[-1] for site in self.sites])

    @property
    def diy_features_variables(self) -> list[tuple[int, dict[str, float], dict[str, float]]]:
        diy_features_variables: list[float] = list()
        for site in self.site_date_feature_values:
            for d in self.site_date_feature_values[site]:
                day_number = d.timetuple().tm_yday
                normalized_features: dict[str, float] = self.normalize(self.site_date_feature_values[site][d])
                variable_values: dict[str, list[float]] = self.site_date_variable_values[site][d]
                diy_features_variables.append((day_number, normalized_features, variable_values))
        return diy_features_variables

    def normalize(self, feature_values: dict[str, float]) -> dict[str, float]:
        normalized_data = dict()
        for var in feature_values:
            if var in self.features_min_max:
                min_var: float = self.features_min_max[var][0]
                max_var: float = self.features_min_max[var][1]
                normalized_data[var] = (feature_values[var] - min_var) / (max_var - min_var)
            else:
                normalized_data[var] = feature_values[var]
        return normalized_data

    def plot(self):
        TimeSeriesPlotter(self.site_weather_data.series(), self.site_weather_data.datetimes, self.site_weather_data.units())

    def plot_prospective_comparison(self, prospective_climate: ProspectiveClimateDRIAS) -> None:
        feature_name_errors: dict[str, list[float]] = {fname: list() for fname in self.feature_names}
        prospective_dates = list()
        prospective_name_features: dict[str, list[float]] = {fname: list() for fname in self.feature_names}
        earliest_historical_date = self.earliest_datetime.date()
        latest_historical_date = self.latest_datetime.date()
        #tzinfo = self.earliest_datetime.tzinfo
        for d in prospective_climate.date_name_features.keys():
            # d = d.replace(tzinfo=tzinfo)
            if earliest_historical_date <= d <= latest_historical_date:
                prospective_dates.append(d)
                for fname in self.feature_names:  # #
                    prospective_name_features[fname].append(prospective_climate.date_name_features[d][fname])  # #

        historical_name_features: list[float] = {vname: list() for vname in self.feature_names}
        historical_dates: list[datetime] = list()
        print('Processing data for actual and prospective comparisons')
        tic: float = tm.time()

        for d in prospective_dates:
            dt: datetime = datetime.combine(d, time(hour=0))
            for site in self.sites:
                site_datetimes: list[datetime] = set(site.datetimes)
                # print(site_datetimes[0].tzinfo, '<=', dt.tzinfo, '<=', site_datetimes[-1].tzinfo)
                dt = dt.replace(tzinfo=site.datetimes[0].tzinfo)
                if dt in site_datetimes:
                    valid = False
                    for fname in self.feature_names:
                        merger: Merger = self.feature_name_mergers[fname]
                        variable_values: list[float] = self.site_date_variable_values[site][d][merger.variable_name]
                        if len(variable_values) > 0:
                            merger_feature_value: float = merger(variable_values)
                            feature_name_errors[fname].append(abs(merger_feature_value - prospective_climate.date_name_features[d][fname]))
                            valid = True
                            historical_name_features[fname].append(merger_feature_value)
                    if valid:
                        historical_dates.append(d)
                    break
                else:
                    continue
            continue
        print(tm.time()-tic, ' seconds')
        # for fname in self.feature_names:
        #     print('Feature error on %s (%s)' % (fname, prospective_climate.feature_units[fname]))
        #     print(feature_name_errors)
        #     print(type(feature_name_errors))
        #     print('Feature error on %s (%s) = %f' % (fname, prospective_climate.feature_units[fname], mean(feature_name_errors[fname])))
        print('Generating plots')
        for fname in self.feature_names:
            fig = go.Figure(layout=go.Layout(title='actual prospective plot'))
            fig.add_trace(go.Scatter(x=prospective_dates, y=prospective_name_features[fname], mode='lines', name='prospective_%s' % fname))
            fig.add_trace(go.Scatter(x=historical_dates, y=historical_name_features[fname], mode='lines', name='historical_%s' % fname))
            fig.show()

    def __str__(self) -> str:
        string = "The historical database contains:\n"
        for site in self.sites:
            dates = list(self.site_date_datetimes[site].keys())
            string += "- %i days from %s to %s located at %s" % (len(self.site_date_datetimes[site]), date_to_stringdate(dates[0]), date_to_stringdate(dates[-1]), site.location)
        return string


class ProspectiveClimateDRIAS:
    "See https://www.drias-climat.fr/commande Données corrigées DRIAS-2020 2006-2100"

    def __init__(self, filename: str, starting_stringdate: str = None, ending_stringdate: str = None, separators: tuple[str] = (';', ' ', '\t', ',',)):
        self.data_to_feature_names: dict[str, str] = {'Date': 'date', 'Latitude': 'latitude', 'Longitude': 'longitude', 'tasAdjust': 'temperature', 'tasminAdjust': 'temperature_min', 'tasmaxAdjust': 'temperature_max', 'prtotAdjust': 'precipitation_mass', 'prsnAdjust': 'snowfall_mass', 'hussAdjust': 'absolute_humidity', 'rsdsAdjust': 'direct_normal_irradiance_instant', 'sfcWindAdjust': 'wind_speed_m_per_s'}  # 'rldsAdjust': 'infrared',
        self.model_name: str = filename.rsplit('.', 1)[0]
        self.starting_date, self.ending_date = None, None
        if starting_stringdate is not None:
            self.starting_date = stringdate_to_date(starting_stringdate)
        if ending_stringdate is not None:
            self.ending_date = stringdate_to_date(ending_stringdate)
        self.gps = None
        self.date_name_features:  dict[date, dict[str, list[float]]] = dict()

        separators = '|'.join(separators)
        self.feature_descriptions: dict[str, str] = {'date': 'format DD/MM/YYYY', 'latitude': 'latitude in decimal degree north', 'longitude': 'longitude in decimal degree west'}
        self.feature_names = list()
        self.feature_units: dict[str, float] = dict()
        self.dates = list()

        print('loading prospective climate change data from', config['folders']['data'] + filename)
        tic: float = tm.time()

        feature_name_missing_data_value: dict[str, float] = dict()
        flag = True
        row_counter = 0
        with open(config['folders']['data'] + filename, "r") as datafile:
            rows: list[str] = datafile.readlines()
            while row_counter < len(rows):
                row: str = rows[row_counter]

                if row[0:1] == '#' and re.search('^#\\s', row):  # ------------------- read drias feature file header
                    if not re.search('^#\\s-+', row[0:-1]):
                        period_match = re.search("^#\\sPeriode\\s:\\s([0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4})\\s-\\s([0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4})", row)
                        parameter_match = re.search("^#\\sParametre\\s(\\d)\\s:\\s(.+)$", row[0:-1])
                        format_match = re.search('^#\\sFormat\\sde\\sla\\sligne\\s:', row[0:-1])

                        if period_match:
                            _starting_stringdate, _ending_stringdate = period_match.groups()
                            print('DRTAS prospective climate model for %s from %s to %s' % (self.model_name, _starting_stringdate, _ending_stringdate))

                        if parameter_match:
                            feature_id, feature_description = parameter_match.groups()
                            feature_id = int(feature_id)
                            row_counter += 1

                            mnemonic_match = re.search("^#\\sMnemonique\\s%i\\s:\\s(.+)$" % feature_id, rows[row_counter][0:-1])
                            drias_name = mnemonic_match.groups()[0]
                            if drias_name in self.data_to_feature_names:
                                feature_name = self.data_to_feature_names[drias_name]
                            else:
                                feature_name = drias_name
                            self.feature_names.append(feature_name)
                            self.feature_descriptions[feature_name] = feature_description

                            row_counter += 1
                            unit_match = re.search("^#\\sUnite\\s%i\\s:\\s(.+)$" % feature_id, rows[row_counter][0:-1])
                            unit = unit_match.groups()[0]
                            if unit == 'K':
                                unit = '°C'
                            if drias_name in self.data_to_feature_names:
                                self.feature_units[self.data_to_feature_names[drias_name]] = unit
                            else:
                                self.feature_units[drias_name] = unit

                            row_counter += 1
                            missing_match = re.search("^#\\sValeur\\sdu\\sparametre\\smanquant\\s%i\\s:\\s(-?\\d+.?\\d+)$" % feature_id, rows[row_counter][0:-1])
                            feature_name_missing_data_value[feature_name] = missing_match.groups()[0]

                        if format_match:
                            row_counter += 1
                        else:
                            print(row[2:-1])
                else:  # ########################################## read drias file payload i.e. the feature data
                    if flag:
                        flag = False
                    a_date = None
                    data_values: list[str] = re.split(separators, row)

                    latitude, longitude = None, None
                    feature_values = dict()
                    data_names = tuple(self.feature_descriptions.keys())
                    for i in range(len(data_names)):
                        if data_names[i] == 'date':
                            a_date: date = stringdate_to_date(data_values[i], date_format='%Y%m%d')
                            if self.starting_date is None:
                                self.starting_date: date = a_date
                        elif data_names[i] == 'latitude':
                            latitude = float(data_values[i])
                        elif data_names[i] == 'longitude':
                            longitude = float(data_values[i])
                            if self.gps is not None and self.gps != (latitude, longitude):
                                raise ValueError("Only one GPS location can be proceed per run")
                            self.gps: tuple[float, float] = (latitude, longitude)
                        else:
                            if data_names[i] not in self.data_to_feature_names:
                                data_value = float(data_values[i])
                                if data_value == feature_name_missing_data_value[data_names[i]]:
                                    data_value = float('nan')
                                if self.feature_units[data_names[i]] == '°C':
                                    data_value: float = data_value - 273.15
                                feature_values[data_names[i]] = data_value
                                if i == len(data_names) - 1:
                                    if self.starting_date is not None and a_date >= self.starting_date:
                                        self.date_name_features[a_date] = feature_values
                    if self.ending_date is not None and a_date >= self.ending_date:
                        break
                row_counter += 1
            if self.ending_date is None:
                self.ending_date: date = a_date
            self.dates = tuple(self.date_name_features.keys())
        print('DRIAS2100 data loaded')
        print(tm.time() - tic, 'seconds')

    def __call__(self, a_date: date, feature_name: str = None) -> dict[date, dict[str, list[float]]] | dict[str, list[float]]:
        if feature_name is not None:
            return self.date_name_features[a_date][feature_name]
        else:
            return self.date_name_features[a_date]

    @property
    def starting_stringdate(self) -> str:
        return date_to_stringdate(self.starting_date)

    @property
    def ending_stringdate(self):
        return date_to_stringdate(self.ending_date)

    def __str__(self) -> str:
        return 'Prospective climate data (%s -> %s) from file "%s" containing the following features: \n- ' % (date_to_stringdate(self.starting_date), date_to_stringdate(self.ending_date), self.model_name) + '\n- '.join(self.feature_names) + '\nfor gps location: (LAT:%f, LON:%f)' % (self.gps[0], self.gps[1])


class ProspectiveClimateRefiner:

    def __init__(self, prospective_climate: ProspectiveClimateDRIAS, historical_database: HistoricalDatabase, the_timezone: str = "Europe/Paris") -> None:
        if not os.path.isdir(config['folders']['data']):
            os.mkdir(config['folders']['data'])
        france_tz = timezone(the_timezone)
        self.historical_database = historical_database
        self.prospective_climate = prospective_climate
        self.dates: list[date] = prospective_climate.dates
        self._datetimes: list[datetime] = list()
        self.date_datetimes: dict[date, list[datetime]] = dict()

        initial_datetime = france_tz.localize(datetime.combine(self.dates[0], time(hour=0)))
        final_datetime: datetime = france_tz.localize(datetime.combine(self.dates[-1] + timedelta(days=1), time(hour=0)))
        dt: datetime = initial_datetime
        while dt < final_datetime:
            self._datetimes.append(dt)
            d = dt.date()
            if d not in self.date_datetimes:
                self.date_datetimes[d] = list()
            self.date_datetimes[d].append(dt)
            dt += timedelta(hours=1)
        for d in self.date_datetimes:
            if len(self.date_datetimes[d]) != 24:
                print(d, len(self.date_datetimes[d]))

        feature_merger_weights: dict[Merger, float] = historical_database.feature_merger_weights
        self.feature_mergers = tuple(feature_merger_weights.keys())
        total: float = sum([feature_merger_weights[merger] for merger in feature_merger_weights])
        self.feature_weights: dict[str, float] = {merger.feature_name: feature_merger_weights[merger]/total for merger in feature_merger_weights}
        str_weights = "-".join([str(self.feature_weights[f]) for f in self.feature_weights],)
        parameters: str = ''
        for site in self.historical_database.sites:
            parameters += site.location + site.from_stringdate + site.to_stringdate
        parameters += self.prospective_climate.starting_stringdate + self.prospective_climate.ending_stringdate + str_weights

        data_model_file_name: str = config['folders']['data'] + self.prospective_climate.model_name + '_%i' % int(shake_128(parameters.encode('utf-8')).hexdigest(8), 16) + '.pickle'
        self.prospective_climate: ProspectiveClimateDRIAS = prospective_climate
        self.historical_database: HistoricalDatabase = historical_database
        historical_diy_features_variables: list[tuple[int, dict[str, float], dict[str, float]]] = self.historical_database.diy_features_variables

        if os.path.exists(data_model_file_name):
            print('loading', data_model_file_name)
            with open(data_model_file_name, 'rb') as file:
                data = pickle.load(file)
                self._day_shifts = data['day_shifts']
                self._errors = data['errors']
                self._variable_values = data['hourly_variable_values']
                self._feature_values = data['hourly_feature_values']
                self._feature_normalized_values = data['hourly_feature_normalized_values']
        else:
            self._day_shifts: list[int] = list()
            self._errors: list[float] = list()
            self._variable_values: dict[str, list[float]] = {v: list() for v in self.historical_database.variable_names}
            self._feature_values: dict[str, list[float]] = {v: list() for v in self.historical_database.feature_names}
            self._feature_normalized_values: dict[str, list[float]] = {v: list() for v in self.historical_database.feature_names}
            print('Searching for best matches in the historical database')
            tic: float = tm.time()
            for i, d in enumerate(self.date_datetimes):
                if i % 10 == 0:
                    print('.', end='')
                prospective_features: dict[str, float] = self.prospective_climate(a_date=d)
                normalized_prospective_features: dict[str, float] = self.historical_database.normalize(self.prospective_climate(a_date=d))
                errors: list[float] = [sum([self.feature_weights[fname]*abs(historical_diy_features_variables[_][1][fname]-normalized_prospective_features[fname]) for fname in self._feature_normalized_values]) for _ in range(len(historical_diy_features_variables))] * len(self.date_datetimes[d])
                min_error: float = min(errors)  # [min(errors)] * len(self.date_datetimes[d])
                i: int = errors.index(min_error)
                self._errors.extend([min_error] * len(self.date_datetimes[d]))

                diy, features, variables = historical_diy_features_variables[i]
                self._day_shifts.extend([min(abs(diy-d.timetuple().tm_yday), 366-abs(diy-d.timetuple().tm_yday))] * len(self.date_datetimes[d]))
                for v in self.historical_database.variable_names:
                    self._variable_values[v].extend(variables[v])
                for fname in self.historical_database.feature_names:
                    self._feature_values[fname].extend([prospective_features[fname]] * len(self.date_datetimes[d]))
                    self._feature_normalized_values[fname].extend([normalized_prospective_features[fname]] * len(self.date_datetimes[d]))
                data = {'day_shifts': self._day_shifts, 'errors': self._errors, 'hourly_variable_values': self._variable_values, 'hourly_feature_values': self._feature_values, 'hourly_feature_normalized_values': self._feature_normalized_values}
            print('\n', round(tm.time() - tic, 0), 'seconds')
            print()
            print('\nsaving', data_model_file_name)
            with open(data_model_file_name, 'wb') as file:
                pickle.dump(data, file)

    @property
    def datetimes(self) -> list[datetime]:
        return self._datetimes

    @property
    def day_shifts(self) -> list[int]:
        return self._day_shifts

    @property
    def errors_percent(self) -> list[float]:
        return [err*100 for err in self._errors]

    @property
    def variable_values(self) -> dict[str, list[float]]:
        return self._variable_values

    @property
    def variable_units(self) -> dict[str, str]:
        return self.historical_database.site_weather_data.variable_units

    @property
    def feature_values(self) -> dict[str, list[float]]:
        return {"feat_"+fname: self._feature_values[fname] for fname in self._feature_values}

    @property
    def feature_normalized_values(self) -> dict[str, list[float]]:
        return {"nfeat_"+fname: self._feature_normalized_values[fname] for fname in self._feature_normalized_values}

    def make_prospective_site_weather_data(self, location: str, albedo=0.1, pollution=0.1, timezone="Europe/Paris") -> SiteWeatherData:
        print('making a site_weather_data container')
        site_weather_data = SiteWeatherData(location, self.prospective_climate.gps[0], self.prospective_climate.gps[1], albedo, pollution, timezone, _direct_call=False)
        site_weather_data.datetimes = self.datetimes
        for v in self.variable_values:
            site_weather_data.add_variable(v, self.historical_database.site_weather_data.units(v), self.variable_values[v])
        site_weather_data.origin = "openmeteo"
        return site_weather_data

    def plot(self) -> None:
        data = {'errors_percent': self.errors_percent, 'day_shifts': self.day_shifts}
        data |= self.variable_values
        data |= self.feature_values
        TimeSeriesPlotter(data, self.datetimes, self.variable_units)

    def actual_prospective_plot(self) -> None:
        actual_datetimes: list[datetime] = self.historical_database.site_weather_data.datetimes
        actual_data: dict[str, list[float]] = {v: self.historical_database.site_weather_data(v) for v in self.historical_database.feature_variable_names}
        fig = go.Figure(layout=go.Layout(title='actual prospective plot'))
        for v in actual_data:
            fig.add_trace(go.Scatter(x=actual_datetimes, y=actual_data[v], mode='lines', name='actual_%s' % v))
        for v in self.historical_database.feature_variable_names:
            fig.add_trace(go.Scatter(x=self.datetimes, y=self.variable_values[v], mode='lines', name='prospective_%s' % v))
        fig.show()
