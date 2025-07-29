__version__ = "0.1.0"

from .client import UniWeatherClient as _UniWeatherClient

uniWeather = _UniWeatherClient
connect = _UniWeatherClient.connect

del _UniWeatherClient 