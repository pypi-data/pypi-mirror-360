# MirrorEarth SDK

Python SDK for accessing Open Mirror Earth API data.

## Installation

```
pip install .
```

## Quick Start

**使用前必备**

登录[镜像地球开放平台](https://open.mirror-earth.com)，个人中心中获取apikey

### 使用预报数据API

文档: [链接](https://open.mirror-earth.com/docs/get-started/2-forecast-api)

```python
from mirrorearth_sdk import forecast_api


elements = [
    'temperature_2m', 'dew_point_2m', 'surface_temperature', 'temperature_80m', 'temperature_100m',
    'wet_bulb_temperature_2m', 'wind_gusts_10m', 'wind_speed_10m', 'wind_direction_10m', 'wind_speed_20m',
    'cloud_cover', 'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high',
    'shortwave_radiation', 'longwave_radiation_downward', 'shortwave_radiation_upward', 'longwave_radiation_upward', 'soil_temperature_0_to_10cm',
    'soil_temperature_10_to_40cm', 'soil_temperature_40_to_100cm', 'soil_temperature_100_to_200cm', 'soil_moisture_0_to_10cm', 'soil_moisture_10_to_40cm',
    'soil_moisture_40_to_100cm', 'soil_moisture_100_to_200cm', 'precipitation', 'snow_depth', 'pressure_msl',
    'surface_pressure', 'visibility', 'relative_humidity_2m', 'vapour_pressure_deficit'
]
apikey = '请在镜像地球开放平台，个人中心获取'

resp = forecast_api(lon='118', lat='32', apikey=apikey, hourly=','.join(elements), daily='temperature_2m_max', models='ecmwf', forecast_days=15)
point1 = resp[0]  # 通过下标获取第一个坐标点的数据，如果传入了多个坐标，可以循环获得数据
print(point1.metedata) # 打印元数据
print(point1.hourly_df())  # 获取hourly小时级(或者是分钟级)数据，是一个DataFrame
print(point1.daily_df()) # 获取daily逐日数据

>>> output:
Metadata(location: 0, coords: (32.0, 118.0), model: gfs025)

                     temperature_2m_°C  dew_point_2m_°C  ...  visibility_m  relative_humidity_2m_%
2025-05-15 08:00:00          22.450001        18.423653  ...       24135.0               78.000000
2025-05-15 09:00:00          23.150000        18.686502  ...       24135.0               76.000000
2025-05-15 10:00:00          23.049999        18.798883  ...       24135.0               77.000000
2025-05-15 11:00:00          23.900000        18.983398  ...       24135.0               74.000000
2025-05-15 12:00:00          23.150000        19.307074  ...       24135.0               79.000000
...                                ...              ...  ...           ...                     ...
2025-05-31 04:00:00          19.448149        11.189207  ...       24135.0               58.851852
2025-05-31 05:00:00          19.299999        11.088128  ...       24135.0               59.000000
2025-05-31 06:00:00          19.322222        11.259768  ...       24135.0               59.592594
2025-05-31 07:00:00          19.449999        11.585191  ...       24135.0               60.407406
2025-05-31 08:00:00          19.549999        11.827236  ...       24135.0               61.000000

[385 rows x 44 columns]
    
```

###　使用历史数据API

文档: [链接](https://open.mirror-earth.com/docs/get-started/4-history-api)

```python
from mirrorearth_sdk import forecast_api

apikey = '请在镜像地球开放平台，个人中心获取'
resp = forecast_api(lon='118', lat='32', apikey=apikey, hourly='temperature_2m', daily='temperature_2m_max', start_date='2023-01-01', end_date='2023-12-31')
point1 = resp[0]  # 通过下标获取第一个坐标点的数据，如果传入了多个坐标，可以循环获得数据
print(point1.metedata) # 打印元数据
print(point1.hourly_df())  # 获取hourly小时级(或者是分钟级)数据，是一个DataFrame
print(point1.daily_df()) # 获取daily逐日数据
```

### 使用历史预报数据API

文档: [链接](https://open.mirror-earth.com/docs/get-started/3-archive-forecast-api)

```python
from mirrorearth_sdk import archive_forecast_api

apikey = '请在镜像地球开放平台，个人中心获取'
resp = archive_forecast_api(lon='118', lat='32', apikey=apikey, hourly='temperature_2m', start_hour='2025-07-01T00:00', models='archive_ifs')
point1 = resp[0]  # 通过下标获取第一个坐标点的数据，如果传入了多个坐标，可以循环获得数据
print(point1.metedata) # 打印元数据
print(point1.hourly_df())  # 获取hourly小时级(或者是分钟级)数据，是一个DataFrame
print(point1.daily_df()) # 获取daily逐日数据
```

### 使用无缝数据API

无缝数据指的是从历史数据到未来预报数据无缝衔接。使用ERA5+ECMWF预报，可以覆盖1940年~未来15天，让数据不间断！
文档: [链接](https://open.mirror-earth.com/docs/get-started/5-seamless-data)

```python
from mirrorearth_sdk import seamless_api

apikey = '请在镜像地球开放平台，个人中心获取'
resp = archive_forecast_api(lon='118', lat='32', apikey=apikey, hourly='temperature_2m', forecast_days=15, past_days=15)
point1 = resp[0]  # 通过下标获取第一个坐标点的数据，如果传入了多个坐标，可以循环获得数据
print(point1.metedata) # 打印元数据
print(point1.hourly_df())  # 获取hourly小时级(或者是分钟级)数据，是一个DataFrame
print(point1.daily_df()) # 获取daily逐日数据
```

