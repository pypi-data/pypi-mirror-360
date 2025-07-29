"""Combined weather model."""

# pylint: disable=too-many-locals,too-many-statements,too-many-branches
from ..weather_model import WeatherModel
from .null_check import is_null


def create_combined_weather_model(
    weather_models: list[WeatherModel],
) -> WeatherModel | None:
    """Create a weather model by combining many weather models."""
    if not weather_models:
        return None
    temperature = None
    relative_humidity = None
    dew_point = None
    apparent_temperature = None
    precipitation_probability = None
    precipitation = None
    rain = None
    showers = None
    snowfall = None
    snow_depth = None
    weather_code = None
    sealevel_pressure = None
    surface_pressure = None
    cloud_cover_total = None
    cloud_cover_low = None
    cloud_cover_mid = None
    cloud_cover_high = None
    visibility = None
    evapotranspiration = None
    reference_evapotranspiration = None
    vapour_pressure_deficit = None
    wind_speed_10m = None
    wind_speed_80m = None
    wind_speed_120m = None
    wind_speed_180m = None
    wind_direction_10m = None
    wind_direction_80m = None
    wind_direction_120m = None
    wind_direction_180m = None
    wind_gusts = None
    temperature_80m = None
    temperature_120m = None
    temperature_180m = None
    soil_temperature_0cm = None
    soil_temperature_6cm = None
    soil_temperature_18cm = None
    soil_temperature_54cm = None
    soil_moisture_0cm = None
    soil_moisture_1cm = None
    soil_moisture_3cm = None
    soil_moisture_9cm = None
    soil_moisture_27cm = None
    daily_weather_code = None
    daily_maximum_temperature_2m = None
    daily_minimum_temperature_2m = None
    daily_maximum_apparent_temperature_2m = None
    daily_minimum_apparent_temperature_2m = None
    sunrise = None
    sunset = None
    daylight_duration = None
    sunshine_duration = None
    uv_index = None
    uv_index_clear_sky = None
    rain_sum = None
    showers_sum = None
    snowfall_sum = None
    precipitation_sum = None
    precipitation_hours = None
    precipitation_probability_max = None
    maximum_wind_speed_10m = None
    maximum_wind_gusts_10m = None
    dominant_wind_direction = None
    shortwave_radiation_sum = None
    daily_reference_evapotranspiration = None
    for weather_model in weather_models:
        weather_model_temperature = weather_model.temperature
        if not is_null(weather_model_temperature):
            temperature = weather_model_temperature
        weather_model_relative_humidity = weather_model.relative_humidity
        if not is_null(weather_model_relative_humidity):
            relative_humidity = weather_model_relative_humidity
        weather_model_dew_point = weather_model.dew_point
        if not is_null(weather_model_dew_point):
            dew_point = weather_model_dew_point
        weather_model_apparent_temperature = weather_model.apparent_temperature
        if not is_null(weather_model_apparent_temperature):
            apparent_temperature = weather_model_apparent_temperature
        weather_model_precipitation_probability = (
            weather_model.precipitation_probability
        )
        if not is_null(weather_model_precipitation_probability):
            precipitation_probability = weather_model_precipitation_probability
        weather_model_precipitation = weather_model.precipitation
        if not is_null(weather_model_precipitation):
            precipitation = weather_model_precipitation
        weather_model_rain = weather_model.rain
        if not is_null(weather_model_rain):
            rain = weather_model_rain
        weather_model_showers = weather_model.showers
        if not is_null(weather_model_showers):
            showers = weather_model_showers
        weather_model_snowfall = weather_model.snowfall
        if not is_null(weather_model_snowfall):
            snowfall = weather_model_snowfall
        weather_model_snow_depth = weather_model.snow_depth
        if not is_null(weather_model_snow_depth):
            snow_depth = weather_model_snow_depth
        weather_model_weather_code = weather_model.weather_code
        if not is_null(weather_model_weather_code):
            weather_code = weather_model_weather_code
        weather_model_sealevel_pressure = weather_model.sealevel_pressure
        if not is_null(weather_model_sealevel_pressure):
            sealevel_pressure = weather_model_sealevel_pressure
        weather_model_surface_pressure = weather_model.surface_pressure
        if not is_null(weather_model_surface_pressure):
            surface_pressure = weather_model_surface_pressure
        weather_model_cloud_cover_total = weather_model.cloud_cover_total
        if not is_null(weather_model_cloud_cover_total):
            cloud_cover_total = weather_model_cloud_cover_total
        weather_model_cloud_cover_low = weather_model.cloud_cover_low
        if not is_null(weather_model_cloud_cover_low):
            cloud_cover_low = weather_model_cloud_cover_low
        weather_model_cloud_cover_mid = weather_model.cloud_cover_mid
        if not is_null(weather_model_cloud_cover_mid):
            cloud_cover_mid = weather_model_cloud_cover_mid
        weather_model_cloud_cover_high = weather_model.cloud_cover_high
        if not is_null(weather_model_cloud_cover_high):
            cloud_cover_high = weather_model_cloud_cover_high
        weather_model_visibility = weather_model.visibility
        if not is_null(weather_model_visibility):
            visibility = weather_model_visibility
        weather_model_evapotranspiration = weather_model.evapotranspiration
        if not is_null(weather_model_evapotranspiration):
            evapotranspiration = weather_model_evapotranspiration
        weather_model_reference_evapotranspiration = (
            weather_model.reference_evapotranspiration
        )
        if not is_null(weather_model_reference_evapotranspiration):
            reference_evapotranspiration = weather_model_reference_evapotranspiration
        weather_model_vapour_pressure_deficit = weather_model.vapour_pressure_deficit
        if not is_null(weather_model_vapour_pressure_deficit):
            vapour_pressure_deficit = weather_model_vapour_pressure_deficit
        weather_model_wind_speed_10m = weather_model.wind_speed_10m
        if not is_null(weather_model_wind_speed_10m):
            wind_speed_10m = weather_model_wind_speed_10m
        weather_model_wind_speed_80m = weather_model.wind_speed_80m
        if not is_null(weather_model_wind_speed_80m):
            wind_speed_80m = weather_model_wind_speed_80m
        weather_model_wind_speed_120m = weather_model.wind_speed_120m
        if not is_null(weather_model_wind_speed_120m):
            wind_speed_120m = weather_model_wind_speed_120m
        weather_model_wind_speed_180m = weather_model.wind_speed_180m
        if not is_null(weather_model_wind_speed_180m):
            wind_speed_180m = weather_model.wind_speed_180m
        weather_model_wind_direction_10m = weather_model.wind_direction_10m
        if not is_null(weather_model_wind_direction_10m):
            wind_direction_10m = weather_model.wind_direction_10m
        weather_model_wind_direction_80m = weather_model.wind_direction_80m
        if not is_null(weather_model_wind_direction_80m):
            wind_direction_80m = weather_model_wind_direction_80m
        weather_model_wind_direction_120m = weather_model.wind_direction_120m
        if not is_null(weather_model_wind_direction_120m):
            wind_direction_120m = weather_model_wind_direction_120m
        weather_model_wind_direction_180m = weather_model.wind_direction_180m
        if not is_null(weather_model_wind_direction_180m):
            wind_direction_180m = weather_model_wind_direction_180m
        weather_model_wind_gusts = weather_model.wind_gusts
        if not is_null(weather_model_wind_gusts):
            wind_gusts = weather_model_wind_gusts
        weather_model_temperature_80m = weather_model.temperature_80m
        if not is_null(weather_model_temperature_80m):
            temperature_80m = weather_model_temperature_80m
        weather_model_temperature_120m = weather_model.temperature_120m
        if not is_null(weather_model_temperature_120m):
            temperature_120m = weather_model_temperature_120m
        weather_model_temperature_180m = weather_model.temperature_180m
        if not is_null(weather_model_temperature_180m):
            temperature_180m = weather_model_temperature_180m
        weather_model_soil_temperature_0cm = weather_model.soil_temperature_0cm
        if not is_null(weather_model_soil_temperature_0cm):
            soil_temperature_0cm = weather_model_soil_temperature_0cm
        weather_model_soil_temperature_6cm = weather_model.soil_temperature_6cm
        if not is_null(weather_model_soil_temperature_6cm):
            soil_temperature_6cm = weather_model_soil_temperature_6cm
        weather_model_soil_temperature_18cm = weather_model.soil_temperature_18cm
        if not is_null(weather_model_soil_temperature_18cm):
            soil_temperature_18cm = weather_model_soil_temperature_18cm
        weather_model_soil_temperature_54cm = weather_model.soil_temperature_54cm
        if not is_null(weather_model_soil_temperature_54cm):
            soil_temperature_54cm = weather_model_soil_temperature_54cm
        weather_model_soil_moisture_0cm = weather_model.soil_moisture_0cm
        if not is_null(weather_model_soil_moisture_0cm):
            soil_moisture_0cm = weather_model.soil_moisture_0cm
        weather_model_soil_moisture_1cm = weather_model.soil_moisture_1cm
        if not is_null(weather_model_soil_moisture_1cm):
            soil_moisture_1cm = weather_model_soil_moisture_1cm
        weather_model_soil_moisture_3cm = weather_model.soil_moisture_3cm
        if not is_null(weather_model_soil_moisture_3cm):
            soil_moisture_3cm = weather_model_soil_moisture_3cm
        weather_model_soil_moisture_9cm = weather_model.soil_moisture_9cm
        if not is_null(weather_model_soil_moisture_9cm):
            soil_moisture_9cm = weather_model_soil_moisture_9cm
        weather_model_soil_moisture_27cm = weather_model.soil_moisture_27cm
        if not is_null(weather_model_soil_moisture_27cm):
            soil_moisture_27cm = weather_model_soil_moisture_27cm
        weather_model_daily_weather_code = weather_model.daily_weather_code
        if not is_null(weather_model_daily_weather_code):
            daily_weather_code = weather_model_daily_weather_code
        weather_model_daily_maximum_temperature_2m = (
            weather_model.daily_maximum_temperature_2m
        )
        if not is_null(weather_model_daily_maximum_temperature_2m):
            daily_maximum_temperature_2m = weather_model_daily_maximum_temperature_2m
        weather_model_daily_minimum_temperature_2m = (
            weather_model.daily_minimum_temperature_2m
        )
        if not is_null(weather_model_daily_minimum_temperature_2m):
            daily_minimum_temperature_2m = weather_model_daily_minimum_temperature_2m
        weather_model_daily_maximum_apparent_temperature_2m = (
            weather_model.daily_maximum_apparent_temperature_2m
        )
        if not is_null(weather_model_daily_maximum_apparent_temperature_2m):
            daily_maximum_apparent_temperature_2m = (
                weather_model_daily_maximum_apparent_temperature_2m
            )
        weather_model_daily_minimum_apparent_temperature_2m = (
            weather_model.daily_minimum_apparent_temperature_2m
        )
        if not is_null(weather_model_daily_minimum_apparent_temperature_2m):
            daily_minimum_apparent_temperature_2m = (
                weather_model_daily_minimum_apparent_temperature_2m
            )
        weather_model_sunrise = weather_model.sunrise
        if not is_null(weather_model_sunrise):
            sunrise = weather_model_sunrise
        weather_model_sunset = weather_model.sunset
        if not is_null(weather_model_sunset):
            sunset = weather_model_sunset
        weather_model_daylight_duration = weather_model.daylight_duration
        if not is_null(weather_model_daylight_duration):
            daylight_duration = weather_model_daylight_duration
        weather_model_sunshine_duration = weather_model.sunshine_duration
        if not is_null(weather_model_sunshine_duration):
            sunshine_duration = weather_model_sunshine_duration
        weather_model_uv_index = weather_model.uv_index
        if not is_null(weather_model_uv_index):
            uv_index = weather_model_uv_index
        weather_model_uv_index_clear_sky = weather_model.uv_index_clear_sky
        if not is_null(weather_model_uv_index_clear_sky):
            uv_index_clear_sky = weather_model_uv_index_clear_sky
        weather_model_rain_sum = weather_model.rain_sum
        if not is_null(weather_model_rain_sum):
            rain_sum = weather_model_rain_sum
        weather_model_showers_sum = weather_model.showers_sum
        if not is_null(weather_model_showers_sum):
            showers_sum = weather_model_showers_sum
        weather_model_snowfall_sum = weather_model.snowfall_sum
        if not is_null(weather_model_snowfall_sum):
            snowfall_sum = weather_model_snowfall_sum
        weather_model_precipitation_sum = weather_model.precipitation_sum
        if not is_null(weather_model_precipitation_sum):
            precipitation_sum = weather_model_precipitation_sum
        weather_model_precipitation_hours = weather_model.precipitation_hours
        if not is_null(weather_model_precipitation_hours):
            precipitation_hours = weather_model_precipitation_hours
        weather_model_precipitation_probability_max = (
            weather_model.precipitation_probability_max
        )
        if not is_null(weather_model_precipitation_probability_max):
            precipitation_probability_max = weather_model_precipitation_probability_max
        weather_model_maximum_wind_speed_10m = weather_model.maximum_wind_speed_10m
        if not is_null(weather_model_maximum_wind_speed_10m):
            maximum_wind_speed_10m = weather_model_maximum_wind_speed_10m
        weather_model_maximum_wind_gusts_10m = weather_model.maximum_wind_gusts_10m
        if not is_null(weather_model_maximum_wind_gusts_10m):
            maximum_wind_gusts_10m = weather_model_maximum_wind_gusts_10m
        weather_model_dominant_wind_direction = weather_model.dominant_wind_direction
        if not is_null(weather_model_dominant_wind_direction):
            dominant_wind_direction = weather_model.dominant_wind_direction
        weather_model_shortwave_radiation_sum = weather_model.shortwave_radiation_sum
        if not is_null(weather_model_shortwave_radiation_sum):
            shortwave_radiation_sum = weather_model_shortwave_radiation_sum
        weather_model_daily_reference_evapotranspiration = (
            weather_model.daily_reference_evapotranspiration
        )
        if not is_null(weather_model_daily_reference_evapotranspiration):
            daily_reference_evapotranspiration = (
                weather_model_daily_reference_evapotranspiration
            )

    return WeatherModel(
        temperature=temperature,
        relative_humidity=relative_humidity,
        dew_point=dew_point,
        apparent_temperature=apparent_temperature,
        precipitation_probability=precipitation_probability,
        precipitation=precipitation,
        rain=rain,
        showers=showers,
        snowfall=snowfall,
        snow_depth=snow_depth,
        weather_code=weather_code,
        sealevel_pressure=sealevel_pressure,
        surface_pressure=surface_pressure,
        cloud_cover_total=cloud_cover_total,
        cloud_cover_low=cloud_cover_low,
        cloud_cover_mid=cloud_cover_mid,
        cloud_cover_high=cloud_cover_high,
        visibility=visibility,
        evapotranspiration=evapotranspiration,
        reference_evapotranspiration=reference_evapotranspiration,
        vapour_pressure_deficit=vapour_pressure_deficit,
        wind_speed_10m=wind_speed_10m,
        wind_speed_80m=wind_speed_80m,
        wind_speed_120m=wind_speed_120m,
        wind_speed_180m=wind_speed_180m,
        wind_direction_10m=wind_direction_10m,
        wind_direction_80m=wind_direction_80m,
        wind_direction_120m=wind_direction_120m,
        wind_direction_180m=wind_direction_180m,
        wind_gusts=wind_gusts,
        temperature_80m=temperature_80m,
        temperature_120m=temperature_120m,
        temperature_180m=temperature_180m,
        soil_temperature_0cm=soil_temperature_0cm,
        soil_temperature_6cm=soil_temperature_6cm,
        soil_temperature_18cm=soil_temperature_18cm,
        soil_temperature_54cm=soil_temperature_54cm,
        soil_moisture_0cm=soil_moisture_0cm,
        soil_moisture_1cm=soil_moisture_1cm,
        soil_moisture_3cm=soil_moisture_3cm,
        soil_moisture_9cm=soil_moisture_9cm,
        soil_moisture_27cm=soil_moisture_27cm,
        daily_weather_code=daily_weather_code,
        daily_maximum_temperature_2m=daily_maximum_temperature_2m,
        daily_minimum_temperature_2m=daily_minimum_temperature_2m,
        daily_maximum_apparent_temperature_2m=daily_maximum_apparent_temperature_2m,
        daily_minimum_apparent_temperature_2m=daily_minimum_apparent_temperature_2m,
        sunrise=sunrise,
        sunset=sunset,
        daylight_duration=daylight_duration,
        sunshine_duration=sunshine_duration,
        uv_index=uv_index,
        uv_index_clear_sky=uv_index_clear_sky,
        rain_sum=rain_sum,
        showers_sum=showers_sum,
        snowfall_sum=snowfall_sum,
        precipitation_sum=precipitation_sum,
        precipitation_hours=precipitation_hours,
        precipitation_probability_max=precipitation_probability_max,
        maximum_wind_speed_10m=maximum_wind_speed_10m,
        maximum_wind_gusts_10m=maximum_wind_gusts_10m,
        dominant_wind_direction=dominant_wind_direction,
        shortwave_radiation_sum=shortwave_radiation_sum,
        daily_reference_evapotranspiration=daily_reference_evapotranspiration,
    )
