import time
import asyncio
from src.esp32_receiver.core.config import settings

class UsageTracker:
    def __init__(self):
        self.phone_usage_start = None
        self.alert_sent = False
        self.lock = asyncio.Lock()

    async def update(self, usage_detected: bool) -> bool:
        """Updates the state and returns True if an alert should be triggered."""
        async with self.lock:
            if usage_detected:
                if self.phone_usage_start is None:
                    self.phone_usage_start = time.time()
                    self.alert_sent = False
                    return False
                else:
                    elapsed = time.time() - self.phone_usage_start
                    if elapsed >= settings.PHONE_USAGE_THRESHOLD_SECONDS and not self.alert_sent:
                        self.alert_sent = True
                        return True
                    return False
            else:
                self.phone_usage_start = None
                self.alert_sent = False
                return False

    def get_streak_info(self):
        if self.phone_usage_start:
            return f"{(time.time() - self.phone_usage_start):.1f}s streak"
        return "none"

tracker = UsageTracker()
