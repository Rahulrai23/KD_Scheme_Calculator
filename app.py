from flask import Flask, render_template, request, abort
import requests
import os

app = Flask(__name__)

# --------------------------------------------------
# STATE → TEMPLATE MAPPING (KEYS NORMALIZED)
# --------------------------------------------------
STATE_TEMPLATE_MAP = {
    "delhi": "scheme_delhi_ncr.html",
    "national capital territory of delhi": "scheme_delhi_ncr.html",
    "haryana": "scheme_haryana.html",
    "rajasthan": "scheme_rajasthan.html",
    "punjab": "scheme_punjab.html",
    "uttar pradesh": "scheme_uttar_pradesh.html",
    "gujarat": "scheme_gujarat.html",
    "maharashtra": "scheme_mumbai.html",
    "tamil nadu": "scheme_tamil_nadu.html",
    "karnataka": "scheme_karnataka.html",
    "telangana": "scheme_telangana.html",
    "west bengal": "scheme_west_bengal.html",
    "kerala": "scheme_kerala.html",
    "odisha": "scheme_odisha.html",
    "jharkhand": "scheme_jharkhand.html",
    "bihar": "scheme_bihar.html",
    "assam": "scheme_assam.html",
    "chhattisgarh": "scheme_chhattisgarh.html",
    "madhya pradesh": "scheme_madhya_pradesh.html",
    "uttarakhand": "scheme_uttarakhand.html",
    "andhra pradesh": "scheme_andhra_pradesh.html",
    "rest of maharashtra": "scheme_rest_of_maharashtra.html"
}

# --------------------------------------------------
# IP → STATE DETECTION (RENDER SAFE)
# --------------------------------------------------
def get_client_ip():
    """
    Handles Render / proxy headers safely
    """
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


def detect_state(ip):
    """
    Uses ipapi (India-friendly)
    """
    try:
        res = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=4
        ).json()

        # Prefer region, fallback to city-based NCR logic
        region = res.get("region", "").strip()
        city = res.get("city", "").lower()

        # NCR override (important)
        if city in ["delhi", "new delhi", "noida", "gurgaon", "faridabad", "ghaziabad"]:
            return "delhi"

        return region.lower()

    except Exception:
        return None


# --------------------------------------------------
# HOME
# --------------------------------------------------
@app.route("/")
def home():
    return "KC Scheme Calculator Running ✅"


# --------------------------------------------------
# SINGLE ENTRY POINT (SECURE)
# --------------------------------------------------
@app.route("/scheme")
def scheme():
    ip = get_client_ip()
    state = detect_state(ip)

    if not state:
        abort(403, "❌ Unable to detect your location")

    template = STATE_TEMPLATE_MAP.get(state)

    if not template:
        abort(403, f"❌ Scheme not available for {state.title()}")

    return render_template(
        template,
        state_name=state.upper()
    )


# --------------------------------------------------
# BLOCK DIRECT STATE ACCESS
# --------------------------------------------------
@app.route("/scheme/<path:anything>")
def block_direct_access(anything):
    abort(403, "❌ Direct access is not allowed. Please use /scheme")


# --------------------------------------------------
# REQUIRED FOR RENDER
# --------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
