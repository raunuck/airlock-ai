# Model Choices

Since MRPL needs everything on-premise, no cloud calls at all, here's what I'm going with and why:

## Models

**General reasoning + RAG:** `qwen2.5:7b`
Handles SOPs and document questions well. Will be the main model for most tasks.

**Coding tasks:** `qwen2.5-coder:7b`
Trained specifically on code so it's noticeably better than the general model for write/debug tasks. Worth having as a separate model.

**Images and scanned docs:** `pytesseract` this week, `llava:7b` later
LLaVA is actually multimodal so it can read images directly. For now pytesseract works fine as a placeholder and is one less thing to debug. We can say this out loud in the demo, not a big deal.

## Why not use OpenAI or anything cloud based
MRPL's whole requirement is confidential and sovereign. OpenAI/Gemini are off the table by default. Qwen and LLaVA run fully through Ollama so nothing leaves the machine.

## Hardware
7B quantized models need around 6-8GB RAM. Please test on the actual demo laptop early, not on Day 4. If it's too slow just drop to `qwen2.5:3b`.

## Ollama pulls
```
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b
ollama pull llava:7b
ollama pull qwen2.5:3b
ollama pull qwen2.5-coder:3b
```
