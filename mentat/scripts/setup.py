#!/usr/bin/env python3
"""Wire Mentat into this machine: vault, sync, every installed agent, timer.

Safe to re-run: each step checks before it writes, so a second run only fixes
what drifted. `--dry-run` prints the plan and changes nothing — show it to the
person before running for real, since it edits other agents' global config.

What stays with the agent, not this script: absorbing what each agent already
remembered on its own. That takes judgment (new, duplicate or trivia?), so this
script only inventories it.

Mentat as the main memory is opt-in per agent: `--agents` names the ones that
get the pointer block, `--agents none` leaves Mentat as a skill to consult only.
`--uninstall` takes the blocks and the timer back out and never touches the vault.

    setup.py --dry-run
    setup.py [--remote git@github.com:you/mentat-memory.git] [--agents claude,codex] [--no-timer]
    setup.py --uninstall [--agents codex] [--dry-run]
"""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import vault

SKILL_DIR = Path(__file__).resolve().parent.parent
HOME = Path.home()
BLOCK_START, BLOCK_END = "<!-- mentat:start -->", "<!-- mentat:end -->"
POINTER_BLOCK = f"""{BLOCK_START}
## Memory (Mentat)

Your persistent memory is the Mentat vault at `{vault.VAULT}`, shared across agents and machines. Use the `mentat` skill:
- before answering about past work, or deciding something that may already be decided, recall from it;
- to remember something durable, write it through the skill, never to this agent's own memory.
{BLOCK_END}"""


@dataclass(frozen=True)
class Agent:
    key: str
    name: str
    home: Path
    instructions: Path
    skill_dirs: tuple[Path, ...]
    native_memory: tuple[str, ...] = ()  # globs under home


AGENTS = (
    Agent("claude", "Claude Code", HOME / ".claude", HOME / ".claude/CLAUDE.md",
          (HOME / ".claude/skills",), ("projects/*/memory/*.md",)),
    Agent("codex", "Codex", HOME / ".codex", HOME / ".codex/AGENTS.md",
          (HOME / ".codex/skills",), ("memories/**/*",)),
    Agent("antigravity", "Antigravity", HOME / ".gemini", HOME / ".gemini/GEMINI.md",
          (HOME / ".gemini/antigravity/skills", HOME / ".gemini/skills"),
          ("antigravity/knowledge/**/*.md",)),
    Agent("opencode", "OpenCode", HOME / ".config/opencode", HOME / ".config/opencode/AGENTS.md",
          (HOME / ".config/opencode/skills",)),
)


@dataclass
class Plan:
    steps: list[tuple[str, Callable[[], None]]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, description: str, action: Callable[[], None]) -> None:
        self.steps.append((description, action))


def run(*args: str, cwd: Path | None = None) -> None:
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if done.returncode:
        sys.exit(f"error: {' '.join(args)} failed: {done.stderr.strip()}")


# --- vault and remote --------------------------------------------------------


def plan_vault(plan: Plan, remote: str | None) -> None:
    has_git = (vault.VAULT / ".git").exists()
    cloned = bool(remote) and not vault.VAULT.exists()
    if cloned:
        plan.add(f"clone {remote} into {vault.VAULT}", lambda: run("git", "clone", "-q", remote, str(vault.VAULT)))
        has_git = True
    if cloned or not all((vault.VAULT / part).exists() for part in ("entries", "maps", "index.md")):
        plan.add(f"create or repair the vault structure at {vault.VAULT}",
                 lambda: run("bash", str(SKILL_DIR / "scripts/init-vault.sh")))
    if remote and vault.VAULT.exists() and not has_git:
        plan.add(f"turn {vault.VAULT} into a git repository", lambda: run("git", "init", "-q", "-b", "main", cwd=vault.VAULT))
        has_git = True
    if not has_git:
        plan.notes.append(f"sync off: {vault.VAULT} has no git repository — re-run with --remote <url> to share it")
        return
    # Before the first push, so the merge rules travel with the vault from day one.
    if cloned or needs_sync_config():
        plan.add("install the merge rules (.gitattributes, entry merge driver)", vault.ensure_sync_config)
    if remote and not cloned and not vault.git("remote").stdout.strip():
        plan.add(f"set remote origin to {remote} and push the vault", lambda: publish(remote))


def needs_sync_config() -> bool:
    attributes = vault.VAULT / ".gitattributes"
    configured = (vault.VAULT / ".git").exists() and vault.git("config", f"merge.{vault.ENTRY_DRIVER}.driver").stdout.strip()
    return not (attributes.exists() and configured)


def publish(remote: str) -> None:
    run("git", "remote", "add", "origin", remote, cwd=vault.VAULT)
    vault.commit_all("chore(memoria): versionar vault mentat")
    branch = vault.git("branch", "--show-current").stdout.strip() or "main"
    run("git", "push", "-q", "-u", "origin", branch, cwd=vault.VAULT)
    vault.restore_local()


# --- agents ------------------------------------------------------------------


