# PromptForge Specification (SPECS.md)

## Goal
Small local web app that runs in the background, serves a browser UI form for building an AI-chatbot prompt (fields: Title, Context, AI Role, Additional Info, Output Format, Target Audience), calls Ollama to refine/compose a high-quality prompt (C.R.A.F.T.), shows/copies/stores the result, and exposes a simple history usable by browser extensions.

---

# High-level design
- **Backend**: Python FastAPI + Uvicorn (single process), serves:
  - static frontend (single-page app HTML/JS/CSS)
  - JSON API for generating refined prompts (`/api/generate`)
  - optional persistence endpoints (`/api/history`, `/api/config`) — disabled by default
  - config loader (JSON/YAML) for Ollama endpoint, model name, bind address, port, persistence toggles

- **Frontend**: HTML + vanilla JS (small footprint) or React-lite if preferred. Single page form, shows result, copy button, history saved in `localStorage` (IndexedDB optional).

- **Ollama integration**: backend makes `POST` to local Ollama HTTP API (e.g. `http://localhost:11434/api/generate`) using configured model.

- **Packaging**: produce single executable for Windows and macOS via PyInstaller. Include service-mode flag to run headless and auto-start instructions.

- **Security**: Bind to `127.0.0.1` by default; CORS limited to same origin.

---

# Files & repo layout
```
promptforge/
├─ backend/
│  ├─ app.py
│  ├─ ollama_client.py
│  ├─ config.py
│  ├─ history_store.py
│  ├─ requirements.txt
│  └─ build_scripts/
│     ├─ build_mac.sh
│     └─ build_win.bat
├─ frontend/
│  ├─ index.html
│  ├─ app.js
│  └─ styles.css
├─ README.md
└─ packaging/
   ├─ pyinstaller.spec
   └─ ...
```

---

# Backend: API contract
All JSON responses `{ ok: true|false, data: ..., error?: ... }`.

### `/api/generate` (POST)
**Request:**
```json
{
  "title": "string",
  "context": "string",
  "ai_role": "string",
  "additional_info": "string",
  "output_format": "string",
  "target_audience": "string",
  "model": "optional string"
}
```
**Response:**
```json
{
  "ok": true,
  "data": {
    "crafted_prompt": "string",
    "ollama_response": "string"
  }
}
```

### `/api/history` (GET/POST, optional)
Returns or saves prompt history if enabled.

### `/api/config` (GET)
Returns current configuration (non-sensitive).

---

# Config file
Located at `~/.promptforge/config.json` or `config.yaml`.

Example:
```json
{
  "bind": "127.0.0.1",
  "port": 11435,
  "ollama_url": "http://localhost:11434",
  "default_model": "gpt-oss",
  "enable_history_api": false,
  "history_file": "~/.promptforge/history.json"
}
```

---

# Prompt template (C.R.A.F.T.)
```
Title:
  {title}

Context:
  {context}

Role (AI):
  You are {ai_role}. Your tone and constraints: be concise, factual, and explain assumptions.

Additional Information:
  {additional_info}

Format:
  {output_format}

Target Audience:
  {target_audience}

Goal:
  Compose a high-quality assistant prompt that, when given to a chatbot, will produce useful and accurate outputs for the target audience.
```

---

# Frontend UX flow
- Form with fields and buttons (Generate, Copy, Save, Clear)
- Shows generated prompt and allows copy/export
- History stored in `localStorage`
- Optionally syncs to server if persistence enabled
* Minimal form with labeled fields (Title, Context, AI Role, Additional Info, Output Format, Target Audience).

* Buttons: Generate, Copy Prompt, Save to History, Clear.

* After Generate:

  * Show crafted\_prompt in a scrollable preformatted area.

  * Show ollama\_response (toggleable).

  * Offer Copy and Export (download .txt).

* History:

  * Each saved history entry shows timestamp, title, and snippet.

  * Clicking opens full prompt. Stored in localStorage (key: promptforge.history), optionally syncs to server if enabled and user opts-in.

* Extension integration:

  * Browser extension can read from same localStorage or call GET /api/history if server-side persistence enabled and allowed by CORS.

---

# Persistence & history
- Default: `localStorage`
- Optional: file-based JSON store if enabled in config

---

# Ollama client behavior
Use simple HTTP `POST` to `<ollama_url>/api/generate` with JSON body matching Ollama API.
* Use simple HTTP POST to \<ollama\_url>/api/generate with JSON body matching Ollama API (model selection, prompt).

* Implement timeout and retries (configurable).

