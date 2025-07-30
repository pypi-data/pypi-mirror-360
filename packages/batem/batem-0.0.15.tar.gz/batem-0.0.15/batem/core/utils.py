"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0
"""
from __future__ import annotations
import os
import os.path
import ipywidgets
from random import uniform
import configparser
from IPython.display import display
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, datetime, time
from tkinter import ttk
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express
from batem.core.timemg import TimeSeriesMerger
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.exceptions import ConvergenceWarning
import warnings

# Suppress ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)

config = configparser.ConfigParser()
config.read('setup.ini')


class FilePathChecker:
    def __init__(self) -> None:
        pass

    def is_file_exists(self, file_path: str) -> bool:
        return os.path.isfile(file_path)

    def is_folder_exists(self, folder_path: str) -> bool:
        return os.path.isdir(folder_path)


class FilePathBuilder:
    def __init__(self) -> None:
        pass

    def get_data_folder(self, folder_name: str = 'data') -> str:
        """Get the data folder path. If it does not exist, create it.

        :return: the data folder path
        :rtype: str
        """
        path = config['folders'][folder_name]
        if not FilePathChecker().is_folder_exists(path):
            os.mkdir(path)
        return path

    def get_localizations_file_path(self) -> str:
        """Get the localizations file path.

        :return: the localizations file path
        :rtype: str
        """
        return self.get_data_folder() + 'localizations.json'

    def get_weather_file_path(
            self, location: str) -> str:
        """Get the weather file path as a json file.

        :return: the weather file path
        :rtype: str
        """
        file_path = os.path.join(self.get_data_folder(), location + '.json')
        return file_path


def in_jupyter() -> bool:
    """Determine whether the code is executed as Python code or in Jupyter

    :return: True is executed in Jupyter, False otherwise.
    :rtype: bool
    """
    from IPython import get_ipython
    if get_ipython().__class__.__name__ != 'NoneType':
        return True
    return False


if in_jupyter():
    plotly.offline.init_notebook_mode()
    # from plotly.offline import iplot
else:
    import plotly.io as pio
    pio.renderers.default = 'browser'

    # import matplotlib
    # matplotlib.use('tkagg')
    # from matplotlib.backends.backend_tkagg import *  # noqa
    import tkinter as tk


def mkdir_if_not_exist(path_name: str) -> str:
    sub_folders: list[str] = path_name.split()
    if not path_name.endswith('/'):
        sub_folders = sub_folders[0:-1]
    folder_under_construction = ''
    for i in range(len(sub_folders)):
        folder_under_construction += sub_folders[i] + '/'
        if not os.path.isdir(folder_under_construction):
            os.mkdir(folder_under_construction)
            print("make dir:", folder_under_construction)
    return path_name


def day_averager(datetimes: list[datetime.datetime], vector: list[float], average=True):
    """Compute the average or integration hour-time data to get day data.

    :param average: True to compute an average, False for integration
    :type average: bool
    :param vector: vector of values to be down-sampled
    :return: list of floating numbers
    """
    current_day: int = datetimes[0].day
    day_integrated_vector = list()
    values = list()
    for k in range(len(datetimes)):
        if current_day == datetimes[k].day:
            values.append(vector[k])
        else:
            average_value = sum(values)
            if average:
                average_value = average_value/len(values)
            day_integrated_vector.append(average_value)
            values = list()
        current_day = datetimes[k].day
    return day_integrated_vector


class Averager:

    def __init__(self, values: list[float]) -> None:
        """An averager average a series of values provided at the initialization.
        2 kinds of averaged can be computed: an average computed on a sliding window or
        an average computed on day or month period.

        :param values: the series of values to be averaged
        :type values: list[float]
        """
        self._values: list[float] = values

    def average(self, horizon: int) -> list[float]:
        """compute the average of a series of values considering only the past values of the
        value to be averaged if they exist. If not, the average is computed on the available
        pas horizon

        :param horizon: _description_
        :type horizon: int
        :raises ValueError: _description_
        :return: _description_
        :rtype: list[float]
        """
        _avg_values: list[float] = list()
        for i in range(len(self._values)):
            i_min, i_max = max(0, i - horizon), i
            if i_max > i_min:
                _avg_values.append(
                    sum(self._values[i_min:i_max]) / (i_max - i_min))
            else:
                _avg_values.append(self._values[i])
        return _avg_values

    def day_month_average(self, datetimes: list[datetime], month: bool = False, sum_up: bool = False) -> tuple[list[float], list[int]]:
        """compute the sum or the average value of the current time series group by day or by month

        :param datetimes: the datetimes corresponding to the current time series
        :type datetimes: list[datetime]
        :param month: group by day if True or month otherwise, defaults to False
        :type month: bool, optional
        :param sum_up: compute,the,sum if True or the average otherwise, defaults to False
        :type sum_up: bool, optional
        :return: list of averages-d or summed values, repeated during the same type of period
        :rtype: tuple[list[float], list[int]]
        """
        current_period: int = -1
        accumulator: list[float] = list()
        _periods: list[int] = list()
        _avg_values: list[float] = list()
        for k, dt in enumerate(datetimes):
            if current_period == -1:  # initialization
                current_period = dt.day if not month else dt.month
                accumulator.append(self._values[k])
            else:
                if (not month and dt.day == current_period) or (month and dt.month == current_period):
                    accumulator.append(self._values[k])  # accumulating
                else:
                    if sum_up:
                        avg: float = sum(accumulator)
                    else:
                        avg: float = sum(accumulator) / len(accumulator)
                    _periods.extend(
                        [current_period for _ in range(len(accumulator))])
                    _avg_values.extend([avg for _ in range(len(accumulator))])
                    current_period = dt.day if not month else dt.month
                    accumulator = [self._values[k]]
        if sum_up:
            avg: float = sum(accumulator)
        else:
            avg: float = sum(accumulator) / len(accumulator)
        _periods.extend([current_period for _ in range(len(accumulator))])
        _avg_values.extend([avg for _ in range(len(accumulator))])
        return _avg_values, _periods

    def inertia_filter(self, num: list[float] = [0.019686971644799107, 0.014954617818522536, -0.02795458838964217], den: list[float] = [1, -1.393950, 0.400637], initial_values: list[float] = None) -> list[float]:
        """A realistic transfer function to represent standard inertia

        :param num: _description_, defaults to [0.019686971644799107, 0.014954617818522536, -0.02795458838964217]
        :type num: list[float], optional
        :param den: _description_, defaults to [1, -1.393950, 0.400637]
        :type den: list[float], optional
        :param initial_values: _description_, defaults to None
        :type initial_values: list[float], optional
        :return: _description_
        :rtype: list[float]
        """
        init: int = max(len(num), len(den))
        coef0: float = den[0]
        den = [- den[i] / coef0 for i in range(1, init)]
        num = [v / coef0 for v in num]
        if initial_values is None:
            _avg_values: list[float] = [self._values[k] for k in range(init)]
        else:
            _avg_values: list[float] = [initial_values[k] for k in range(init)]
        for k in range(init, len(self._values)):
            val = 0
            for i in range(len(den)):
                val += den[i] * _avg_values[k-i-1]
            for i in range(len(num)):
                val += num[i] * self._values[k-i]
            _avg_values.append(val)
        return _avg_values


def range_distance(range_1: tuple[float, float], range_2: tuple[float, float]) -> float:
    """Calculate distance between two ranges based on overlap."""
    width_1 = range_1[1] - range_1[0]
    width_2 = range_2[1] - range_2[0]
    range_1_2 = (min(range_1[0], range_2[0]), max(range_1[1], range_2[1]))
    width_1_2 = range_1_2[1] - range_1_2[0]
    if width_1_2 != 0:
        return 1 - max((width_1 / width_1_2, width_2 / width_1_2))
    else:
        return 0


def auto_kmeans(X, kmin=2, kmax=10, metric=range_distance, random_state=0, sensitivity=0):
    # Handle edge case: if X has fewer than 2 elements, return single cluster
    if len(X) < 2:
        return np.zeros(len(X), dtype=int), 1

    # Adjust kmax to not exceed the number of data points
    kmax = min(kmax, len(X))

    # If kmax < kmin after adjustment, set kmin to kmax
    if kmax < kmin:
        kmin = kmax

    best_k = kmin
    best_score = -1
    best_labels = None

    # Precompute pairwise distances (needed for custom metric)
    D = pairwise_distances(X, metric=metric)
    
    if np.max(D) == 0:
        return np.zeros(len(X), dtype=int), 1
    
    for k in range(kmin, kmax + 1):
        # Skip if k is greater than the number of data points
        if k > len(X):
            continue

        model = KMeans(init='k-means++', n_clusters=k,
                       random_state=random_state, n_init='auto').fit(X)
        labels = model.labels_

        # Silhouette score with precomputed distance matrix
        if len(set(labels)) < 2:
            continue  # silhouette score not defined for one cluster

        # For very small datasets, silhouette score might fail
        try:
            score = silhouette_score(D, labels, metric='precomputed')
        except ValueError:
            # If silhouette score fails, use a simple distance-based score
            if len(set(labels)) == 2:
                # For 2 clusters, use the distance between cluster centers
                cluster_centers = []
                for cluster_id in set(labels):
                    cluster_points = X[labels == cluster_id]
                    if len(cluster_points) > 0:
                        cluster_centers.append(np.mean(cluster_points, axis=0))
                if len(cluster_centers) == 2:
                    score = np.linalg.norm(
                        cluster_centers[0] - cluster_centers[1])
                else:
                    score = 0
            else:
                score = 0

        if score > best_score - sensitivity:
            best_score = score
            best_k = k
            best_labels = labels

    return best_labels, best_k


def cluster_variables(variable_data: dict[str, list[float]], max_k: int = 6) -> list[list[str]]:
    matrix = []
    for v in variable_data:
        matrix.append(
            (np.nanmin(variable_data[v]), np.nanmax(variable_data[v])))
    variable_names = list(variable_data.keys())
    X = np.array(matrix)
    labels, k_found = auto_kmeans(X, kmin=1, kmax=max_k, metric=range_distance)
    clustered_variables = []
    for i in range(np.max(labels)+1):
        indices = np.where(labels == i)[0].tolist()
        clustered_variables.append([variable_names[j] for j in indices])
    return clustered_variables


class TimeSeriesPlotter:

    def __init__(self, variable_values: dict[str, list[float]], datetimes: list[datetime] | list[date] = None, units: dict[str, str] = dict(), all: bool = False, plot_type: str = None, averager: str = None, title: str = '') -> None:
        self._variable_names = list()
        self._datetimes = datetimes
        self._variable_min_max: dict[tuple[float, float]] = dict()
        self._variable_values: dict[str, list[float]] = dict()
        self._units: dict[str, str] = units
        averager_types: list[str] = ['- hour', 'avg day', 'avg week', 'avg month', 'avg year', 'sum day', 'sum week',
                                     'sum month', 'sum year', 'max day', 'max week', 'max month', 'max year', 'min day', 'min week', 'min month', 'min year']
        self._all: bool = all
        self._plot_type: str = plot_type
        self._averager: str = averager
        self._title: str = title

        number_of_values: int = None
        for variable_name in variable_values:
            if variable_name != 'datetime' and variable_name != 'epochtimems' and variable_name != 'stringdate':
                is_all_none: bool = False
                for v in variable_values[variable_name]:
                    is_all_none = is_all_none or (v is None)
                if not is_all_none:
                    self._variable_values[variable_name] = variable_values[variable_name]
                    self._variable_min_max[variable_name] = self.minmax(
                        [variable_name])
                    self._variable_names.append(variable_name)
            elif variable_name == 'datetime' and self._datetimes is None:
                self._datetimes = datetimes
            if number_of_values is None:
                number_of_values = len(variable_values[variable_name])
            elif number_of_values != len(variable_values[variable_name]):
                raise ValueError('Variable %s has not the right size (%i instead of %i)' % (
                    variable_name, len(variable_values[variable_name]), number_of_values))
        if self._datetimes is None:
            raise ValueError('datetimes must be provided')
        if len(self._datetimes) != number_of_values:
            raise ValueError('datetimes do not match data time series (%i values instead of %i)' % (
                len(self._datetimes), number_of_values))
        if type(datetimes[0]) is date:
            self._datetimes: list[datetime] = [
                datetime.combine(d, time()) for d in datetimes]
        self.output = ipywidgets.Output()
        if self._all:
            for i, variable_name in enumerate(self._variable_names):
                displayed_variable_name = variable_name
                if variable_name in self._units:
                    displayed_variable_name += ' in %s' % self._units[variable_name]
            selected_variable_values: dict[str,
                                           list[float]] = self._variable_values
            print('Averager: %s' % self._averager)
            for selected_variable_name in self._variable_values:
                operation, period = self._averager.split()
                selected_variable_values[selected_variable_name] = TimeSeriesMerger(
                    self._datetimes, values=self._variable_values[selected_variable_name], group_by=period)(operation)
            if self._plot_type == 'heatmap':
                self._plot_heatmap()
            else:
                self._plot_time_series()
        elif not in_jupyter():  # tkinter selector
            root_window = tk.Tk()
            self.tk_int_vars: list[tk.IntVar] = [
                tk.IntVar(root_window, value=0) for variable_name in self._variable_names]
            self.tk_averager_var = tk.StringVar(
                root_window, value=averager if averager is not None else '- hour')
            root_window.title('variable plotter')
            root_window.protocol("WM_DELETE_WINDOW", exit)
            control_frame = ttk.Frame(root_window)
            control_frame.grid(row=0, column=0, sticky="nw")
            timeplot_button = ttk.Button(
                control_frame, text='timeplot', command=self._plot_time_series)
            timeplot_button.grid(row=0, column=0, sticky="wn")
            heatmap_button = ttk.Button(
                control_frame, text='heatmap', command=self._plot_heatmap)
            heatmap_button.grid(row=0, column=1, sticky="wn")
            if self._plot_type == 'timeplot':
                heatmap_button.config(state="disabled")
            if self._plot_type == 'heatmap':
                timeplot_button.config(state="disabled")
            averager_combo = ttk.Combobox(
                control_frame, textvariable=self.tk_averager_var, values=averager_types)
            averager_combo.grid(row=0, column=2, sticky="wn", pady=4)
            if averager is not None:
                averager_combo.config(state="disabled")
            selection_frame = ttk.Frame(root_window)
            selection_frame.grid(row=1, column=0, sticky="nswe")
            # Configure the grid to expand the frame
            root_window.grid_columnconfigure(0, weight=1)
            root_window.grid_rowconfigure(1, weight=1)
            selection_canvas = tk.Canvas(selection_frame)
            selection_canvas.grid(row=0, column=0, sticky="wns")
            scrollbar = ttk.Scrollbar(
                selection_frame, orient="vertical", command=selection_canvas.yview)
            scrollbar.grid(row=0, column=1, sticky="wns")
            selection_canvas.configure(yscrollcommand=scrollbar.set)
            # Configure the frame to expand with the canvas
            selection_frame.grid_columnconfigure(0, weight=1)
            selection_frame.grid_rowconfigure(0, weight=1)
            selection_canvas.bind("<Configure>", lambda event: selection_canvas.configure(
                scrollregion=selection_canvas.bbox("all")))
            # Create a frame inside the canvas for the widgets
            checkboxes_frame = ttk.Frame(selection_canvas)
            selection_canvas.create_window(
                (0, 0), window=checkboxes_frame, anchor="n")
            for i, variable_name in enumerate(self._variable_names):
                tk_int_var = tk.IntVar(root_window, value=0)
                self.tk_int_vars.append(tk_int_var)
                displayed_variable_name = variable_name
                if variable_name in self._units:
                    displayed_variable_name += ' in %s' % self._units[variable_name]
                ttk.Checkbutton(checkboxes_frame, text=displayed_variable_name,
                                variable=self.tk_int_vars[i], offvalue=0).grid(row=i, column=0, sticky="w")
            checkboxes_frame.update_idletasks()
            root_window.maxsize(root_window.winfo_width(),
                                root_window.winfo_screenheight())
            root_window.geometry(
                str(root_window.winfo_width()) + "x" + str(root_window.winfo_screenheight()))
            root_window.mainloop()
        else:  # in jupyter
            self.variable_selector = ipywidgets.SelectMultiple(
                options=[variable_name for variable_name in self._variable_names], description='Variables', disable=False)
            if averager is None:
                self._averager_selector = ipywidgets.Select(
                    value='- hour', options=averager_types, disabled=False, description='Averager')
            else:
                self._averager_selector = ipywidgets.Select(
                    value=averager, options=averager_types, disabled=True, description='Averager')

            timeplot_button, heatmap_button = None, None
            if self._plot_type == 'timeplot':  # timeplot
                timeplot_button = ipywidgets.Button(description='timeplot')
                heatmap_button = ipywidgets.Button(
                    description='heatmap', disabled=True)
            if self._plot_type == 'heatmap':
                timeplot_button = ipywidgets.Button(
                    description='timeplot', disabled=True)
                heatmap_button = ipywidgets.Button(description='heatmap')
            else:  # both
                timeplot_button = ipywidgets.Button(description='timeplot')
                heatmap_button = ipywidgets.Button(description='heatmap')

            button_box = ipywidgets.VBox([timeplot_button, heatmap_button])
            control_box = ipywidgets.HBox(
                [self.variable_selector, self._averager_selector, button_box])
            main_box = ipywidgets.VBox([control_box, self.output])
            display(main_box)

            def on_timeplot_button_clicked(timeplot_button):
                print('Timeplot coming...')
                self.output.clear_output()
                with self.output:
                    self._plot_time_series()
                self.variable_selector.value = ()
            timeplot_button.on_click(on_timeplot_button_clicked)

            def on_heatmap_button_clicked(heatmap_button):
                print('Heatmap coming...')
                self.output.clear_output()
                with self.output:
                    self._plot_heatmap()
                self.variable_selector.value = ()
            heatmap_button.on_click(on_heatmap_button_clicked)

    def minmax(self, variables: list[str]) -> tuple[float, float]:
        if len(variables) == 0:
            raise ValueError('No variables provided')
        min_value: float = min(
            min(self._variable_values[v]) for v in variables)
        max_value: float = max(
            max(self._variable_values[v]) for v in variables)
        return (min_value, max_value)

    def _plot_heatmap(self) -> None:
        """Versatile method for plotting registered known variables. it detests and adapt the way of plotting to the current context: invoked from Python or from Jupyter. It can plot a heatmap or curves and if variables to be plotted are given, the plot is displayed without opening the selector of variables.

        :param heatmap: True for a heatmap and False for regular curves, defaults to False
        :type heatmap: bool, optional
        """
        selected_variable_values: dict[str, list[float]
                                       ] = self._get_selected_variable_values()
        normalized_values: list[list[float]] = list()
        displayed_variable_names: list[str] = list()
        for variable_name in selected_variable_values:
            normalized_values.append([100*(selected_variable_values[variable_name][j]-self._variable_min_max[variable_name][0]) / (self._variable_min_max[variable_name][1] - self._variable_min_max[variable_name]
                                     [0]) if self._variable_min_max[variable_name][1] != self._variable_min_max[variable_name][0] else 0 for j in range(len(selected_variable_values[variable_name]))])
            displayed_variable_name = '%s (%g→%g' % (
                variable_name, self._variable_min_max[variable_name][0], self._variable_min_max[variable_name][1])
            if variable_name in self._units:
                displayed_variable_name += self._units[variable_name] + ')'
            displayed_variable_names.append(displayed_variable_name)
        if len(normalized_values) > 0:
            fig = plotly.express.imshow(normalized_values, labels=dict(x="time", y='%s Averager: %s' % (self._title, self._averager),
                                        color="min/max normalization"), x=self._datetimes, y=displayed_variable_names, height=1000)
            fig.layout.coloraxis.showscale = True
            fig.update_xaxes(side="top")
            fig.show()

    def _plot_time_series(self) -> None:
        """Use to plot curve using plotly library

        :param int_vars: reference to the variable to be plotted
        :type: list[int]
        """
        selected_variable_values: dict[str, list[float]] = self._get_selected_variable_values()
        variable_groups = cluster_variables(selected_variable_values, max_k=4)

        if len(variable_groups) > 0:
            fig = make_subplots(rows=len(variable_groups), cols=1, shared_xaxes=True,
                                y_title='%s Averager: %s' % (self._title, self._averager))
            for i, group in enumerate(variable_groups):
                for group_variable in group:
                    displayed_variable_name: str = group_variable
                    if group_variable in self._units:
                        displayed_variable_name += ' in %s' % (
                            self._units[group_variable],)
                    displayed_variable_name += ' (disp:%i)' % (i+1,)
                    fig.add_trace(go.Scatter(x=self._datetimes, y=selected_variable_values[group_variable],
                                  name=displayed_variable_name, showlegend=True, line_shape='hv'), row=1+i, col=1)
            fig.show()

    def _get_selected_variable_values(self) -> dict[str, list[float]]:
        if self._all:
            return self._variable_values
        selected_variable_values: dict[str, list[float]] = dict()
        if in_jupyter():  # in jupyter
            print('Averager: %s' % self._averager_selector.value)
            selected_variable_names = self.variable_selector.value
            operation, period = self._averager_selector.value.split()
        else:
            selected_variable_names = list()
            for i in range(len(self.tk_int_vars)):
                if self.tk_int_vars[i].get():
                    selected_variable_names.append(self._variable_names[i])
                    operation, period = self.tk_averager_var.get().split()
                self.tk_int_vars[i].set(0)
        for selected_variable_name in selected_variable_names:
            if operation == '-' or period == 'hour':
                selected_variable_values[selected_variable_name] = self._variable_values[selected_variable_name]
            else:
                selected_variable_values[selected_variable_name] = TimeSeriesMerger(
                    self._datetimes, values=self._variable_values[selected_variable_name], group_by=period)(operation)

        return selected_variable_values

    # def same_group(self, group_variables: list[str], variable: str) -> bool:
    #     rho_comparability: float = 5
    #     min_group_original, max_group_original = self.minmax(group_variables)
    #     min_variable, max_variable = self.minmax([variable])
    #     min_group_final, max_group_final = self.minmax(group_variables + [variable])
    #     score: float = (max_group_original - min_group_original) - (max_group_final - min_group_final)
    #     if (max_group_final - min_group_final) > (max_group_original - min_group_original) * rho_comparability:
    #         return False, score
    #     elif max_group_final - min_group_final > (max_variable - min_variable) * rho_comparability:
    #         return False, score
    #     return True, score


class PlotSaver:
    """This class directly saves a figure containing regular curves into a png file.
    """

    def __init__(self, datetimes: list[datetime], data: dict[str, list[float]]) -> None:
        """Initialize the saver with an independent variable set

        :param datetimes: the list of datetimes
        :type datetimes: list[datetime]
        :param data: the dictionary with variable names as keys and their values as lists of floats
        :type data: dict[str, list[float]]
        """
        self.datetimes: list[datetime] = datetimes
        self.data: dict[str, list[float]] = data
        self.starting_stringdatetime: str = datetimes[0].strftime(
            '%d/%m/%Y %H:%M')
        self.ending_stringdatetime: str = datetimes[-1].strftime(
            '%d/%m/%Y %H:%M')

    def time_plot(self, variable_names: list[str], filename: str) -> None:
        """
        generate and save a time plot
        :param variable_names: names of the variables to be plot
        :type variable_names: list[str]
        :param filename: the file name
        :type filename: str
        """
        styles: tuple[str, str, str, str] = ('-', '--', '-.', ':')
        linewidths = (3.0, 2.5, 2.5, 1.5, 1.0, 0.5, 0.25)
        figure, axes = plt.subplots()
        axes.set_title('from %s to %s' % (
            self.starting_stringdatetime, self.ending_stringdatetime))
        text_legends = list()
        time_data: list[datetime] = self.datetimes
        if len(time_data) > 1:
            sample_time = time_data[-1] - time_data[-2]
            time_data.append(time_data[-1] + sample_time)
        for i in range(len(variable_names)):
            style = styles[i % len(styles)]
            linewidth = linewidths[i // len(styles) % len(linewidths)]
            variable_name: str = variable_names[i]
            variable_data: list[float] = self.data[variable_name]
            if len(time_data) > 1:
                variable_data.append(variable_data[-1])
            axes.step(time_data, variable_data, linewidth=linewidth,
                      linestyle=style, where='post')
            axes.set_xlim([time_data[0], time_data[-1]])
            text_legends.append(variable_names[i])
        axes.legend(text_legends, loc=0)
        axes.xaxis.set_minor_locator(mdates.DayLocator())
        axes.fmt_xdata = mdates.DateFormatter('%d/%m/%Y %H:%M')
        plt.gcf().autofmt_xdate()
        axes.grid(True)
        plt.savefig(filename+'.png')


def monte_carlo(function: callable, precision: float = 0.01, n_draws: int = 10000, **variable_values: dict[str, float | tuple[float, float]]):
    found_values = list()
    for i in range(n_draws):
        name_values: dict[str, float] = dict()
        for v in variable_values:
            variable_value: float = variable_values[v]
            if type(variable_value) is int or type(variable_value) is float:
                name_values[v] = variable_value
            else:
                name_values[v] = uniform(
                    a=variable_value[0], b=variable_value[1])
        PMV: float = function(**name_values)
        if PMV < precision:
            found_values.append(name_values)
    return found_values
