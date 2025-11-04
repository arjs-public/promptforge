"""Client helpers for interacting with an Ollama model server."""

import requests
import json
class OllamaError(Exception):
    pass

def generate_from_ollama(prompt: str, model: str = "gpt-oss", ollama_url: str = "http://127.0.0.1:11434", max_tokens: int = 1024, timeout: int = 20):
    url = f"{ollama_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens
    }
    payload2 = {
        "model": "llama3.2:3b",
        "prompt": "Write a short poem about a sunset over the ocean.",
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except Exception as e:
        raise OllamaError(f"Failed to reach Ollama at {url}: {e}")
    if resp.status_code != 200:
        raise OllamaError(f"Ollama returned {resp.status_code}: {resp.text[:500]}")
    try:
        data = resp.json()
    except Exception as e:
        for line in resp.text.splitlines():
            if not line.strip():
                continue  # skip empty lines
            obj = json.loads(line)  # parse each JSON object
            # do something with obj
            parts = []
            def _extract(obj):
                if isinstance(obj, dict):
                    # common top-level keys
                    for k in ("text", "result", "response", "content", "message", "output"):
                        if k in obj:
                            v = obj[k]
                            # list -> join its items
                            if isinstance(v, list):
                                sub = []
                                for item in v:
                                    if isinstance(item, str):
                                        sub.append(item)
                                    elif isinstance(item, dict):
                                        for kk in ("text", "result", "message", "response", "content"):
                                            if kk in item:
                                                vv = item[kk]
                                                sub.append(vv if isinstance(vv, str) else str(vv))
                                                break
                                        else:
                                            sub.append(str(item))
                                    else:
                                        sub.append(str(item))
                                return "\n".join(sub)
                            # dict -> try nested content/text
                            if isinstance(v, dict):
                                for kk in ("content", "text"):
                                    if kk in v and isinstance(v[kk], str):
                                        return v[kk]
                                return str(v)
                            return v if isinstance(v, str) else str(v)
                    # choices-like fallback
                    if "choices" in obj and isinstance(obj["choices"], list):
                        ch = []
                        for choice in obj["choices"]:
                            if isinstance(choice, dict):
                                if "text" in choice and isinstance(choice["text"], str):
                                    ch.append(choice["text"]); continue
                                msg = choice.get("message") or choice.get("delta")
                                if isinstance(msg, dict):
                                    content = msg.get("content") or msg.get("text")
                                    if isinstance(content, str):
                                        ch.append(content); continue
                                if "content" in choice and isinstance(choice["content"], str):
                                    ch.append(choice["content"]); continue
                            ch.append(str(choice))
                        return "\n".join(ch)
                    return str(obj)
                return str(obj)

            for line in resp.text.splitlines():
                if not line.strip():
                    continue  # skip empty lines
                obj = json.loads(line)  # parse each JSON object
                parts.append(_extract(obj))

            # combine into a single string for downstream processing
            data = "".join([p for p in parts if p]).strip()
            
        if not data:
            raise OllamaError(f"Failed to parse Ollama response as JSON: {e}")

    # If response is a list, try to extract text from its elements
    if isinstance(data, list):
        parts = []
        for item in data:
            if isinstance(item, dict):
                for k in ("text", "result", "output", "message", "response", "content"):
                    if k in item:
                        v = item[k]
                        parts.append(v if isinstance(v, str) else str(v))
                        break
                else:
                    parts.append(str(item))
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()

    # Handle common nested "choices" / "message" shapes (e.g., OpenAI-like)
    if isinstance(data, dict):
        if "choices" in data and isinstance(data["choices"], list):
            parts = []
            for choice in data["choices"]:
                if isinstance(choice, dict):
                    # choice.text
                    if "text" in choice and isinstance(choice["text"], str):
                        parts.append(choice["text"])
                        continue
                    # choice.message.content
                    msg = choice.get("message") or choice.get("delta")
                    if isinstance(msg, dict):
                        content = msg.get("content") or msg.get("text")
                        if isinstance(content, str):
                            parts.append(content)
                            continue
                    # choice.content
                    if "content" in choice and isinstance(choice["content"], str):
                        parts.append(choice["content"])
                        continue
                parts.append(str(choice))
            return "\n".join(parts).strip()

        # If "output" is a list, join its items
        if "output" in data and isinstance(data["output"], list):
            parts = []
            for o in data["output"]:
                if isinstance(o, dict):
                    for k in ("text", "result", "message", "response", "content"):
                        if k in o:
                            v = o[k]
                            parts.append(v if isinstance(v, str) else str(v))
                            break
                    else:
                        parts.append(str(o))
                else:
                    parts.append(str(o))
            return "\n".join(parts).strip()

    # Fall through to the existing extraction logic below
    # Ollama's response shape may differ; try to extract text safely
    if isinstance(data, dict):
        for k in ("text", "result", "output", "message", "response"):
            if k in data:
                return data[k]
        # fallback
        return str(data)
    return str(data)
