from datetime import datetime

from flask import Blueprint, flash, redirect, render_template_string, request, url_for

from app.models import get_db

bp = Blueprint("reviews", __name__)


@bp.route("/products/<int:product_id>/reviews", methods=["POST"])
def add_review(product_id):
    author_name = request.form.get("author_name", "")
    rating = request.form.get("rating", "5")
    comment = request.form.get("comment", "")

    conn = get_db()
    conn.execute(
        "INSERT INTO reviews (product_id, author_name, rating, comment, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (product_id, author_name, rating, comment, datetime.utcnow().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()

    # 脆弱性(問8, SSTI): お名前をテンプレート文字列に直接埋め込んで render_template_string に渡している。
    # 例: {{ config.FLAG_08 }} を投稿すると、サーバー設定値がそのまま評価・出力されてしまう。
    greeting = render_template_string(f"{author_name}さんのレビューを投稿しました。")
    flash(f"{greeting}\nご協力ありがとうございます！")
    return redirect(url_for("products.product_detail", product_id=product_id))
