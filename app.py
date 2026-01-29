from flask import Flask, render_template, abort
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return "Scheme Calculator is Running ✅"

# 🔥 DYNAMIC STATE ROUTE
@app.route("/scheme/<state>")
def scheme_state(state):
    template_name = f"scheme_{state}.html"

    try:
        return render_template(template_name)
    except:
        abort(404)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
