from threading import Thread


class CommunicationTest(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.reading = True
        self.terminated = False

    def run(self):
        while not self.terminated:
            self.test_reading()

    def test_reading(self):
        while self.reading:
            print("reading...")

    def test_writing(self, text):
        self.reading = False
        for i in range(0, 50):
            print(text)
        self.reading = True
