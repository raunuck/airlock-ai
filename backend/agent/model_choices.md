# Model Choices

Okay so for MRPL everything has to stay on-premise — no cloud, no external API calls. 
Keeping that in mind, here's what I think we should go with:

## The 3 model slots

**General reasoning + RAG (document Q&A)**
→ `qwen2.5:7b`
Good at reading long SOPs, following instructions, answering grounded questions. This is our main workhorse.

**Coding tasks**
→ `qwen2.5-coder:7b`
Fine-tuned specifically for code — noticeably better than the general model when the task is write/debug/run code.

**Image / scanned documents**
→ `pytesseract` for now, `llava:7b` later
LLaVA can read images natively (actual multimodal), but for this week pytesseract does the job as a placeholder. We should be honest about this in the demo.

## Why only open-weight models
MRPL's whole point is sovereign + confidential. OpenAI/Gemini are out by definition. Qwen and LLaVA are open-weight, run fully through Ollama, nothing leaves the machine.

## Hardware note
Quantized 7B models need ~6-8GB RAM. 
→ Test on the actual demo laptop on Day 1 itself
→ If it's lagging, drop to `qwen2.5:3b` — don't wait till Day 4 to find out it's slow

## Ollama pulls needed
```
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b
ollama pull llava:7b        # for Day 5 onwards
```
