import time
from threading import Lock

class RateLimiter:
    def __init__(self, rate_limit_per_minute):
        self.capacity = rate_limit_per_minute
        self.tokens = self.capacity
        self.fill_rate = self.capacity / 60  # tokens per second
        self.timestamp = time.time()
        self.lock = Lock()

    def allow(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.timestamp
            self.timestamp = now
            self.tokens += elapsed * self.fill_rate
            if self.tokens > self.capacity:
                self.tokens = self.capacity

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    def wait(self):
        while not self.allow():
            time.sleep(0.5)
