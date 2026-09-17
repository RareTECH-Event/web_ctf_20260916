import os

from flask import Flask

import flags


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev")
    # 問8（SSTI）で {{ config.FLAG_08 }} として読み出させるための設定値
    app.config["FLAG_08"] = flags.FLAG_08

    _write_secret_flag_file()
    _write_pickle_flag_file()
    _write_debug_js_comment()
    _init_database()
    _register_blueprints(app)

    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}

    return app


def _write_secret_flag_file():
    """問7（パストラバーサル）用のフラグファイルを起動時に生成する。

    フラグ文字列はソースコードに直書きせず、環境変数から都度書き出す。
    """
    secret_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secret")
    os.makedirs(secret_dir, exist_ok=True)
    flag_path = os.path.join(secret_dir, "flag07.txt")
    content = (
        "おめでとうございます！\n\n"
        "このフォルダの外にあるファイルを\n"
        "読み取ることに成功しました。\n\n"
        f"{flags.FLAG_07 or 'FLAG_07_NOT_SET'}\n"
    )
    with open(flag_path, "w") as f:
        f.write(content)


def _write_pickle_flag_file():
    """問10（pickleデシリアライゼーション）用に、RCEで読み出させるフラグファイルを生成する。"""
    secret_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secret")
    os.makedirs(secret_dir, exist_ok=True)
    flag_path = os.path.join(secret_dir, "flag10.txt")
    with open(flag_path, "w") as f:
        f.write(flags.FLAG_10 or "FLAG_10_NOT_SET\n")


def _write_debug_js_comment():
    """問2（JSコメント埋め込み）用に、商品一覧ページ専用JSへ起動時にデバッグコメントを書き出す。"""
    js_path = os.path.join(os.path.dirname(__file__), "static", "js", "products.js")
    content = (
        "// TODO: remove before deploy\n"
        f"// {flags.FLAG_02 or 'FLAG_02_NOT_SET'}\n"
        'console.log("debug mode: on");\n'
    )
    with open(js_path, "w") as f:
        f.write(content)


def _init_database():
    from app.db_init import seed

    seed()


def _register_blueprints(app):
    from app.cart import bp as cart_bp
    from app.challenges.ch01_top_page import bp as top_bp
    from app.challenges.ch02_product_list import bp as products_bp
    from app.challenges.ch03_robots import bp as robots_bp
    from app.challenges.ch04_cookie_role import bp as mypage_bp
    from app.challenges.ch05_sqli_login import bp as auth_bp
    from app.challenges.ch06_idor_orders import bp as orders_bp
    from app.challenges.ch07_path_traversal import bp as receipts_bp
    from app.challenges.ch08_ssti_review import bp as reviews_bp
    from app.challenges.ch09_jwt_none import bp as api_bp
    from app.challenges.ch10_pickle_backup import bp as cart_backup_bp

    app.register_blueprint(top_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(robots_bp)
    app.register_blueprint(mypage_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(cart_backup_bp)
    app.register_blueprint(cart_bp)
