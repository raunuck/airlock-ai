# Agent Loop — How it works

Basic idea: instead of one LLM call and done, the agent runs in a loop.
It thinks → picks a tool → runs it → looks at the result → thinks again → repeat until done.

## The loop (pseudocode)

```
function run_agent(user_goal):

    history = [user_goal]

    repeat up to 5 times:

        # think
        ask LLM: "given the goal and everything so far, what's the next step?"
        
        LLM replies with one of two things:
            CALL_TOOL: <tool_name> : <input>
            DONE: <final answer>

        if DONE → return the answer, we're finished ✓

        if CALL_TOOL:
            figure out which tool and what input
            run that tool
            add the result back to history
            loop again

    if 5 steps done and still no DONE:
        return "couldn't complete the task"
```

## Tools the agent can call

| Tool | What it does |
|------|-------------|
| `search_docs` | searches Chroma for relevant SOP/manual chunks |
| `run_code` | runs generated code in a sandboxed subprocess |
| `extract_text` | pytesseract OCR on an uploaded image |
| `write_docx` | writes findings into a .docx approval note |

## Example — Scenario 2 (approval note from scanned report)

```
User: "Read this inspection report image and draft an approval note"

→ CALL_TOOL: extract_text : report.jpg
   result: [raw text from the image]

→ CALL_TOOL: search_docs : "valve inspection clause 4.2"
   result: [relevant SOP chunks from Chroma]

→ CALL_TOOL: write_docx : "findings: ..."
   result: approval_note.docx created

→ DONE: approval note saved at approval_note.docx ✓
```

## A few things to keep in mind
- Every step should be logged to SQLite (Raunak's part) — this is what the trace view reads from, don't skip it
- The LLM sometimes doesn't follow the CALL_TOOL/DONE format exactly — few-shot examples in the system prompt fix this most of the time
- 5 step limit is intentional — prevents infinite loops during the demo
