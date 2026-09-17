from flask import Blueprint, abort, redirect, render_template, session, url_for

from app.models import get_db

bp = Blueprint("orders", __name__)


@bp.route("/orders")
def order_list():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))
    conn = get_db()
    orders = conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,)
    ).fetchall()
    conn.close()
    return render_template("orders/list.html", orders=orders)


@bp.route("/orders/<int:order_id>")
def order_detail(order_id):
    # 脆弱性(問6, IDOR): ログイン済みであることしか確認しておらず、
    # order['user_id'] とログインユーザーの一致を検証していない。
    if session.get("user_id") is None:
        return redirect(url_for("auth.login"))
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        conn.close()
        abort(404)
    items = conn.execute(
        """
        SELECT order_items.*, products.name AS product_name
        FROM order_items
        JOIN products ON products.id = order_items.product_id
        WHERE order_items.order_id = ?
        """,
        (order_id,),
    ).fetchall()
    conn.close()
    return render_template("orders/detail.html", order=order, items=items)
