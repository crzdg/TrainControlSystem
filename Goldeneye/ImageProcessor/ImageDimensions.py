# make an image dimension class, which contains w,h,etc.
# classes inherit from it, and set the specific variables
# from ImageProcessor set the class with the dimension
# in code call only imagedimension.width
from enum import Enum


class ImageDimensions(Enum):
    IMG_1648_1232_SCALED_UP = 0
    IMG_1648_1232 = 1
    IMG_1280_720 = 2
    IMG_640_480 = 3