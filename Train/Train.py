import time

from Train.Communication import Communication
from Train.InstructionSet import InstructionSet
from Train.Signaler import Signaler
from Train.TrainStates import TrainStates


class Train:

    def __init__(self):
        self.states = TrainStates()
        self.com = Communication(self)
        self.__init_train()
        self.__sensor_data = []

    def __init_train(self):
        self.com.start()
        self.states.COMMUNICATION_RUNNING = True

    def signalize(self, number_to_signalize):
        Signaler(number_to_signalize)

    def execute_instruction(self, instruction: InstructionSet) -> None:
        self.states.EXECUTING = True
        self.com.send(instruction.value)

    def set_speed(self, speed):
        self.states.MOTOR_WAITING = True
        self.states.EXECUTING = True
        self.com.send(instruction=InstructionSet.MOTOR_SET_SPEED_SEND.value)
        time.sleep(0.2)
        self.com.send(speed)
        if speed == 0:
            self.states.MOTOR_RUNNING = False
        else:
            self.states.MOTOR_RUNNING = True
        self.states.MOTOR_SPEED = speed

    def terminate(self):
        self.com.stop()
        self.com.join()

    def change_state(self, status_code):
        self.states.change_state(status_code)

    def add_sensor_data(self, data):
        self.__sensor_data.append(data)

    def sensor_data(self):
        return self.__sensor_data








