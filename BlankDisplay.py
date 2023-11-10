import sys
import os

resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
if os.path.exists(resources_dir):
    sys.path.append(resources_dir)

from resources import epd2in7 as Screen
from time import sleep

import logging

LOGGING_LEVEL = logging.DEBUG

if __name__ == '__main__':
    epd = None
    try:
        logging.basicConfig()
        logger = logging.getLogger(__name__)
        logger.setLevel(LOGGING_LEVEL)

        epd = Screen.EPD()
        epd.init()

        epd.Clear(0xFF)
        sleep(1)

        epd.Clear(0xCC)
        sleep(1)

        epd.Clear(0xFF)

        epd.sleep()

    except IOError as e:
        logging.error(e)

    except KeyboardInterrupt:
        logging.info("Exiting by keyboard interrupt")
        if epd:
            Screen.epdconfig.module_exit()
