import time
from collections import deque
from datetime import datetime

import psutil

from spike import SpikeDetector, baseline
from suspects import prime, top_by_cpu, top_by_memory, top_by_connections

HISTORY_LENGTH = 120

# For each metric: how to find suspects, and how to describe each one.
SUSPECTS = {
    "cpu": (top_by_cpu, lambda i: f"{i['cpu_percent']:.0f}% CPU"),
    "memory": (top_by_memory, lambda i: f"{i['memory_percent']:.1f}% RAM"),
    "disk": (top_by_cpu, lambda i: f"{i['cpu_percent']:.0f}% CPU at the time"),
    "network": (top_by_connections, lambda i: f"{i['connections']} connections"),
}


class Monitor:
    def __init__(self):
        self.detector = SpikeDetector()
        self.history = {m: deque(maxlen=HISTORY_LENGTH) for m in SUSPECTS}
        self.timestamps = deque(maxlen=HISTORY_LENGTH)
        self.incidents = deque(maxlen=50)

        prime()
        psutil.cpu_percent(None)
        self._prev_disk = psutil.disk_io_counters()
        self._prev_net = psutil.net_io_counters()
        self._prev_time = time.time()

    def _read(self):
        now = time.time()
        elapsed = max(now - self._prev_time, 0.001)
        disk = psutil.disk_io_counters()
        net = psutil.net_io_counters()

        disk_bytes = (disk.read_bytes + disk.write_bytes) - (
            self._prev_disk.read_bytes + self._prev_disk.write_bytes)
        net_bytes = (net.bytes_sent + net.bytes_recv) - (
            self._prev_net.bytes_sent + self._prev_net.bytes_recv)

        self._prev_disk, self._prev_net, self._prev_time = disk, net, now

        return {
            "cpu": psutil.cpu_percent(None),
            "memory": psutil.virtual_memory().percent,
            "disk": disk_bytes / elapsed / 1_000_000,
            "network": net_bytes / elapsed / 1_000_000,
        }

    def _record_incident(self, metric, value):
        find, describe = SUSPECTS[metric]
        mean, _ = baseline(list(self.history[metric])[-30:])
        self.incidents.appendleft({
            "time": datetime.now().strftime("%H:%M:%S"),
            "metric": metric,
            "value": round(value, 1),
            "baseline": round(mean, 1),
            "suspects": [
                {"pid": i["pid"], "name": i["name"], "detail": describe(i)}
                for i in find()
            ],
        })

    def tick(self):
        readings = self._read()

        # Check BEFORE adding, so a spike never hides inside its own baseline.
        for metric, value in readings.items():
            if self.detector.check(metric, value, self.history[metric]):
                self._record_incident(metric, value)

        for metric, value in readings.items():
            self.history[metric].append(value)
        self.timestamps.append(datetime.now().strftime("%H:%M:%S"))


if __name__ == "__main__":
    monitor = Monitor()
    time.sleep(1)
    seen = 0
    while True:
        monitor.tick()
        if len(monitor.incidents) > seen:
            seen = len(monitor.incidents)
            inc = monitor.incidents[0]
            print(f"\n[{inc['time']}] {inc['metric'].upper()} spike: "
                  f"{inc['value']} (normal {inc['baseline']})")
            for s in inc["suspects"]:
                print(f"    {s['name']} (pid {s['pid']}): {s['detail']}")
        time.sleep(1)