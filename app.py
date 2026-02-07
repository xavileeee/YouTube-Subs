import os
from flask import Flask, render_template, request, flash
from download_subs import fetch_subs

app = Flask(__name__)
app.secret_key = "dev-secret"  # para flash


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    url_value = request.form.get("url", "")
    lang_value = request.form.get("lang", "es")
    if request.method == "POST":
        url = url_value.strip()
        lang = lang_value
        if not url:
            flash("Introduce una URL válida")
        else:
            try:
                raw, cleaned, _ = fetch_subs(url, lang)
                result = {"raw": raw, "cleaned": cleaned, "lang": lang}
            except Exception as e:
                flash(str(e))
    return render_template("index.html", result=result, url=url_value, lang=lang_value)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5555))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
