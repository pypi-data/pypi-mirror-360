"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0

This module transform a RC graphical representation into a state space model.
It is also for the easy design of multi-zone buildings.
It models both the thermal behavior and the evolution of the CO2 concentration.
The thermal part is using thermal module
"""
from __future__ import annotations
import enum
from typing import List, Tuple
import matplotlib.pyplot as plt
import networkx
from .statemodel import StateModel
import numpy
import numpy.linalg
import scipy.linalg
from math import pi, sqrt
from typing import Any
import abc
from .library import properties
from .library import ZONE_TYPES, SIDE_TYPES
from .components import Zone, WallSide, LayeredWallSide, BlockWallSide
from .data import DataProvider
import warnings

# Suppress specific warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*overflow.*')
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*invalid value.*')
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*divide by zero.*')


class CAUSALITY(enum.Enum):
    """
    Tags used for labeling causality of a node variable.

    :param enum: input (IN), used to say a variable is known
    :type enum: str
    """
    IN = "IN"
    UNDEF = "-"
    OUT = "OUT"


def concatenate(*lists):
    """ Combine tuples of lists into a single list without duplicated values.

    :param lists: a tuple [of tuple of tuple] of list of elements
    :type lists: a tuple [of tuple of tuple] of list of elements
    :return: a concatenated list of elements
    :rtype: list (of str usually)
    """
    if lists is None:
        return list()
    while type(lists[0]) is tuple:
        lists = lists[0]
    returned_list = list()
    for a_list in lists:
        for element in a_list:
            if element not in returned_list:
                returned_list.append(element)
    return returned_list


def clean(selection_matrix: numpy.matrix) -> numpy.matrix:
    """
    Remove row full of zeros in a selection matrix (one value per row and at most one value per column).

    :param selection_matrix: a selection matrix
    :type selection_matrix: numpy.matrix
    :raises ValueError: triggered if the matrix given as argument is not a selection matrix
    :return: the provided selection but without rows full of zeros
    :rtype: Matrix
    """
    if selection_matrix.shape[0] > selection_matrix.shape[1]:
        raise ValueError('bar only operates on row matrices')
    i: int = 0
    while i < selection_matrix.shape[0]:
        number_of_non_null_elements: int = 0
        for j in range(selection_matrix.shape[1]):
            if selection_matrix[i, j] != 0:
                number_of_non_null_elements += 1
        if number_of_non_null_elements == 0:
            selection_matrix = numpy.delete(selection_matrix, i, axis=0)
        elif number_of_non_null_elements > 1:
            raise ValueError('bar only operates on selection matrices')
        else:
            i += 1
    return selection_matrix


def bar(a_matrix: numpy.matrix) -> numpy.matrix:
    """
    Compute the complementary matrix to the provided row matrix i.e bar_M such as [[M], [bar_M]] is invertible, bar_M.T * bar_M = I and M.T * bar_M = 0.

    A specific fast computation approach is used if M is a selection matrix.

    :param matrix: a row matrix, possibly a selection Matrix (one value per row and at most one value per column)
    :type matrix: Matrix
    :return: a complementary matrix
    :rtype: sympy.Matrix
    """
    try:
        i: int = 0
        while i < a_matrix.shape[0]:
            number_of_non_null_elements: int = 0
            for j in range(a_matrix.shape[1]):
                if a_matrix[i, j] != 0:
                    number_of_non_null_elements += 1
            if number_of_non_null_elements == 0:
                a_matrix: numpy.matrix = numpy.delete(a_matrix, i, axis=0)
            elif number_of_non_null_elements > 1:
                pass
            else:
                i += 1
        n_rows, n_columns = a_matrix.shape
        complement_matrix: numpy.matrix = numpy.matrix(numpy.zeros((n_columns - n_rows, n_columns)))
        k: int = 0
        for i in range(n_columns):
            found: bool = False
            j: int = 0
            while (not found) and j < n_rows:
                if a_matrix[j, i] != 0:
                    found = True
                j += 1
            if not found:
                complement_matrix[k, i] = 1
                k += 1
    except:  # noqa
        vectors: numpy.matrix = numpy.matrix(scipy.linalg.null_space(a_matrix.T))
        complement_matrix = vectors[0]
        for i in range(1, len(vectors)):
            complement_matrix = numpy.concatenate((complement_matrix, vectors[i]), axis=1)
        complement_matrix = complement_matrix.T
    return complement_matrix


def pinv(matrix: numpy.matrix) -> numpy.matrix:
    """
    compute pseudo-inverse of a full column rank matrix

    :param matrix: a full column rank matrix
    :type matrix: sympy.Matrix
    :return: the pseudo inverse computed as (matrix*matrix.T).inv() * matrix
    :rtype: numpy.matrix
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return scipy.linalg.pinv(matrix, atol=1e-10)


class NODE_TYPE(enum.Enum):
    """Tags used for labeling types of node variables .

    :param enum: heat flow or temperature
    :type enum: str
    """
    HEAT = "heat"
    TEMPERATURE = "temperature"


class ELEMENT_TYPE(enum.Enum):
    """
    Tags used for labeling of element corresponding to an edge.

    :param enum: thermal resistance (Rth), thermal capacitance (Cth) or heat source (heat)
    :type enum: str
    """
    R = "Rth"
    C = "Cth"
    P = "heat"


