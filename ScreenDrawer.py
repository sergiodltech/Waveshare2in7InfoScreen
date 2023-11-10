import sys
import os

resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
if os.path.exists(resources_dir):
    sys.path.append(resources_dir)

import errno
from math import ceil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pprint import pformat
from Weather import Weather
from resources import epd2in7 as Screen
from resources import wttrconstants as Constants

import logging

USE_IS = True
LOGGING_LEVEL = logging.INFO

class ImageDrawer:
    useLocalFont = True
    customFontDir = ''
    margin = 6 # px
    interline = 5 # px
    image = None

    def __init__(self, debug: bool = False) -> None:
        self.tempUnit = 'C' if USE_IS else 'F'
        self.windUnit = 'Kmph' if USE_IS else 'Miles'
        self.pressureUnit = '' if USE_IS else 'Inches'
        self.precipitationUnit = 'MM' if USE_IS else 'Inches'
        self.debug = debug

        self._setFonts()
        logging.basicConfig()
        self.log = logging.getLogger(__name__)
        if self.debug:
            self.log.setLevel(LOGGING_LEVEL)

    def _setFonts(self):
        fontdir = os.path.join(resources_dir, 'Fonts') if self.useLocalFont else self.customFontDir

        font_file = os.path.join(fontdir, 'DejaVuSans-Bold.ttf')
        if not os.path.exists(font_file):
            raise FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                font_file)

        self.font12 = ImageFont.truetype(font_file, 12)
        self.font18 = ImageFont.truetype(font_file, 18)
        self.font24 = ImageFont.truetype(font_file, 24)

        font_file = os.path.join(fontdir, 'NotoEmoji-Bold.ttf')
        if not os.path.exists(font_file):
            raise FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                font_file)

        self.emoji12 = ImageFont.truetype(font_file, 12)
        self.emoji18 = ImageFont.truetype(font_file, 18)
        self.emoji24 = ImageFont.truetype(font_file, 24)

    def _canvas(self) -> ImageDraw.ImageDraw:
        screen_dims = (Screen.EPD_HEIGHT, Screen.EPD_WIDTH)
        self.log.debug(f'Screen Dimensions: {screen_dims}') # Landscape image
        self.image = Image.new('L', screen_dims, 255) # 'L' for grayscale image
        return ImageDraw.Draw(self.image)

    def _getWeatherIconUnicode(self, weatherCode: str) -> str:
        desc = Constants.WWO_CODE.get(weatherCode, "Unknown")
        return Constants.WEATHER_SYMBOL.get(desc, Constants.WEATHER_SYMBOL["Unknown"])

    def _precipitationFormat(self, precipitation: str) -> str:
        precipInt = ceil(float(precipitation))
        return '  ' if precipInt == 0 else f"{precipInt}"

    def _joinWeatherPrecip(self, weatherCode: str, precipitation: str) -> str:
        icon = self._getWeatherIconUnicode(weatherCode)
        precipTxt = self._precipitationFormat(precipitation)
        return f"{icon}{precipTxt}"

    def _relevantData(self, forecast: dict, isCurrent: bool = False) -> dict:
        if isCurrent:
            date = datetime.strptime(forecast['localObsDateTime'], '%Y-%m-%d %I:%M %p')
            return {
                'ObservationDate': date,
                'Humidity': forecast.get('humidity', ''),
                'Temp': forecast['temp_' + self.tempUnit],
                'FeelsLike': forecast.get('FeelsLike' + self.tempUnit, ''),
                'WindSpeed': forecast.get('windspeed' + self.windUnit, ''),
                'WeatherCode': forecast['weatherCode'],
                'Weather': forecast['weatherDesc'][0]['value'],
                'Pressure': forecast.get('pressure' + self.pressureUnit, ''),
                'UVIndex': forecast['uvIndex'],
            }

        date = datetime.strptime(forecast['date'], '%Y-%m-%d')
        hourly = forecast['hourly']
        return {
            'Date': date,
            'TempMax': forecast['maxtemp' + self.tempUnit],
            'TempMin': forecast['mintemp' + self.tempUnit],
            'UVIndex': forecast['uvIndex'],
            'Morning': {
                'Humidity': hourly[2].get('humidity', ''),
                'Temp': hourly[2]['temp' + self.tempUnit],
                'FeelsLike': hourly[2].get('FeelsLike' + self.tempUnit, ''),
                'WindSpeed': hourly[2].get('windspeed' + self.windUnit, ''),
                'WeatherCode': hourly[2]['weatherCode'],
                'Weather': hourly[2]['weatherDesc'][0]['value'],
                'Pressure': hourly[2].get('pressure' + self.pressureUnit, ''),
                'Precipitation': hourly[2].get('precip' + self.precipitationUnit, ''),
            },
            'Noon': {
                'Humidity': hourly[4].get('humidity', ''),
                'Temp': hourly[4]['temp' + self.tempUnit],
                'FeelsLike': hourly[4].get('FeelsLike' + self.tempUnit, ''),
                'WindSpeed': hourly[4].get('windspeed' + self.windUnit, ''),
                'WeatherCode': hourly[4]['weatherCode'],
                'Weather': hourly[4]['weatherDesc'][0]['value'],
                'Pressure': hourly[4].get('pressure' + self.pressureUnit, ''),
                'Precipitation': hourly[4].get('precip' + self.precipitationUnit, ''),
            },
            'Night': {
                'Humidity': hourly[7].get('humidity', ''),
                'Temp': hourly[7]['temp' + self.tempUnit],
                'FeelsLike': hourly[7].get('FeelsLike' + self.tempUnit, ''),
                'WindSpeed': hourly[7].get('windspeed' + self.windUnit, ''),
                'WeatherCode': hourly[7]['weatherCode'],
                'Weather': hourly[7]['weatherDesc'][0]['value'],
                'Pressure': hourly[7].get('pressure' + self.pressureUnit, ''),
                'Precipitation': hourly[7].get('precip' + self.precipitationUnit, ''),
            },
        }

    def Forecast(self, place: str) -> dict:
        weather = Weather(place)
        data = weather.GetJsonData()
        current = self._relevantData(data['current_condition'][0], True)
        today = self._relevantData(data['weather'][0])
        tomorrow = self._relevantData(data['weather'][1])
        forecast = {
            'Current': current,
            'Today': today,
            'Tomorrow': tomorrow,
        }
        self.log.debug("Forecast:\n{0}".format(pformat(forecast)))
        return forecast

    def WeatherScreen(self, place: str) -> ImageDraw.ImageDraw:
        data = self.Forecast(place)
        canvas = self._canvas()

        origin = (self.margin, self.margin)
        canvas.text(
            origin,
            data['Today']['Date'].strftime('%a %d'),
            font = self.font12,
            fill = Screen.GRAY4)

        line_two = (origin[0], origin[1] + 12 + self.interline)
        cur = data['Current']
        feelsLike = cur['FeelsLike']
        feelsLike = f'({feelsLike})' if feelsLike else ''
        canvas.text(
            line_two,
            '{0}{1}°{2} {3}% {4}km/h'.format(
                cur['Temp'], feelsLike, self.tempUnit,
                cur['Humidity'], cur['WindSpeed']),
            font = self.font18,
            fill = Screen.GRAY4)
        line_two_right = (Screen.EPD_HEIGHT - 22, line_two[1])
        canvas.text(
            line_two_right,
            self._getWeatherIconUnicode(cur['WeatherCode']),
            font = self.emoji18,
            fill = Screen.GRAY4)

        line_three = (origin[0], line_two[1] + 18 + 3)
        canvas.text(
            line_three,
            '{0} uv{1} p{2}'.format(
                cur['Weather'], cur['UVIndex'], cur['Pressure']),
            font = self.font12,
            fill = Screen.GRAY4)

        line_four = (origin[0], line_three[1] + 12 + (self.interline*2))
        today = data['Today']
        canvas.text(
            line_four,
            '{0}: {1}/{2}°{3} uv{4}'.format(
                today['Date'].strftime('%a %d'),
                today['TempMin'], today['TempMax'], self.tempUnit, today['UVIndex'],
            ),
            font = self.font12,
            fill = Screen.GRAY4)
        line_four_right = (Screen.EPD_HEIGHT - 110, line_four[1])
        canvas.text(
            line_four_right,
            '{0} {1} {2}'.format(
                self._getWeatherIconUnicode(today['Morning']['WeatherCode']),
                self._getWeatherIconUnicode(today['Noon']['WeatherCode']),
                self._getWeatherIconUnicode(today['Night']['WeatherCode']),
            ),
            font = self.emoji12,
            fill = Screen.GRAY4)
        canvas.text(
            (Screen.EPD_HEIGHT - 95, line_four[1]),
            '{0}  {1}  {2}'.format(
                self._precipitationFormat(today['Morning']['Precipitation']),
                self._precipitationFormat(today['Noon']['Precipitation']),
                self._precipitationFormat(today['Night']['Precipitation']),
            ),
            font = self.font12,
            fill = Screen.GRAY3)

        line_five = (origin[0], line_four[1] + 12 + self.interline)
        tomorrow = data['Tomorrow']
        canvas.text(
            line_five,
            '{0}: {1}/{2}°{3} uv{4}'.format(
                tomorrow['Date'].strftime('%a %d'),
                tomorrow['TempMin'], tomorrow['TempMax'], self.tempUnit, tomorrow['UVIndex'],
            ),
            font = self.font12,
            fill = Screen.GRAY4)
        line_five_right = (Screen.EPD_HEIGHT - 110, line_five[1])
        canvas.text(
            line_five_right,
            '{0} {1} {2}'.format(
                self._getWeatherIconUnicode(tomorrow['Morning']['WeatherCode']),
                self._getWeatherIconUnicode(tomorrow['Noon']['WeatherCode']),
                self._getWeatherIconUnicode(tomorrow['Night']['WeatherCode']),
            ),
            font = self.emoji12,
            fill = Screen.GRAY4)
        canvas.text(
            (Screen.EPD_HEIGHT - 95, line_five[1]),
            '{0}  {1}  {2}'.format(
                self._precipitationFormat(tomorrow['Morning']['Precipitation']),
                self._precipitationFormat(tomorrow['Noon']['Precipitation']),
                self._precipitationFormat(tomorrow['Night']['Precipitation']),
            ),
            font = self.font12,
            fill = Screen.GRAY3)

        return canvas

if __name__ == '__main__':
    drawer = ImageDrawer(debug = True)
    draw = drawer.WeatherScreen('NaraSentan')
    if drawer.image:
        drawer.image.show()
