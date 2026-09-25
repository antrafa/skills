#!/usr/bin/env python3
"""PreToolUse guard for the forja skill: the No-write rule, enforced in code.

Armed only while ~/.forja/tutor-active exists. The marker holds the id of the session
that armed it, so a marker left behind by a closed session, or armed by a concurrent
one, never guards anyone else. Reads the hook payload on stdin, prints a deny decision
on stdout.

Run `forja-guard.py --self-test` to check the decision logic.
"""
import json
import os
import re
import shlex
import sys

HOME = os.path.expanduser("~")
MARKER = os.path.join(HOME, ".forja", "tutor-active")
ALLOWED_ROOT = os.path.join(HOME, ".forja")

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# Commands that change the project no matter what their arguments are. Deliberately
# broad: a false deny is visible and recoverable, a false allow is silent.
ALWAYS_WRITES = re.compile(
    r"(\bdd\b.*\bof=)"
    r"|(\bsed\b.*\s-i\b)"
    r"|(\b(npm|pnpm|yarn|bun)\s+(i|install|add|create|init)\b)"
    r"|(\bnpx\b)"
    r"|(\bgit\s+(commit|push|add|checkout|apply|restore|reset|merge|stash)\b)"
    r"|(\bapply_patch\b)"
)

# Commands whose every operand must sit under ~/.forja.
FILE_COMMANDS = {"cp", "mv", "rm", "mkdir", "touch", "truncate", "chmod", "ln", "tee"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", ">&"}
SEPARATORS = {"&&", "||", ";", "|", "&", "|&", "(", ")"}
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?")


def is_under_forja(path):
    path = path.replace("$HOME", HOME).replace("${HOME}", HOME)
    resolved = os.path.realpath(os.path.expanduser(path))
    root = os.path.realpath(ALLOWED_ROOT)
    return resolved == root or resolved.startswith(root + os.sep)


def strip_heredoc_bodies(command):
    """Drop heredoc bodies: they are data, and their `>` or `;` are not shell syntax."""
    lines, kept, terminator = command.split("\n"), [], None
    for line in lines:
        if terminator:
            if line.strip() == terminator:
                terminator = None
            continue
        kept.append(line)
        match = HEREDOC.search(line)
        if match:
            terminator = match.group(1)
    return "\n".join(kept)


def tokenize(command):
    # shlex reads a newline as plain whitespace; to the shell it ends a command.
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


def write_targets(tokens):
    """Yield every path the command writes to, or None for a write we cannot place."""
    command_word = True
    for i, token in enumerate(tokens):
        following = tokens[i + 1] if i + 1 < len(tokens) else None
        if token in SEPARATORS:
            command_word = True
            continue
        if token in REDIRECTS:
            is_fd_copy = token == ">&" and following and (following.isdigit() or following == "-")
            if not is_fd_copy and following != "/dev/null":
                yield following
            continue
        if command_word:
            command_word = False
            if os.path.basename(token) in FILE_COMMANDS:
                for operand in tokens[i + 1:]:
                    if operand in SEPARATORS or operand in REDIRECTS:
                        break
                    if not operand.startswith("-"):
                        yield operand


def shell_write_outside_forja(command):
    if ALWAYS_WRITES.search(command):
        return True
    body = strip_heredoc_bodies(command)
    try:
        targets = list(write_targets(tokenize(body)))
    except ValueError:
        return True  # Unbalanced quotes: we cannot tell what it writes, so assume the worst.
    if any(target is None or not is_under_forja(target) for target in targets):
        return True
    # ponytail: a heredoc feeding an interpreter (`python3 - <<PY`) can write anywhere;
    # we only let it through when its output is redirected into ~/.forja.
    return bool(HEREDOC.search(body)) and not targets


def marker_owner():
    """The session id stored in the marker, "" for a legacy empty marker, None if absent."""
    try:
        with open(MARKER) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def is_armed_for(session_id):
    owner = marker_owner()
    if owner is None:
        return False
    # An empty marker predates session binding: guard everyone rather than no one.
    return owner == "" or owner == session_id


def arms_tutor_mode(tool_name, tool_input):
    command = tool_input.get("command", "") if tool_name == "Bash" else ""
    return "tutor-active" in command and re.search(r"\btouch\b", command) is not None


def bind_marker(session_id):
    # ponytail: one owner per machine; a second session arming a track takes the guard over.
    os.makedirs(ALLOWED_ROOT, exist_ok=True)
    with open(MARKER, "w") as f:
        f.write(session_id)


def decision(tool_name, tool_input, session_id=""):
    """Return a deny reason, or None to stay out of the way."""
    if not is_armed_for(session_id):
        return None

    if tool_name in WRITE_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        resolved = os.path.realpath(os.path.expanduser(path)) if path else ""
        root = os.path.realpath(ALLOWED_ROOT)
        if resolved == root or resolved.startswith(root + os.sep):
            return None
        return (
            "forja No-write rule: the student writes their own implementation files. "
            "Only ~/.forja/ is writable while tutor mode is on. Show the snippet and the "
            "exact file path in chat instead, or run `/forja off` if they deliberately "
            "want you to take over."
        )

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if shell_write_outside_forja(command):
            return (
                "forja No-write rule: this command creates, modifies, or installs "
                "something in the student's project. Read-only diagnostics are fine "
                "(ls, cat, git log, git status, npm view, tsc --noEmit). Hand the command "
                "to the student to run, or `/forja off` to take over deliberately."
            )

    return None


def self_test():
    previous = marker_owner()
    os.makedirs(ALLOWED_ROOT, exist_ok=True)
    open(MARKER, "w").close()
    try:
        assert decision("Write", {"file_path": "/tmp/agent.ts"})
        assert decision("Edit", {"file_path": "src/mastra/index.ts"})
        assert decision("Write", {"file_path": "~/.forja/progress/mastra.md"}) is None
        assert decision("Bash", {"command": "cat src/index.ts"}) is None
        assert decision("Bash", {"command": "git status"}) is None
        assert decision("Bash", {"command": "npm view mastra version"}) is None
        assert decision("Bash", {"command": "tsc --noEmit"}) is None
        assert decision("Bash", {"command": "echo hi > src/agent.ts"})
        assert decision("Bash", {"command": "npm install ai zod"})
        assert decision("Bash", {"command": "git commit -m x"})
        assert decision("Bash", {"command": "touch ~/.forja/tutor-active"}) is None
        assert decision("Read", {"file_path": "/etc/hosts"}) is None
        assert decision("Bash", {"command": "tsc --noEmit 2>&1 | head"}) is None
        assert decision("Bash", {"command": "ls src 2>/dev/null"}) is None
        assert decision("Bash", {"command": "mkdir -p ~/.forja && touch ~/.forja/tutor-active"}) is None
        assert decision("Bash", {"command": "rm -f ~/.forja/tutor-active"}) is None
        assert decision("Bash", {"command": "cat > ~/.forja/progress/m.md <<'EOF'\na > b; c\nEOF"}) is None
        assert decision("Bash", {"command": "cat ~/.forja/progress/m.md && npm install lodash"})
        assert decision("Bash", {"command": "echo x > ~/.forja/log; echo y > src/agent.ts"})
        assert decision("Bash", {"command": "mv ~/.forja/draft.ts src/agent.ts"})
        assert decision("Bash", {"command": "cat <<'EOF' > ~/.forja/x\nhi\nEOF\ntouch src/a.ts"})
        assert decision("Bash", {"command": "python3 - <<'PY'\nopen('src/a.ts','w')\nPY"})
        assert decision("Bash", {"command": "echo 'unbalanced > src/a.ts"})
        assert decision("Bash", {"command": "(cd src && touch a.ts)"})

        assert arms_tutor_mode("Bash", {"command": "mkdir -p ~/.forja && touch ~/.forja/tutor-active"})
        assert not arms_tutor_mode("Bash", {"command": "rm -f ~/.forja/tutor-active"})
        bind_marker("session-a")
        assert decision("Write", {"file_path": "/tmp/agent.ts"}, "session-a")
        assert decision("Write", {"file_path": "/tmp/agent.ts"}, "session-b") is None

        os.remove(MARKER)
        assert decision("Write", {"file_path": "/tmp/agent.ts"}, "session-a") is None
    finally:
        if previous is None:
            if os.path.exists(MARKER):
                os.remove(MARKER)
        else:
            with open(MARKER, "w") as f:
                f.write(previous)
    print("ok")


def main():
    if "--self-test" in sys.argv:
        return self_test()

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return  # Never break the host on a payload we don't understand.

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    session_id = payload.get("session_id", "")
    if session_id and arms_tutor_mode(tool_name, tool_input):
        bind_marker(session_id)
    reason = decision(tool_name, tool_input, session_id)
    if reason:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            sys.stdout,
        )


if __name__ == "__main__":
    main()
