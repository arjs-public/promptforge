"""Configuration loading helpers for PromptForge backend."""

from pathlib import Path
import json
import yaml

DEFAULT = {
    "bind": "127.0.0.1",
    "port": 11435,
    "ollama_url": "http://localhost:11434",
    "default_model": "gpt-oss:20b",
    "enable_history_api": False,
    "history_file": str(Path.home() / ".promptforge" / "history.json")
}

def load_config():
    cfg = DEFAULT.copy()
    cfg_path = Path.home() / ".promptforge" / "config.yaml"
    if cfg_path.exists():
        try:
            with open(cfg_path, "r") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
    return cfg
