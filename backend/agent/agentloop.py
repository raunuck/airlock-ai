from rag.retrieval import answer_rag_query
from llm_client import chat as llm_chat
from app.tools.docgen import write_approval_note
from app.tools.sandbox import run_code_sandboxed
import uuid
from app.db import log_agent_step
from app.tools.ocr import extract_text


# tools

def search_docs(query: str) -> str:
    result = answer_rag_query(query)
    if not result["context_found"]:
        return "No relevant SOP content found for this query."
    sources = ", ".join(result["sources"])
    return f"{result['answer']}\n\nSource(s): {sources}"

def write_docx(findings: str) -> str:
    path = write_approval_note(findings)
    return f"Approval note saved at {path}"

def run_code(code: str) -> str:
    result = run_code_sandboxed(code)
    if result["passed"]:
        return f"Code ran successfully.\nOutput: {result['stdout']}"
    return f"Code failed.\nError: {result['stderr']}"


TOOLS = {
    "search_docs": search_docs,
    "write_docx": write_docx,
    "run_code": run_code,
    "extract_text": extract_text,
}


# agent loop

SYSTEM_PROMPT = """You are an agent helping with industrial tasks at an oil refinery.
Always respond in English unless the user explicitly requests another language.

You have access to the following tools:

- search_docs: searches the local SOP knowledge base and returns relevant content with citations
- extract_text: extracts text from an image using OCR (input: image file path)
- write_docx: takes a findings summary and creates an approval note as a .docx file
- run_code: runs a python code snippet and returns the output

To use a tool, respond EXACTLY like this:
CALL_TOOL: tool_name : input here

When you have enough information to answer, respond EXACTLY like this:
DONE: your final answer here

IMPORTANT:
- When writing, debugging, or fixing code, you can use run_code to test it. Your final DONE: answer MUST include the complete fixed/written code formatted in markdown code blocks (```python ... ```), along with a clear explanation of what was fixed or implemented.
- Always try search_docs first before saying you don't know something.

Examples:
User: What are the safety procedures for valve inspection?
Assistant: CALL_TOOL: search_docs : valve inspection safety procedures

User: Tool result: [some content]
Assistant: DONE: Based on the SOPs, the safety procedures are...

User: fix this code print(helloworld)
Assistant: CALL_TOOL: run_code : print("helloworld")

User: Tool result: Code ran successfully.\nOutput: helloworld
Assistant: DONE: Here is the corrected code:

```python
print("helloworld")
```

**Explanation:** The string literal `helloworld` was missing quotation marks. Adding quotes fixes the syntax error.
"""


def run_agent(user_goal: str, max_steps: int = 5, model_key: str = "general") -> dict:
    run_id = str(uuid.uuid4())
    history = [
        {"role": "user", "content": user_goal}
    ]

    steps = []

    for step_num in range(1, max_steps + 1):

        response = llm_chat(
            messages=history,
            system=SYSTEM_PROMPT,
            model_key=model_key,
        )

        plan = response["content"].strip()

        steps.append({
            "step": step_num,
            "llm_output": plan,
            "tool_called": None,
            "tool_result": None,
        })

        if plan.startswith("DONE:"):
            final_answer = plan[len("DONE:"):].strip()
            steps[-1]["final"] = True
            log_agent_step(run_id, step_num, plan, None, None, is_final=True)
            return {
                "answer": final_answer,
                "steps": steps,
                "completed": True,
                "run_id": run_id,
            }

        if plan.startswith("CALL_TOOL:"):
            try:
                _, tool_name, tool_input = plan.split(":", 2)
                tool_name = tool_name.strip()
                tool_input = tool_input.strip()
            except ValueError:
                log_agent_step(run_id, step_num, plan, None, "malformed tool call", is_final=False)
                history.append({
                    "role": "user",
                    "content": "Tool call format was wrong. Use: CALL_TOOL: tool_name : input"
                })
                continue

            if tool_name not in TOOLS:
                tool_result = f"Tool '{tool_name}' not found. Available: {list(TOOLS.keys())}"
            else:
                try:
                    tool_result = TOOLS[tool_name](tool_input)
                except Exception as e:
                    tool_result = f"Error running tool '{tool_name}': {e}"

            steps[-1]["tool_called"] = tool_name
            steps[-1]["tool_result"] = tool_result
            log_agent_step(run_id, step_num, plan, tool_name, str(tool_result), is_final=False)

            history.append({"role": "assistant", "content": plan})
            history.append({"role": "user", "content": f"Tool result: {tool_result}"})

        else:
            history.append({
                "role": "user",
                "content": "Please respond with either CALL_TOOL: tool_name : input or DONE: answer"
            })

    return {
        "answer": "Could not complete the task within the step limit.",
        "steps": steps,
        "completed": False,
        "run_id": run_id,
    }


# quick test

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
