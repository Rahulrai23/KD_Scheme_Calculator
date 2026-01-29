from flask import Flask, render_template, abort, jsonify
import os

app = Flask(__name__)

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def home():
    return render_template("detect.html")

# -------------------------------
# AUTO-DETECT ENTRY POINT
# -------------------------------
@app.route("/scheme")
def detect_scheme():
    return render_template("detect.html")

# -------------------------------
# ALL STATES (DYNAMIC)
# -------------------------------
@app.route("/scheme/<state>")
def scheme(state):
    template_name = f"scheme_{state}.html"
    try:
        return render_template(template_name)
    except Exception:
        abort(404, description=f"Scheme not available for {state}")

# -------------------------------
# REQUIRED FOR RENDER
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
