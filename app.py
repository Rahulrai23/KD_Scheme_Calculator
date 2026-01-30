from flask import Flask, render_template, request, abort
import requests
import os

app = Flask(__name__)

# -------------------------------
# STATE → TEMPLATE MAPPING
# -------------------------------
STATE_TEMPLATE_MAP = {
    "Delhi": "scheme_delhi_ncr.html",
    "Haryana": "scheme_haryana.html",
    "Rajasthan": "scheme_rajasthan.html",
    "Punjab": "scheme_punjab.html",
    "Uttar Pradesh": "scheme_uttar_pradesh.html",
    "Gujarat": "scheme_gujarat.html",
    "Maharashtra": "scheme_mumbai.html",
    "Tamil Nadu": "scheme_tamil_nadu.html",
    "Karnataka": "scheme_karnataka.html",
    "Telangana": "scheme_telangana.html",
    "West Bengal": "scheme_west_bengal.html",
    "Kerala": "scheme_kerala.html",
    "Odisha": "scheme_odisha.html",
    "Jharkhand": "scheme_jharkhand.html",
    "Bihar": "scheme_bihar.html",
    "Assam": "scheme_assam.html",
    "Chhattisgarh": "scheme_chhattisgarh.html",
    "Madhya Pradesh": "scheme_madhya_pradesh.html",
    "Uttarakhand": "scheme_uttarakhand.html",
    "Andhra Pradesh": "scheme_andhra_pradesh.html",
    "Rest of Maharashtra": "scheme_rest_of_maharashtra.html"
}

# -------------------------------
# IP → STATE DETECTION
# -------------------------------
def detect_state(ip):
    try:
        res = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3).json()
        return res.get("region")
    except:
        return None

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def home():
    return "KC Scheme Calculator Running ✅"

# -------------------------------
# SINGLE ENTRY POINT (SECURE)
# -------------------------------
@app.route("/scheme")
def scheme():
    # Render forwards real client IP here
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    state = detect_state(ip)

    if not state:
        return "❌ Unable to detect your location", 403

    template = STATE_TEMPLATE_MAP.get(state)

    if not template:
        return f"❌ Scheme not available for {state}", 403

    return render_template(template)

# -------------------------------
# BLOCK DIRECT STATE ACCESS
# -------------------------------
@app.route("/scheme/<state>")
def block_direct_access(state):
    abort(403, "Direct access is not allowed. Please use /scheme")

# -------------------------------
# REQUIRED FOR RENDER
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
