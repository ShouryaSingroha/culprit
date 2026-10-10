import time
import psutil

prev_disk = psutil.disk_io_counters()
prev_net = psutil.net_io_counters()
prev_time = time.time()

while True:
    time.sleep(1)

    disk = psutil.disk_io_counters()
    net = psutil.net_io_counters()
    now = time.time()
    elapsed = now - prev_time

    disk_bytes = (disk.read_bytes + disk.write_bytes) - (prev_disk.read_bytes + prev_disk.write_bytes)
    net_bytes = (net.bytes_sent + net.bytes_recv) - (prev_net.bytes_sent + prev_net.bytes_recv)

    print(f"Disk: {disk_bytes / elapsed / 1_000_000:.2f} MB/s   Net: {net_bytes / elapsed / 1_000_000:.2f} MB/s")

    prev_disk, prev_net, prev_time = disk, net, now