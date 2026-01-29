@app.route("/scheme/rajasthan")
def scheme_rajasthan():
    return render_template("scheme_rajasthan.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

