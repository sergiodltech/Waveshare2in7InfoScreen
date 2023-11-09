import requests, sys

class Weather:
    domain = 'wttr.in'
    protocol = 'http'
    query_options = 'format=j1'

    def __init__(self, place: str):
        self.SetLocation(place)

    def SetLocation(self, place: str) -> None:
        self.loc_query = {
            'NaraSentan': '~Nara+Institute+of+Science+and+Technology'
            }.get(place, '')
        self.url = f'{protocol}://{domain}/{loc_place}?{query_options}'

    def GetJsonData(self) -> dict:
        data = requests.get(self.url)
        return data.json()

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
