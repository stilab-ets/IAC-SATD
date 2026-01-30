import time
from collections import deque


class APIKeyManager:
    def __init__(self, api_keys, rate_limit=20, time_window=90):
        self.api_keys = deque(api_keys)  # Rotate keys in a round-robin manner
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.usage = {key: deque() for key in api_keys}  # Track request timestamps per key

    def get_available_key(self):

        while True:

            for _ in range(len(self.api_keys)):
                key = self.api_keys[0]  # Get the first key in the queue
                timestamps = self.usage[key]

                # Remove timestamps older than the time window
                while timestamps and timestamps[0] < time.time() - self.time_window:
                    timestamps.popleft()

                if len(timestamps) < self.rate_limit:
                    timestamps.append(time.time())  # Record usage
                    self.api_keys.rotate(-1)  # Move this key to the end
                    return key

                self.api_keys.rotate(-1)  # Move this key to the end if it exceeded the limit

            # If all keys are exhausted, wait a short period before retrying
            time.sleep(60)