class AbstractThermalNetwork(networkx.DiGraph):
    """
    Digraph representing a thermal model, with nodes standing for variables (temperatures or heat flows) and edges for elements like thermal resistance, thermal capacitance and heat sources. The aim of this class is to generate state space model corresponding to a thermal network.

    This is the abstract class specialized in ThermalNetwork

    :param networkx: superclass digraph for networkx
    :type networkx: networkx.DiGraph
    """

    def __init__(self) -> None:
        """Initialize an empty thermal network
        """
        super().__init__(directed=True)
        self.Tref = self.T('TREF', CAUSALITY.IN)
        self.R_counter = 0
        self.C_counter = 0
        self.P_counter = 0
        self.T_counter = 1
        self.__select_elements = dict()

    def _edge_attr_str_vals(self, edge: Tuple[str, str]):
        """Convert edge attributes into a printable string

        :param edge: edge whose attributes have to be converted
        :type node: (str, str)
        :return: a string representing the edge attributes with values
        :rtype: str
        """
        _attr_vals = list()
        for attr_name in self.edges[edge]:
            _attr_value = self.edges[edge][attr_name]
            if type(_attr_value) is str:
                _attr_vals.append(_attr_value)
            elif isinstance(_attr_value, ELEMENT_TYPE):
                _attr_vals.append(_attr_value.value)
        return _attr_vals

    def _node_attr_str_vals(self, node: str):
        """Convert node attributes into a printable string

        :param node: node whose attributes have to be converted
        :type node: str
        :return: a string representing the node attributes with values
        :rtype: str
        """
        _attr_vals = list()
        for attr_name in self.nodes[node]:
            _attr_value = self.nodes[node][attr_name]
            if type(_attr_value) is str:
                _attr_vals.append(_attr_value)
            elif isinstance(_attr_value, NODE_TYPE) or isinstance(_attr_value, CAUSALITY):
                _attr_vals.append(_attr_value.value)
        return _attr_vals

    def T(self, name: str = None, causality: CAUSALITY = CAUSALITY.UNDEF) -> str:
        """Create a temperature node.

        :param name: temperature node name (should conventionally start by T), defaults to None with name generated automatically
        :type name: str, optional
        :param causality: type of causality, defaults to NODE_CAUSALITY.UNDEF
        :type causality: NODE_CAUSALITY, optional
        :return: name of the temperature node
        :rtype: str
        """
        if name in self.nodes:
            return name
        elif name is None:
            name: str = 'T' + str(self.T_counter)
            self.T_counter += 1
            symbol = name
        elif name == 'TREF':
            symbol: int = 0
        else:
            symbol = name
        self.add_node(name, causality=causality, ntype=NODE_TYPE.TEMPERATURE, value=symbol)
        return name

    def HEAT(self, T: str,  name: str = None) -> str:
        """Create a heat source node.

        :param T: temperature node where the heat source will inject its power
        :type T: str
        :param name: name of the heat source (should conventionally start by P), defaults to None with name generated automatically
        :type name: str, optional
        :return: name of the heat source node
        :rtype: str
        """
        if name is None:
            name = 'P'+str(self.P_counter)
            self.P_counter += 1
        self.add_node(name, causality=CAUSALITY.IN, ntype=NODE_TYPE.HEAT, value=name)
        self.add_edge(name, T, flow=name, element=ELEMENT_TYPE.P, value=name)
        return name

    def R(self, fromT: str = None, toT: str = None, name: str = None, heat_flow_name: str = None, val: float = None) -> tuple(str, str):
        """Create a resistance edge element between 2 temperature nodes, directed by the conventional heat flow.

        :param fromT: name of the temperature node where heat flow starts, defaults to None (0 reference temperature)
        :type fromT: str, optional
        :param toT: name of the temperature node where heat flow ends, defaults to None (0 reference temperature)
        :type toT: str, optional
        :param resistance_name: name of the thermal resistance, defaults to None with name generated automatically (RXXX)
        :type resistance_name: str, optional
        :param heat_flow_name: name of the heat_flow passing through thermal resistance, defaults to None with name generated automatically (PXX`X)
        :type heat_flow_name: str, optional
        :param value: value of the thermal resistance, defaults to None
        :type float: float, optional
        :raises ValueError: fromT and toT cannot be set to None simultaneously
        :return: thermal resistance name and heat flow name
        :rtype: tuple(str, str)
        """
        if fromT is None and toT is None:
            raise ValueError('At least one temperature must not be None')
        elif fromT is None:
            fromT: str = self.Tref
        elif fromT not in self.nodes:
            self.T(name=fromT)
        elif toT is None:
            toT: str = self.Tref
        elif toT not in self.nodes:
            self.T(name=toT)
        if name is None:
            name: str = 'R'+str(self.R_counter)
            self.R_counter += 1
        if heat_flow_name is None:
            heat_flow_name: str = 'P'+str(self.P_counter)
        self.P_counter += 1
        if val is not None:
            self.add_edge(fromT, toT, name=name, flow=heat_flow_name, element=ELEMENT_TYPE.R, value=val)
        return name, heat_flow_name

    def C(self, toT: str, name: str = None, heat_flow_name: str = None, val: float = None):
        """Create a thermal capacitance edge element between 0 reference temperature and a temperature node, directed by the conventional heat flow to the specified temperature node.

        :param T: name of the temperature node where heat flow ends, defaults to None (0 reference temperature)
        :type toT: str, optional
        :param capacitance_name: name of the thermal resistance, defaults to None with name generated automatically (CXXX)
        :type capacitance_name: str, optional
        :param heat_flow_name: name of the heat_flow passing through thermal resistance, defaults to None with name generated automatically (PXXX)
        :type heat_flow_name: str, optional
        :return: thermal resistance name and heat flow name
        :rtype: tuple(str, str)
        """
        if toT not in self.nodes:
            self.T(name=toT)
        if name is None:
            name: str = 'C' + str(self.C_counter)
            self.C_counter += 1
        if heat_flow_name is None:
            heat_flow_name: str = 'P'+str(self.P_counter)
        self.P_counter += 1
        self.add_edge(self.Tref, toT, name=name, flow=heat_flow_name, element=ELEMENT_TYPE.C, value=float(val))
        return name, heat_flow_name
    
    def RCs(self, fromT: str, toT: str = None, n_layers: int = 1, name: str = None, Rtotal: float = None, Ctotal: float = None):
        if name is None:
            if fromT is None:
                name = toT
                fromT, toT = toT, fromT
            else:
                if toT is not None:
                    name = fromT + '-' + toT
                else:
                    name = fromT
            if fromT is None:
                raise ValueError('At least one temperature node must be specified')
        if n_layers <= 1:
            middle_layer_temperature_name = name + 'm'
            self.R(fromT=fromT, toT=middle_layer_temperature_name, name='R0_'+middle_layer_temperature_name,  val=Rtotal/2)
            self.R(fromT=middle_layer_temperature_name, toT=toT, name='R1_'+middle_layer_temperature_name, val=Rtotal/2)
            self.C(toT=middle_layer_temperature_name, name='C_', val=Ctotal)
        else:
            R = Rtotal / 2 / n_layers
            C = Ctotal / n_layers
            for layer_index in range(n_layers):
                layer_name0: str = fromT if layer_index == 0 else name + '_%i' % layer_index
                layer1_name: str = toT if layer_index == n_layers - 1 else name + '_%i' % (layer_index+1)
                layer_middle_name: str = name + '_%i' % layer_index + 'm'
                self.R(fromT=layer_name0, toT=layer_middle_name, name='R0_'+layer_middle_name, val=R)
                self.R(fromT=layer_middle_name, toT=layer1_name, name='R1_'+layer_middle_name, val=R)
                self.C(toT=layer_middle_name, val=C)

    def _select_elements(self, element_type: ELEMENT_TYPE = None):
        """Return a list of a specified type of elements

        :param element_type: type of elements ELEMENT_TYPE (ELEMENT_TYPE.R for resistance, ELEMENT_TYPE.C for capacitance and ELEMENT_TYPE.P for heat source), defaults to None for all edge elements
        :type element_type: ELEMENT_TYPE, optional
        :return: list of requested elements
        :rtype: list of Networkx edges i.e. list of tuples (str, str)
        **SLOW**
        """
        if element_type is None:
            return self.edges
        else:
            if element_type not in self.__select_elements:
                self.__select_elements[element_type] = list(filter(lambda edge: edge is not None and self.edges[edge]['element'] == element_type, self.edges))
            return self.__select_elements[element_type]

    def _select_nodes(self, node_type: NODE_TYPE, node_causality: CAUSALITY = None):
        """Return a list of a specified type of nodes

        :param node_type: type of nodes (NODE_TYPE.TEMPERATURE for temperature, NODE_TYPE.HEAT for heat source), defaults to None for all node types
        :type node_type: NODE_TYPE
        :param node_causality: causality of nodes (NODE_CAUSALITY.IN for input, NODE_CAUSALITY.OUT for output and NODE_CAUSALITY.UNDEF for intermediate), defaults to None for all causalities
        :type node_causality: NODE_CAUSALITY
        :return: list of requested nodes
        :rtype: list of Networkx nodes i.e. list of str
        **SLOW**
        """
        if node_type is None and node_causality is None:
            return self.nodes
        elif node_type is None:
            return list(filter(lambda node: self.nodes[node]['causality'] == node_causality, self.nodes))
        elif node_causality is None:
            return list(filter(lambda node: self.nodes[node]['ntype'] == node_type, self.nodes))
        else:
            # l1 = list(filter(lambda node: self.nodes[node]['ntype'] == node_type, self.nodes))
            # l2 = list(filter(lambda node: self.nodes[node]['causality'] == node_causality, self.nodes))
            # l3 = list(filter(lambda node: self.nodes[node]['ntype'] == node_type and self.nodes[node]['causality'] == node_causality, self.nodes))
            return list(filter(lambda node: self.nodes[node]['ntype'] == node_type and self.nodes[node]['causality'] == node_causality, self.nodes))

    def _causal_temperatures(self) -> tuple:
        """ Return a tuple of lists of categorized temperature names
        :return: input temperatures, temperatures appearing as derivative, intermediate temperatures and output temperatures
        :rtype: tuple of lists of str
        """
        temperatures_state = list()
        for Cedge in self._select_elements(ELEMENT_TYPE.C):
            if Cedge[0] != "TREF" and Cedge[0] not in temperatures_state:
                temperatures_state.append(Cedge[0])
            if Cedge[1] != "TREF" and Cedge[1] not in temperatures_state:
                temperatures_state.append(Cedge[1])
        temperatures_remaining = list()
        for temperature in self._select_nodes(NODE_TYPE.TEMPERATURE):
            if temperature not in self.temperatures_in and temperature not in temperatures_state:
                temperatures_remaining.append(temperature)
        return temperatures_state, temperatures_remaining

    @property
    def temperatures_in(self) -> List[str]:
        """
        Return the names of temperatures tagged with Causality.IN. These variables are obtained either from the state vector, or from a combination of input variables and variables from state vector

        :return: temperature names requested for being simulated
        :rtype: Tuple[str]
        """
        _temperatures_in = list(self._select_nodes(NODE_TYPE.TEMPERATURE, CAUSALITY.IN))
        _temperatures_in.remove('TREF')
        return _temperatures_in

    @property
    def temperatures_out(self) -> Tuple[str]:
        """
        Return the names of temperatures tagged with Causality.OUT. These variables are obtained either from the state vector, or from a combination of input variables and variables from state vector

        :return: temperature names requested for being simulated
        :rtype: Tuple[str]
        """
        _temperatures_out = self._select_nodes(NODE_TYPE.TEMPERATURE, CAUSALITY.OUT)
        if len(_temperatures_out) == 0:
            for temperature in self._select_nodes(NODE_TYPE.TEMPERATURE):
                if temperature not in self._select_nodes(NODE_TYPE.TEMPERATURE, CAUSALITY.IN) and temperature != 'TREF':
                    _temperatures_out.append(temperature)
        return _temperatures_out

    @property
    def all_temperatures(self):
        """
        Return the list of all the variables representing temperatures

        :return: list of temperature names
        :rtype: List[str]
        """
        return concatenate(self.temperatures_in, *self._causal_temperatures())

    def _typed_heatflows(self):
        """Return the list of edge element heatflows by type. It returns 3 vectors of heat flows:
        - heatflows_R: the list of heatflows going through thermal resistances
        - heatflows_C: the list of heatflows going through thermal capacitances
        - heatflows_P: the list of heatflows sources

        :return: list of edge element heatflows by type: edges corresponding to resistance, then those corresponding to capacitance and finally those corresponding to power heatflows
        :rtype: Tuple[List[(str, str)]]
        """
        heatflows_R = [self.edges[edge]['flow'] for edge in self._select_elements(ELEMENT_TYPE.R)]
        heatflows_C = [self.edges[edge]['flow'] for edge in self._select_elements(ELEMENT_TYPE.C)]
        heatflows_P = [self.edges[edge]['flow'] for edge in self._select_elements(ELEMENT_TYPE.P)]
        return heatflows_R, heatflows_C, heatflows_P

    @property
    def heatflows_sources(self):
        """
        Return the list of heatflow sources

        :return: heatflow sources
        :rtype: List[str]
        """
        _, _, heatflows_P = self._typed_heatflows()
        return heatflows_P

    def _number_of_elements(self, type: ELEMENT_TYPE) -> int:
        """number of elements of the specified type in the thermal network

        :param type: type of elements to be counted
        :type type: ELEMENT_TYPE
        :return: number of edges tags as resistances
        :rtype: int
        """
        return len(self._select_elements(type))


