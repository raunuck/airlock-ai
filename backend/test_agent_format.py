from agent.agentloop import run_agent

TEST_PROMPTS = [
    "What are the safety procedures for pump maintenance?",
    "What is the procedure for valve inspection?",
    "What's 15 times 23?",
    "How do I approve a compressor for use after inspection?",
    "Tell me a joke.",
]


def check_format(step):
    output = step["llm_output"]
    return output.startswith("CALL_TOOL:") or output.startswith("DONE:")


for prompt in TEST_PROMPTS:

    print("=" * 60)
    print("PROMPT:", prompt)
    print("=" * 60)

    result = run_agent(prompt)

    malformed = [
        s for s in result["steps"]
        if not check_format(s)
    ]

    print("Completed:", result["completed"])
    print("Steps:", len(result["steps"]))
    print("Malformed:", len(malformed))

    if malformed:
        print("\nFORMAT ISSUES:")
        for s in malformed:
            print(f"Step {s['step']}:")
            print(s["llm_output"][:200])

    print("\nAnswer:")
    print(result["answer"])
    print()