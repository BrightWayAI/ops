#!/usr/bin/env python3
"""Append one metadata line to the agent-run log when a sub-agent starts or stops.

Run by the SubagentStart and SubagentStop hooks in hooks/hooks.json. It must
never disturb a session: it prints nothing, always exits 0, and writes nothing
when the config root cannot be resolved or reached.

It records WHICH agent ran, WHEN, in WHICH session, and FOR WHOM. It never
records the prompt, the agent's reply, file paths, or any other content.

Log location: <config-root>/plugins/ops/agent-runs/<YYYY-MM>.jsonl
Schema: references/agent-log-schema.md
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "2.0.0"
EVENTS = {"SubagentStart": "start", "SubagentStop": "stop"}
_ACTOR_LINE = re.compile(r"^\s*-\s*\*\*Actor ID:\*\*\s*(.+?)\s*$", re.MULTILINE)
_ACTOR_OK = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_NAME_OK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,127}$")


def _pointer(path: Path) -> Path | None:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text or "\n" in text:
        return None
    return Path(text).expanduser()


def resolve_config_root(home: Path, environ: dict) -> Path | None:
    """Same precedence as cortex's resolver, minus the legacy default folder.

    Returns None when nothing points at a root. A logger must not create or
    guess a config root; it only writes into one that already exists.
    """
    env = (environ.get("CORTEX_CONFIG_ROOT") or "").strip()
    candidates = [Path(env).expanduser()] if env else []
    for pointer in (home / ".cortex" / "config-root", home / "Documents" / ".claude-plugin-config-root"):
        target = _pointer(pointer)
        if target is not None:
            candidates.append(target)
    default = home / "cortex-root"
    if (default / ".cortex-repos.json").is_file():
        candidates.append(default)
    for candidate in candidates:
        return candidate if candidate.is_dir() else None  # first source wins; never fall through
    return None


def actor_id(root: Path) -> str:
    try:
        m = _ACTOR_LINE.search((root / "memory" / "me" / "identity.md").read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return "unresolved"
    value = m.group(1).strip() if m else ""
    return value if _ACTOR_OK.match(value) else "unresolved"


def _clean(value: object) -> str | None:
    return value if isinstance(value, str) and _NAME_OK.match(value) else None


def build_entry(payload: dict, root: Path, now: datetime) -> dict | None:
    event = EVENTS.get(payload.get("hook_event_name"))
    agent = _clean(payload.get("agent_type"))
    if event is None or agent is None:
        return None
    return {
        "schema_version": SCHEMA_VERSION,
        "ts": now.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "event": event,
        "agent": agent,
        "agent_id": _clean(payload.get("agent_id")),
        "session_id": _clean(payload.get("session_id")),
        "actor_id": actor_id(root),
        "source": "hook",
    }


def log_path(root: Path, now: datetime) -> Path:
    return root / "plugins" / "ops" / "agent-runs" / f"{now.astimezone(timezone.utc):%Y-%m}.jsonl"


def record(payload: dict, home: Path, environ: dict, now: datetime) -> Path | None:
    root = resolve_config_root(home, environ)
    if root is None:
        return None
    entry = build_entry(payload, root, now)
    if entry is None:
        return None
    target = log_path(root, now)
    target.parent.mkdir(parents=True, exist_ok=True)
    line = (json.dumps(entry, separators=(",", ":")) + "\n").encode("utf-8")
    # One O_APPEND write per line, so concurrent agents cannot interleave entries.
    fd = os.open(target, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)
    return target


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if isinstance(payload, dict):
            record(payload, Path.home(), dict(os.environ), datetime.now(timezone.utc))
    except Exception:  # noqa: BLE001 - a logger must never break the session
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
