from flask import Flask, render_template, request, abort, make_response
import requests
import os

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
# DISABLE CACHE (IMPORTANT)
# ----------------------------------
@app.after_request
def disable_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# ----------------------------------
# CLIENT IP (RENDER SAFE)
# ----------------------------------
def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0].strip() if forwarded else request.remote_addr

# ----------------------------------
# GPS → STATE
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
        state = (data.get("address", {}).get("state") or "").lower()
        return state if state in STATE_TEMPLATE_MAP else None
    except Exception:
        return None

# ----------------------------------
# IP → STATE
# ----------------------------------
def detect_state_from_ip(ip):
    try:
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3).json()
        city = (resp.get("city") or "").lower()
        region = (resp.get("region") or "").lower()

        if "delhi" in city or "delhi" in region:
            return "delhi"

        return region if region in STATE_TEMPLATE_MAP else None
    except Exception:
        return None

# ----------------------------------
# HOME
# ----------------------------------
@app.route("/")
def home():
    return render_template("detect.html")

# ----------------------------------
# GPS ENDPOINT (SHORT COOKIE)
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
            max_age=30,
            httponly=True,
            samesite="Lax"
        )

    return resp

# ----------------------------------
# SCHEME RESOLUTION (GPS → IP → PARAM)
# ----------------------------------
@app.route("/scheme")
def scheme():
    # 1️⃣ GPS cookie (highest priority)
    state = (request.cookies.get("gps_state") or "").lower()

    # 2️⃣ IP fallback
    if not state:
        state = detect_state_from_ip(get_client_ip()) or ""

    # 3️⃣ Explicit query param fallback (manual selection)
    if not state:
        raw = request.args.get("state", "").lower()
        if "delhi" in raw or "nct" in raw:
            state = "delhi"
        elif raw in STATE_TEMPLATE_MAP:
            state = raw

    # FINAL CHECK
    if state in STATE_TEMPLATE_MAP:
        return render_template(
            STATE_TEMPLATE_MAP[state],
            state_name=state.upper()
        )

    return render_template(
        "error.html",
        message="State Scheme Not Found"
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
