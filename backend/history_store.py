"""Persistent history storage utilities for PromptForge."""

from pathlib import Path
import json
from typing import List

class HistoryStore:
    def __init__(self, path):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])
    def _read(self):
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    def _write(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)
    def add(self, item: dict):
        data = self._read()
        data.insert(0, item)
        # keep last 200
        data = data[:200]
        self._write(data)
    def list(self) -> List[dict]:
        return self._read()
