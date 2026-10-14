
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from main import read_logs

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "sample_logs" / "app.log"
DB_FILE = BASE_DIR / "minitrace.db"

VALID_LEVELS = {"INFO", "WARNING", "ERROR"}


def get_db():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'app.log',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, level, message, source)
            )
        """)


def import_logs():
    if not LOG_FILE.exists():
        return

    with get_db() as connection:
        for line in read_logs(LOG_FILE):
            parts = line.split(" ", 2)

            if len(parts) < 3:
                continue

            timestamp = f"{parts[0]} {parts[1]}"
            remainder = parts[2]
            level, separator, message = remainder.partition(" ")

            if not separator or level not in VALID_LEVELS:
                continue

            connection.execute("""
                INSERT OR IGNORE INTO logs
                    (timestamp, level, message, source)
                VALUES (?, ?, ?, ?)
            """, (timestamp, level, message, LOG_FILE.name))


def fetch_logs(level=None, keyword=None):
    query = "SELECT * FROM logs WHERE 1=1"
    parameters = []

    if level:
        query += " AND level = ?"
        parameters.append(level)

    if keyword:
        query += " AND (message LIKE ? OR source LIKE ?)"
        pattern = f"%{keyword}%"
        parameters.extend([pattern, pattern])

    query += " ORDER BY timestamp DESC, id DESC"

    with get_db() as connection:
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]


def get_stats():
    with get_db() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM logs"
        ).fetchone()[0]

        rows = connection.execute("""
            SELECT level, COUNT(*) AS count
            FROM logs
            GROUP BY level
        """).fetchall()

    summary = {"INFO": 0, "WARNING": 0, "ERROR": 0}

    for row in rows:
        summary[row["level"]] = row["count"]

    return {"total": total, "summary": summary}


@app.route("/")
def dashboard():
    stats = get_stats()

    return render_template(
        "index.html",
        total=stats["total"],
        summary=stats["summary"],
        logs=fetch_logs()
    )


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "MiniTrace"
    })


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/logs", methods=["GET", "POST"])
def api_logs():
    if request.method == "POST":
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Send a valid JSON object."
            }), 400

        level = data.get("level", "")
        message = data.get("message", "")
        source = data.get("source", "manual")

        if not isinstance(level, str):
            return jsonify({"error": "Level must be a string."}), 400

        if not isinstance(message, str):
            return jsonify({"error": "Message must be a string."}), 400

        if not isinstance(source, str):
            return jsonify({"error": "Source must be a string."}), 400

        level = level.upper().strip()
        message = message.strip()
        source = source.strip()

        if level not in VALID_LEVELS:
            return jsonify({
                "error": "Level must be INFO, WARNING, or ERROR."
            }), 400

        if not message:
            return jsonify({"error": "Message cannot be empty."}), 400

        if len(message) > 1000:
            return jsonify({
                "error": "Message cannot exceed 1000 characters."
            }), 400

        if not source:
            source = "manual"

        if len(source) > 100:
            return jsonify({
                "error": "Source cannot exceed 100 characters."
            }), 400

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with get_db() as connection:
                cursor = connection.execute("""
                    INSERT INTO logs (timestamp, level, message, source)
                    VALUES (?, ?, ?, ?)
                """, (timestamp, level, message, source))

                log_id = cursor.lastrowid

                saved_log = connection.execute(
                    "SELECT * FROM logs WHERE id = ?",
                    (log_id,)
                ).fetchone()

            return jsonify({
                "message": "Log created successfully.",
                "log": dict(saved_log)
            }), 201

        except sqlite3.IntegrityError:
            return jsonify({
                "error": "This log already exists."
            }), 409

    level = request.args.get("level", "").upper().strip()
    keyword = request.args.get("keyword", "").strip()

    if level and level not in VALID_LEVELS:
        return jsonify({
            "error": "Invalid level. Use INFO, WARNING, or ERROR."
        }), 400

    if len(keyword) > 200:
        return jsonify({
            "error": "Keyword is too long."
        }), 400

    logs = fetch_logs(level or None, keyword or None)

    return jsonify({
        "count": len(logs),
        "logs": logs
    })


init_db()
import_logs()


if __name__ == "__main__":
    app.run(debug=True)
