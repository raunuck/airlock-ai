import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "workbench.db"

DEFAULT_TASK_MODELS = [
    ("document", "qwen2.5:7b"),
    ("code", "qwen2.5-coder:7b"),
    ("rag_query", "qwen2.5:7b"),
    ("general", "qwen2.5:7b"),
]

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS model_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            task_type TEXT NOT NULL   -- e.g. 'code', 'document', 'rag_query', 'general'
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rag_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            sources TEXT,
            answer TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            step_num INTEGER,
            llm_output TEXT,
            tool_called TEXT,
            tool_result TEXT,
            is_final INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_agent_step(run_id: str, step_num: int, llm_output: str,
                    tool_called: str | None, tool_result: str | None, is_final: bool):
    conn = get_connection()
    conn.execute(
        "INSERT INTO agent_logs (run_id, step_num, llm_output, tool_called, tool_result, is_final) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (run_id, step_num, llm_output, tool_called, tool_result, int(is_final)),
    )
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
    if row:
        return row["model_name"]

    fallbacks = {
        "code": "qwen2.5-coder:7b",
        "document": "qwen2.5:7b",
        "rag_query": "qwen2.5:7b",
        "general": "qwen2.5:7b",
    }
    return fallbacks.get(task_type, "qwen2.5:7b")

def seed_registry():
    conn = get_connection()
    for task_type, model_name in DEFAULT_TASK_MODELS:
        existing = conn.execute(
            "SELECT COUNT(*) FROM model_registry WHERE task_type = ?", (task_type,)
        ).fetchone()[0]
        if existing == 0:
            conn.execute(
                "INSERT INTO model_registry (model_name, task_type) VALUES (?, ?)",
                (model_name, task_type),
            )
    conn.commit()
    conn.close()

def log_rag_query(prompt: str, sources: list[str], answer: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO rag_logs (prompt, sources, answer) VALUES (?, ?, ?)",
        (prompt, ", ".join(sources), answer),
    )
    conn.commit()
    conn.close()