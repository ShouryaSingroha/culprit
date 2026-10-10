import time
from collections import deque

import psutil

from spike import SpikeDetector
from suspects import prime, top_by_cpu

prime()
time.sleep(1)

detector = SpikeDetector()
history = deque(maxlen=30)

while True:
    cpu = psutil.cpu_percent(interval=1)

    if detector.check("cpu", cpu, history):
        print(f"\nSPIKE: CPU {cpu:.0f}%")
        for info in top_by_cpu():
            print(f"   {info['name']} (pid {info['pid']}): {info['cpu_percent']}%")

    history.append(cpu)