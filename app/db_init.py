import secrets
from datetime import datetime, timedelta

import flags
from app.models import get_db, init_db


def seed():
    """アプリ起動のたびにDBを初期化し、デモ用データを投入する。"""
    init_db()
    conn = get_db()

    # 問5(SQLi)でログインをバイパスして到達させる管理者アカウント。
    # パスワードは推測させないためランダム値にする。
    # customer1より先に登録し、"OR '1'='1'" のような全件一致の injection で
    # ORDER BYなしのSELECTが最初に返す行(=このadmin行)としてログインが成立するようにする。
    conn.execute(
        "INSERT INTO users (username, password, address) VALUES (?, ?, ?)",
        ("admin", secrets.token_hex(16), flags.FLAG_05 or "FLAG_05_NOT_SET"),
    )
    conn.execute(
        "INSERT INTO users (username, password, address) VALUES (?, ?, ?)",
        ("customer1", "password123", "東京都千代田区1-1-1"),
    )

    # 商品ID(1〜5)は注文データから参照されているため並び順を変更しない。
    products = [
        ("防水バックパック 25L", 6800, "通勤にも旅行にも使える防水加工のバックパック。", "backpack.jpg", 42, "バッグ・かばん"),
        ("ノイズキャンセリングイヤホン", 12800, "長時間装着でも疲れにくい軽量設計。", "earphones.jpg", 15, "家電・PC周辺機器"),
        ("ステンレスタンブラー 400ml", 2200, "保温・保冷に優れたステンレス製タンブラー。", "tumbler.jpg", 120, "キッチン用品"),
        ("メカニカルキーボード", 9800, "静音赤軸を採用したコンパクトキーボード。", "keyboard.jpg", 8, "家電・PC周辺機器"),
        ("オーガニックコットンTシャツ", 3400, "肌触りの良いオーガニックコットン100%。", "tshirt.jpg", 60, "ファッション"),
        ("キャンバストートバッグ", 2800, "A4サイズがすっぽり入る大容量トートバッグ。", "tote.jpg", 34, "バッグ・かばん"),
        ("コンパクト三つ折り財布", 4200, "薄型で持ち運びやすいミニウォレット。", "wallet.jpg", 27, "バッグ・かばん"),
        ("撥水デイパック 20L", 7600, "自転車通勤にもおすすめの軽量リュック。", "daypack.jpg", 19, "バッグ・かばん"),
        ("モバイルバッテリー 10000mAh", 3200, "スマホを約2回フル充電できる大容量タイプ。", "powerbank.jpg", 48, "家電・PC周辺機器"),
        ("静音ワイヤレスマウス", 2400, "クリック音を抑えたオフィス向けマウス。", "mouse.jpg", 55, "家電・PC周辺機器"),
        ("USB-C 6in1 ハブ", 4800, "HDMI・SD・USB-Aに対応するマルチハブ。", "hub.jpg", 22, "家電・PC周辺機器"),
        ("鋳物ホーロー鍋 20cm", 8900, "煮込み料理に最適な保温性の高いホーロー鍋。", "pot.jpg", 12, "キッチン用品"),
        ("電動コーヒーミル", 5400, "均一に挽ける電動式のコーヒーミル。", "grinder.jpg", 16, "キッチン用品"),
        ("抗菌まな板 Mサイズ", 1800, "食洗機対応で衛生的に使えるまな板。", "board.jpg", 70, "キッチン用品"),
        ("ウールブレンドマフラー", 3900, "秋冬に活躍する柔らかい肌触りのマフラー。", "muffler.jpg", 38, "ファッション"),
        ("キャンバススニーカー", 5600, "どんな服装にも合わせやすいローカットスニーカー。", "sneaker.jpg", 25, "ファッション"),
    ]
    conn.executemany(
        "INSERT INTO products (name, price, description, image, stock, category) VALUES (?, ?, ?, ?, ?, ?)",
        products,
    )

    now = datetime.utcnow()
    conn.execute(
        "INSERT INTO orders (user_id, created_at, total, status) VALUES (?, ?, ?, ?)",
        (2, (now - timedelta(days=3)).isoformat(timespec="seconds"), 9000, "completed"),
    )
    conn.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
        (1, 1, 1, 6800),
    )
    conn.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
        (1, 3, 1, 2200),
    )

    # 問6(IDOR)用: admin(user_id=1)の注文。所有者チェックを省略した /orders/<id> から
    # 他ユーザーがこの注文番号を直接指定して到達できるようにする。
    conn.execute(
        "INSERT INTO orders (user_id, created_at, total, status, notes) VALUES (?, ?, ?, ?, ?)",
        (
            1,
            (now - timedelta(days=1)).isoformat(timespec="seconds"),
            12800,
            "completed",
            flags.FLAG_06 or "FLAG_06_NOT_SET",
        ),
    )
    conn.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
        (2, 2, 1, 12800),
    )

    reviews = [
        (1, "山田太郎", 5, "軽くて容量も十分でした。", now - timedelta(days=10)),
        (1, "佐藤花子", 4, "雨の日も安心して使えています。", now - timedelta(days=4)),
        (2, "鈴木一郎", 5, "外音取り込みが自然で満足しています。", now - timedelta(days=8)),
        (3, "田中みき", 4, "保冷効果が高く、夏場に重宝しています。", now - timedelta(days=2)),
        (9, "小林健", 5, "旅行先での充電切れがなくなりました。", now - timedelta(days=6)),
        (16, "中村さゆり", 3, "サイズ感がやや大きめでした。", now - timedelta(days=1)),
    ]
    conn.executemany(
        "INSERT INTO reviews (product_id, author_name, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
        [(pid, author, rating, comment, created.isoformat(timespec="seconds"))
         for pid, author, rating, comment, created in reviews],
    )

    conn.commit()
    conn.close()
