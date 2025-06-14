import json
import os
import sys
import types
from pathlib import Path
import importlib
import builtins

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Stub modules before importing Chat
sys.modules.setdefault('openai', types.SimpleNamespace(api_key=None))
sys.modules.setdefault('requests', types.SimpleNamespace())


def test_save_session(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("DEHASHED_API_KEY", "x")
    import Chat
    importlib.reload(Chat)

    temp_file = tmp_path / "session.json"
    monkeypatch.setattr(Chat, "SESSION_FILE", str(temp_file))
    monkeypatch.setattr(Chat, "chat_sessions", {})

    sample_data = [{"question": "hi", "response": "hello"}]
    Chat.save_session("session1", sample_data)

    with open(temp_file, "r") as f:
        content = json.load(f)

    assert content == {"session1": sample_data}


def test_malformed_session_file(tmp_path, monkeypatch):
    invalid = tmp_path / "bad.json"
    invalid.write_text("{ invalid")

    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("DEHASHED_API_KEY", "x")

    def fake_exists(path):
        return True if path == "chat_sessions.json" else os.path.exists(path)

    original_open = builtins.open

    def fake_open(path, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        if path == "chat_sessions.json" and "r" in mode:
            return original_open(invalid, *args, **kwargs)
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(os.path, "exists", fake_exists)
    monkeypatch.setattr(builtins, "open", fake_open)

    import Chat
    importlib.reload(Chat)

    assert Chat.chat_sessions == {}
