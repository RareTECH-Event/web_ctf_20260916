from flask import Blueprint, redirect, render_template, request, session, url_for

import flags
from app.models import get_db

bp = Blueprint("mypage", __name__)


@bp.route("/mypage")
def mypage():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return render_template("mypage.html", user=user)


@bp.route("/store-admin")
def store_admin():
    # 脆弱性(問4): サーバー側の認可判定を、署名なしのCookie値だけで行っている。
    # ログイン時に発行される role Cookie を admin に書き換えるだけで突破できる。
    if request.cookies.get("role") == "admin":
        return render_template("store_admin.html", flag_04=flags.FLAG_04)
    return render_template("store_admin_denied.html"), 403
