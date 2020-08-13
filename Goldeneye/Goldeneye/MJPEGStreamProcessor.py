from Goldeneye.Goldeneye.GoldeneyeMode import GoldeneyeMode


class MJPEGStreamProcessor:

    def __init__(self, pool_semaphore, buffer, mode):
        self.pool_semaphore = pool_semaphore
        self.buffer = buffer
        self.images_captured = 0
        self.images_processed = 0
        self.mode = mode

    def _write_buffered(self, frame):
        self.buffer.put(frame)
        self.images_processed += 1

    def _write_skipped(self, frame):
        if self.pool_semaphore.value > 0:
            self.buffer.put(frame)
            self.images_processed += 1

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.images_captured += 1
            frame = [buf, self.images_captured]

            if self.mode == GoldeneyeMode.SKIPPED:
                self._write_skipped(frame)

            if self.mode == GoldeneyeMode.BUFFERED:
                self._write_buffered(frame)