* Return ollama\_response trimmed to useful size (avoid huge payloads). Allow full\_response query param if needed.

Example:
```python
payload = {
  "model": model,
  "prompt": crafted_prompt,
  "max_tokens": 1024
}
```

---

# Packaging & background service
- `promptforge run` — foreground
- `promptforge service` — background
- Built with PyInstaller for macOS/Windows

---

# Testing
- Unit: config loader, Ollama client, prompt assembly
- E2E: form submission -> generated prompt display
- Security: restrict to localhost

---

# Acceptance criteria
1. Server starts on localhost and serves UI
2. Generated C.R.A.F.T. prompt displayed and copyable
3. History persists in localStorage
4. Configurable model and Ollama URL
5. Optional server-side history works
6. Packaged into single executable

---

# Implementation steps for coding agent
1. Scaffold repo & environment
2. Implement config loader
3. Ollama client
4. FastAPI endpoints
5. Frontend SPA
6. Packaging scripts
7. Tests
8. Docs

---
# **Testing & QA**

* Unit tests for:

  * config loader parsing (YAML/JSON)

  * Ollama client (mocked)

  * prompt template assembly (various inputs; assert CRAFT sections present)

* E2E tests:

  * Start server, load frontend, submit form, verify crafted\_prompt returned.

  * localStorage history saved and readable.

* Security checks:

  * Ensure server binds to 127.0.0.1 by default and CORS only allows http://localhost:\<port>.

---
# **Acceptance criteria (what “done” looks like)**

1. Running executable starts a background process bound to 127.0.0.1:\<port>.

2. Opening http://localhost:\<port> shows the form.

3. Filling the form and pressing Generate returns a well-structured C.R.A.F.T.-oriented prompt and displays it.

4. The prompt can be copied to clipboard and exported as .txt.

5. History is saved in localStorage and can be cleared.

6. Config file allows changing default\_model and Ollama URL.

7. Optional: server-side history persists when enabled.

8. A short README explains packaging and install steps for macOS and Windows.

---
# **Coding-agent task breakdown (steps to implement)**

1. **Scaffold repo & environment**: create layout, requirements (fastapi, uvicorn, requests, pyyaml).

2. **Config loader**: implement defaults, override from ~/.promptforge/config.(json|yaml), CLI flags.

3. **Ollama client** wrapper with error handling.

4. **FastAPI endpoints** (serve static files + /api/generate, /api/history optional).

5. **Frontend SPA**: light JS form, localStorage history, copy-to-clipboard, fetch to /api/generate.

6. **Packaging scripts** for PyInstaller.

7. **Tests**: unit & simple E2E.

8. **Docs**: README, launch instructions, plist example for macOS launchd, NSSM/schtasks notes for Windows.

---
# **Implementation notes & edge cases**

* **Rate / token limits**: Ollama is local but still support max\_tokens safe default.

* **Large inputs**: Trim fields or warn if too long; provide preview of used prompt.

* **Privacy**: default to local-only storage. Server-side storage opt-in must be explicit.

* **Extensibility**: add later: OAuth for remote LLM endpoints, plugin hooks to transform prompts.

---
# **Example minimal&#xA0;**

**app.py** skeleton (concept) 
_(I won’t produce full code here unless you want—this is to make the tasks clear to a coding agent.)_
# app.py (high-level)
```from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from config import load_config
from ollama_client import generate_from_ollama

app = FastAPI()
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

@app.post("/api/generate")
async def generate(payload: dict):
    crafted = assemble_craft(payload)
    ollama_resp = generate_from_ollama(crafted, model=payload.get("model"))
    return {"ok": True, "data": {"crafted_prompt": crafted, "ollama_response": ollama_resp}}
```

---
# **Deliverables for the coding agent**

* Fully working repo with above layout.

* README.md with run and packaging steps.

* One-line build scripts for macOS and Windows (PyInstaller-based).

* Unit tests & minimal E2E test script.

* Example config and optional launch scripts for macOS (plist) and Windows (NSSM/schtasks snippet).
---
# **Packaging & run-as-background**

* Provide two CLI modes:

  * promptforge run — foreground (logs to console)

  * promptforge service — background/daemon (no console; on Windows register as service or use NSSM; on macOS provide plist sample)

* Packaging:

  * Use PyInstaller to build single-file executable for each platform.

  * Include a small installer instructions or packaging script:

    * Windows: PyInstaller + create a .exe; optionally create an NSSM service wrapper or a scheduled task to start at login.

    * macOS: PyInstaller + a launchd plist template for user-level agent.

* During packaging, ensure static frontend files are bundled (--add-data).
