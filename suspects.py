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

def top_by_connections(limit=5):
    counts = {}
    try:
        connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        return []
    for c in connections:
        if c.pid:
            counts[c.pid] = counts.get(c.pid, 0) + 1

    results = []
    for pid, n in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]:
        try:
            results.append({"pid": pid, "name": psutil.Process(pid).name(), "connections": n})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return results


if __name__ == "__main__":
    import time

    prime()
    time.sleep(1)
    for info in top_by_cpu():
        print(f"{info['name']:<30} pid {info['pid']:<7} {info['cpu_percent']}% CPU")