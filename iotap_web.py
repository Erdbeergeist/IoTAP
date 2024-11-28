from flask import Flask, jsonify, render_template
import subprocess
import logging

app = Flask(__name__)

AP_NAME = "iotap"
logging.basicConfig(filename='ap_control.log', level=logging.DEBUG)

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
    if get_ap_status():
        subprocess.run(["sudo", "nmcli", "connection", "down", AP_NAME])
        return False
    else:
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
