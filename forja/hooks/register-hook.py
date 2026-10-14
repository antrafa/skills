#!/usr/bin/env python3
"""Registers forja-guard.py as a PreToolUse hook in Claude Code settings. Idempotent."""
import json, os, sys

settings_path, script = sys.argv[1], sys.argv[2]
command = f"python3 {script}"
matcher = "Write|Edit|MultiEdit|NotebookEdit|Bash"

try:
    with open(settings_path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

entries = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
for entry in entries:
    hooks = entry.get("hooks", [])
    if any("forja-guard.py" in h.get("command", "") for h in hooks):
        # Repoint an existing registration instead of stacking a second one.
        entry["matcher"] = matcher
        for h in hooks:
            if "forja-guard.py" in h.get("command", ""):
                h["command"] = command
        break
else:
    entries.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})

os.makedirs(os.path.dirname(settings_path), exist_ok=True)
with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
print(f"  hook  {settings_path} -> forja-guard.py")
