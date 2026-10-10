import statistics
from collections import deque

import psutil

cpu_history = deque(maxlen=30)  # last 30 readings

while True:
    cpu = psutil.cpu_percent(interval=1)

    if len(cpu_history) == 30:
        mean = statistics.mean(cpu_history)
        stdev = statistics.pstdev(cpu_history)
        print(f"CPU: {cpu:5.1f}%   normal: {mean:5.1f}%   wobble: {stdev:4.1f}")
    else:
        print(f"CPU: {cpu:5.1f}%   learning what's normal... ({len(cpu_history)}/30)")

    cpu_history.append(cpu)