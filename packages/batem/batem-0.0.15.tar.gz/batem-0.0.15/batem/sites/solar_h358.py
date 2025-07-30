"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0
"""
from __future__ import annotations
import matplotlib.pyplot as plt
import core.solar
import core.weather
from pandas.plotting import register_matplotlib_converters
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from core.library import DIRECTIONS_SREF, SLOPES

register_matplotlib_converters()
site_weather_data: core.weather.SiteWeatherData = core.weather.SiteWeatherDataBuilder(
    location='Grenoble', from_requested_stringdate="1/01/2019", to_requested_stringdate="31/12/2019", given_latitude_north_deg=45.19154994547585, given_longitude_east_deg=5.722065312331381).site_weather_data
solar_model = core.solar.SolarModel(site_weather_data)

fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
officeH358_with_mask = core.solar.SolarSystem(solar_model)
core.solar.Collector(officeH358_with_mask, 'main', surface_m2=2, exposure_deg=-13, slope_deg=90,
                     solar_factor=0.85, collector_mask=core.solar.InvertedMask(core.solar.RectangularMask((-86, 60), (20, 68))))
officeH358_with_mask.generate_dd_solar_gain_xls(
    'officeH358', heat_temperature_reference=21, cool_temperature_reference=26)
global_solar_gains_with_mask = officeH358_with_mask.solar_gains_W(
    gather_collectors=True)
print('total_solar_gain with mask in kWh:',
      sum(global_solar_gains_with_mask)/1000)
# for g in detailed_solar_gains_with_mask:
#     fig.add_trace(go.Scatter(x=officeH358_with_mask.datetimes, y=detailed_solar_gains_with_mask[g], name='%s solar gain with mask in Wh' % g, line_shape='hv'), row=1, col=1)

officeH358_nomask = core.solar.SolarSystem(solar_model)
core.solar.Collector(officeH358_nomask, 'window', surface_m2=2,
                     exposure_deg=-13, slope_deg=90, solar_factor=0.85, collector_mask=None)
global_solar_gains_without_mask = officeH358_nomask.solar_gains_W(
    gather_collectors=True)
print('total_solar_gain without mask in kWh:',
      sum(global_solar_gains_without_mask)/1000)
# for g in detailed_solar_gains_without_mask:
#     fig.add_trace(go.Scatter(x=officeH358_nomask.datetimes, y=detailed_solar_gains_without_mask[g], name='%s solar gain without mask in Wh' % g, line_shape='hv'), row=1, col=1)
# fig.update_layout(title="total heat gain", xaxis_title="date & time (each hour)", yaxis_title="collected heat in Wh")
# fig.show()

register_matplotlib_converters()
site_weather_data = core.weather.SiteWeatherDataBuilder(location='Grenoble', from_requested_stringdate='01/01/2005', to_requested_stringdate='01/01/2006',
                                                        albedo=.1, given_latitude_north_deg=45.19154994547585, given_longitude_east_deg=5.722065312331381).site_weather_data

# solar_model.plot_solar_cardinal_irradiations()

tests = ((DIRECTIONS_SREF.SOUTH, SLOPES.VERTICAL), (DIRECTIONS_SREF.NORTH, SLOPES.VERTICAL), (DIRECTIONS_SREF.EAST, SLOPES.VERTICAL), (DIRECTIONS_SREF.WEST, SLOPES.VERTICAL), (DIRECTIONS_SREF.SOUTH, SLOPES.HORIZONTAL_UP),
         (DIRECTIONS_SREF.NORTH, SLOPES.HORIZONTAL_UP), (DIRECTIONS_SREF.EAST, SLOPES.HORIZONTAL_UP), (DIRECTIONS_SREF.WEST, SLOPES.HORIZONTAL_UP), (DIRECTIONS_SREF.SOUTH, SLOPES.BEST), (DIRECTIONS_SREF.SOUTH, SLOPES.HORIZONTAL_DOWN),)

solar_system = core.solar.SolarSystem(solar_model)
for test in tests:
    print(test)
    exposure_deg, slope_deg = test
    core.solar.Collector(solar_system, exposure_deg.name+'|'+slope_deg.name, surface_m2=1.6,
                         exposure_deg=exposure_deg.value, slope_deg=slope_deg.value, solar_factor=.2)

fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
phis = solar_system.solar_gains_W()
for test in tests:
    collector_name = test[0].name + '|' + test[1].name
    print("Collected Energy on %s: %.2fkWh about %.2f€" % (collector_name,
          sum(phis[collector_name])/1000, sum(phis[collector_name])/1000*.2))
    fig.add_trace(go.Scatter(x=solar_model.site_weather_data.get(
        'datetime'), y=phis[collector_name], name=collector_name, line_shape='hv'), row=1, col=1)

fig.update_layout(title="total heat gain",
                  xaxis_title="date & time (each hour)", yaxis_title="collected heat in Wh")
fig.show()

# solar_model.plot_angles()
# solar_model.plot_heliodon(2015, 'heliodon')
# plt.show()
