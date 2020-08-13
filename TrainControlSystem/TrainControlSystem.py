import logging
import os
import time

from Goldeneye.Goldeneye.Goldeneye import Goldeneye
from Goldeneye.ImageProcessor.SignalType import SignalType
from Goldeneye.Recognizers.RecognizerType import RecognizerType
from Goldeneye.SignalTrackingSystem.SignalTrackingSystem import SignalTrackingSystem
from Train.InstructionSet import InstructionSet
from Train.Train import Train
from TrainControlSystem.TrackConfiguration import TrackConfiguration
import queue

class TrainControlSystem:
    def __init__(self):
        self.logger = self.__create_logger()
        self.train = Train()
        self.eye = Goldeneye()
        self.sts = SignalTrackingSystem(queue=self.eye.result)
        self.info_number = 0
        self.rounds_done = 0
        self.stop_signals = []
        self.signals_seen = 0

    def do_PREN_first_round(self):
        self.logger.info("Starting PREN Routine")
        self.sts.start()
        self.eye.prepare_goldeneye()
        self.eye.start()
        self.logger.info("Warming Up!")
        time.sleep(10.0)
        self.__phase_one()
        self.__phase_two()
        self.__phase_three()
        self.__phase_four()

        self.logger.info("Terminating")

        self.__terminate()

        print(self.eye.stats())

    def do_PREN_second_round(self):
        self.logger.info("Starting PREN Routine")
        self.sts.start()
        self.eye.prepare_goldeneye()
        self.eye.start()
        self.logger.info("Warming Up!")
        time.sleep(10.0)
        self.__phase_one_no_sensor()
        self.__phase_two()
        self.__phase_three()
        self.__phase_four()

        self.logger.info("Terminating")

        self.__terminate()

        print(self.eye.stats())

    def do_PREN_precise_hold(self):
        self.logger.info("Starting PREN Routine")
        self.sts.start()
        self.eye.prepare_goldeneye()
        self.eye.start()
        self.logger.info("Warming Up!")
        time.sleep(10.0)
        self.__phase_one_no_sensor()
        self.__phase_two()
        self.__phase_three_precise()
        self.__phase_four()

        self.logger.info("Terminating")

        self.__terminate()

        print(self.eye.stats())


    def __phase_one(self):
        self.logger.info("Starting Phase 1")
        self.logger.info("Send Instruction for Crane Loading")
        self.train.execute_instruction(InstructionSet.SENSOR_CALIBRATE_SEND)
        self.train.execute_instruction(InstructionSet.LOAD_START_SEND)
        while not self.train.states.CRANE_LOADED:
            time.sleep(0.05)

    def __phase_one_no_sensor(self):
        self.logger.info("Starting Phase 1")
        self.logger.info("Send Instruction for Crane Loading")
        self.train.execute_instruction(InstructionSet.SENSOR_CALIBRATE_SEND)
        self.train.execute_instruction(InstructionSet.LOAD_NO_SENSOR_START_SEND)
        while not self.train.states.CRANE_LOADED:
            time.sleep(0.05)

    def __phase_two(self):
        self.logger.info("Starting Phase 2")

        self.logger.info("Start Tracking on STS")
        self.sts.start_tracking()

        self.logger.info("Accelerate Train")
        self.train.set_speed(160)

        self.logger.info("Starting Sensor Data recording")
        self.train.execute_instruction(InstructionSet.SENSOR_START_SEND)

        self.logger.info("Acceleration Train done")

        self.__phase_run_info_signal()

        self.train.set_speed(160)
        self.logger.info("Signals detected!")

        self.__phase_round_signal_finish()

        self.train.set_speed(46)
        self.eye.change_recognizers(RecognizerType.RecognizerCDNN)
        self.logger.info("Run Done")


    def __phase_three(self):
        self.logger.info("Starting Phase 3")
        self.__phase_halt_at_found_stop_signal_number()
        self.train.execute_instruction(InstructionSet.MOTOR_STOP_SEND)

    def __phase_three_precise(self):
        self.logger.info("Starting Phase 3")
        self.train.set_speed(40)
        self.__phase_halt_at_found_stop_signal_number_precise()
        self.train.execute_instruction(InstructionSet.MOTOR_STOP_SEND)

    def __phase_four(self):
        self.logger.info("Starting Phase 4")
        self.train.execute_instruction(InstructionSet.SENSOR_STOP_SEND)
        self.logger.info("Stopping Sensor! Waiting for Data Transfer finished")
        time.sleep(5)
        self.__csv_writer(self.train.sensor_data())

    def __phase_run_number_signals_detecting(self):
        finished = False
        self.sts.start_tracking()
        while not finished:
            confirmation = self.sts.confirmed_queue.get()
            if confirmation[1] is SignalType.INFO.value:
                self.info_number = confirmation[0]
                self.signals_seen += 1
                self.train.signalize(self.info_number)
            if confirmation[1] is SignalType.STOP.value:
                self.signals_seen += 1
                self.stop_signals.append(confirmation[0])
            if confirmation[1] is SignalType.ROUND.value:
                self.rounds_done += 1
                self.train.signalize(1)
                self.signals_seen += 1
                self.eye.change_recognizers(RecognizerType.RecognizerCDNN)

            if self.signals_seen % TrackConfiguration.NUMBER_SIGNALS_ON_ROUND is 0:
                self.eye.change_recognizers(RecognizerType.RecognizerRoundSignal)

            if self.rounds_done is TrackConfiguration.ROUNDS_TO_DRIVE:
                finished = True
        self.sts.stop_tracking()

    def __phase_run_info_signal(self):
        finished = False
        self.sts.start_tracking()
        while not finished:
            confirmation = self.sts.confirmed_queue.get()
            if confirmation[1] is SignalType.INFO.value:
                self.info_number = confirmation[0]
                self.rounds_done += 1
                self.signals_seen += 1
                self.train.signalize(self.info_number)
                self.sts.stop_tracking()
                #self.logger.info("Signal Number detected: " + self.info_number)
                if self.rounds_done is TrackConfiguration.ROUNDS_TO_DRIVE:
                    finished = True
                else:
                    time.sleep(0.2)
                    self.sts.start_tracking()
        self.sts.stop_tracking()

    def __phase_round_signal_finish(self):
        finished = False
        self.eye.change_recognizers(RecognizerType.RecognizerRoundSignal)
        self.sts.start_tracking()
        while not finished:
            confirmation = self.sts.confirmed_queue.get()
            if confirmation[1] is SignalType.ROUND.value:
                self.rounds_done += 1
                self.signals_seen += 1
                finished = True
        self.sts.stop_tracking()

    def __phase_run_info_and_round_signal(self):
        finished = False
        self.sts.start_tracking()
        while not finished:
            confirmation = self.sts.confirmed_queue.get()
            if confirmation[1] is SignalType.INFO.value:
                self.info_number = confirmation[0]
                self.signals_seen += 1
                self.train.signalize(self.info_number)
                self.eye.change_recognizers(RecognizerType.RecognizerRoundSignal)
            if confirmation[1] is SignalType.STOP.value:
                self.rounds_done += 1
                self.signals_seen += 1
                self.train.signalize(1)
                self.eye.change_recognizers(RecognizerType.RecognizerCDNN)

            if self.rounds_done is TrackConfiguration.ROUNDS_TO_DRIVE:
                finished = True
        self.sts.stop_tracking()

    def __phase_halt_at_found_stop_signal_number(self):
        finished = False
        self.sts.start_tracking()
        while not finished:
            confirmation = self.sts.confirmed_queue.get()
            if confirmation[1] is 1 and confirmation[0] is self.info_number:
                finished = True

    def __phase_halt_at_found_stop_signal_number_precise(self):
        finished = False
        self.sts.start_tracking()
        valid = 0
        while not finished:
            confirmation = self.sts.confirmed_queue.get()
            if confirmation[1] is 1 and confirmation[0] is self.info_number:
                valid += 1
                finished = True
        finished = False
        self.sts.start_tracking()
        while not finished:
            try:
                confirmation = self.sts.confirmed_queue.get(timeout=0.05, block=True)
                if confirmation[1] is 1 and confirmation[0] is self.info_number:
                    valid += 1
                if valid > 1:
                    finished = True
            except queue.Empty:
                finished = True

    def __terminate(self):
        self.train.terminate()

        self.sts.terminate()
        self.sts.join()

        self.eye.stop()
        self.eye.terminate()

    @staticmethod
    def __csv_writer(data):
        if os.path.isfile('./sensordata.csv'):
            csv_file = open('sensordata.csv', 'a')
        else:
            csv_file = open('sensordata.csv', 'w')
        csv_file.write("sep=;")
        csv_file.write("\n")
        for line in data:
            csv_file.write(line)
            csv_file.write("\n")
        csv_file.close()

    @staticmethod
    def __create_logger():
        logger = logging.getLogger("TrainControlSystem")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

