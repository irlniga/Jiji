import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "data.db")


def run(sql, args=(), fetch=False):
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute(sql, args)
        rows = [dict(r) for r in cur.fetchall()] if fetch else None
        con.commit()
        return rows
    finally:
        con.close()


run("""CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL)""")


@app.after_request
def add_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/debug")
def debug():
    return jsonify({"folder": BASE_DIR, "files": os.listdir(BASE_DIR)})


@app.route("/api/items", methods=["GET"])
def list_items():
    return jsonify(run("SELECT * FROM items ORDER BY id DESC", fetch=True))


@app.route("/api/items", methods=["POST"])
def add_item():
    data = request.get_json(force=True, silent=True) or {}
    name = str(data.get("name", "")).strip()[:100]
    if not name:
        return jsonify({"error": "Name required"}), 400
    run("INSERT INTO items (name) VALUES (?)", (name,))
    return jsonify({"ok": True}), 201


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    run("DELETE FROM items WHERE id = ?", (item_id,))
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Serving files from:", BASE_DIR)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)