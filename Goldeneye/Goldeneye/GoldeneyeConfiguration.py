from Goldeneye.Goldeneye.GoldeneyeMode import GoldeneyeMode


class GoldeneyeConfiguration:
    x_resolution = 320
    y_resolution = 240
    fps = 40
    shutter_speed = 500
    iso = 350
    number_of_image_processors = 5
    mode = GoldeneyeMode.SKIPPED
    vertical_camera_flip = True
    horizontal_camera_flip = True
    flip = (vertical_camera_flip, horizontal_camera_flip)
