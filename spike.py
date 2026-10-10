import statistics
import time

def baseline(samples):
    mean = statistics.mean(samples)
    stdev = statistics.pstdev(samples) or 1.0  # flat data would give 0
    return mean, stdev


def is_spike(value, mean, stdev, multiplier=2.5, floor=20):
    threshold = mean + max(multiplier * stdev, floor)
    return value > threshold
    

class SpikeDetector:
    def __init__(self, cooldown_seconds=8, window=30):
        self.cooldown_seconds = cooldown_seconds
        self.window = window
        self.last_flagged = {}  # metric name -> time of last alert

    def check(self, metric, value, history):
        if len(history) < self.window:
            return False  # still learning what's normal

        mean, stdev = baseline(list(history)[-self.window:])
        if not is_spike(value, mean, stdev):
            return False

        now = time.time()
        last = self.last_flagged.get(metric)
        if last is not None and now - last < self.cooldown_seconds:
            return False  # same burst, already reported

        self.last_flagged[metric] = now
        return True


if __name__ == "__main__":
    quiet = [2, 3, 2, 4, 2, 3, 2, 3, 2, 3]
    mean, stdev = baseline(quiet)
    print(f"baseline: mean={mean:.1f} stdev={stdev:.2f}")
    print("jump to 8%: ", is_spike(8, mean, stdev))
    print("jump to 45%:", is_spike(45, mean, stdev))