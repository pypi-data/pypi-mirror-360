from core.solar import RADIATION_TYPE, SolarModel, SolarSystem, Collector, InvertedMask, RectangularMask
from core.weather import SiteWeatherData, SiteWeatherDataBuilder
from core.utils import TimeSeriesPlotter
from core.data import DataProvider

data_provider = DataProvider('Grenoble', latitude_deg_north=45.190823325765166, longitude_deg_east=5.727264569512632,
                             starting_stringdate='1/01/2023', ending_stringdate='31/12/2023', albedo=0.1, pollution=0.1)
grenoble_weather_data: SiteWeatherData = data_provider.weather_data
grenoble_solar_model = SolarModel(grenoble_weather_data)

grenoble_solar_system = SolarSystem(grenoble_solar_model)
reflectivity_limit = 30
directions: dict[str, tuple[int, int]] = {'top': (
    0, 0), 'east': (-90, 90), 'south': (0, 90), 'west': (90, 90), 'north': (180, 90)}
for d in directions:
    exposure_deg, slope_deg = directions[d]
    Collector(grenoble_solar_system, d, surface_m2=1, exposure_deg=exposure_deg, slope_deg=slope_deg, solar_factor=1, collector_mask=InvertedMask(
        RectangularMask((exposure_deg-90+reflectivity_limit, exposure_deg-reflectivity_limit), (slope_deg-90+reflectivity_limit, slope_deg+90-reflectivity_limit))))
    axes = grenoble_solar_model.plot_heliodon(2013, d)
    grenoble_solar_system.plot_mask(d)

global_solar_gains_with_mask: dict[str, dict[RADIATION_TYPE, list[float]]
                                   ] = grenoble_solar_system.solar_gains_W(gather_collectors=False)
for d in directions:
    data_provider.add_external_variable(
        d+' irradiance Wh', global_solar_gains_with_mask[d])
    print('total_solar_gain with mask in kWh (%s):' %
          d, sum(global_solar_gains_with_mask[d])/1000)
data_provider.plot()
# solar_system.collector()


# cayenne_weather_data: SiteWeatherData = WeatherJsonReader(location='Cayenne', from_requested_stringdate='1/01/2023', to_requested_stringdate='31/12/2023', albedo=0.1, pollution=0.1, latitude_deg_north=4.924435336591809, longitude_deg_east=-52.31276008988111).site_weather_data
# cayenne_solar_model = SolarModel(cayenne_weather_data)

# sydney_weather_data: SiteWeatherData = WeatherJsonReader(location='Sydney', from_requested_stringdate='1/01/2023', to_requested_stringdate='2/01/2023', albedo=0.1, pollution=0.1, latitude_deg_north=-33.854658939897334, longitude_deg_east=151.20826073584536).site_weather_data
# sydney_weather_data.plot()
# sydney_solar_model = SolarModel(sydney_weather_data)

# grenoble_solar_model.plot_angles(with_matplotlib=False)
# cayenne_solar_model.plot_angles(with_matplotlib=False)
# sydney_solar_model.plot_angles(with_matplotlib=False)
