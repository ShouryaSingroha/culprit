import psutil
from collections import deque

from spike import baseline, is_spike

history = deque(maxlen=30)

while True:
    cpu = psutil.cpu_percent(interval=1)

    if len(history) == 30:
        mean, stdev = baseline(history)
        if is_spike(cpu, mean, stdev):
            print(f"SPIKE: CPU {cpu:.0f}% (normal {mean:.0f}%)")

    history.append(cpu)