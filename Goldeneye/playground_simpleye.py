import select
import sys
import threading
import time

from ResultSaver.SimpleResultSaver import SimpleResultSaver
from Simpleye.Simpleye import Simpleye
from WebServer.SimpleStreamingHandler import SimpleStreamingHandler
from WebServer.StreamingServer import StreamingServer

if __name__ == "__main__":

    # Configuration for Simpleye
    fps = 40
    x = 320
    y = 240
    shutter_speed = 750

    to_save = []
    saving = True

    address = ('', 8000)
    SimpleStreamingHandler.frame = None
    server = StreamingServer(address, SimpleStreamingHandler)

    eye = Simpleye(fps=fps, x=x, y=y, shutter_speed=shutter_speed)
    eye.start()

    web_server = threading.Thread(target=server.serve_forever, daemon=True)
    web_server.start()

    while True:
        frame = eye.buffer.get()
        SimpleStreamingHandler.frame = frame[0]
        if saving:
            to_save.append(frame)
        i, _, _ = select.select([sys.stdin], [], [], 0.01)
        if i == [sys.stdin]:
            break
    print("Stopping!")
    eye.stop()
    time.sleep(1)
    print(eye.stats())
    print("-------------------------------------")
    while eye.buffer.qsize() > 0:
        frame = eye.buffer.get()
        SimpleStreamingHandler.frame = frame[0]
        if saving:
            to_save.append(frame)
        i, _, _ = select.select([sys.stdin], [], [], 0.01)
    if saving:
        SimpleResultSaver(to_save)
    time.sleep(5)  # wait for streaming server
    eye.terminate()

# !!!!!!!!!!!!!!!
# Camera position
# 84.49 mm



