import select
import sys
import threading
import time

import serial
from keras import backend as K
from Goldeneye.Goldeneye.Goldeneye import Goldeneye
from Goldeneye.Goldeneye.GoldeneyeMode import GoldeneyeMode
from Goldeneye.ResultSaver.ResultSaver import ResultSaver
from Goldeneye.ResultSaver.ResultSaverStream import ResultSaverWebstream
from Goldeneye.ResultSaver.SaveMode import SaveMode
from Goldeneye.WebServer.StreamingHandler import StreamingHandler
from Goldeneye.WebServer.StreamingServer import StreamingServer
from Goldeneye.Goldeneye.GoldeneyeConfiguration import GoldeneyeConfiguration

if __name__ == "__main__":

    to_save = []
    saving = False
    saving_webstream = True
    saving_mode = SaveMode.CONTINUOUS

    address = ('', 8000)
    StreamingHandler.result = None
    server = StreamingServer(address, StreamingHandler)

    GoldeneyeConfiguration.vertical_camera_flip = True
    GoldeneyeConfiguration.horizontal_camera_flip = True

    K.clear_session()
    eye = Goldeneye()
    eye.start()

    web_server = threading.Thread(target=server.serve_forever, daemon=True)
    web_server.start()

    ard = serial.Serial('/dev/serial0', 115200, timeout=10)
    ard.close()
    ard.open()
    ard.reset_input_buffer()
    ard.reset_output_buffer()

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

    ard.write("140\n".encode())
    ard.write("160\n".encode())

    while True:
        result = eye.result.get()
        if eye.mode == GoldeneyeMode.SKIPPED:
            p_fps_divider = eye.stream_processor.images_processed
        else:
            p_fps_divider = result[0][2]
        result.append([(time.time() - eye.camera.start_time),
                       eye.stream_processor.images_captured,
                       p_fps_divider])
        StreamingHandler.result = result
        if result[0][0] is not -1:
            print("Time taken: {}".format(result[1][2]))
            print("Frame Number: {}".format(result[0][2]))
            print("Signal Number: {}".format(result[0][0]))
            print("Signal Type: {}".format(result[0][1]))
            print("-------------------------------------")
        if saving or saving_webstream:
            to_save.append(result)
        i, _, _ = select.select([sys.stdin], [], [], 0.01)
        if i == [sys.stdin]:
            break

    print("Stopping!")
    ard.write("140\n".encode())
    ard.write("100\n".encode())

    time.sleep(4)

    ard.write("140\n".encode())
    ard.write("60\n".encode())

    time.sleep(4)

    ard.write("190\n".encode())

    eye.stop()
    time.sleep(1)
    print(eye.stats())
    print("-------------------------------------")

    while eye.result.qsize() > 0:
        result = eye.result.get()
        if eye.mode == GoldeneyeMode.SKIPPED:
            p_fps_divider = eye.stream_processor.images_processed
        else:
            p_fps_divider = result[0][2]
        result.append([(time.time() - eye.camera.start_time),
                       eye.stream_processor.images_captured,
                       p_fps_divider])
        StreamingHandler.result = result
        if result[0][0] is not -1:
            print("Time taken: {}".format(result[1][2]))
            print("Frame Number: {}".format(result[0][2]))
            print("Signal Number: {}".format(result[0][0]))
            print("Signal Type: {}".format(result[0][1]))
            print("-------------------------------------")
        if saving or saving_webstream:
            to_save.append(result)

    if saving:
        ResultSaver(to_save, save_mode=saving_mode)
    if saving_webstream:
        ResultSaverWebstream(to_save)
    time.sleep(5)  # wait for streaming server
    eye.terminate()

# !!!!!!!!!!!!!!!
# Camera position
# 84.49 mm



