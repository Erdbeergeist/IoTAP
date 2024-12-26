from flask import Flask, jsonify, render_template
import time
import threading
import subprocess
import logging

app = Flask(__name__)
shutdown_timer = None
timeout = 1200 
shutdown_expiration = None

AP_NAME = "iotap"
logging.basicConfig(filename='ap_control.log', level=logging.DEBUG)

def disable_wifi():
    """Disable wifi"""
    shutdown_timer = None
    shutdown_expiration = None
    subprocess.run(["sudo", "nmcli", "connection", "down", AP_NAME])


def get_ap_status():
    """Check if the access point is active."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "ACTIVE", "connection", "show", AP_NAME],
            capture_output=True, text=True
        )
        return "general.state:activated" in result.stdout.strip().lower()
    except Exception as e:
        print(f"Error checking AP status: {e}")
        return False

def toggle_ap():
    """Toggle the access point state."""
    global shutdown_timer, shutdown_expiration
    if get_ap_status():
        shutdown_expiration = None
        if shutdown_timer:
            shutdown_timer.cancel()
        subprocess.run(["sudo", "nmcli", "connection", "down", AP_NAME])
        return False
    else:
        if shutdown_timer:
            shutdown_timer.cancel()
        shutdown_timer = threading.Timer(timeout, disable_wifi)
        shutdown_expiration = time.time() + timeout
        shutdown_timer.start()
        subprocess.run(["sudo", "nmcli", "connection", "up", AP_NAME])
        return True

@app.route("/")
def index():
    """Serve the webpage with the toggle button."""
    status = get_ap_status()
    return render_template("index.html", status=status)

@app.route("/status")
def status():
    """API endpoint to check AP status."""
    return jsonify({"ap_active": get_ap_status()})

@app.route("/toggle", methods=["POST"])
def toggle():
    """API endpoint to toggle AP status."""
    new_status = toggle_ap()
    return jsonify({"ap_active": new_status})

@app.route("/remaining_time", methods=["GET"])
def get_remaining_time():
    global shutdown_expiration
    if get_ap_status() and shutdown_expiration:
        remaining_time = max(0, int(shutdown_expiration - time.time()))
        return jsonify({"remaining_time": remaining_time}), 200
    else:
        return jsonify({"remaining_time": 0}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
