# Agent Loop

Instead of one LLM call and done, the agent keeps going in a loop until the task is finished. It thinks, picks a tool, runs it, sees the result, then thinks again.

## Pseudocode

```
function run_agent(user_goal):

    history = [user_goal]

    repeat up to 5 times:

        ask LLM: "given the goal and history so far, what do we do next?"

        LLM replies with either:
            CALL_TOOL: <tool_name> : <input>
            DONE: <final answer>

        if DONE, return the answer and stop

        if CALL_TOOL:
            run the tool with the given input
            add result to history
            go back to top

    if still not done after 5 steps:
        return "could not complete the task"
```

## Tools available

| Tool | What it does |
|------|-------------|
| `search_docs` | pulls relevant chunks from Chroma |
| `run_code` | runs code in a sandboxed subprocess |
| `extract_text` | OCR on an uploaded image using pytesseract |
| `write_docx` | creates the approval note as a .docx file |

## Notes
- Each step needs to be logged to SQLite so the trace view works. Raunak is handling the DB part but the logging call has to happen inside this loop.
- The LLM sometimes won't follow the CALL_TOOL/DONE format properly. Few-shot examples in the system prompt usually fix this.
- 5 step cap is intentional so we don't get stuck in a loop during the demo.
