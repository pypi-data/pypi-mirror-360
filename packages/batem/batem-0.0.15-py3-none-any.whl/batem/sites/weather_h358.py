"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0
"""
from __future__ import annotations
import core.weather
import core.solar
import core.timemg
import matplotlib.pylab as plt
# import matplotlib.colors as mcolors
from pandas.plotting import register_matplotlib_converters
from matplotlib.patches import Ellipse
from datetime import datetime


def plot_rain_events(datetimes: list[datetime], precipitations: list[float], ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    days_with_rain: list[str] = list()
    days: list[str] = list()
    rains_dict: dict[tuple[float, float], int] = dict()
    rains_months_dict: dict[tuple[float, float], list[str]] = dict()
    rain_duration: int = 0
    max_duration = 0
    rain_quantity: float = 0
    max_quantity = 0
    threshold = 0.1
    was_raining = False
    for k, precipitation in enumerate(precipitations):
        stringdate = core.timemg.datetime_to_stringdate(
            datetimes[k]).split(' ')[0]
        if stringdate not in days:
            days.append(stringdate)
        if was_raining and precipitation > 0:  # ongoing rain event
            rain_duration += 1
            rain_quantity += precipitation
            if stringdate not in days_with_rain:
                days_with_rain.append(stringdate)
        elif was_raining and precipitation == 0:  # end of rain event
            characteristics: tuple[int, int] = (
                rain_duration, round(10*rain_quantity/rain_duration)/10)
            max_duration: int = max(max_duration, characteristics[0])
            max_quantity: int = max(max_quantity, characteristics[1])
            month = datetimes[k].month
            if characteristics in rains_dict:
                rains_dict[characteristics] += 1
                if str(month) not in rains_months_dict[characteristics]:
                    rains_months_dict[characteristics].append(str(month))
            else:
                rains_dict[characteristics] = 1
                rains_months_dict[characteristics] = [str(month)]
            was_raining = False
            rain_duration = 0
            rain_quantity = 0
        elif not was_raining and precipitation > threshold:  # beginning of rain event
            if stringdate not in days_with_rain:
                days_with_rain.append(stringdate)
            rain_duration = 1
            rain_quantity = precipitation
            was_raining = True

    ax.set(xlim=(0, max_duration), ylim=(0, max_quantity))
    for characteristics in rains_dict:
        ellipse = Ellipse(characteristics, width=rains_dict[characteristics],
                          height=rains_dict[characteristics], edgecolor='black', facecolor='orange')
        ax.add_artist(ellipse)
        # ellipse.set_clip_box(ax.bbox)
        ellipse.set_alpha(0.5)
        plt.annotate(
            ','.join(rains_months_dict[characteristics]), characteristics)
    ax.set_title('rain events (numbers stands for month# (%i raining days out of %i)' % (
        len(days_with_rain), len(days)))
    ax.set_xlabel('duration in hours')
    ax.set_ylabel('quantity in mm')


register_matplotlib_converters()
site_weather_data = core.weather.SiteWeatherDataBuilder().build(
    location='grenoble',
    from_requested_stringdate='1/01/2019',
    to_requested_stringdate='1/01/2020',
    albedo=.1,
    given_latitude_north_deg=45.19154994547585,
    given_longitude_east_deg=5.722065312331381)

print(site_weather_data)

solar_model = core.solar.SolarModel(site_weather_data)


fig, ax = plt.subplots()
plt.plot(site_weather_data.get('datetime'), site_weather_data.get(
    'direct_radiation'), label='direct (weather)')  # total
plt.plot(site_weather_data.get('datetime'), site_weather_data.get(
    'diffuse_radiation'), label='diffuse (weather)')  # diffuse
plt.plot(site_weather_data.get('datetime'), site_weather_data.get(
    'direct_normal_irradiance'), label='normal (weather)')  # direct
# - 90 east, 90 west, 0 south, 180 north (clockwise with South as reference)
exposure = 0
slope = 0  # 0 facing the sky, 90 facing the exposure
# , mask=buildingenergy.solar.RectangularMask(minmax_azimuths_deg=(-90+exposure, 90+exposure), minmax_altitudes_deg=(-90+slope, 90+slope))
irradiances = solar_model.irradiance_W(exposure_deg=exposure, slope_deg=slope)

print('openmeteo (direct): %f' %
      (sum(site_weather_data.get('direct_radiation'))/1000))
print('calculus: %f' %
      (sum(irradiances[core.solar.RADIATION_TYPE.DIRECT])/1000))

plt.plot(site_weather_data.get('datetime'),
         # direct
         irradiances[core.solar.RADIATION_TYPE.DIRECT], label='model_direct')
plt.plot(site_weather_data.get('datetime'),
         # diffuse
         irradiances[core.solar.RADIATION_TYPE.DIFFUSE], label='model_diffuse')
plt.plot(site_weather_data.get('datetime'),
         irradiances[core.solar.RADIATION_TYPE.REFLECTED], label='model_reflected')
plt.plot(site_weather_data.get('datetime'),
         # total
         irradiances[core.solar.RADIATION_TYPE.TOTAL], label='model_total')
plt.plot(site_weather_data.get('datetime'),
         # normal
         irradiances[core.solar.RADIATION_TYPE.NORMAL], label='model_normal')

ax.set_title('irradiances')
plt.legend()
ax.axis('tight')
# fig, ax = plt.subplots()
# plt.plot(site_weather_data2.get('datetime'), solar_model.sun_altitudes_deg, label='altitude')
# plt.plot(site_weather_data2.get('datetime'), solar_model.sun_azimuths_deg, label = 'azimuth')
# ax.set_title('angles')
# plt.legend()
# ax.axis('tight')

# datetimes: list[float] = site_weather_data.get('datetime')
# precipitations: list[float] = site_weather_data.get('precipitation')
# plot_rain_events(datetimes, precipitations)
plt.show()
