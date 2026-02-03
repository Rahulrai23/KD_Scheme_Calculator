from flask import Flask, render_template, request, abort, make_response
import requests
import os
import re

app = Flask(__name__)

# ----------------------------------
# STATE → TEMPLATE MAP
# ----------------------------------
STATE_TEMPLATE_MAP = {
    "andhra pradesh": "scheme_andhra_pradesh.html",
    "assam": "scheme_assam.html",
    "bihar": "scheme_bihar.html",
    "chhattisgarh": "scheme_chhattisgarh.html",
    "delhi": "scheme_delhi_ncr.html",
    "gujarat": "scheme_gujarat.html",
    "haryana": "scheme_haryana.html",
    "jharkhand": "scheme_jharkhand.html",
    "karnataka": "scheme_karnataka.html",
    "kerala": "scheme_kerala.html",
    "madhya pradesh": "scheme_madhya_pradesh.html",
    "maharashtra": "scheme_rest_of_maharashtra.html",
    "odisha": "scheme_odisha.html",
    "punjab": "scheme_punjab.html",
    "rajasthan": "scheme_rajasthan.html",
    "tamil nadu": "scheme_tamil_nadu.html",
    "telangana": "scheme_telangana.html",
    "uttar pradesh": "scheme_uttar_pradesh.html",
    "uttarakhand": "scheme_uttarakhand.html",
    "west bengal": "scheme_west_bengal.html"
}

DEFAULT_STATE = "delhi"   # FINAL SAFETY NET

# ----------------------------------
# NO CACHE
# ----------------------------------
@app.after_request
def disable_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# ----------------------------------
# NORMALIZE STATE
# ----------------------------------
def normalize_state(raw):
    if not raw:
        return None

    raw = raw.lower().strip()
    raw = re.sub(r"^state of ", "", raw)
    raw = re.sub(r"^national capital territory of ", "", raw)

    if "delhi" in raw or "nct" in raw:
        return "delhi"

    return raw if raw in STATE_TEMPLATE_MAP else None

# ----------------------------------
# GPS → STATE (PRIMARY)
# ----------------------------------
def detect_state_from_gps(lat, lon):
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "kc-scheme-calculator"},
            timeout=5
        )
        data = resp.json()
        return normalize_state(data.get("address", {}).get("state"))
    except Exception:
        return None

# ----------------------------------
# IP → STATE (BEST EFFORT ONLY)
# ----------------------------------
def detect_state_from_ip():
    try:
        ip = request.headers.get("X-Forwarded-For", "").split(",")[0]
        if not ip:
            return None

        resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3).json()
        return normalize_state(resp.get("region"))
    except Exception:
        return None

# ----------------------------------
# HOME
# ----------------------------------
@app.route("/")
def home():
    return render_template("detect.html")

# ----------------------------------
# GPS CAPTURE
# ----------------------------------
@app.route("/gps-detect", methods=["POST"])
def gps_detect():
    data = request.get_json() or {}
    lat, lon = data.get("lat"), data.get("lon")

    resp = make_response("", 204)

    state = detect_state_from_gps(lat, lon) if lat and lon else None
    if state:
        resp.set_cookie(
            "gps_state",
            state,
            max_age=300,
            path="/",
            samesite="Lax"
        )

    return resp

# ----------------------------------
# SCHEME (FINAL)
# ----------------------------------
@app.route("/scheme")
def scheme():
    # 1️⃣ GPS cookie
    state = normalize_state(request.cookies.get("gps_state"))

    # 2️⃣ IP fallback
    if not state:
        state = detect_state_from_ip()

    # 3️⃣ Final fallback
    if not state:
        state = DEFAULT_STATE

    return render_template(
        STATE_TEMPLATE_MAP[state],
        state_name=state.upper()
    )

# ----------------------------------
# BLOCK URL TAMPERING
# ----------------------------------
@app.route("/scheme/<path:anything>")
def block(anything):
    abort(403)

# ----------------------------------
# RUN
# ----------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
