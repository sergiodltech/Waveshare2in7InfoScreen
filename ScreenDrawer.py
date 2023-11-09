import os
import errno
from pprint import pprint
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from Weather import Weather
import epd2in7 as Screen

USE_IS = True

import logging

class ImageDrawer:
    useLocalFont = True
    customFontDir = ''
    margin = 6 # px
    interline = 5 # px

    def __init__(self, debug: bool = False) -> None:
        fontdir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'Fonts'
        ) if self.useLocalFont else self.customFontDir
        font_file = os.path.join(fontdir, 'DejaVuSans.ttf')
        if not os.path.exists(font_file):
            raise FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                font_file)

        self.font18 = ImageFont.truetype(font_file, 18)
        self.font24 = ImageFont.truetype(font_file, 24)
        self.font35 = ImageFont.truetype(font_file, 35)
        self.tempUnit = 'C' if USE_IS else 'F'
        self.windUnit = 'Kmph' if USE_IS else 'Miles'
        self.pressureUnit = '' if USE_IS else 'Inches'
        self.precipitationUnit = 'MM' if USE_IS else 'Inches'
        self.debug = debug

        logging.basicConfig()
        self.log = logging.getLogger(__name__)
        if self.debug:
            self.log.setLevel(logging.DEBUG)

    def _canvas(self) -> ImageDraw.ImageDraw:
        screen_dims = (Screen.EPD_HEIGHT, Screen.EPD_WIDTH)
        self.log.debug(f'Screen Dimensions: {screen_dims}') # Landscape image
        image = Image.new('L', screen_dims, 0) # 'L' for grayscale image
        return ImageDraw.Draw(image)

    def _relevantData(self, forecast: dict, isCurrent: bool = False) -> dict:
        if isCurrent:
            date = datetime.strptime(forecast['localObsDateTime'], '%Y-%m-%d %I:%M %p')
            return {
                'ObservationDate': date,
                'Humidity': forecast['humidity'] + '%',
                'Temp': forecast['temp_' + self.tempUnit],
                'FeelsLike': forecast['FeelsLike' + self.tempUnit],
                'WindSpeed': forecast['windspeed' + self.windUnit],
                'WeatherCode': forecast['weatherCode'],
                'Weather': forecast['weatherDesc'][0]['value'],
                'Pressure': forecast['pressure' + self.pressureUnit],
            }

        date = datetime.strptime(forecast['date'], '%Y-%m-%d')
        hourly = forecast['hourly']
        return {
            'Date': date,
            'TempMax': forecast['maxtemp' + self.tempUnit],
            'TempMin': forecast['mintemp' + self.tempUnit],
            'UVIndex': forecast['uvIndex'],
            'Morning': {
                'Humidity': hourly[2]['humidity'] + '%',
                'Temp': hourly[2]['temp' + self.tempUnit],
                'FeelsLike': hourly[2]['FeelsLike' + self.tempUnit],
                'WindSpeed': hourly[2]['windspeed' + self.windUnit],
                'WeatherCode': hourly[2]['weatherCode'],
                'Weather': hourly[2]['weatherDesc'][0]['value'],
                'Pressure': hourly[2]['pressure' + self.pressureUnit],
                'Precipitation': hourly[2]['precip' + self.precipitationUnit],
            },
            'Noon': {
                'Humidity': hourly[4]['humidity'] + '%',
                'Temp': hourly[4]['temp' + self.tempUnit],
                'FeelsLike': hourly[4]['FeelsLike' + self.tempUnit],
                'WindSpeed': hourly[4]['windspeed' + self.windUnit],
                'WeatherCode': hourly[4]['weatherCode'],
                'Weather': hourly[4]['weatherDesc'][0]['value'],
                'Pressure': hourly[4]['pressure' + self.pressureUnit],
                'Precipitation': hourly[4]['precip' + self.precipitationUnit],
            },
            'Night': {
                'Humidity': hourly[7]['humidity'] + '%',
                'Temp': hourly[7]['temp' + self.tempUnit],
                'FeelsLike': hourly[7]['FeelsLike' + self.tempUnit],
                'WindSpeed': hourly[7]['windspeed' + self.windUnit],
                'WeatherCode': hourly[7]['weatherCode'],
                'Weather': hourly[7]['weatherDesc'][0]['value'],
                'Pressure': hourly[7]['pressure' + self.pressureUnit],
                'Precipitation': hourly[7]['precip' + self.precipitationUnit],
            },
        }

    def Forecast(self, place: str) -> dict:
        weather = Weather(place)
        data = weather.GetJsonData()
        current = self._relevantData(data['current_condition'][0], True)
        today = self._relevantData(data['weather'][0])
        tomorrow = self._relevantData(data['weather'][1])
        return {
            'Current': current,
            'Today': today,
            'Tomorrow': tomorrow,
        }

    def WeatherScreen(self, place: str) -> ImageDraw.ImageDraw:
        data = self.Forecast(place)
        canvas = self._canvas()
        origin = (self.margin, self.margin)
        canvas.text(origin, data['Today']['Date'].strftime('%a %d'), font = self.font24)
        line_two = (origin[0], origin[1] + 24 + self.interline)
        canvas.text(line_two, '{0}'.format())
        return canvas

if __name__ == '__main__':
    drawer = ImageDrawer(debug = True)
    pprint(drawer.Forecast('NaraSentan'))