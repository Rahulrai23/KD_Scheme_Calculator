from flask import Flask, render_template, request
import os
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Scheme Calculator Running ✅"

@app.route("/scheme")
def scheme():
    # Detect user IP
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    try:
        # Free IP → State API
        res = requests.get(f"https://ipapi.co/{ip}/json/").json()
        state = res.get("region", "").lower()
    except:
        state = ""

    # State-based routing
    if "rajasthan" in state:
        return render_template("scheme_rajasthan.html")

    elif "delhi" in state or "ncr" in state:
        return render_template("scheme_delhi.html")

    elif "maharashtra" in state:
        return render_template("scheme_maharashtra.html")

    # Fallback (important)
    return render_template("scheme_rajasthan.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
