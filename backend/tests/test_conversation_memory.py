import sys
import uuid
from pathlib import Path

# Set path to backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db import (
    init_db, add_message,
    get_session_history_for_llm, get_connection
)

def test_history_retrieval():
    init_db()
    conn = get_connection()
    user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    conn.close()
    
    user_id = user["id"] if user else "test-user-id"
    test_session = f"test-mem-{uuid.uuid4().hex[:8]}"

    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO users (id, username, password_hash, salt) VALUES (?, 'mem_test', 'hash', 'salt')", (user_id,))
    conn.execute("INSERT INTO chat_sessions (id, user_id, title) VALUES (?, ?, 'Memory Test')", (test_session, user_id))
    conn.commit()
    conn.close()

    # Add 6 turns of conversation
    messages_data = [
        ("user", "Hello turn 1"),
        ("assistant", "Hi turn 1 response"),
        ("user", "Question turn 2"),
        ("assistant", "Answer turn 2 response"),
        ("user", "Fix this code: print(x)"),
        ("assistant", "Here is the fix: x = 10; print(x)"),
    ]

    for role, text in messages_data:
        add_message(test_session, role, text)

    # Test 1: Fetch with limit=4
    history_limit_4 = get_session_history_for_llm(test_session, limit=4)
    assert len(history_limit_4) == 4, f"Expected 4 messages, got {len(history_limit_4)}"
    assert history_limit_4[0]["content"] == "Question turn 2", f"First msg expected 'Question turn 2', got '{history_limit_4[0]['content']}'"
    assert history_limit_4[-1]["content"] == "Here is the fix: x = 10; print(x)"
    print("PASS: Sliding window limit=4 returns the 4 most recent messages in chronological order.")

    # Test 2: Fetch with limit=10 (should return all 6)
    history_all = get_session_history_for_llm(test_session, limit=10)
    assert len(history_all) == 6, f"Expected 6 messages, got {len(history_all)}"
    assert history_all[0]["content"] == "Hello turn 1"
    assert history_all[-1]["content"] == "Here is the fix: x = 10; print(x)"
    print("PASS: Full history retrieval returned all 6 messages chronologically.")

    # Cleanup
    conn = get_connection()
    conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (test_session,))
    conn.execute("DELETE FROM chat_sessions WHERE id = ?", (test_session,))
    conn.commit()
    conn.close()
    print("PASS: Test cleanup completed successfully.")

if __name__ == "__main__":
    test_history_retrieval()
    print("\nALL CONVERSATION MEMORY UNIT TESTS PASSED!")
