

class TrainStates:

    def __init__(self):

        self.EXECUTING = False

        self.MOTOR_RUNNING = False
        self.MOTOR_WAITING = False
        self.MOTOR_SPEED = 0

        self.CRANE_LOADED = False
        self.CRANE_LOADING = False

        self.COMMUNICATION_RUNNING = False
        self.SIGNALER_RUNNING = False

        self.ACCELERATION_SENSOR_RUNNING = False
        self.ACCELERATION_SENSOR_DATA_READING = False

    def change_state(self, status_code):
        self.__state_tree(status_code)

    def __state_tree(self, status_code):
        code = self.__string_to_array(status_code)
        component = code[0]

        # Motor
        if component == 1:
            self.__state_changer_motor(code)

        # Crane
        if component == 2:
            self.__state_changer_crane(code)

        # # IR Sensor 1
        # if component == 3:
        #     status_changer_ir1(code)

        # Acceleration sensor
        if component == 5:
            self.__state_changer_acceleration(code)

        # Load
        if component == 7:
            self.__state_changer_load(code)

    def __state_changer_motor(self, code):
        instruction = code[1]
        status = code[2]

        if status == 1:
            self.EXECUTING = True

        if status == 2:
            self.EXECUTING = False

        if instruction == 2:
            if status == 1:
                self.MOTOR_RUNNING = True
                self.MOTOR_WAITING = True
            if status == 2:
                self.MOTOR_RUNNING = True
                self.MOTOR_WAITING = False
                self.MOTOR_SPEED = 50

        if instruction == 3:
            if status == 1:
                self.MOTOR_RUNNING = True
                self.MOTOR_WAITING = True
            if status == 2:
                self.MOTOR_RUNNING = True
                self.MOTOR_WAITING = False
                self.MOTOR_SPEED = 200

        if instruction == 4:
            if status == 1:
                self.MOTOR_WAITING = True
            if status == 2:
                self.MOTOR_WAITING = False

        if instruction == 9:
            if status == 1:
                self.MOTOR_RUNNING = True
                self.MOTOR_WAITING = True
            if status == 2:
                self.MOTOR_RUNNING = False
                self.MOTOR_SPEED = 0

    def __state_changer_crane(self, code):
        instruction = code[1]
        status = code[2]
        if instruction == 1:
            if status == 1:
                self.CRANE_LOADING = True
                self.MOTOR_RUNNING = True

        if instruction == 1:
            if status == 2:
                self.CRANE_LOADED = True
                self.CRANE_LOADING = False
                self.MOTOR_RUNNING = False

    # def status_changer_ir1(code):
    #     instruction = code[1]
    #     status = code[2]
    #     if instruction == 1:
    #         if status == 2:
    #             self.IR_1_STARTED = True

    # def status_changer_tof(code):
    #     instruction = code[1]
    #     status = code[2]
    #     if instruction == 1:
    #         if status == 2:
    #             States.IR_1_STARTED = True

    def __state_changer_acceleration(self, code):
        instruction = code[1]
        status = code[2]
        if instruction == 1:
            if status == 2:
                self.ACCELERATION_SENSOR_RUNNING = True
        if instruction == 9:
            if status == 2:
                self.ACCELERATION_SENSOR_RUNNING = False

    def __state_changer_sensor_data(self, code):
        instruction = code[1]
        status = code[2]
        if instruction == 9:
            if status == 1:
                self.ACCELERATION_SENSOR_DATA_READING = True
        if instruction == 9:
            if status == 2:
                self.ACCELERATION_SENSOR_DATA_READING = False

    def __state_changer_load(self, code):
        instruction = code[1]
        status = code[2]

        if instruction == 1:
            if status == 1:
                self.CRANE_LOADING = True
                self.MOTOR_RUNNING = True

        if instruction == 1:
            if status == 2:
                self.CRANE_LOADING = False
                self.CRANE_LOADED = True
                self.MOTOR_RUNNING = False

        if instruction == 2:
            if status == 1:
                self.CRANE_LOADING = True
                self.MOTOR_RUNNING = True

        if instruction == 2:
            if status == 2:
                self.CRANE_LOADING = False
                self.CRANE_LOADED = True
                self.MOTOR_RUNNING = False

    def __string_to_array(self, figure):
        try:
            return [int(i) for i in str(figure)]

        except:
            print("could not convert to string array")
            return [int(i) for i in str(000)]