class ThermalNetwork(AbstractThermalNetwork):
    """
    Specialized main class for transforming RC graphs into State Space model

    :param AbstractThermalNetwork: abstract super class
    """

    def __init__(self) -> None:
        """
        See superclass AbstractThermalNetwork.
        """
        super().__init__()

    def _matrices_MR_MC(self) -> Tuple[numpy.matrix, numpy.matrix]:
        """
        incidence matrices (-1 for starting flow and +1 for ending) leading to delta temperatures for R and C elements from temperatures
        :return: matrices MR and MC
        :rtype: sympy.Matrix, sympy.Matrix
        """
        Redges = self._select_elements(ELEMENT_TYPE.R)
        Cedges = self._select_elements(ELEMENT_TYPE.C)
        all_temperatures = self.all_temperatures
        MR: numpy.matrix = numpy.matrix(numpy.zeros((self._number_of_elements(ELEMENT_TYPE.R), len(all_temperatures))))
        MC: numpy.matrix = numpy.matrix(numpy.zeros((self._number_of_elements(ELEMENT_TYPE.C), len(all_temperatures))))
        components = []
        for i, Redge in enumerate(Redges):
            components.append(self.edges[Redge]['name'])
            for j, node in enumerate(Redge):
                if node in all_temperatures:
                    MR[i, all_temperatures.index(node)] = 1 - 2 * j
        for i, Cedge in enumerate(Cedges):
            components.append(self.edges[Cedge]['name'])
            for j, node in enumerate(Cedge):
                if node in all_temperatures:
                    MC[i, all_temperatures.index(node)] = 1 - 2 * j
        return MR, MC

    def _matrix_R(self) -> numpy.matrix:
        """ Return a diagonal matrix with thermal resistance coefficient in the diagonal.

        :return: diagonal matrix R
        :rtype: sympy.matrix
        """
        Redges = self._select_elements(ELEMENT_TYPE.R)
        R_heat_flows = self._typed_heatflows()[0]
        matrix_R: numpy.matrix = numpy.matrix(numpy.zeros((len(R_heat_flows), len(R_heat_flows))))
        for Redge in Redges:
            i: int = R_heat_flows.index(self.edges[Redge]['flow'])
            matrix_R[i, i] = self.edges[Redge]['value']
        return matrix_R

    def _matrix_C(self) -> numpy.matrix:
        """" Return a diagonal matrix with thermal capacitance coefficient in the diagonal.

        :return: diagonal matrix C
        :rtype: sympy.matrix
        """
        Cedges = self._select_elements(ELEMENT_TYPE.C)
        C_heat_flows = self._typed_heatflows()[1]
        matrix_C: numpy.matrix = numpy.matrix(numpy.zeros((len(C_heat_flows), len(C_heat_flows))))
        for Cedge in Cedges:
            i: int = C_heat_flows.index(self.edges[Cedge]['flow'])
            matrix_C[i, i] = self.edges[Cedge]['value']
        return matrix_C

    @property
    def _matrices_Gamma_RCP(self) -> Tuple[numpy.matrix, numpy.matrix, numpy.matrix]:
        """ Return heatflow balances at each node as a set of 3 incidence (-1: node leaving flow and 1: node entering flow) matrices:

        heatflows_balance_R_matrix * R_heatflows + heatflows_balance_C_matrix * C_heatflows + heatflows_balance_P_matrix * P_heatflows = 0

        :return: matrices heatflows_balance_R_matrix (GammaR), heatflows_balance_C_matrix (GammaC), heatflows_balance_P_matrix (GammaP)
        :rtype: sympy.Matrix, sympy.Matrix, sympy.Matrix
        """
        heatflows_R, heatflows_C, heatflows_P = self._typed_heatflows()
        heatflows_R_matrix = list()
        heatflows_C_matrix = list()
        heatflows_P_matrix = list()
        number_of_heat_balances = 0
        for node in self.all_temperatures:
            flows_in = [self.edges[edge]['flow'] for edge in self.in_edges(nbunch=node)]
            flows_out = [self.edges[edge]['flow'] for edge in self.out_edges(nbunch=node)]
            if node != 'TREF' and len(flows_in) + len(flows_out) > 1:
                heatflows_R_matrix.append([0 for i in range(len(heatflows_R))])
                heatflows_C_matrix.append([0 for i in range(len(heatflows_C))])
                heatflows_P_matrix.append([0 for i in range(len(heatflows_P))])
                for flow in concatenate(flows_in, flows_out):
                    incidence = -1 if flow in flows_out else 1
                    flow_index = self.all_heatflows.index(flow)
                    if flow_index < len(heatflows_R):
                        heatflows_R_matrix[number_of_heat_balances][flow_index] = incidence
                    elif flow_index < len(heatflows_R) + len(heatflows_C):
                        heatflows_C_matrix[number_of_heat_balances][flow_index - len(heatflows_R)] = incidence
                    else:
                        heatflows_P_matrix[number_of_heat_balances][flow_index - len(heatflows_R) - len(heatflows_C)] = - incidence
                number_of_heat_balances += 1
        return numpy.matrix(heatflows_R_matrix), numpy.matrix(heatflows_C_matrix), numpy.matrix(heatflows_P_matrix)

    def _temperatures_selection_matrix(self, selected_temperatures: List[str], all_temperatures: List[str] = None):
        """Create a selection matrix for the temperature provided as inputs and considering all the temperature nodes

        :param selected_temperatures: list of temperatures for which the selection matrix is computer
        :type selected_temperatures: List[str]
        :return: the selection matrix
        :rtype: scipy.Matrix
        """
        if all_temperatures is None:
            all_temperatures: List[str] = self.all_temperatures
        selection_matrix: numpy.matrix = numpy.matrix(numpy.zeros((len(selected_temperatures), len(all_temperatures))))
        for i, temperature in enumerate(selected_temperatures):
            selection_matrix[i, all_temperatures.index(temperature)] = 1
        return selection_matrix

    def _Sselect(self) -> numpy.matrix:
        """
        Generate a selection matrix to get from all the temperatures except the input and the state ones, the ones that has been tagged with CAUSALITY.OUT

        :return: a selection matrix with 0 or 1 insides
        :rtype: Matrix
        """
        if self.temperatures_select is None or len(self.temperatures_select) == 0:
            selection_matrix: numpy.matrix = numpy.matrix(numpy.eye(len(self.temperatures_remaining)))
        else:
            selection_matrix: numpy.matrix = numpy.matrix(numpy.zeros((len(self.temperatures_select), len(self.temperatures_remaining))))
            for i, temperature in enumerate(self.temperatures_select):
                if temperature in self.temperatures_remaining:
                    selection_matrix[i, self.temperatures_remaining.index(temperature)] = 1
        return selection_matrix

    @property
    def all_heatflows(self):
        """
        List 3 vectors of heat flows:
        - heatflows_R: the list of heatflows going to thermal resistances
        - heatflows_C: the list of heatflows going to thermal capacitances
        - heatflows_P: the list of heatflows sources

        :return: _description_
        :rtype: List[str,
        """
        heatflows_R, heatflows_C, P_heatflows = self._typed_heatflows()
        return concatenate(heatflows_R, heatflows_C, P_heatflows)

    def _heatflows_selection_matrix(self, selected_heat_flows: List[str]):
        """
        Internally used to generate a selection matrix for extracting some heatflows .

        :param selected_heat_flows: the heatflows that will correspond to the selection matrix
        :type selected_heat_flows: List[str]
        :return: a selection matrix S such as:

            selected_heat_flows = S * all_heatflows
        :rtype: List[str]
        """
        selection_matrix: numpy.matrix = numpy.matrix(numpy.zeros((len(selected_heat_flows), len(self.all_heatflows))))
        for i, heat_flow in enumerate(selected_heat_flows):
            selection_matrix[i, self.all_heatflows.index(heat_flow)] = 1
        return selection_matrix

    def _Sin(self):
        """
        Generate a selection matrix corresponding to the known temperatures temperatures_in used as inputs.

        :return: a full row rank selection Matrix that can be used to extract the known value variables i.e. variables in the vector temperatures_in
        :rtype: sympy.Matrix
        """
        return self._temperatures_selection_matrix(self.temperatures_in)

    def _Sstate(self):
        """
        Generate a selection matrix corresponding to the temperatures with derivatives temperatures_state used as state vector.

        :return: a full row rank selection Matrix that can be used to extract the state variables
        :rtype: sympy.Matrix
        """
        temperatures_state, _ = self._causal_temperatures()
        Sstate = self._temperatures_selection_matrix(temperatures_state)
        return Sstate

    @property
    def temperatures_state(self):
        """
        Vector containing the list of state variables

        :return: the temperatures corresponding to the state variables
        :rtype: sympy.Matrix
        """
        temperatures_state, _ = self._causal_temperatures()
        return temperatures_state

    def _Sremaining(self):
        """
        Generate a selection matrix corresponding to the temperatures which are not belonging to the inputs and to the states.

        :return: a full row rank selection Matrix that can be used to extract the temperatures which are not belonging to the inputs and to the states.
        :rtype: sympy.Matrix
        """
        _, temperatures_remaining = self._causal_temperatures()
        Sremaining = self._temperatures_selection_matrix(temperatures_remaining)
        return Sremaining

    @property
    def temperatures_ignore(self):
        _temperatures_ignore = list()
        for temperature in self.temperatures_remaining:
            if temperature not in self.temperatures_out:
                _temperatures_ignore.append(temperature)
        return _temperatures_ignore

    def _Signore(self):
        """
        Generate a selection matrix corresponding to the temperatures which are not belonging to the inputs and to the states.

        :return: a full row rank selection Matrix that can be used to extract the temperatures which are not belonging to the inputs and to the states.
        :rtype: sympy.Matrix
        """
        Signore = self._temperatures_selection_matrix(self.temperatures_ignore)
        return Signore

    def _Sout(self):
        """
        Return a selection matrix leading to output temperature variable from the vector of all the temperature variables

        :return: a selection matrix for extracting temperature variables, which have been tagged with Causality.OUT
        :rtype: Matrix
        """
        return self._temperatures_selection_matrix(self.temperatures_out)

    @property
    def temperatures_remaining(self):
        """
        Vector containing the list of temperatures which are not belonging to the inputs and to the states.

        :return: the temperatures corresponding to the temperatures which are not belonging to the inputs and to the states.
        :rtype: sympy.Matrix
        """
        _, temperatures_remaining = self._causal_temperatures()
        return temperatures_remaining

    @property
    def temperatures_select(self) -> tuple:
        """
        Return the selected temperatures, tagged with CAUSALITY.OUT, to be at the output of the state space output equation except the temperatures belonging to the state ones

        :return: _description_
        :rtype: tuple
        """
        temperatures_sel = list()
        for temperature in self.temperatures_out:
            if temperature in self.temperatures_remaining:
                temperatures_sel.append(temperature)
        return temperatures_sel

    @property
    def CDstate_heatflows_matrices(self):
        """
        Return the matrices of the following linear static model:

        temperatures_out = D_temperatures_in temperatures_in + D_heatflow_sources heatflows_sources

        :return: Matrices D_temperatures_in and D_heatflow_sources
        :rtype: Tuple(sympy.Matrix, sympy.Matrix)
        :raises ValueError: if the graphical model contains capacitance
        """
        if len(self.temperatures_state) != 0:
            raise ValueError('A linear static model can\'t be obtained from a model with capacitance')
        GammaR, _, GammaP = self._matrices_Gamma_RCP
        MR, _ = self._matrices_MR_MC()
        Psi_R = numpy.linalg.inv(GammaR * self._matrix_R()) * MR
        D_Tin = numpy.linalg.inv(self._matrix_R()) * MR * (numpy.eye(len(self.all_temperatures)) - self._Sremaining().T * pinv(Psi_R * self._Sremaining().T) * Psi_R) * self._Sin().T
        if len(self.heatflows_sources) == 0:
            D_heat = GammaP
        else:
            D_heat = numpy.linalg.inv(self._matrix_R()) * MR * self._Sremaining().T * pinv(Psi_R * self._Sremaining().T) * GammaP
        return D_Tin, D_heat

    def _diffeq_variables(self):
        """
        Compute internal matrices for state space model

        :return: internal matrices: GammaR, GammaC, GammaP, MR, MC, Psi_R, Psi_C, Phi, Pi
        :rtype: List[float]
        """
        GammaR, GammaC, GammaP = self._matrices_Gamma_RCP
        MR, MC = self._matrices_MR_MC()
        Psi_R = GammaR * numpy.linalg.inv(self._matrix_R()) * MR
        Psi_C = GammaC * self._matrix_C() * MC
        Phi = bar(self._Sstate() * Psi_C.T) * Psi_R * self._Sremaining().T
        Pi = pinv(Psi_C * self._Sstate().T) * (numpy.eye(Psi_R.shape[0]) - Psi_R * self._Sremaining().T * pinv(Phi) * bar(self._Sstate()*Psi_C.T))
        return GammaR, GammaC, GammaP, MR, MC, Psi_R, Psi_C, Phi, Pi

    def _ABstate_matrices(self):
        """ Compute matrices A, B of the state space model corresponding to the thermal network

        d/dt temperatures_state = A temperatures_state + B_in temperatures_in + B_heat heat_sources

        :return: matrices of the state space representation corresponding to the thermal network with temperature corresponding to capacitance as state variables
        :rtype: List[sympy.matrix]
        """
        if len(self.temperatures_state) == 0:
            raise ValueError('A state space model can only be obtained for a model with capacitance')

        _, _, GammaP, _, _, Psi_R, _, _, Pi = self._diffeq_variables()
        A = - Pi * Psi_R * self._Sstate().T
        B_temperatures_in = - Pi * Psi_R * self._Sin().T
        if len(self.heatflows_sources) == 0:
            B_heatflow_sources = GammaP
        else:
            B_heatflow_sources = Pi * GammaP

        return A, B_temperatures_in, B_heatflow_sources

    def _CDstate_matrices(self):
        """
        Compute matrices C_rem, D_temperatures_in and D_heatflow_sources of the state space model corresponding to the thermal network where output temperature is corresponding to temperatures_in

        :return: matrices C_rem, D_temperatures_in and D_heatflow_source
        :rtype: _type_
        """
        _, _, GammaP, _, _, Psi_R, Psi_C, Phi, _ = self._diffeq_variables()
        if numpy.any(Psi_C):
            C_rem = - pinv(Phi) * bar(self._Sstate() * Psi_C.T) * Psi_R * self._Sstate().T
            D_rem_temperatures_in = - pinv(Phi) * bar(self._Sstate() * Psi_C.T) * Psi_R * self._Sin().T
            if len(self.heatflows_sources) == 0:
                D_rem_heatflow_sources = GammaP
            else:
                D_rem_heatflow_sources = pinv(Phi) * bar(self._Sstate() * Psi_C.T) * GammaP
            if self.temperatures_select is None or self.temperatures_select == 0:
                return C_rem, D_rem_temperatures_in, D_rem_heatflow_sources
            if len(self.heatflows_sources) > 0:
                return self._Sselect() * C_rem, self._Sselect() * D_rem_temperatures_in, self._Sselect() * D_rem_heatflow_sources
            else:
                return self._Sselect() * C_rem, self._Sselect() * D_rem_temperatures_in, None
        else:
            Kout = pinv(Psi_R * self._Sout().T)
            Kignore = - pinv(Psi_R * self._Signore().T)
            if numpy.any(Kignore) and not ('TREF' in self.temperatures_ignore and len(self.temperatures_ignore) == 1):
                raise ValueError("Missing temperatures: "+','.join(self.temperatures_ignore))
            D_rem_temperatures_in = - Kout * Psi_R * self._Sin().T
            D_rem_heatflow_sources = Kout * GammaP
            return None, D_rem_temperatures_in, D_rem_heatflow_sources

    @property
    def CDheatflows_matrices(self) -> Tuple[numpy.matrix]:
        """
        Compute matrices C and D leading to the estimations of heatflows going through resistances and capacitances

        :return: Matrices
        :rtype: Tuple[Matrix]
        """
        GammaR, GammaC, GammaP, MR, MC, Psi_R, Psi_C, Phi, Pi = self._diffeq_variables()
        Pi1 = numpy.linalg.inv(self._matrix_R()) * MR * (numpy.eye(len(self.all_temperatures)) + self._Sremaining().T * pinv(Phi) * bar(self._Sstate() * Psi_C.T) * Psi_R)
        C_R = Pi1 * self._Sstate().T
        D_R_in = Pi1 * self._Sin().T
        if len(self.heatflows_sources) == 0:
            D_R_varphi_P = GammaP
        else:
            D_R_varphi_P = -numpy.linalg.inv(self._matrix_R()) * MR * self._Sremaining().T * pinv(Phi) * bar(self._Sstate() * Psi_C.T) * GammaP
        Pi2 = - self._matrix_C() * MC * self._Sstate().T * Pi * Psi_R
        C_C = Pi2 * self._Sstate().T
        D_C_in = Pi2 * self._Sin().T
        if len(self.heatflows_sources) == 0:
            D_C_varphi_P = GammaP
        else:
            D_C_varphi_P = self._matrix_C() * MC * self._Sstate().T * Pi * GammaP
        C = numpy.concatenate((C_R, C_C), axis=0)
        D_in = numpy.concatenate((D_R_in, D_C_in), axis=0)
        D_varphi_P = numpy.concatenate((D_R_varphi_P, D_C_varphi_P), axis=0)
        return C, D_in, D_varphi_P

    def draw(self):
        """
        plot the thermal network
        """
        layout = networkx.shell_layout(self)
        node_colors = list()
        for node in self.nodes():
            if node[0] == 'P':
                node_colors.append('yellow')
            elif node == 'TREF':
                node_colors.append('blue')
            else:
                if self.nodes[node]['causality'] == CAUSALITY.IN:
                    node_colors.append('cyan')
                else:
                    node_colors.append('pink')
        edge_colors = list()
        for edge in self.edges():
            if edge in self._select_elements(ELEMENT_TYPE.R):
                edge_colors.append('blue')
            elif edge in self._select_elements(ELEMENT_TYPE.C):
                edge_colors.append('red')
            else:
                edge_colors.append('black')

        plt.figure()
        networkx.draw(self, layout, with_labels=True, edge_color=edge_colors, width=1, linewidths=1, node_size=500, font_size='medium', node_color=node_colors, alpha=1)
        networkx.drawing.draw_networkx_labels(self, layout,  font_size='x-small', verticalalignment='top', labels={node: '\n'+','.join(self._node_attr_str_vals(node)) for node in self.nodes})
        networkx.draw_networkx_edge_labels(self, layout, font_size='x-small', font_color='r', edge_labels={edge: ','.join(self._edge_attr_str_vals(edge)) for edge in self.edges})

    def state_model(self) -> StateModel | dict:
        """
        Return the matrices of state space model (with capacitance) or the static model (no capacitance)

        :return: list of matrices A, B_Tin, B_heat, C, D_Tin, D_heat with variables Y, X, U_Tin, U_heat. Additionally, the type 'differential' or 'static' is given depending on wether there is at least one capacitance or not.
        :rtype: Tuple[Matrix, Matrix, Matrix, Matrix, Matrix, Matrix, Matrix, List[float], List[float], List[float], List[float], str]
        """

        temperatures_out_state = list()
        for temperature in self.temperatures_out:
            if temperature in self.temperatures_state:
                temperatures_out_state.append(temperature)
        if len(self.temperatures_state) > 0:  # dynamic model
            X = self.temperatures_state
            A, B_Tin, B_heat = self._ABstate_matrices()
            _Sout: numpy.matrix = self._temperatures_selection_matrix(temperatures_out_state, X)
            C_state: numpy.matrix = _Sout
            D_state_Tin: numpy.matrix = numpy.matrix(numpy.zeros((len(temperatures_out_state), len(self.temperatures_in))))
            D_state_heat: numpy.matrix = numpy.matrix(numpy.zeros((len(temperatures_out_state), len(self.heatflows_sources))))

            C_select, D_select_Tin, D_select_heat = None, None, None
            temperatures_out_select = list()
            for temperature in self.temperatures_out:
                if temperature in self.temperatures_select and temperature not in self.temperatures_state:
                    temperatures_out_select.append(temperature)
            if len(temperatures_out_select) > 0:
                _Sout = self._temperatures_selection_matrix(temperatures_out_select, self.temperatures_select)
                C_select, D_select_Tin, D_select_heat = self._CDstate_matrices()
                C_select = _Sout * C_select
                D_select_Tin = _Sout * D_select_Tin
                if D_select_heat is not None:
                    D_select_heat = _Sout * D_select_heat

            if C_state is not None and C_select is None:
                # state_model = {'A': A, 'B_Tin': B_Tin, 'B_heat': B_heat, 'C': C_state, 'D_Tin': D_state_Tin, 'D_heat': D_state_heat, 'Y': temperatures_out_state, 'X': X, 'U_Tin': self.temperatures_in, 'U_heat': self.heatflows_sources, 'type': 'differential'}
                input_names = self.temperatures_in
                input_names.extend(self.heatflows_sources)
                _state_model = StateModel((A, numpy.hstack((B_Tin, B_heat)), C_state, numpy.hstack((D_state_Tin, D_state_heat))), input_names=input_names, output_names=temperatures_out_state)
                _state_model.create_Upartition('main', temperatures=self.temperatures_in, heats=self.heatflows_sources)
                return _state_model
            if C_state is None and C_select is not None:
                # state_model = {'A': A, 'B_Tin': B_Tin, 'B_heat': B_heat, 'C': C_select, 'D_Tin': D_select_Tin, 'D_heat': D_select_heat, 'Y': temperatures_out_select, 'X': X, 'U_Tin': self.temperatures_in, 'U_heat': self.heatflows_sources, 'type': 'differential'}
                input_names = self.temperatures_in
                input_names.extend(self.heatflows_sources)
                _state_model = StateModel((A, numpy.hstack((B_Tin, B_heat)), C_select, numpy.hstack((D_select_Tin, D_select_heat))), input_names=input_names, output_names=temperatures_out_select)
                _state_model.create_Upartition('main', temperatures=self.temperatures_in, heats=self.heatflows_sources)
                return _state_model
            if C_state is not None and C_select is not None:
                temperatures_out_state.extend(temperatures_out_select)
                # state_model = {'A': A, 'B_Tin': B_Tin, 'B_heat': B_heat, 'C': numpy.concatenate((C_state, C_select), axis=0), 'D_Tin': numpy.concatenate((D_state_Tin, D_select_Tin), axis=0), 'D_heat': numpy.concatenate((D_state_heat, D_select_heat), axis=0), 'Y': temperatures_out_state, 'X': X, 'U_Tin': self.temperatures_in, 'U_heat': self.heatflows_sources, 'type': 'differential'}
                input_names = self.temperatures_in
                input_names.extend(self.heatflows_sources)
                if D_select_heat is not None:
                    _state_model = StateModel((A, numpy.hstack((B_Tin, B_heat)), numpy.vstack((C_state, C_select)), numpy.hstack((numpy.vstack((D_state_Tin, D_select_Tin)), numpy.vstack((D_state_heat, D_select_heat))))), input_names=input_names, output_names=temperatures_out_state)
                    _state_model.create_Upartition('main', temperatures=self.temperatures_in, heats=self.heatflows_sources)
                else:
                    _state_model = StateModel((A, B_Tin, numpy.vstack((C_state, C_select)), numpy.vstack((D_state_Tin, D_select_Tin))), input_names=input_names, output_names=temperatures_out_state)
                return _state_model

            C: numpy.matrix = numpy.matrix(numpy.eye(len(self.temperatures_state)))
            D_Tin: numpy.matrix = numpy.matrix(numpy.zeros((len(self.temperatures_state), len(self.temperatures_in))))
            D_heat: numpy.matrix = numpy.matrix(numpy.zeros((len(self.temperatures_state), len(self.heatflows_sources))))
            # Y = X
            # state_model = {'A': A, 'B_Tin': B_Tin, 'B_heat': B_heat, 'C': C, 'D_Tin': D_Tin, 'D_heat': D_heat, 'Y': Y, 'X': X, 'U_Tin': self.temperatures_in, 'U_heat': self.heatflows_sources, 'type': 'differential'}

            input_names: list[str] = self.temperatures_in
            input_names.extend(self.heatflows_sources)
            _state_model = StateModel((A, numpy.hstack((B_Tin, B_heat)), C, numpy.hstack((D_Tin, D_heat))), input_names=input_names, output_names=self.temperatures_state)
            _state_model.create_Upartition('main', temperatures=self.temperatures_in, heats=self.heatflows_sources)
            return _state_model
        else:  # static model
            D_state_Tin: numpy.matrix = numpy.matrix(numpy.zeros((len(self.temperatures_out), len(self.temperatures_in))))
            D_state_heat: numpy.matrix = numpy.matrix(numpy.zeros((len(self.temperatures_out), len(self.heatflows_sources))))

            C_select, D_select_Tin, D_select_heat = None, None, None
            temperatures_out_select = list()
            for temperature in self.temperatures_out:
                if temperature in self.temperatures_select:
                    temperatures_out_select.append(temperature)
            if len(temperatures_out_select) > 0:
                C_select, D_select_Tin, D_select_heat = self._CDstate_matrices()
            input_names = self.temperatures_in
            input_names.extend(self.heatflows_sources)
            D = numpy.hstack((D_select_Tin, D_select_heat))
            _state_model = StateModel((None, None, None, D), input_names=input_names, output_names=temperatures_out_select)
            _state_model.create_Upartition('main', temperatures=self.temperatures_in, heats=self.heatflows_sources)
            return _state_model


