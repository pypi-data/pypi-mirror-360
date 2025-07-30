import time

class HealthMonitor:
    def __init__(self):
        self.status = {}

    def record_success(self, backend_host):
        self.status[backend_host] = {
            "status": "healthy",
            "last_success": time.time(),
            "last_error": None
        }

    def record_failure(self, backend_host, error_message):
        self.status[backend_host] = {
            "status": "failed",
            "last_success": self.status.get(backend_host, {}).get("last_success"),
            "last_error": {
                "timestamp": time.time(),
                "message": str(error_message)
            }
        }

    def get_health(self):
        return self.status

