from flask import Flask, render_template, request, abort, make_response
import ipaddress
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
# NORMALIZE STATE
# ----------------------------------
def normalize_state(raw_state):
    state = (raw_state or "").strip().lower()

    if not state:
        return ""

    if "delhi" in state or "nct" in state:
        return "delhi"

    return state

# ----------------------------------
# GPS → STATE (SAFE)
# ----------------------------------
def detect_state_from_gps(lat, lon):
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "kc-scheme-calculator"},
            timeout=5
        )

        if not resp.headers.get("Content-Type", "").startswith("application/json"):
            return None

        data = resp.json()
        state = normalize_state(data.get("address", {}).get("state"))

        if state in STATE_TEMPLATE_MAP:
            return state

    except Exception:
        pass

    return None

# ----------------------------------
# IP → STATE (BULLETPROOF)
# ----------------------------------
def detect_state_from_ip(ip):
    ip_is_private = False
    if ip:
        try:
            ip_is_private = ipaddress.ip_address(ip).is_private
        except ValueError:
            ip_is_private = False

    # -------- 1️⃣ ipapi.co --------
    try:
        ipapi_url = "https://ipapi.co/json/" if ip_is_private or not ip else f"https://ipapi.co/{ip}/json/"
        resp = requests.get(ipapi_url, timeout=3)
        if resp.headers.get("Content-Type", "").startswith("application/json"):
            data = resp.json()
            region = normalize_state(data.get("region"))

            if region in STATE_TEMPLATE_MAP:
                return region
    except Exception:
        pass

    # -------- 2️⃣ ipinfo.io (FALLBACK) --------
    try:
        ipinfo_url = "https://ipinfo.io/json" if ip_is_private or not ip else f"https://ipinfo.io/{ip}/json"
        resp = requests.get(ipinfo_url, timeout=3)
        if resp.headers.get("Content-Type", "").startswith("application/json"):
            data = resp.json()
            region = normalize_state(data.get("region"))

            if region in STATE_TEMPLATE_MAP:
                return region
    except Exception:
        pass

    return None

# ----------------------------------
# HOME
# ----------------------------------
@app.route("/")
def home():
    return render_template("detect.html")

# ----------------------------------
# GPS ENDPOINT (SHORT-LIVED COOKIE)
# ----------------------------------
@app.route("/gps-detect", methods=["POST"])
def gps_detect():
    data = request.get_json() or {}
    lat, lon = data.get("lat"), data.get("lon")

    resp = make_response("", 204)

    if lat and lon:
        state = detect_state_from_gps(lat, lon)
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
# SCHEME (GPS → IP → ERROR)
# ----------------------------------
@app.route("/scheme")
def scheme():
    candidates = []

    raw_state = normalize_state(request.args.get("state"))
    if raw_state:
        candidates.append(raw_state)

    gps_state = normalize_state(request.cookies.get("gps_state"))
    if gps_state:
        candidates.append(gps_state)

    ip_state = detect_state_from_ip(get_client_ip())
    if ip_state:
        candidates.append(ip_state)

    for candidate in candidates:
        if candidate in STATE_TEMPLATE_MAP:
            return render_template(
                STATE_TEMPLATE_MAP[candidate],
                state_name=candidate.upper()
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
# RUN (RENDER)
# ----------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
