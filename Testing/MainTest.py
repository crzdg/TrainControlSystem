from Train import InstructionSet
from States.States import States
from Train.Signaler import Signaler
from Train.Communication import Communication
import StatusChanger.StatusChanger as StatusChanger
from TrainControlSystem.TrackConfiguration import TrackConfiguration as CONFIG
from threading import Thread
import time


class FuncThread(Thread):
    def __init__(self, target, *args):
        Thread.__init__(self)
        self._target = target
        self._args = args

    def run(self):
        self._target(*self._args)


class Main:
    t_signaler = Signaler()
    # eye = Goldeneye()
    t_crawler = None
    t_communication = Communication()

    @staticmethod
    def main():
        States.PHASE_1 = True
        while True:
            if States.PHASE_1:
                if States.COMMUNICATION_RUNNING is None:
                    Main._start_com()
                if States.EYE_RUNNING is None:
                    time.sleep(30)
                    # Main._start_img_recognition()
                if States.SIGNALER_RUNNING is None:
                    time.sleep(5)
                    # Main._start_signaler()
                if (States.CRANE_LOADING is None) and (States.CRANE_LOADED is None):
                    time.sleep(10)
                    States.CRANE_LOADED = True
                    # Communication.send(Instructionset.LOAD_START)

                if States.CRANE_LOADED:
                    if States.MOTOR_STARTED:
                        Communication.send(InstructionSet.MOTOR_STOP)
                    if States.MOTOR_STARTED is None:
                        Communication.send(InstructionSet.SENSOR_START)
                        States.PHASE_1 = None
                        States.PHASE_2 = True

            if States.PHASE_2:
                if States.MOTOR_FAST is None:
                    Communication.send(InstructionSet.MOTOR_FAST)
                if States.INFO_DETECTED_ON_CURRENT_ROUND and States.INFO_SIGNALIZED is None:
                    Main.t_signaler.set_number(States.INFO_NUMBER)
                    States.INFO_SIGNALIZED = True

                if States.ROUNDS_DRIVEN is CONFIG.ROUND_TO_DRIVE:
                    Communication.send(InstructionSet.MOTOR_SLOW)
                    States.PHASE_2 = None
                    States.PHASE_3 = True

            if States.PHASE_3:
                if States.STOP_DETECTED:
                    Main.eye.stop()
                    Communication.send(InstructionSet.TOF_START)
                    if States.TRAIN_STOPPED:
                        Main._stop_img_recognition()
                        Communication.send(InstructionSet.SENSOR_STOP)
                        States.PHASE_3 = None
                        States.PHASE_4 = True

            if States.PHASE_4:
                States.READING_DATA = True
                Communication.send(InstructionSet.CALL_SENSOR_DATA)

    @staticmethod
    def _start_img_recognition():
        Main.eye.start()
        Main.t_crawler = FuncThread(Main._pic_crawler, Main.eye)
        Main.t_crawler.start()
        States.EYE_RUNNING = True

    @staticmethod
    def _stop_img_recognition():
        Main.eye.stop()
        Main.t_crawler.join()

    @staticmethod
    def _pic_crawler():
        while True:
            result = Main.eye.result.get()
            if States.PHASE_1:
                result = None
            if result:
                StatusChanger.status_changer_img(result)
                result = None

    @staticmethod
    def _start_com():
        Main.t_communication.start()
        States.COMMUNICATION_RUNNING = True

    @staticmethod
    def _start_signaler():
        Main.t_signaler.start()
        States.SIGNALER_RUNNING = True
