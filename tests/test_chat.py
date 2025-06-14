import json
import sys
import types
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Stub modules before importing Chat
sys.modules.setdefault('openai', types.SimpleNamespace(api_key=None))
sys.modules.setdefault('requests', types.SimpleNamespace())

import Chat


def test_save_session(tmp_path, monkeypatch):
    temp_file = tmp_path / "session.json"
    monkeypatch.setattr(Chat, "SESSION_FILE", str(temp_file))
    monkeypatch.setattr(Chat, "chat_sessions", {})

    sample_data = [{"question": "hi", "response": "hello"}]
    Chat.save_session("session1", sample_data)

    with open(temp_file, "r") as f:
        content = json.load(f)

    assert content == {"session1": sample_data}
