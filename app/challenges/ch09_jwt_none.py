import jwt
from flask import Blueprint, current_app, jsonify, request

import flags
from app.models import get_db

bp = Blueprint("api", __name__)


def _issue_token(user):
    payload = {"user_id": user["id"], "username": user["username"], "role": "user"}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _decode_token(token):
    # 脆弱性(問9, JWT alg:none): header の alg を信用し、"none" を許容する分岐を用意している。
    # 攻撃者は署名部分を空にして alg=none のトークンを作るだけでペイロードを自由に書き換えられる。
    header = jwt.get_unverified_header(token)
    if header.get("alg", "").lower() == "none":
        return jwt.decode(token, options={"verify_signature": False}, algorithms=["none"])
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


@bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()
    conn.close()

    if user is None:
        return jsonify({"error": "invalid credentials"}), 401

    token = _issue_token(user)
    return jsonify({"token": token})


def _auth_payload():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):]
    try:
        return _decode_token(token)
    except jwt.PyJWTError:
        return None


@bp.route("/api/purchases")
def api_purchases():
    payload = _auth_payload()
    if payload is None:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    orders = conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (payload["user_id"],)
    ).fetchall()
    conn.close()
    return jsonify([dict(order) for order in orders])


@bp.route("/api/admin-dashboard")
def api_admin_dashboard():
    payload = _auth_payload()
    if payload is None or payload.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"message": "management dashboard", "flag": flags.FLAG_09})
