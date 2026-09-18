import base64
import os
import pickle

from flask import Blueprint, Response, flash, redirect, request, session, url_for

bp = Blueprint("cart_backup", __name__)

RCE_OUTPUT_PATH = "/tmp/output"


@bp.route("/cart/backup")
def backup_cart():
    cart = session.get("cart", {})
    payload = base64.b64encode(pickle.dumps(cart))
    return Response(
        payload,
        mimetype="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=cart_backup.dat"},
    )


@bp.route("/cart/restore", methods=["POST"])
def restore_cart():
    data = request.form.get("backup_data", "")
    try:
        # 脆弱性(問10, 安全でないデシリアライゼーション):
        # ユーザーが送ってきたデータをそのまま pickle.loads() に渡している。
        # __reduce__ を実装したオブジェクトを送ると、復元時に任意の呼び出しが実行される。
        restored = pickle.loads(base64.b64decode(data))
    except Exception as exc:
        flash(f"復元に失敗しました: {exc}")
        return redirect(url_for("cart.view_cart"))

    # 例: os.system('cat /app/secret/flag10.txt > /tmp/output') のようなペイロードの
    # 実行結果を、シェルを取らなくても確認できるようにレスポンスに含めてキャプチャする。
    captured = None
    if os.path.exists(RCE_OUTPUT_PATH):
        with open(RCE_OUTPUT_PATH) as f:
            captured = f.read().strip()
        os.remove(RCE_OUTPUT_PATH)

    if captured:
        flash(f"復元結果: {captured}")
    elif isinstance(restored, dict):
        session["cart"] = restored
        flash("カートを復元しました。")
    else:
        # __reduce__ の戻り値をそのまま返す形のペイロード（例: os.getenv）にも対応する。
        flash(f"復元結果: {restored}")
    return redirect(url_for("cart.view_cart"))
