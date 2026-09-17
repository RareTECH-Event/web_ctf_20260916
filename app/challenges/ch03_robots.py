from flask import Blueprint, Response, render_template

import flags

bp = Blueprint("robots", __name__)

INVENTORY_PATH = "/warehouse-admin-9x7f2"


@bp.route("/robots.txt")
def robots_txt():
    lines = [
        "User-agent: *",
        f"Disallow: {INVENTORY_PATH}",
    ]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


@bp.route(INVENTORY_PATH)
def inventory():
    return render_template("inventory.html", flag_03=flags.FLAG_03)
