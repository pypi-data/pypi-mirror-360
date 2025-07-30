from collections import defaultdict

class Analytics:
    def __init__(self):
        self.metrics = defaultdict(int)

    def record(self, event, backend_host=None):
        key = f"{event}:{backend_host}" if backend_host else event
        self.metrics[key] += 1

    def get_metrics(self):
        return dict(self.metrics)
