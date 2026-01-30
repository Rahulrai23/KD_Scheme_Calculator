from flask import Flask, render_template, request, abort, session
import requests, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "kc-secure-key")

STATE_TEMPLATE_MAP = {
    "delhi": "scheme_delhi.html",
    "haryana": "scheme_haryana.html",
    "rajasthan": "scheme_rajasthan.html",
    "karnataka": "scheme_karnataka.html",
    "tamil nadu": "scheme_tamil_nadu.html",
    "telangana": "scheme_telangana.html",
    "maharashtra": "scheme_mumbai.html"
}

def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0] if forwarded else request.remote_addr

def detect_state(ip):
    try:
        res = requests.get(f"https://ipapi.co/{ip}/json/", timeout=4).json()
        city = res.get("city", "").lower()
        region = res.get("region", "").lower()

        if city in ["delhi", "new delhi", "noida", "gurgaon", "faridabad", "ghaziabad"]:
            return "delhi"

        return region
    except:
        return None

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("detect.html")

# ---------------- AUTO STATE ENTRY ----------------
@app.route("/scheme")
def scheme():
    ip = get_client_ip()
    state = detect_state(ip)

    if not state or state not in STATE_TEMPLATE_MAP:
        abort(403, "Scheme not available for your location")

    session["locked_state"] = state

    return render_template(
        STATE_TEMPLATE_MAP[state],
        state_name=state.upper()
    )

# ---------------- BLOCK ALL DIRECT ACCESS ----------------
@app.route("/scheme/confirm/<state>")
def block_state_switch(state):
    locked_state = session.get("locked_state")

    if not locked_state or state != locked_state:
        abort(403, "Unauthorized state access")

    return render_template(
        STATE_TEMPLATE_MAP[state],
        state_name=state.upper()
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
