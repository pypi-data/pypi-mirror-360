import batem.core.weather
import batem.core.solar
import configparser

location: str = 'Tirana'
latitude_deg_north = 41.330815
longitude_deg_east = 19.819229
weather_year: int = 2023
albedo = 0.1

site_weather_data = batem.core.weather.SiteWeatherDataBuilder().build(
    location=location,
    from_requested_stringdate='1/01/%i' % weather_year,
    to_requested_stringdate='1/01/%i' % (weather_year+1),
    albedo=albedo,
    pollution=0.1,
    given_latitude_north_deg=latitude_deg_north,
    given_longitude_east_deg=longitude_deg_east)

window_solar_mask = None
# window_solar_mask = buildingenergy.solar.RectangularMask((-86, 60), (20, 68))

solar_model = core.solar.SolarModel(site_weather_data)
solar_system = core.solar.SolarSystem(solar_model)
core.solar.Collector(solar_system, 'south', exposure_deg=0, slope_deg=90,
                     surface_m2=1, solar_factor=1, collector_mask=window_solar_mask)
# solar_system.add_collector('south', surface_m2=1, exposure_deg=0, slope_deg=90, solar_factor=1, collector_mask=window_solar_mask)
core.solar.Collector(solar_system, 'east', exposure_deg=-90, slope_deg=90,
                     surface_m2=1, solar_factor=1, collector_mask=window_solar_mask)
# solar_system.add_collector('east', surface_m2=1, exposure_deg=-90, slope_deg=90, solar_factor=1, collector_mask=window_solar_mask)
core.solar.Collector(solar_system, 'west', exposure_deg=90, slope_deg=90,
                     surface_m2=1, solar_factor=1, collector_mask=window_solar_mask)
# solar_system.add_collector('west', surface_m2=1, exposure_deg=90, slope_deg=90, solar_factor=1, collector_mask=window_solar_mask)
core.solar.Collector(solar_system, 'north', exposure_deg=180, slope_deg=90,
                     surface_m2=1, solar_factor=1, collector_mask=window_solar_mask)
core.solar.Collector(solar_system, 'horizontal', exposure_deg=0, slope_deg=180,
                     surface_m2=1, solar_factor=1, collector_mask=window_solar_mask)

# solar_system.add_collector('north', surface_m2=1, exposure_deg=180, slope_deg=90, solar_factor=1, collector_mask=window_solar_mask)

# solar_system.add_collector('horizontal', surface_m2=1, exposure_deg=0, slope_deg=0, solar_factor=1, collector_mask=window_solar_mask)

config = configparser.ConfigParser()
config.read('setup.ini')
solar_system.generate_dd_solar_gain_xls(
    'dju20-26', heat_temperature_reference=20, cool_temperature_reference=26)
