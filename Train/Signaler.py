import RPi.GPIO as GPIO
from time import sleep
from threading import Thread


class Signaler(Thread):
    def __init__(self, number):
        Thread.__init__(self)
        self.buzzer_gpio_pin = 23
        self.number_to_signalize = number
        self.terminated = False
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzer_gpio_pin, GPIO.OUT)
        self.start()

    def run(self):
        while not self.terminated:
            if self.number_to_signalize is not None:
                for _ in range(0, self.number_to_signalize):
                    GPIO.output(self.buzzer_gpio_pin, GPIO.HIGH)
                    sleep(0.2)
                    GPIO.output(self.buzzer_gpio_pin, GPIO.LOW)
                    sleep(0.2)
                self.stop()

    def set_number(self, number):
        self.number_to_signalize = number

    def stop(self):
        self.terminated = True
