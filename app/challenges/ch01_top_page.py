from flask import Blueprint, render_template

import flags

bp = Blueprint("top", __name__)


@bp.route("/")
def index():
    return render_template("index.html", flag_01=flags.FLAG_01)
