from flask import Blueprint, abort, render_template, request

from app.models import get_db

bp = Blueprint("products", __name__)


@bp.route("/products")
def list_products():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    conn = get_db()
    if query:
        products = conn.execute(
            "SELECT * FROM products WHERE name LIKE ? ORDER BY id",
            (f"%{query}%",),
        ).fetchall()
    elif category:
        products = conn.execute(
            "SELECT * FROM products WHERE category = ? ORDER BY id",
            (category,),
        ).fetchall()
    else:
        products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return render_template(
        "products/list.html", products=products, query=query, category=category
    )


@bp.route("/products/<int:product_id>")
def product_detail(product_id):
    conn = get_db()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    if product is None:
        conn.close()
        abort(404)
    reviews = conn.execute(
        "SELECT * FROM reviews WHERE product_id = ? ORDER BY id DESC", (product_id,)
    ).fetchall()
    conn.close()

    review_count = len(reviews)
    avg_rating = (
        sum(review["rating"] for review in reviews) / review_count
        if review_count
        else 0
    )
    return render_template(
        "products/detail.html",
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=review_count,
    )
