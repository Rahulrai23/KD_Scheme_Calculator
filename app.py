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

# ----------------------------------
# NO GLOBAL CACHE (CRITICAL)
# ----------------------------------
@app.after_request
def disable_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp

# ----------------------------------
# HELPERS
# ----------------------------------
def normalize_state(raw):
    if not raw:
        return None

    raw = raw.lower().strip()
    raw = re.sub(r"^state of ", "", raw)
    raw = re.sub(r"^national capital territory of ", "", raw)

    if "delhi" in raw:
        return "delhi"

    return raw if raw in STATE_TEMPLATE_MAP else None

def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0].strip() if forwarded else request.remote_addr

# ----------------------------------
# GPS → STATE (ONLY SOURCE WE CACHE)
# ----------------------------------
def detect_state_from_gps(lat, lon):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "kc-scheme-calculator"},
            timeout=5
        )
        data = r.json()
        return normalize_state(data.get("address", {}).get("state"))
    except:
        return None

# ----------------------------------
# IP → STATE (NO CACHE)
# ----------------------------------
def detect_state_from_ip(ip):
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3).json()
        return normalize_state(r.get("region"))
    except:
        return None

# ----------------------------------
# HOME
# ----------------------------------
@app.route("/")
def home():
    return render_template("detect.html")

# ----------------------------------
# GPS COOKIE (SHORT LIVED, SAFE)
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
            max_age=120,   # ⏱ 2 minutes only
            path="/",
            samesite="Lax"
        )

    return resp

# ----------------------------------
# SCHEME (GPS → IP)
# ----------------------------------
@app.route("/scheme")
def scheme():
    # 1️⃣ GPS cookie (cached per user)
    state = normalize_state(request.cookies.get("gps_state"))

    # 2️⃣ IP fallback (NOT cached)
    if not state:
        state = detect_state_from_ip(get_client_ip())

    if state in STATE_TEMPLATE_MAP:
        return render_template(
            STATE_TEMPLATE_MAP[state],
            state_name=state.upper()
        )

    return render_template("error.html", message="Scheme not available")

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
