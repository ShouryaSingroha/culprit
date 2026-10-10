import threading
import time

from flask import Flask, jsonify, render_template

from engine import Monitor

app = Flask(__name__)
monitor = Monitor()
lock = threading.Lock()


def run_monitor():
    time.sleep(1)
    while True:
        with lock:
            monitor.tick()
        time.sleep(1)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def stats():
    with lock:
        data = {metric: list(h) for metric, h in monitor.history.items()}
        data["timestamps"] = list(monitor.timestamps)
    return jsonify(data)


@app.route("/api/incidents")
def incidents():
    with lock:
        return jsonify(list(monitor.incidents))


if __name__ == "__main__":
    threading.Thread(target=run_monitor, daemon=True).start()
    app.run(host="127.0.0.1", port=5000, debug=False)