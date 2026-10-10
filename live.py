import psutil
from collections import deque

from spike import SpikeDetector

detector = SpikeDetector()
history = deque(maxlen=30)

while True:
    cpu = psutil.cpu_percent(interval=1)

    if detector.check("cpu", cpu, history):
        print(f"SPIKE: CPU {cpu:.0f}%")

    history.append(cpu)