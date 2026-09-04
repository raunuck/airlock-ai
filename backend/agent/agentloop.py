from pathlib import Path

# make sure backend/ is on the path so imports work

from backend.rag.retrieval import answer_rag_query
from backend.llm_client import prompt as llm_prompt


# Tools
# Each tool is just a plain function that takes a string and returns a string.
# Add more tools here as the week goes on (run_code, write_docx, extract_text).

def search_docs(query: str) -> str:
    result = answer_rag_query(query)
    if not result["context_found"]:
        return "No relevant SOP content found for this query."
    sources = ", ".join(result["sources"])
    return f"{result['answer']}\n\nSource(s): {sources}"


TOOLS = {
    "search_docs": search_docs,
    # "run_code": run_code,       # Viral's part - Day 4
    # "extract_text": extract_text, # Arya's part - Day 5
    # "write_docx": write_docx,   # Viral's part - Day 4
}


# Agent loop 

SYSTEM_PROMPT = """You are an agent helping with industrial tasks at an oil refinery.
You have access to the following tools:

- search_docs: searches the local SOP knowledge base and returns relevant content with citations

To use a tool, respond EXACTLY like this (nothing else on that line):
CALL_TOOL: search_docs : your query here

When you have enough information to answer, respond EXACTLY like this:
DONE: your final answer here

Always try search_docs first before saying you don't know something.

Examples:
User: What are the safety procedures for valve inspection?
Assistant: CALL_TOOL: search_docs : valve inspection safety procedures

User: Tool result: [some content]
Assistant: DONE: Based on the SOPs, the safety procedures are...
"""


def run_agent(user_goal: str, max_steps: int = 5) -> dict:
    """
    Run the agent loop for a given user goal.

    Returns:
        {
            "answer": str,
            "steps": list of dicts with step-by-step trace,
            "completed": bool
        }
    """
    history = [
        {"role": "user", "content": user_goal}
    ]

    steps = []

    for step_num in range(1, max_steps + 1):

        # ask the LLM what to do next
        response = llm_prompt(
            text=history[-1]["content"] if step_num == 1 else "Continue.",
            system=SYSTEM_PROMPT,
            model_key="general",
        )

        plan = response["content"].strip()

        # log this step
        steps.append({
            "step": step_num,
            "llm_output": plan,
            "tool_called": None,
            "tool_result": None,
        })

        # check if done
        if plan.startswith("DONE:"):
            final_answer = plan.replace("DONE:", "").strip()
            steps[-1]["final"] = True
            return {
                "answer": final_answer,
                "steps": steps,
                "completed": True,
            }

        # check if tool call
        if plan.startswith("CALL_TOOL:"):
            try:
                _, tool_name, tool_input = plan.split(":", 2)
                tool_name = tool_name.strip()
                tool_input = tool_input.strip()
            except ValueError:
                history.append({
                    "role": "user",
                    "content": "Tool call format was wrong. Use: CALL_TOOL: tool_name : input"
                })
                continue

            if tool_name not in TOOLS:
                tool_result = f"Tool '{tool_name}' not found. Available tools: {list(TOOLS.keys())}"
            else:
                tool_result = TOOLS[tool_name](tool_input)

            # update step log
            steps[-1]["tool_called"] = tool_name
            steps[-1]["tool_result"] = tool_result

            # feed result back into history
            history.append({"role": "assistant", "content": plan})
            history.append({"role": "user", "content": f"Tool result: {tool_result}"})

        else:
            # LLM didn't follow the format, nudge it
            history.append({
                "role": "user",
                "content": "Please respond with either CALL_TOOL: tool_name : input or DONE: answer"
            })

    return {
        "answer": "Could not complete the task within the step limit.",
        "steps": steps,
        "completed": False,
    }


# Quick test

if __name__ == "__main__":
    result = run_agent("What are the safety procedures for pump maintenance?")

    print("\n===== FINAL ANSWER =====")
    print(result["answer"])

    print("\n===== AGENT TRACE =====")
    for step in result["steps"]:
        print(f"\nStep {step['step']}:")
        print(f"  LLM: {step['llm_output'][:100]}...")
        if step["tool_called"]:
            print(f"  Tool: {step['tool_called']}")
            print(f"  Result: {str(step['tool_result'])[:100]}...")

    print(f"\nCompleted: {result['completed']}")
