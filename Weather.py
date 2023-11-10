import requests
import json
import hashlib
import yaml
import os
from datetime import datetime

YAML_FILE = './config.yml'
DEFAULT_CFG = {
    'LastQuery': {
        'Timestamp': 0,
        'Datetime': '',
        'ForecastMD5Hash': ''
    }
}

class Weather:
    domain = 'wttr.in'
    protocol = 'http'
    query_options = 'format=j1'

    def __init__(self, place: str) -> None:
        self.SetLocation(place)
        self._config = DEFAULT_CFG
        self._loadConfig()

    def _loadConfig(self) -> None:
        if os.path.exists(YAML_FILE):
            with open(YAML_FILE, 'r') as fh:
                self._config = yaml.safe_load(fh)
        else:
            self._saveConfig()

    def _saveConfig(self) -> None:
        with open(YAML_FILE, 'w') as fh:
            fh.write(yaml.safe_dump(self._config))

    def SetLocation(self, place: str) -> None:
        self.loc_query = {
            'NaraSentan': '~Nara+Institute+of+Science+and+Technology'
            }.get(place, '')
        self.url = f'{self.protocol}://{self.domain}/{self.loc_query}?{self.query_options}'

    def GetJsonData(self) -> dict:
        raw_data = requests.get(self.url)
        data = raw_data.json() # it returns a dict
        date = datetime.now()
        md5 = hashlib.new('md5', json.dumps(data).encode("utf-8"))
        self._config = {
            'LastQuery': {
                'Timestamp': date.timestamp(),
                'Datetime': date.isoformat(),
                'ForecastMD5Hash': md5.hexdigest()
            }
        }
        self._saveConfig()
        return data

    def GetLastQueryMetadata(self) -> dict:
        return self._config['LastQuery']

    def GetCurrentWeather(self, simple: bool = True) -> dict:
        cur_weather = self.GetJsonData()['current_condition'][0]
        if not simple:
            return cur_weather

        temp = cur_weather['temp_C']
        feels = cur_weather['FeelsLikeC']
        tempStr = f'{temp}°C' if temp == feels else f'{temp}°C({feels})'
        one_liner = '{0} {1} {2}% {3}'.format(
            cur_weather['windspeedKmph'],
            cur_weather['pressure'],
            cur_weather['humidity'],
            tempStr)
        return {
            'CurrentWeather': one_liner
        }
