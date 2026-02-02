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
        state = (data.get("address", {}).get("state") or "").lower()

        if state in STATE_TEMPLATE_MAP:
            return state

    except Exception:
        pass

    return None

# ----------------------------------
# IP → STATE (BULLETPROOF)
# ----------------------------------
def detect_state_from_ip(ip):
    try:
        resp = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=3
        )

        if not resp.headers.get("Content-Type", "").startswith("application/json"):
            return None

        data = resp.json()

        city = (data.get("city") or "").lower()
        region = (data.get("region") or "").lower()

        # 🔑 ALL Delhi / NCR / NCT variations
        delhi_aliases = [
            "delhi",
            "new delhi",
            "delhi ncr",
            "nct",
            "nct delhi",
            "nct of delhi",
            "national capital territory",
            "national capital territory of delhi"
        ]

        if any(x in city for x in delhi_aliases) or any(x in region for x in delhi_aliases):
            return "delhi"

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

    # 1️⃣ GPS cookie (fresh)
    gps_state = request.cookies.get("gps_state")
    if gps_state in STATE_TEMPLATE_MAP:
        return render_template(
            STATE_TEMPLATE_MAP[gps_state],
            state_name=gps_state.upper()
        )

    # 2️⃣ IP fallback
    ip = get_client_ip()
    state = detect_state_from_ip(ip)

    if state in STATE_TEMPLATE_MAP:
        return render_template(
            STATE_TEMPLATE_MAP[state],
            state_name=state.upper()
        )

    # 3️⃣ Final fallback (NO CRASH)
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
