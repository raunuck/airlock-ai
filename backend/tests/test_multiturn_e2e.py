import sys
from pathlib import Path

# Set path to backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from main import app
from app.db import get_session_messages, get_connection

client = TestClient(app)

def test_multiturn_flow():
    conn = get_connection()
    user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    conn.close()
    user_id = user["id"] if user else "test-user"

    headers = {"user-id": user_id}

    # Turn 1: General math or greeting
    res1 = client.post("/task", json={"prompt": "Remember the secret word: 'APPLE'."}, headers=headers)
    assert res1.status_code == 200, f"Turn 1 failed: {res1.text}"
    data1 = res1.json()
    session_id = data1["session_id"]
    print(f"Turn 1 Response: {data1['response'][:80]}... (Session: {session_id})")

    # Turn 2: Follow-up asking about the secret word
    res2 = client.post("/task", json={"prompt": "What was the secret word I told you earlier?", "session_id": session_id}, headers=headers)
    assert res2.status_code == 200, f"Turn 2 failed: {res2.text}"
    data2 = res2.json()
    print(f"Turn 2 Response: {data2['response']}")
    assert "apple" in data2["response"].lower(), f"Expected 'apple' in response, got: {data2['response']}"

    # Verify messages in database
    msgs = get_session_messages(session_id, user_id)
    assert len(msgs) >= 4, f"Expected at least 4 messages in DB, got {len(msgs)}"
    print(f"PASS: Multi-turn flow retained context and successfully answered follow-up ({len(msgs)} messages stored in session).")

if __name__ == "__main__":
    test_multiturn_flow()
