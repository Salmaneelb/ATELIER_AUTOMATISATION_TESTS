import json, sqlite3, os

DB_PATH = os.environ.get("DB_PATH", "runs.db")

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp    TEXT NOT NULL,
                api          TEXT NOT NULL,
                passed       INTEGER,
                failed       INTEGER,
                errors       INTEGER,
                error_rate   REAL,
                availability REAL,
                latency_avg  REAL,
                latency_p95  REAL,
                raw_json     TEXT
            )
        """)
        conn.commit()

def save_run(report: dict):
    s = report.get("summary", {})
    with _connect() as conn:
        conn.execute("""
            INSERT INTO runs
              (timestamp, api, passed, failed, errors, error_rate,
               availability, latency_avg, latency_p95, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report.get("timestamp"), report.get("api"),
            s.get("passed"), s.get("failed"), s.get("errors"),
            s.get("error_rate"), s.get("availability"),
            s.get("latency_ms_avg"), s.get("latency_ms_p95"),
            json.dumps(report),
        ))
        conn.commit()

def list_runs(limit=20):
    with _connect() as conn:
        rows = conn.execute("""
            SELECT id, timestamp, api, passed, failed, errors,
                   error_rate, availability, latency_avg, latency_p95
            FROM runs ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_run(run_id: int):
    with _connect() as conn:
        row = conn.execute("SELECT raw_json FROM runs WHERE id=?", (run_id,)).fetchone()
    return json.loads(row["raw_json"]) if row else None

def get_last_run():
    with _connect() as conn:
        row = conn.execute("SELECT raw_json FROM runs ORDER BY id DESC LIMIT 1").fetchone()
    return json.loads(row["raw_json"]) if row else None
