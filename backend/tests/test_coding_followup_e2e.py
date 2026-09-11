import sys
from pathlib import Path

# Set path to backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from main import app
from app.db import get_connection

client = TestClient(app)

def test_coding_followup():
    conn = get_connection()
    user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    conn.close()
    user_id = user["id"] if user else "test-user"

    headers = {"user-id": user_id}

    # Turn 1: Write a python function
    prompt1 = "Write a python script to calculate the area of a circle with radius 5"
    print(f"Sending Turn 1: '{prompt1}'")
    res1 = client.post("/task", json={"prompt": prompt1}, headers=headers)
    assert res1.status_code == 200, f"Turn 1 failed: {res1.text}"
    data1 = res1.json()
    session_id = data1["session_id"]
    print(f"Turn 1 Task Type: {data1['task_type']}, Model: {data1['model_used']}")
    print(f"Turn 1 Answer snippet: {data1['response'][:100]}...\n")

    # Turn 2: Follow up requesting same logic in Java
    prompt2 = "Need the same logic for Java"
    print(f"Sending Turn 2: '{prompt2}' with session_id={session_id}")
    res2 = client.post(
        "/task",
        json={
            "prompt": prompt2,
            "session_id": session_id,
            "previous_task_type": data1["task_type"]
        },
        headers=headers
    )
    assert res2.status_code == 200, f"Turn 2 failed: {res2.text}"
    data2 = res2.json()
    print(f"Turn 2 Task Type: {data2['task_type']}, Model: {data2['model_used']}")
    print(f"Turn 2 Answer:\n{data2['response']}")

    # Check for java keywords or circle/area in response
    resp_lower = data2["response"].lower()
    assert ("java" in resp_lower or "class" in resp_lower or "public" in resp_lower) and ("area" in resp_lower or "circle" in resp_lower or "radius" in resp_lower), "Expected Java area calculation response"
    print("\nPASS: Coding follow-up successfully understood context from previous turn!")

if __name__ == "__main__":
    test_coding_followup()
