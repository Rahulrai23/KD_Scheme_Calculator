from flask import Flask, render_template, request, abort, session
import requests, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "kc-secure-key")

# -------------------------------------
# STATE → TEMPLATE MAP (LOCKED)
# -------------------------------------
STATE_TEMPLATE_MAP = {
    "delhi": "scheme_delhi.html",
    "haryana": "scheme_haryana.html",
    "rajasthan": "scheme_rajasthan.html",
    "karnataka": "scheme_karnataka.html",
    "tamil nadu": "scheme_tamil_nadu.html",
    "telangana": "scheme_telangana.html",
    "maharashtra": "scheme_mumbai.html"
}

# -------------------------------------
# CLIENT IP (RENDER SAFE)
# -------------------------------------
def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr

# -------------------------------------
# IP → STATE DETECTION
# -------------------------------------
def detect_state(ip):
    try:
        res = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=4
        ).json()

        city = res.get("city", "").lower()
        region = res.get("region", "").lower()

        # NCR override
        if city in ["delhi", "new delhi", "noida", "gurgaon", "faridabad", "ghaziabad"]:
            return "delhi"

        return region

    except Exception:
        return None

# -------------------------------------
# HOME (DETECT PAGE)
# -------------------------------------
@app.route("/")
def home():
    return render_template("detect.html")

# -------------------------------------
# SINGLE ENTRY POINT (LOCKED)
# -------------------------------------
@app.route("/scheme")
def scheme():
    # If state already locked, reuse it
    if "locked_state" in session:
        state = session["locked_state"]
    else:
        ip = get_client_ip()
        state = detect_state(ip)

        if not state or state not in STATE_TEMPLATE_MAP:
            abort(403, "Scheme not available for your location")

        session["locked_state"] = state  # 🔐 lock once

    return render_template(
        STATE_TEMPLATE_MAP[state],
        state_name=state.upper()
    )

# -------------------------------------
# BLOCK EVERYTHING ELSE
# -------------------------------------
@app.route("/scheme/<path:anything>")
def block_all(anything):
    abort(403, "Unauthorized state access")

# -------------------------------------
# RUN
# -------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
