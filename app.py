from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def home():
    return "Scheme Calculator Running ✅"

# -------------------------------
# MAIN ENTRY (ONE LINK)
# -------------------------------
@app.route("/scheme")
def scheme():
    return render_template("scheme_loader.html")

# -------------------------------
# DETECT STATE (SIMPLIFIED)
# -------------------------------
@app.route("/detect_state", methods=["POST"])
def detect_state():
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")

    # 🔴 TEMP LOGIC (India state approx mapping)
    # Later we can use Google Maps / Mapbox API
    if 23 <= lat <= 30 and 69 <= lon <= 78:
        state = "rajasthan"
    elif 20 <= lat <= 24 and 68 <= lon <= 75:
        state = "gujarat"
    elif 15 <= lat <= 22 and 72 <= lon <= 80:
        state = "maharashtra"
    else:
        state = "unknown"

    return jsonify({"state": state})

# -------------------------------
# LOAD STATE SCHEME
# -------------------------------
@app.route("/scheme_view/<state>")
def scheme_view(state):
    try:
        return render_template(f"scheme_{state}.html")
    except:
        return render_template("scheme_unknown.html")

# -------------------------------
# START
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