def with_pointer_block(text: str) -> str:
    """Insert or replace the marked block, leaving everything else untouched."""
    if BLOCK_START in text and BLOCK_END in text:
        before, _, rest = text.partition(BLOCK_START)
        _, _, after = rest.partition(BLOCK_END)
        return before + POINTER_BLOCK + after
    return (text.rstrip() + "\n\n" if text.strip() else "") + POINTER_BLOCK + "\n"


def without_pointer_block(text: str) -> str:
    if BLOCK_START not in text or BLOCK_END not in text:
        return text
    before, _, rest = text.partition(BLOCK_START)
    _, _, after = rest.partition(BLOCK_END)
    remaining = before.rstrip() + ("\n\n" + after.lstrip() if after.strip() else "")
    return remaining.strip() + "\n" if remaining.strip() else ""


def remove_pointer(path: Path) -> None:
    path.write_text(without_pointer_block(path.read_text(encoding="utf-8")), encoding="utf-8")


def write_pointer(path: Path) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(with_pointer_block(current), encoding="utf-8")


def link_skill(target: Path) -> None:
    if target.is_symlink():
        target.unlink()  # only reached for a broken link
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(SKILL_DIR, target_is_directory=True)


def installed_agents() -> list[Agent]:
    return [a for a in AGENTS if a.home.is_dir()]


def select_agents(raw: str) -> set[str]:
    """`all`, `none` or a comma list of agent keys."""
    if raw == "all":
        return {a.key for a in AGENTS}
    if raw == "none":
        return set()
    chosen = {k.strip().lower() for k in raw.split(",") if k.strip()}
    unknown = chosen - {a.key for a in AGENTS}
    if unknown:
        sys.exit(f"error: unknown agent {', '.join(sorted(unknown))} — use {', '.join(a.key for a in AGENTS)}, all or none")
    return chosen


def plan_agents(plan: Plan, chosen: set[str]) -> list[Agent]:
    """Link the skill everywhere; the pointer block only where it was chosen.

    The skill is useful to consult even where the agent keeps its own memory,
    so linking it is not the opt-in — the block that makes it THE memory is.
    Agents left out are not touched, so a block from an earlier run stays.
    """
    found = installed_agents()
    for agent in found:
        current = agent.instructions.read_text(encoding="utf-8") if agent.instructions.exists() else ""
        if agent.key in chosen and with_pointer_block(current) != current:
            plan.add(f"{agent.name}: memory pointer block in {agent.instructions}",
                     lambda p=agent.instructions: write_pointer(p))
        for skills in agent.skill_dirs:
            target = skills / "mentat"
            if not target.exists():  # missing, or a symlink whose source moved
                plan.add(f"{agent.name}: link the skill at {target}", lambda t=target: link_skill(t))
    missing = [a.name for a in AGENTS if a not in found]
    if missing:
        plan.notes.append(f"not installed here, skipped: {', '.join(missing)}")
    consult_only = [a.name for a in found if a.key not in chosen]
    if consult_only:
        plan.notes.append(f"Mentat as a skill to consult only, own memory kept: {', '.join(consult_only)}")
    return [a for a in found if a.key in chosen]


def plan_uninstall(plan: Plan, chosen: set[str], every_agent: bool) -> None:
    """Undo setup for the chosen agents; the timer goes only when all of them do.

    The vault and the skill links stay: removing memory is Forget's job, and a
    linked skill nobody points at costs nothing.
    """
    for agent in installed_agents():
        if agent.key not in chosen:
            continue
        if agent.instructions.exists() and BLOCK_START in agent.instructions.read_text(encoding="utf-8"):
            plan.add(f"{agent.name}: remove the memory pointer block from {agent.instructions}",
                     lambda p=agent.instructions: remove_pointer(p))
        for backup in sorted(agent.home.glob("projects/*/memory/MEMORY.md.pre-mentat")):
            plan.add(f"{agent.name}: restore {backup.with_suffix('')} from its pre-Mentat copy",
                     lambda b=backup: b.replace(b.with_suffix("")))
    if every_agent:
        plan_timer_removal(plan)
    plan.notes.append(f"kept: the vault at {vault.VAULT} and the skill links")


def native_memory(agent: Agent) -> list[Path]:
    """Files an agent remembered on its own, minus pointers this setup left behind."""
    files = [p for pattern in agent.native_memory for p in agent.home.glob(pattern) if p.is_file()]
    return sorted(p for p in files if not is_pointer(p))


def is_pointer(path: Path) -> bool:
    return path.name == "MEMORY.md" and "mentat" in path.read_text(encoding="utf-8", errors="ignore").lower()


# --- timer -------------------------------------------------------------------

SYSTEMD_DIR = HOME / ".config/systemd/user"
LAUNCHD_PLIST = HOME / "Library/LaunchAgents/com.mentat.sync.plist"
SYNC_INTERVAL_MIN = 30


def sync_command() -> list[str]:
    return [sys.executable, str(SKILL_DIR / "scripts/vault.py"), "sync"]


