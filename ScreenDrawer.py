import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from Weather import Weather
import epd2in7 as Screen

USE_IS = True

class ImageDrawer:
    useLocalFont = True
    customFontDir = ''

    def __init__(self) -> None:
        fontdir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'Fonts'
        ) if self.useLocalFont else self.customFontDir
        self.font18 = ImageFont.truetype(os.path.join(fontdir, 'DejaVuSans.tff'), 18)
        self.font24 = ImageFont.truetype(os.path.join(fontdir, 'DejaVuSans.tff'), 24)
        self.font35 = ImageFont.truetype(os.path.join(fontdir, 'DejaVuSans.tff'), 35)
        self.tempUnit = 'C' if USE_IS else 'F'
        self.windUnit = 'Kmph' if USE_IS else 'Miles'

    def _canvas(self) -> ImageDraw.ImageDraw:
        image = Image.new('L', (Screen.EPD_WIDTH, Screen.EPD_HEIGHT), 0)
        return ImageDraw.Draw(image)

    def _relevantData(self, forecast: dict, isCurrent: bool = False) -> dict:
        if isCurrent:
            date = datetime.strptime(forecast['localObsDateTime'], '%Y-%m-%d %I:%M %p')
            return {
                'ObservationDate': date,
                'Humidity': forecast['humidity'] + '%',
                'Temp': forecast['temp_' + self.tempUnit],
                'FeelsLike': forecast['FeelsLike' + self.tempUnit],
            }

        date = datetime.strptime(forecast['date'], '%Y-%m-%d')
        hourly = forecast['hourly']
        return {
            'Date': date,
        }

    def _getWeather(self, place: str) -> dict:
        weather = Weather(place)
        data = weather.GetJsonData()
        today = data['weather'][0]
        current = data['current_condition'][0]
        obs_date = datetime.strptime(current['localObsDateTime'], '%Y-%m-%d %I:%M %p')
        tomorrow = data['weather'][1]
        tom_date = datetime.strptime(tomorrow['date'], '%Y-%m-%d')
        return {
            'Current': current,
            'Today': today,
            'Tomorrow': tomorrow,
        }
