import json, os
from datetime import datetime

class QueueManager:
    def __init__(self, queue_file="queue.json"):
        self.queue_file = queue_file

    def load(self):
        if not os.path.exists(self.queue_file):
            return []
        with open(self.queue_file, "r") as f:
            return json.load(f)

    def save(self, queue):
        with open(self.queue_file, "w") as f:
            json.dump(queue, f, indent=2)

    def add(self, job):
        queue = self.load()
        job["queued_at"] = datetime.utcnow().isoformat()
        queue.append(job)
        self.save(queue)

    def pop(self):
        queue = self.load()
        if not queue:
            return None
        job = queue.pop(0)
        self.save(queue)
        return job

    def clear(self):
        self.save([])