def install_systemd() -> None:
    SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)
    (SYSTEMD_DIR / "mentat-sync.service").write_text(
        "[Unit]\nDescription=Sync the Mentat vault with its remote\n\n"
        f"[Service]\nType=oneshot\nEnvironment=MENTAT_VAULT={vault.VAULT}\n"
        f"ExecStart={' '.join(sync_command())}\n", encoding="utf-8")
    (SYSTEMD_DIR / "mentat-sync.timer").write_text(
        "[Unit]\nDescription=Sync the Mentat vault periodically\n\n"
        f"[Timer]\nOnBootSec=2min\nOnUnitActiveSec={SYNC_INTERVAL_MIN}min\n\n"
        "[Install]\nWantedBy=timers.target\n", encoding="utf-8")
    run("systemctl", "--user", "daemon-reload")
    run("systemctl", "--user", "enable", "--now", "mentat-sync.timer")


def install_launchd() -> None:
    args = "".join(f"<string>{a}</string>" for a in sync_command())
    LAUNCHD_PLIST.parent.mkdir(parents=True, exist_ok=True)
    LAUNCHD_PLIST.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0"><dict>'
        "<key>Label</key><string>com.mentat.sync</string>"
        f"<key>ProgramArguments</key><array>{args}</array>"
        f"<key>EnvironmentVariables</key><dict><key>MENTAT_VAULT</key><string>{vault.VAULT}</string></dict>"
        f"<key>StartInterval</key><integer>{SYNC_INTERVAL_MIN * 60}</integer>"
        "<key>RunAtLoad</key><true/></dict></plist>\n", encoding="utf-8")
    subprocess.run(["launchctl", "unload", str(LAUNCHD_PLIST)], capture_output=True)
    run("launchctl", "load", str(LAUNCHD_PLIST))


def plan_timer(plan: Plan, will_have_remote: bool) -> None:
    if not will_have_remote:
        plan.notes.append("no timer: there is no remote to sync with")
        return
    system = platform.system()
    if system == "Linux" and (SYSTEMD_DIR / "mentat-sync.timer").exists():
        return
    if system == "Darwin" and LAUNCHD_PLIST.exists():
        return
    every = f"every {SYNC_INTERVAL_MIN} min"
    if system == "Linux":
        plan.add(f"systemd user timer: vault.py sync {every} and at boot", install_systemd)
    elif system == "Darwin":
        plan.add(f"launchd agent: vault.py sync {every} and at login", install_launchd)
    else:
        plan.notes.append(f"no timer on {system}: schedule `{' '.join(sync_command())}` yourself")


def remove_systemd() -> None:
    subprocess.run(["systemctl", "--user", "disable", "--now", "mentat-sync.timer"], capture_output=True)
    for unit in ("mentat-sync.timer", "mentat-sync.service"):
        (SYSTEMD_DIR / unit).unlink(missing_ok=True)
    run("systemctl", "--user", "daemon-reload")


def remove_launchd() -> None:
    subprocess.run(["launchctl", "unload", str(LAUNCHD_PLIST)], capture_output=True)
    LAUNCHD_PLIST.unlink(missing_ok=True)


def plan_timer_removal(plan: Plan) -> None:
    if (SYSTEMD_DIR / "mentat-sync.timer").exists():
        plan.add("remove the systemd sync timer", remove_systemd)
    if LAUNCHD_PLIST.exists():
        plan.add("remove the launchd sync agent", remove_launchd)


# --- main --------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--remote", help="git URL of a private repository for the vault")
    parser.add_argument("--no-timer", action="store_true", help="sync only when asked")
    parser.add_argument("--agents", default="all",
                        help=f"who gets Mentat as main memory: all, none, or a list of {','.join(a.key for a in AGENTS)}")
    parser.add_argument("--uninstall", action="store_true", help="remove the pointer blocks and the timer")
    parser.add_argument("--dry-run", action="store_true", help="print the plan, change nothing")
    args = parser.parse_args()
    chosen = select_agents(args.agents)

    plan = Plan()
    if args.uninstall:
        plan_uninstall(plan, chosen, every_agent=args.agents == "all")
        execute(plan, args.dry_run)
        return
    plan_vault(plan, args.remote)
    agents = plan_agents(plan, chosen)
    has_remote = bool(args.remote) or vault.sync_blocker() is None
    if not args.no_timer:
        plan_timer(plan, has_remote)
    execute(plan, args.dry_run)

    print("\nnative memory to absorb (judgment, not this script):")
    inventory = [(a, native_memory(a)) for a in agents]
    for agent, files in inventory:
        print(f"  {agent.name}: {len(files)} files")
    if not any(files for _, files in inventory):
        print("  nothing outside the vault")


def execute(plan: Plan, dry_run: bool) -> None:
    print("plan:" if dry_run else "setup:")
    for description, action in plan.steps:
        print(f"  - {description}")
        if not dry_run:
            action()
    if not plan.steps:
        print("  - nothing to change, everything already in place")
    for note in plan.notes:
        print(f"note: {note}")


if __name__ == "__main__":
    main()
