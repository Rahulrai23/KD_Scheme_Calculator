from flask import Flask, render_template, abort
import os

app = Flask(__name__)

# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route("/")
def home():
    return """
    <h2>KC Scheme Calculator</h2>
    <p>Use URL format:</p>
    <code>/scheme/&lt;state_name&gt;</code>
    <br><br>
    Example:
    <ul>
      <li>/scheme/rajasthan</li>
      <li>/scheme/delhi_ncr</li>
      <li>/scheme/tamil_nadu</li>
    </ul>
    """

# -------------------------------
# SINGLE DYNAMIC ROUTE FOR ALL STATES
# -------------------------------
@app.route("/scheme/<state>")
def scheme(state):
    """
    Converts URL state into template name
    Example:
    /scheme/delhi_ncr -> scheme_delhi_ncr.html
    """

    template_name = f"scheme_{state}.html"

    try:
        return render_template(template_name)
    except Exception:
        abort(404, description=f"Scheme not available for: {state}")

# -------------------------------
# REQUIRED FOR RENDER
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
