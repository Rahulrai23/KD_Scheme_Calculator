from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# --------------------------------
# ROOT (HEALTH CHECK)
# --------------------------------
@app.route("/")
def home():
    return "Scheme Calculator Running ✅"

# --------------------------------
# SINGLE ENTRY POINT (IMPORTANT)
# --------------------------------
@app.route("/scheme")
def scheme():
    return render_template("scheme_rajasthan.html")

# --------------------------------
# REQUIRED FOR RENDER
# --------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
