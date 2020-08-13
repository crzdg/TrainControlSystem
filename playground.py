import csv

import os
import time
import serial

from Train.InstructionSet import InstructionSet
from Train.Train import Train


def __encode_string(string):
    return (string + "\\n").encode()

def state_tester():
    ard = serial.Serial('/dev/serial0', 115200, timeout=10)
    ard.close()
    ard.open()
    ard.reset_input_buffer()
    ard.reset_output_buffer()
    print(ard.in_waiting)
    print(ard.out_waiting)
    print("Main started!")

    command = "900\n".encode()
    ard.write(command)
    print(ard.in_waiting)
    print(ard.out_waiting)
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to 900, expecting 901: {}".format(answer))
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to 900, expecting 902: {}".format(answer))

    command = "900\n".encode()
    ard.write(command)
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to 900, expecting 902: {}".format(answer))

    # command = "710\n".encode()
    # ard.write(command)
    # answer = ard.readline()
    # answer = answer.decode()[0:3]
    # print("Answer to 711, expecting 711: {}".format(answer))
    # time.sleep(20)
    # answer = ard.readline()
    # answer = answer.decode()[0:3]
    # print("Answer to 712, expecting 712: {}".format(answer))


    command = "120\n".encode()
    ard.write(command)
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '121': {}".format(command, answer))
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '122': {}".format(command, answer))

    time.sleep(6)

    command = "190\n".encode()
    ard.write(command)
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '191': {}".format(command, answer))
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '192': {}".format(command, answer))

    time.sleep(3)

    command = "140\n".encode()
    ard.write(command)
    speed = "200\n".encode()
    ard.write(speed)
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '141': {}".format(command, answer))
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '142': {}".format(command, answer))

    time.sleep(20)

    command = "140\n".encode()
    ard.write(command)
    speed = "100\n".encode()
    ard.write(speed)
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '141': {}".format(command, answer))
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '142': {}".format(command, answer))

    time.sleep(20)

    command = "190\n".encode()
    ard.write(command)
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '191': {}".format(command, answer))
    answer = ard.readline()
    answer = answer.decode()[0:3]
    print("Answer to {}, expecting '192': {}".format(command, answer))

    time.sleep(10)

def stop_train():
    ard = serial.Serial('/dev/serial0', 9600, timeout=10)
    ard.close()
    ard.open()
    ard.reset_input_buffer()
    print(ard.in_waiting)
    print(ard.out_waiting)
    print("Main started!")

    command = "140\n".encode()
    ard.write(command)

    command = "55\n".encode()
    ard.write(command)
    time.sleep(2)

    command = "190\n".encode()
    ard.write(command)



def distance_sensor_tester():
    ard = serial.Serial('/dev/serial0', 9600, timeout=10)
    ard.close()
    ard.open()
    ard.reset_input_buffer()
    print(ard.in_waiting)
    print(ard.out_waiting)
    print("Sending 160")
    command = "160\n".encode()
    ard.write(command)
    while True:
        answer = ard.readline()
        print(answer)

def csv_writer(data):
    if os.path.isfile('./sensordata.csv'):
        csvFile = open('sensordata.csv', 'a')
    else:
        csvFile = open('sensordata.csv', 'w')
    csvFile.write("sep=;")
    csvFile.write("\n")
    for line in data:
        csvFile.write(line)
        csvFile.write("\n")
    csvFile.close()

def train_tester():
    train = Train()
    train.execute_instruction(InstructionSet.SENSOR_START_SEND)
    time.sleep(30)
    train.execute_instruction(InstructionSet.SENSOR_STOP_SEND)
    time.sleep(3)
    print(train.sensor_data)
    train.terminate()




if __name__ == '__main__':
    stop_train()













