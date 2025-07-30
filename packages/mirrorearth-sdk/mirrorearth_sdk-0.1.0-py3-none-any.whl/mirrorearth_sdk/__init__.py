from .parse import get_flat_response, WeatherResponse
from functools import partial
import requests


def get_meteo_data(longitude: str, latitude: str, apikey: str, path: str,
                   hourly=None, daily=None, forecast_days=None, 
                   past_days=None, start_date=None, end_date=None, 
                   start_hour=None, end_hour=None, forecast_hours=None, 
                   temporal_resolution=None, models=None, timezone=None) -> WeatherResponse:
    """
    获取气象数据的主要函数
    
    该函数通过 Mirror Earth API 获取指定位置的气象数据，支持多种时间范围和气象要素。
    
    Args:
        longitude (str): 经度，多个经度用逗号分隔，必须和latitude数量一致，例如 "118,119"
        latitude (str): 纬度，多个纬度用逗号分隔，必须和longitude数量一致，例如 "32,33"
        apikey (str): API Key，登录后自动填充，或在个人中心获取
        path (str): API路径，指定要获取的数据类型
        hourly (str, optional): 小时要素，多个要素用逗号分隔，例如 "temperature_2m,precipitation"
        daily (str, optional): 逐日要素，多个要素用逗号分隔，例如 "temperature_2m_max,temperature_2m_min,precipitation_sum"
        forecast_days (int, optional): 预报天数，可以和past_days同时使用，但是不能和start_date/end_date/start_hour/end_hour同时使用
        past_days (int, optional): 过去天数，可以和forecast_days同时使用，但是不能和start_date/end_date/start_hour/end_hour同时使用
        start_date (str, optional): 开始日期，只能搭配end_date使用，例如 "2025-01-01"
        end_date (str, optional): 结束日期，只能搭配start_date使用，例如 "2025-01-02"
        start_hour (str, optional): 开始时间，只能搭配end_hour使用，例如 "2025-01-01T00:00"
        end_hour (str, optional): 结束时间，只能搭配start_hour使用，例如 "2025-01-01T23:00"
        forecast_hours (int, optional): 预报小时数
        temporal_resolution (str, optional): 时间分辨率，默认都是1小时(hourly_1)，可选10分钟(minutely_10)，15分钟(minutely_15)，30分钟(minutely_30)
        models (str, optional): 数据源，多个数据源用逗号分隔，例如 "ecmwf,cma"
        timezone (str, optional): 时区，默认为世界时，auto表示根据经度自动计算全部时区
        
    Returns:
        WeatherResponse
        
    """
    
    url = f"https://api.mirror-earth.com/v1/{path}"
    data = {
        'longitude': longitude,
        'latitude': latitude,
        'apikey': apikey,
        'format': 'flatbuffers'
    }
    if hourly:
        data['hourly'] = hourly
    if daily:
        data['daily'] = daily
    if forecast_days:
        data['forecast_days'] = forecast_days
    if past_days:
        data['past_days'] = past_days
    if start_date:
        data['start_date'] = start_date
    if end_date:
        data['end_date'] = end_date
    if start_hour:
        data['start_hour'] = start_hour
    if end_hour:
        data['end_hour'] = end_hour
    if forecast_hours:
        data['forecast_hours'] = forecast_hours
    if temporal_resolution:
        data['temporal_resolution'] = temporal_resolution
    if models:
        data['models'] = models
    if timezone:
        data['timezone'] = timezone
    
    response = requests.get(url, params=data, headers={'User-Agent': 'api'})
    return get_flat_response(response)


seamless_api = partial(get_meteo_data, path="ec-seamless")
forecast_api = partial(get_meteo_data, path="forecast")
archive_api = partial(get_meteo_data, path="archive")
archive_forecast_api = partial(get_meteo_data, path="archive-forecast")




