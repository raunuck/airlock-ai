"""
Simple smoke test for llm_client.py.

Run:
    python test_llm_client.py
"""

from backend.llm_client import prompt

print("=" * 50)
print("Testing General Model")
print("=" * 50)

response = prompt("What is 2 + 2?")

print(response)
print()

print("=" * 50)
print("Testing Coding Model")
print("=" * 50)


response = prompt("Write a Python function to reverse a string.", model_key="coding")

print(f"Model: {response['model']}")
print()
print(response["content"])