def name_layers(left_name: str, right_name: str, number_of_layers: int, prefix: str = '') -> tuple[list[str], list[tuple[str, str]]]:
    """generate series of suffixes to name a given number of layers: name are provided for each layer but also for the 2 borders delimiting a layer

    :param left_name: left hand side existing layer name
    :type left_name: str
    :param right_name: right hand side existing layer name
    :type right_name: str
    :param number_of_layers: number of layers to be named
    :type number_of_layers: int
    :param prefix: prefix added to each name (and inside name by composition of names), defaults to ''
    :type prefix: str, optional
    :return: first a list of names for each layer and second, a list of pairs of variable names representing both sides of a layer. Of course, the left hand side name of a layer n is equal to the right hand side name of the layer n-1
    :rtype: tuple[list[str], list[tuple[str, str]]]
    """
    layer_border_names = list()
    layer_names = list()
    for i in range(number_of_layers):
        left_border_name: str = left_name + '-' + right_name + ':' + str(i - 1) if i > 0 else left_name
        right_border_name: str = left_name + '-' + right_name + ':' + str(i) if i < number_of_layers-1 else right_name
        layer_border_names.append((prefix+left_border_name, prefix+right_border_name))
        layer_names.append(prefix+left_name + '-' + right_name + ':' + str(i) + 'm')
    return layer_names, layer_border_names


