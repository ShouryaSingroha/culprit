import psutil


def prime():
    """Call once at startup so later cpu_percent readings are real."""
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def top_by_cpu(limit=5):
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
        procs.append(p.info)
    procs.sort(key=lambda info: info["cpu_percent"] or 0, reverse=True)
    return procs[:limit]


def top_by_memory(limit=5):
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_percent"]):
        procs.append(p.info)
    procs.sort(key=lambda info: info["memory_percent"] or 0, reverse=True)
    return procs[:limit]


if __name__ == "__main__":
    import time

    prime()
    time.sleep(1)
    for info in top_by_cpu():
        print(f"{info['name']:<30} pid {info['pid']:<7} {info['cpu_percent']}% CPU")