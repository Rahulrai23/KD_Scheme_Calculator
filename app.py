from flask import Flask, render_template, request, abort, session
import requests, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "kc-secure-key")

# ----------------------------------
# STATE → TEMPLATE MAP (FIXED)
# ----------------------------------
STATE_TEMPLATE_MAP = {
    "delhi": "scheme_delhi_ncr.html",   # ✅ FIXED NAME
    "haryana": "scheme_haryana.html",
    "rajasthan": "scheme_rajasthan.html",
    "karnataka": "scheme_karnataka.html",
    "tamil nadu": "scheme_tamil_nadu.html",
    "telangana": "scheme_telangana.html",
    "maharashtra": "scheme_mumbai.html"
}

DEFAULT_STATE = "delhi"   # ✅ HARD FALLBACK (NEVER FAIL)

# ----------------------------------
# CLIENT IP (RENDER SAFE)
# ----------------------------------
def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0].strip() if forwarded else request.remote_addr

# ----------------------------------
# SAFE STATE DETECTION
# ----------------------------------
def detect_state(ip):
    try:
        res = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=3
        ).json()

        city = (res.get("city") or "").lower()
        region = (res.get("region") or "").lower()

        # NCR override
        if city in ["delhi", "new delhi", "noida", "gurgaon", "faridabad", "ghaziabad"]:
            return "delhi"

        if region in STATE_TEMPLATE_MAP:
            return region

    except Exception:
        pass

    # 🚑 FINAL SAFETY NET
    return DEFAULT_STATE

# ----------------------------------
# HOME (ENTRY POINT)
# ----------------------------------
@app.route("/")
def home():
    return render_template("detect.html")

# ----------------------------------
# SINGLE SECURE ENTRY POINT
# ----------------------------------
@app.route("/scheme")
def scheme():
    # Already locked → reuse
    if "locked_state" in session:
        state = session["locked_state"]
    else:
        ip = get_client_ip()
        state = detect_state(ip)
        session["locked_state"] = state   # 🔐 lock once

    return render_template(
        STATE_TEMPLATE_MAP[state],
        state_name=state.upper()
    )

# ----------------------------------
# BLOCK URL TAMPERING COMPLETELY
# ----------------------------------
@app.route("/scheme/<path:anything>")
def block(anything):
    abort(403, "Unauthorized state access")

# ----------------------------------
# RUN (RENDER)
# ----------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