class ThermalNetworkMaker(abc.ABC):
    """
    This class represents the thermal part of a building with its zones, its layered and block wall sides separating 2 zones.
    It contains a superset of the class building, which is the thermal part of the API exposed to the designer of building.
    """

    def __init__(self, *zone_names: str, periodic_depth_seconds: float, data_provider: DataProvider):
        """
        Initialize a site

        :param zone_names: names of the zones except for 'outdoor', which is automatically created
        :type zone_names: Tuple[str]
        :param args: set the order of the resulting reduced order thermal state model with order=integer value. If the value is set to None, there won't be order reduction of the thermal state model, default to None
        :type args: Dict[str, float], optional
        """
        self.sample_time_seconds: int = data_provider.sample_time_in_secs
        self.data_provider: DataProvider = data_provider
        # self.state_model_order_max: int = state_model_order_max
        self.name_zones: dict[str, Zone] = dict()
        self.zone_names: tuple[str] = zone_names
        for zone_name in zone_names:
            if zone_name in self.name_zones:
                raise ValueError('Zone %s is duplicated' % zone_name)
            self.name_zones[zone_name] = Zone(zone_name)
        self.layered_wall_sides: list[WallSide] = list()
        self.block_wall_sides: list[WallSide] = list()
        # self.thermal_state_model_order = None
        self.name_zones['outdoor'] = Zone('outdoor', kind=ZONE_TYPES.OUTDOOR)
        self.thermal_network = None
        self.periodic_depth_seconds: float = periodic_depth_seconds

    @property
    def wall_sides(self) -> list[WallSide]:
        _wall_sides: list[WallSide] = self.layered_wall_sides.copy()
        _wall_sides.extend(self.block_wall_sides)
        return _wall_sides

    def wall_transmitivities(self, zone1_name: str = None, zone2_name: str = None) -> float | dict[frozenset[str, str], float]:
        _wall_Us = dict()
        for wall_side in self.wall_sides:
            zones: frozenset[str, str] = wall_side.zones
            if zones in _wall_Us:
                _wall_Us[zones] += wall_side.global_USs1_2
            else:
                _wall_Us[zones] = wall_side.global_USs1_2
        if zone1_name is not None and zone2_name is not None:
            return _wall_Us[frozenset((zone1_name, zone2_name))]
        return _wall_Us

    # def wall_capacitances(self, zone1_name: str = None, zone2_name: str = None) -> float | dict[frozenset[str, str], float]:
    #     _wall_Cs = dict()
    #     for wall_side in self.wall_sides:
    #         zones: frozenset[str, str] = wall_side.zones
    #         if zones in _wall_Cs:
    #             _wall_Cs[zones] += wall_side.global_Cs1_2
    #         else:
    #             _wall_Cs[zones] = wall_side.global_Cs1_2
    #     if zone1_name is not None and zone2_name is not None:
    #         return _wall_Cs[frozenset((zone1_name, zone2_name))]
    #     return _wall_Cs

    def wall_resistances(self, zone1_name: str = None, zone2_name: str = None):
        if zone1_name is not None and zone2_name is not None:
            return 1 / self.wall_transmitivities(zone1_name, zone2_name)
        else:
            _wall_transmitivities = self.wall_transmitivities()
            return {1 / _wall_transmitivities[zones] for zones in _wall_transmitivities}

    def wall_global_capacitances(self, zone1_name: str, zone2_name: str) -> Any | set[Any | float]:
        _wall_capacitance = 0
        wall = frozenset((zone1_name, zone2_name))
        for wall_side in self.wall_sides:
            if wall_side.zones == wall:
                _wall_capacitance += wall_side.global_Cs1_2
        return _wall_capacitance
        # _wall_capacitance = self.wall_transmitivities()
        # return {_wall_capacitance[zones] for zones in _wall_capacitance}

    @property
    def simulated_zone_names(self) -> list[str]:
        simulated_zone_names: list[str] = list()
        for zone in self.zone_names:
            if self.name_zones[zone].volume is not None:
                simulated_zone_names.append(self.name_zones[zone])
        return simulated_zone_names

    def simulate_zone(self, *zone_names: str) -> None:
        """
        define a zone as for being simulated regarding CO2 concentration

        :param zone_name: name of the zone
        :type zone_name: str
        """
        for zone_name in zone_names:
            if zone_name not in self.name_zones:
                raise ValueError("Can't simulate the zone %s because it has not been created before" % zone_name)
            data_name = zone_name + ':volume'
            if zone_name + ':volume' in self.data_provider:
                print('Zone %s is going to be simulated: the volume has to be given by the data provider under the name "%s"' % (zone_name, data_name))
                volume = self.data_provider(zone_name + ':volume')
                print('Volume of zone %s is: %f m3' % (zone_name, volume))
            self.name_zones[zone_name].set_volume(volume)

    def layered_wall_side(self, zone1_name: str, zone2_name: str, side_type: SIDE_TYPES, surface: float) -> LayeredWallSide:
        """
        add a layered wall side between 2 zones

        :param zone1_name: first zone name
        :type zone1_name: str
        :param zone2_name: second zone name
        :type zone2_name: str
        :param side_type: type of wall side
        :type side_type: SideType
        :param surface: surface of the interface in m2
        :type surface: float
        :return: the layered wall side where the layers can be added from zone1 to zone2
        :rtype: LayeredWallSide
        """
        layered_side = LayeredWallSide(self.name_zones[zone1_name], self.name_zones[zone2_name], side_type, surface)
        self.layered_wall_sides.append(layered_side)
        return layered_side

    def block_wall_side(self, zone1_name: str, zone2_name: str, side_type: SIDE_TYPES, total_US: float, total_capacitance: float = None) -> BlockWallSide:
        """add a block wall side with only one layer and potentially no capacitance

        :param zone1_name: first zone name
        :type zone1_name: str
        :param zone2_name: seconde zone name
        :type zone2_name: str
        :param side_type: type of side
        :type side_type: SideType
        :param total_US: total transmission coefficient for the whole block side
        :type total_US: float
        :param total_capacitance: total capacitance for the whole block side, defaults to None
        :type total_capacitance: float, optional
        :return: the created block side
        :rtype: BlockSide
        """
        self.block_wall_sides.append(BlockWallSide(self.name_zones[zone1_name], self.name_zones[zone2_name], side_type, total_US, total_capacitance))

    def make_thermal_network_k(self) -> ThermalNetwork:
        """
        Utility private method that transforms the geometrical description of a building, taking into account adjustment factors for model calibration, into a thermal network, from which a state model can be deduced. This method is called by the method 'make_state_model()' in Building.
        It has to be called anytime an adjustment factor is changed to regenerate a thermal network.

        :param side_Rfactor: adjustment multiplicative factors applying to the resulting resistances for the referred wall sides. It's a dictionary {(zone1, zone2): Rfactor1_2, (zone1, zone5): Rfactor1_5, ...}
        :type side_Rfactor: dict[tuple[str,str], float]
        :param side_Cfactor: adjustment multiplicative factors applying to the resulting capacitances for the referred wall sides. It's a dictionary {(zone1, zone2): Cfactor1_2, (zone1, zone5): Cfactor1_5, ...}
        :type side_Cfactor: dict[tuple[str,str], float]
        :param Vfactor: adjustment multiplicative factors applying to the specified zone. It's a dictionary {zone1: Vfactor1, zone2: Vfactor2, ...}
        :type Vfactor: dict[str,float]
        :return: the thermal network
        :rtype: buildingenergy.thermal.ThermalNetwork
        """
        self.thermal_network = ThermalNetwork()
        air_properties: dict[str, float] = properties.get('air')
        rhoCp_air: float = air_properties['density'] * air_properties['Cp']

        for zone_name in self.name_zones:
            zone: Zone = self.name_zones[zone_name]
            if zone.zone_type == ZONE_TYPES.SIMULATED:
                self.thermal_network.T(zone.air_temperature_name, CAUSALITY.OUT)
                self.thermal_network.HEAT(T=zone.air_temperature_name, name=zone.power_gain_name)
                Cair: float = rhoCp_air * self.data_provider('%s:volume' % zone_name)
                self.thermal_network.C(toT=zone.air_temperature_name, name=zone.air_capacitance_name, val=Cair)
            else:
                self.thermal_network.T(zone.air_temperature_name, CAUSALITY.IN)

        for wall_side in self.wall_sides:
            if ('%s-%s:Rfactor' % (wall_side.zone1.name, wall_side.zone2.name)) in self.data_provider:
                Rfactor = self.data_provider('%s-%s:Rfactor' % (wall_side.zone1.name, wall_side.zone2.name))
            else:
                Rfactor = 1
            if ('%s-%s:Cfactor' % (wall_side.zone1.name, wall_side.zone2.name)) in self.data_provider:
                Cfactor = self.data_provider('%s-%s:Cfactor' % (wall_side.zone1.name, wall_side.zone2.name))
            else:
                Cfactor = 1
            number_of_layers: int = len(wall_side.Rs1_2)
            layer_names, layer_border_names = name_layers(wall_side.zone1.air_temperature_name, wall_side.zone2.air_temperature_name, number_of_layers)
            for layer_index in range(number_of_layers):
                layer_left_temperature_name: str = layer_border_names[layer_index][0]
                middle_layer_temperature_name: str = layer_names[layer_index]
                layer_right_temperature_name: str = layer_border_names[layer_index][1]
                R = Rfactor * wall_side.Rs1_2[layer_index] / 2
                if wall_side.Cs1_2[layer_index] is None:
                    self.thermal_network.R(fromT=layer_left_temperature_name, toT=layer_right_temperature_name, val=2*R)
                else:
                    C = Cfactor * wall_side.Cs1_2[layer_index]
                    n_sublayers = 1
                    try:
                        n_sublayers: int = round(sqrt(pi * R * C / self.periodic_depth_seconds))
                    except:  # noqa
                        n_sublayers = 1
                    if n_sublayers <= 1:
                        self.thermal_network.R(fromT=layer_left_temperature_name, toT=middle_layer_temperature_name, val=R)
                        self.thermal_network.R(fromT=middle_layer_temperature_name, toT=layer_right_temperature_name, val=R)
                        self.thermal_network.C(toT=middle_layer_temperature_name, val=C)
                    else:
                        sublayer_names, sublayer_border_names = name_layers(layer_left_temperature_name, layer_right_temperature_name, n_sublayers)
                        R = Rfactor * wall_side.Rs1_2[layer_index] / 2 / n_sublayers
                        C = Cfactor * wall_side.Cs1_2[layer_index] / n_sublayers
                        for sublayer_index in range(n_sublayers):
                            sublayer_left_name: str = sublayer_border_names[sublayer_index][0]
                            sublayer_middle_name: str = sublayer_names[sublayer_index]
                            sublayer_right_name: str = sublayer_border_names[sublayer_index][1]
                            self.thermal_network.R(fromT=sublayer_left_name, toT=sublayer_middle_name, val=R)
                            self.thermal_network.R(fromT=sublayer_middle_name, toT=sublayer_right_name, val=R)
                            self.thermal_network.C(toT=sublayer_middle_name, val=C)
        return self.thermal_network

    def __str__(self) -> str:
        string = 'Zones are:\n'
        for zone in self.name_zones:
            string += str(self.name_zones[zone])
        string += 'Wall sides are:\n'
        for wall_side in self.wall_sides:
            string += str(wall_side)
        return string
