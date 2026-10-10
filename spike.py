import statistics


def baseline(samples):
    mean = statistics.mean(samples)
    stdev = statistics.pstdev(samples) or 1.0  # flat data would give 0
    return mean, stdev


def is_spike(value, mean, stdev, multiplier=2.5, floor=20):
    threshold = mean + max(multiplier * stdev, floor)
    return value > threshold


if __name__ == "__main__":
    quiet = [2, 3, 2, 4, 2, 3, 2, 3, 2, 3]
    mean, stdev = baseline(quiet)
    print(f"baseline: mean={mean:.1f} stdev={stdev:.2f}")
    print("jump to 8%: ", is_spike(8, mean, stdev))
    print("jump to 45%:", is_spike(45, mean, stdev))