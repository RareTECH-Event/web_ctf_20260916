from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.models import get_db

bp = Blueprint("cart", __name__)


def _get_cart():
    return session.setdefault("cart", {})


@bp.route("/cart")
def view_cart():
    cart = _get_cart()
    conn = get_db()
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if product is None:
            continue
        subtotal = product["price"] * quantity
        total += subtotal
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
    conn.close()
    return render_template("cart.html", items=items, total=total)


@bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = _get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    flash("カートに追加しました。")
    return redirect(url_for("cart.view_cart"))


@bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = _get_cart()
    cart.pop(str(product_id), None)
    session["cart"] = cart
    flash("カートから削除しました。")
    return redirect(url_for("cart.view_cart"))
