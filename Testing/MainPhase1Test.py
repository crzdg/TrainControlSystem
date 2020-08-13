from Train.Communication import Communication
import time

from Train import InstructionSet
from States.States import States


class Main:
    # t_signaler = Signaler()
    t_communication = Communication()


    @staticmethod
    def main():
        print("Main started!")
        # t_crawler = None
        States.PHASE_1 = True
        while True:
            if States.PHASE_1:
                if States.COMMUNICATION_RUNNING is False:
                    Main._start_com()
                    print("Wake up send!")
                if States.EYE_RUNNING is False:
                    print("EYE starting")
                    time.sleep(2)
                    States.EYE_RUNNING = True
                    # Main._start_img_recognition()
                if States.SIGNALER_RUNNING is False:
                    print("Signaler starting")
                    time.sleep(2)
                    States.SIGNALER_RUNNING = True
                    # Main._start_signaler()
                if (States.CRANE_LOADING is False) and (States.CRANE_LOADED is False):
                    print("Loading phase")
                    #Main.t_communication.send(InstructionSet.MOTOR_SLOW)
                    #time.sleep(5)
                    Main.t_communication.send(InstructionSet.MOTOR_FAST)
                    time.sleep(15)
                    States.CRANE_LOADED = True
                    # Communication.send(Instructionset.LOAD_START)

                if States.CRANE_LOADED:
                    print("Loaded")
                    if States.MOTOR_STARTED:
                        Main.t_communication.send(InstructionSet.MOTOR_STOP)
                        while States.MOTOR_STARTED:
                            time.sleep(0.05)
                    if States.MOTOR_STARTED is False:
                        # Communication.send(Instructionset.SENSOR_START)
                        print("Phase 1 done")
                        States.PHASE_1 = False
                        States.PHASE_2 = True
                        print("breaking loop")
                        break
        Main.t_communication.stop()
        Main.t_communication.join()

    @staticmethod
    def _start_com():
        Main.t_communication.start()
        States.COMMUNICATION_RUNNING = True
