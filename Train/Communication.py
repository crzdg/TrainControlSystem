import time

import serial
import logging
from threading import Thread

from Train.InstructionSet import InstructionSet


class Communication(Thread):

    def __init__(self, train):
        Thread.__init__(self)
        self.train = train
        self.logger = None
        self.ard = None
        self.reading = True
        self.terminated = False
        self.handshake = False
        self.__create_logger()
        self.__open_serial()
        self.__wake_up()

    def run(self):
        while not self.terminated:
            self.read()

    def __open_serial(self):
        self.logger.info("Open Serial Port")
        self.ard = serial.Serial('/dev/serial0', 9600, timeout=0.05)
        self.ard.close()
        self.ard.open()
        self.ard.reset_input_buffer()
        self.ard.reset_output_buffer()

    def __create_logger(self):
        self.logger = logging.getLogger("Communication")
        self.logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def read(self):
        while self.reading:
            try:
                decoded_string = self.__read_line()
                if decoded_string != "":
                    self.logger.debug("Received Instruction: {}".format(decoded_string))
                    self.train.change_state(decoded_string)
                    if decoded_string == InstructionSet.CALL_SENSOR_DATA_ACK.value:
                        data = (self.ard.readline()).decode()
                        data = data.replace("\r\n", "")
                        self.logger.debug("Reading Sensor Data: {}".format(data))
                        self.train.add_sensor_data(data)
            except IOError as ioe:
                self.logger.info(ioe)

    def __await_reading(self):
        while self.ard.in_waiting > 0:
            self.logger.debug("send: string in input buffer, readline first")
            time.sleep(0.05)
        self.reading = False

    def __read_line(self):
        status = self.ard.readline()
        if status == b'':
            string = ""
        else:
            string = self.__decode_string(status)
        return string

    def send(self, instruction):
        self.__await_reading()
        try:
            self.logger.debug("Sending Instruction: {}".format(instruction))
            self.ard.write(self.__encode_string(str(instruction)))
            self.reading = True
        except IOError as ioe:
            self.logger.warning(ioe)

    """ used for set up connection between raspberry and arduino"""
    def __wake_up(self):
        self.ard.reset_input_buffer()
        self.ard.reset_output_buffer()
        try:
            self.send(InstructionSet.HANDSHAKE_SYN_SEND.value)
            self.logger.debug("sending handshake SYN")
            result = -1
            while result != InstructionSet.HANDSHAKE_SYN_CONFIRMED.value:
                self.logger.debug("waiting for handshake ACK")
                answer = self.__read_line()
                if answer != "":
                    result = answer
                    self.logger.debug("waiting for handshake ACK: {}".format(result))
            self.logger.info("Handshake SYNC Confirmed")
            self.handshake = True
        except IOError as ioe:
            self.logger.warning(ioe)

    """ add new line to given string and encode it for serial communication """
    @staticmethod
    def __encode_string(string):
        return (str(string) + "\n").encode()

    """ remove new line and carrier char which was added per default from arduino serial.println,
        decode it for status changer """
    @staticmethod
    def __decode_string(string):
        return int(string.decode()[0:3])

    def stop(self):
        self.logger.info("Terminating Communication")
        self.reading = False
        self.terminated = True

