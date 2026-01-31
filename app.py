from flask import Flask, render_template, request, abort, session
import requests, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "kc-secure-key")

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
    "west bengal": "scheme_west_bengal.html",
    "unknown": "scheme_unknown.html"
}

# ----------------------------------
# CLIENT IP (RENDER SAFE)
# ----------------------------------
def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0].strip() if forwarded else request.remote_addr

# ----------------------------------
# IP → STATE DETECTION (FIXED)
# ----------------------------------
def detect_state_from_ip(ip):
    try:
        res = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=3
        ).json()

        city = (res.get("city") or "").lower()
        region = (res.get("region") or "").lower()

        # ✅ NCR override ONLY if region matches NCR states
        if (
            city in ["delhi", "new delhi", "noida", "gurgaon", "faridabad", "ghaziabad"]
            and region in ["delhi", "haryana", "uttar pradesh"]
        ):
            return "delhi"

        # ✅ Normal state detection
        if region in STATE_TEMPLATE_MAP:
            return region

    except Exception:
        pass

    return None

# ----------------------------------
# GPS → STATE DETECTION (PRIMARY)
# ----------------------------------
def detect_state_from_gps(lat, lon):
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "json"
            },
            headers={
                "User-Agent": "kc-scheme-calculator"
            },
            timeout=5
        ).json()

        state = (
            res.get("address", {})
               .get("state", "")
               .lower()
        )

        if state in STATE_TEMPLATE_MAP:
            return state

    except Exception:
        pass

    return None

# ----------------------------------
# HOME → GPS REQUEST PAGE
# ----------------------------------
@app.route("/")
def home():
    return render_template("detect.html")

# ----------------------------------
# GPS ENDPOINT (LOCK ONCE)
# ----------------------------------
@app.route("/gps-detect", methods=["POST"])
def gps_detect():

    if "locked_state" in session:
        return "", 204

    data = request.get_json() or {}
    lat = data.get("lat")
    lon = data.get("lon")

    if not lat or not lon:
        return "", 204

    state = detect_state_from_gps(lat, lon)

    if state:
        session["locked_state"] = state

    return "", 204

# ----------------------------------
# SCHEME (GPS → IP → ERROR)
# ----------------------------------
@app.route("/scheme")
def scheme():

    # 🔒 Locked → never change
    if "locked_state" in session:
        state = session["locked_state"]
        return render_template(
            STATE_TEMPLATE_MAP[state],
            state_name=state.upper()
        )

    # 🌐 IP fallback
    ip = get_client_ip()
    state = detect_state_from_ip(ip)

    if not state:
        return render_template(
            "error.html",
            message="State Scheme Not Found"
        )

    session["locked_state"] = state

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
# RUN (RENDER)
# ----------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
