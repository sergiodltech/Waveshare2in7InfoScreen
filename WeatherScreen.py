import sys
import os

resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
if os.path.exists(resources_dir):
    sys.path.append(resources_dir)

from ScreenDrawer import ImageDrawer
from resources import epd2in7 as Screen

import logging

LOGGING_LEVEL = logging.INFO

if __name__ == '__main__':
    epd = None
    try:
        logging.basicConfig()
        logger = logging.getLogger(__name__)
        logger.setLevel(LOGGING_LEVEL)

        drawer = ImageDrawer(debug = True)
        draw = drawer.WeatherScreen('NaraSentan')

        epd = Screen.EPD()
        epd.Init_4Gray()
        epd.display_4Gray(epd.getbuffer_4Gray(drawer.image))
        epd.sleep()

    except IOError as e:
        logging.error(e)

    except KeyboardInterrupt:
        logging.info("Exiting by keyboard interrupt")
        if epd:
            Screen.epdconfig.module_exit()
