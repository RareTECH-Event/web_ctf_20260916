from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.models import get_db

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    conn = get_db()
    # 脆弱性(問5): クエリを文字列結合で組み立てており、パラメータバインディングを使っていない。
    # 例: username = ' OR '1'='1' -- で全行が条件に一致し、最初に登録されている
    # admin アカウント（seedデータで先頭に配置）としてログインが成立してしまう。
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    user = conn.execute(query).fetchone()
    conn.close()

    if user is None:
        flash("ユーザー名またはパスワードが違います。")
        return redirect(url_for("auth.login"))

    session["user_id"] = user["id"]
    role = "admin" if user["username"] == "admin" else "user"

    response = redirect(url_for("mypage.mypage"))
    response.set_cookie("role", role)
    return response


@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    response = redirect(url_for("top.index"))
    response.delete_cookie("role")
    return response
