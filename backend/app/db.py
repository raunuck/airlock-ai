import sqlite3

DB_PATH = "workbench.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS model_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            task_type TEXT NOT NULL   -- e.g. 'code', 'document', 'rag_query'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT,
            model_used TEXT,
            prompt TEXT,
            response TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_task(task_type: str, model_used: str, prompt: str, response: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO task_logs (task_type, model_used, prompt, response) VALUES (?, ?, ?, ?)",
        (task_type, model_used, prompt, response),
    )
    conn.commit()
    conn.close()

def get_model_for_task(task_type: str) -> str:
    conn = get_connection()
    row = conn.execute(
        "SELECT model_name FROM model_registry WHERE task_type = ? LIMIT 1", (task_type,)
    ).fetchone()
    conn.close()
    return row["model_name"] if row else "qwen2.5:7b"  # fallback if nothing registered

def seed_registry():
    conn = get_connection()
    existing = conn.execute("SELECT COUNT(*) FROM model_registry").fetchone()[0]
    if existing == 0:
        conn.executemany(
            "INSERT INTO model_registry (model_name, task_type) VALUES (?, ?)",
            [("qwen2.5:7b", "document"), ("qwen2.5-coder:7b", "code")],
        )
        conn.commit()
    conn.close()