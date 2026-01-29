from flask import Flask, render_template
import os

# ✅ CREATE APP FIRST
app = Flask(__name__)

# ✅ ROUTE AFTER app IS DEFINED
@app.route("/")
def home():
    return "Scheme Calculator is Running ✅"

@app.route("/scheme/rajasthan")
def scheme_rajasthan():
    return render_template("scheme_rajasthan.html")

# ✅ REQUIRED FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
