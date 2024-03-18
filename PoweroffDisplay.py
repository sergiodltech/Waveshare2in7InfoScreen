import sys
import os
import errno

resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
if os.path.exists(resources_dir):
    sys.path.append(resources_dir)

from resources import epd2in7 as Screen

import logging
from PIL import Image, ImageDraw, ImageFont

LOGGING_LEVEL = logging.INFO
# The screen is designed as a vertical screen
# For horizontal images the EDP2IN7 library automatically transposes the byte matrix to vertical
CANVAS_WIDTH = Screen.EPD_HEIGHT
CANVAS_HEIGHT = Screen.EPD_WIDTH

def buildBannerImage(msg: str) -> Image.Image:
    margin = 20 # px
    fontdir = os.path.join(resources_dir, 'Fonts')
    font_file = os.path.join(fontdir, 'DejaVuSans-Bold.ttf')
    if not os.path.exists(font_file):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            font_file)

    fontBig = ImageFont.truetype(font_file, 18)

    screen_dims = (CANVAS_WIDTH, CANVAS_HEIGHT)
    image = Image.new('L', screen_dims, 255) # 'L' for grayscale image
    canvas = ImageDraw.Draw(image)

    origin = (margin, margin)
    canvas.text(
        origin,
        msg,
        font = fontBig,
        fill = Screen.GRAY4)
    return image


if __name__ == '__main__':
    epd = None
    try:
        logging.basicConfig()
        logger = logging.getLogger(__name__)
        logger.setLevel(LOGGING_LEVEL)

        image = buildBannerImage("Bye Bye!!\nPowering off...")

        epd = Screen.EPD()
        epd.Init_4Gray()
        epd.display_4Gray(epd.getbuffer_4Gray(image))
        epd.sleep()

    except IOError as e:
        logging.error(e)

    except KeyboardInterrupt:
        logging.info("Exiting by keyboard interrupt")
        if epd:
            Screen.epdconfig.module_exit()
