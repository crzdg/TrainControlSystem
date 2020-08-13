from Train import InstructionSet
from States.States import States
from Train.Signaler import Signaler
from Train.Communication import Communication
import StatusChanger.StatusChanger as StatusChanger
from TrainControlSystem.TrackConfiguration import TrackConfiguration as CONFIG
import time


class Main:
    t_signaler = Signaler()
    t_crawler = False
    t_communication = Communication()

    @staticmethod
    def main():
        States.PHASE_2 = True
        States.INFO_DETECTED_ON_CURRENT_ROUND = True
        States.INFO_NUMBER = 3
        while True:
            if States.PHASE_2:
                if States.MOTOR_FAST is False:
                    Communication.send(InstructionSet.MOTOR_FAST)
                    time.sleep(20)
                if States.INFO_DETECTED_ON_CURRENT_ROUND and States.INFO_SIGNALIZED is False:
                    Main.t_signaler.set_number(States.INFO_NUMBER)
                    States.INFO_SIGNALIZED = True

                if States.ROUNDS_DRIVEN is CONFIG.ROUND_TO_DRIVE:
                    Communication.send(InstructionSet.MOTOR_SLOW)
                    States.PHASE_2 = False
                    States.PHASE_3 = True

    @staticmethod
    def _stop_img_recognition():
        Main.eye.stop()
        Main.t_crawler.join()

    @staticmethod
    def _pic_crawler():
        while True:
            result = Main.eye.result.get()
            if States.PHASE_1:
                result = False
            if result:
                StatusChanger.status_changer_img(result)
                result = False

    @staticmethod
    def _start_com():
        Main.t_communication.start()
        States.COMMUNICATION_RUNNING = True

    @staticmethod
    def _start_signaler():
        Main.t_signaler.start()
        States.SIGNALER_RUNNING = True
