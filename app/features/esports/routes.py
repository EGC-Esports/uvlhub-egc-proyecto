from flask import render_template

from app.features.esports import esports_bp


@esports_bp.route("/esports", methods=["GET"])
def index():
    return render_template("esports/index.html")
