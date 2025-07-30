"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0
"""
from __future__ import annotations
from ..core.library import SIDE_TYPES
from ..core.components import BlockWallSide, LayeredWallSide
from ..core.statemodel import StateModel
from ..core.data import DataProvider
from ..core.inhabitants import Preference
from ..core.model import BuildingStateModelMaker
from ..sites.data_h358 import make_data_provider
import time


def make_building_state_model_k(dp: DataProvider, periodic_depth_seconds=60*60, state_model_order_max=3, control: bool = False) -> tuple[BuildingStateModelMaker, StateModel]:
    # Construction of the wall sides and specification of the maximum order of the resulting state model but also tune the decomposition of layers into sublayer for a more precise simulation based on the depth penetration of a sine wave
    state_model_maker = BuildingStateModelMaker('office', 'corridor', 'downstairs', data_provider=dp, periodic_depth_seconds=periodic_depth_seconds, state_model_order_max=state_model_order_max)

    # construction of the wall sides between the office and the corridor

    door_surface: float = 80e-2 * 200e-2
    door: LayeredWallSide = state_model_maker.layered_wall_side('office', 'corridor', SIDE_TYPES.DOOR, door_surface)
    door.layer('wood', 5e-3)
    door.layer('air', 15e-3)
    door.layer('wood', 5e-3)

    glass_surface: float = 100e-2 * 100e-2
    glass: LayeredWallSide = state_model_maker.layered_wall_side('office', 'corridor', SIDE_TYPES.GLAZING, glass_surface)
    glass.layer('glass', 4e-3)
    internal_wall_thickness: float = 13e-3 + 34e-3 + 13e-3
    cupboard_corridor_surface: float = (185e-2 + internal_wall_thickness + 34e-2 + 20e-3) * 2.5
    corridor_wall_surface: float = (408e-2 + 406e-2 + internal_wall_thickness) * 2.5 - door_surface - glass_surface - cupboard_corridor_surface

    cupboard: LayeredWallSide = state_model_maker.layered_wall_side('office', 'corridor', SIDE_TYPES.WALL, cupboard_corridor_surface)
    cupboard.layer('plaster', 13e-3)
    cupboard.layer('foam', 34e-3)
    cupboard.layer('plaster', 13e-3)
    cupboard.layer('air', 50e-2 - 20e-3)
    cupboard.layer('wood', 20e-3)

    plain_corridor_wall: LayeredWallSide = state_model_maker.layered_wall_side('office', 'corridor', SIDE_TYPES.WALL, corridor_wall_surface)
    plain_corridor_wall.layer('plaster', 13e-3)
    plain_corridor_wall.layer('foam', 34e-3)
    plain_corridor_wall.layer('plaster', 13e-3)

    # construction of the wall sides between outdoor wall

    west_glass_surface: float = 2 * 130e-2 * 52e-2 + 27e-2 * 52e-2 + 72e-2 * 52e-2
    east_glass_surface: float = 36e-2 * 56e-2
    windows_surface: float = west_glass_surface + east_glass_surface
    no_cavity_surface: float = (685e-2 - 315e-2 - 60e-2) * 2.5 - east_glass_surface
    cavity_surface: float = 315e-2 * 2.5 - west_glass_surface

    windows: LayeredWallSide = state_model_maker.layered_wall_side('office', 'outdoor', SIDE_TYPES.WALL, windows_surface)
    windows.layer('glass', 4e-3)
    windows.layer('air', 12e-3)
    windows.layer('glass', 4e-3)

    plain_wall: LayeredWallSide = state_model_maker.layered_wall_side('office', 'outdoor', SIDE_TYPES.WALL, no_cavity_surface)
    plain_wall.layer('concrete', 30e-2)

    cavity_wall: LayeredWallSide = state_model_maker.layered_wall_side('office', 'outdoor', SIDE_TYPES.WALL, cavity_surface)
    cavity_wall.layer('concrete', 30e-2)
    cavity_wall.layer('air', 34e-2)
    cavity_wall.layer('wood', 20e-3)

    bridge: BlockWallSide = state_model_maker.block_wall_side('office', 'outdoor', SIDE_TYPES.BRIDGE, 0.5 * 0.99 * 685e-2)  # thermal bridge obtained from ThBAT booklet 5, 3.1.1.2, 22B)  # noqa

    # construction of the slab

    slab_thickness = 11.9e-2
    slab_surface: float = (309e-2 + 20e-3 + 34e-2) * (406e-2 + internal_wall_thickness) + 408e-2 * (273e-2 - 60e-2) - 315e-2 * (34e-2 + 20e-3) - (185e-3 + internal_wall_thickness) * 50e-2
    slab: LayeredWallSide = state_model_maker.layered_wall_side('office', 'downstairs', SIDE_TYPES.WALL, slab_surface)
    slab.layer('concrete', slab_thickness)
    slab.layer('air', 20e-2)
    slab.layer('polystyrene', 7e-3)

    # construction of the airflows between zones

    state_model_maker.simulate_zone('office')
    state_model_maker.connect_airflow('office', 'corridor', dp('corridor-office:Q_0'))  # nominal value
    state_model_maker.connect_airflow('office', 'outdoor', dp('office-outdoor:Q_0'))  # nominal value

    nominal_state_model = state_model_maker.make_k()
    return state_model_maker, nominal_state_model


if __name__ == '__main__':
    dp: DataProvider = make_data_provider(starting_stringdate='15/02/2015', ending_stringdate='15/02/2016')
    state_model_maker, nominal_state_model = make_building_state_model_k(dp)
    # display the characteristics of the resulting building
    print('Building characteristics:')
    print(state_model_maker)

    print('\nState model characteristics:')
    print(nominal_state_model)

    # load data and plot results
    print('Loading data...')

    start: float = time.time()
    nominal_state_model.simulate(dp, suffix='_LN')
    print('\nmodel simulation duration: %f secondes' % (time.time() - start))

    # heating period: from April, 15th 2015 --> October, 15th 2015
    preference = Preference(preferred_temperatures=(21, 23), extreme_temperatures=(18, 26), preferred_CO2_concentration=(500, 1500), temperature_weight_wrt_CO2=0.5, power_weight_wrt_comfort=0.5e-3, mode_cop={1: 1, -1: 2})
    preference.print_assessment(datetimes=dp.series('datetime'), Pheater=dp.series('office:Pheater'), modes=None, temperatures=dp.series('Toffice_reference'), CO2_concentrations=dp.series('office_CO2_concentration'), occupancies=dp.series('occupancy'), action_sets=(dp.series('window_opening'), dp.series('window_opening')))

    dp.plot()
