import threading
import time

class TimeOutThread(threading.Thread):
    def __init__(self, resend_interval, get_chunk, key, ip):
        super(TimeOutThread, self).__init__()
        self.resend_interval = resend_interval
        self.get_chunk = get_chunk
        self.key = key
        self.ip = ip
        self.stop_event = threading.Event()

    def run(self):
        start_time = time.time()

        while time.time() - start_time < self.resend_interval:
            if self.stop_event.is_set():
                return
            time.sleep(0.5)
        self.get_chunk(self.key, self.ip)
        return