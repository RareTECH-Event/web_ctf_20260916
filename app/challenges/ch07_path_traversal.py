import os

from flask import Blueprint, abort, render_template, request, send_file, session

from app.models import get_db

bp = Blueprint("receipts", __name__)

RECEIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "receipts")
os.makedirs(RECEIPTS_DIR, exist_ok=True)


def _ensure_receipt_file(order_id):
    """注文詳細から生成した領収書テキストを、受講生が辿れる実ファイルとして保存する。"""
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        conn.close()
        return None
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

    lines = [f"領収書 - 注文番号 {order['id']}", f"注文日時: {order['created_at']}", ""]
    for item in items:
        lines.append(f"{item['product_name']} x{item['quantity']}  \\yen{item['price']}")
    lines.append("")
    lines.append(f"合計: \\yen{order['total']}")

    filename = f"receipt_{order_id}.txt"
    path = os.path.join(RECEIPTS_DIR, filename)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return filename


@bp.route("/receipts/download")
def download_page():
    if session.get("user_id") is None:
        abort(401)

    order_id = request.args.get("order_id", type=int)
    default_filename = _ensure_receipt_file(order_id) if order_id else None
    filename = request.args.get("filename")

    if not filename:
        return render_template("receipts/download.html", default_filename=default_filename)

    # 脆弱性(問7, パストラバーサル): filename パラメータをサニタイズせず、
    # そのまま os.path.join() -> send_file() に渡している。
    # "../" を含む値を渡すと RECEIPTS_DIR の外にあるファイルも読み出せてしまう。
    path = os.path.join(RECEIPTS_DIR, filename)

    if not os.path.isfile(path):
        abort(404)
    return send_file(path, mimetype="text/plain", as_attachment=True, download_name=os.path.basename(filename))
