from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "hooks"))

import log_agent_run as lar  # noqa: E402

NOW = datetime(2026, 11, 16, 15, 4, 5, tzinfo=timezone.utc)
STOP = {"hook_event_name": "SubagentStop", "agent_type": "cortex:verifier", "agent_id": "agent-123",
        "session_id": "sess-9", "last_assistant_message": "SECRET REPLY about Northwind",
        "transcript_path": "/Users/someone/private/path.jsonl", "cwd": "/Users/someone/work"}


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name) / "home"
        self.root = Path(self._tmp.name) / "root"
        (self.home / ".cortex").mkdir(parents=True)
        (self.root / "memory" / "me").mkdir(parents=True)
        (self.root / "memory" / "me" / "identity.md").write_text("## Person\n- **Actor ID:** sample-user\n- **Name:** Sample User\n", encoding="utf-8")
        (self.home / ".cortex" / "config-root").write_text(str(self.root) + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def lines(self) -> list[dict]:
        f = lar.log_path(self.root, NOW)
        return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()] if f.is_file() else []


class Recording(Base):
    def test_stop_event_is_recorded_with_metadata_only(self) -> None:
        target = lar.record(STOP, self.home, {}, NOW)
        self.assertEqual(target, self.root / "plugins" / "ops" / "agent-runs" / "2026-11.jsonl")
        self.assertEqual(self.lines(), [{"schema_version": "2.0.0", "ts": "2026-11-16T15:04:05Z", "event": "stop",
                                         "agent": "cortex:verifier", "agent_id": "agent-123", "session_id": "sess-9",
                                         "actor_id": "sample-user", "source": "hook"}])
        raw = target.read_text(encoding="utf-8")
        for secret in ("SECRET", "Northwind", "/Users/someone", "Sample User"):
            self.assertNotIn(secret, raw)

    def test_start_and_stop_append_in_order(self) -> None:
        lar.record({**STOP, "hook_event_name": "SubagentStart"}, self.home, {}, NOW)
        lar.record(STOP, self.home, {}, NOW)
        self.assertEqual([x["event"] for x in self.lines()], ["start", "stop"])

    def test_env_var_wins_over_pointer(self) -> None:
        other = Path(self._tmp.name) / "other"
        other.mkdir()
        target = lar.record(STOP, self.home, {"CORTEX_CONFIG_ROOT": str(other)}, NOW)
        self.assertTrue(str(target).startswith(str(other)))
        self.assertEqual(self.lines(), [])

    def test_unresolved_or_unreachable_root_writes_nothing(self) -> None:
        empty_home = Path(self._tmp.name) / "empty"
        empty_home.mkdir()
        self.assertIsNone(lar.record(STOP, empty_home, {}, NOW))
        self.assertIsNone(lar.record(STOP, self.home, {"CORTEX_CONFIG_ROOT": str(Path(self._tmp.name) / "missing")}, NOW))
        self.assertFalse((Path(self._tmp.name) / "missing").exists())
        self.assertEqual(self.lines(), [])

    def test_a_dead_first_source_does_not_fall_through_to_another_root(self) -> None:
        # The env var names a missing folder; the pointer names a real one. Do not write to the real one.
        self.assertIsNone(lar.record(STOP, self.home, {"CORTEX_CONFIG_ROOT": "/nonexistent/x"}, NOW))
        self.assertEqual(self.lines(), [])

    def test_no_identity_is_recorded_as_unresolved(self) -> None:
        (self.root / "memory" / "me" / "identity.md").unlink()
        lar.record(STOP, self.home, {}, NOW)
        self.assertEqual(self.lines()[0]["actor_id"], "unresolved")

    def test_other_events_and_bad_agent_names_are_ignored(self) -> None:
        for payload in ({**STOP, "hook_event_name": "Stop"}, {**STOP, "agent_type": "has spaces and\nnewline"},
                        {**STOP, "agent_type": None}, {"hook_event_name": "SubagentStop"}):
            self.assertIsNone(lar.record(payload, self.home, {}, NOW))
        self.assertEqual(self.lines(), [])

    def test_odd_ids_are_dropped_not_written(self) -> None:
        lar.record({**STOP, "agent_id": "x y\n{inject}", "session_id": 42}, self.home, {}, NOW)
        entry = self.lines()[0]
        self.assertIsNone(entry["agent_id"])
        self.assertIsNone(entry["session_id"])


class Cli(Base):
    def run_hook(self, stdin: str, env_root: str | None = None) -> subprocess.CompletedProcess:
        env = {"HOME": str(self.home), "PATH": "/usr/bin:/bin"}
        if env_root:
            env["CORTEX_CONFIG_ROOT"] = env_root
        return subprocess.run([sys.executable, str(REPO / "hooks" / "log_agent_run.py")], input=stdin,
                              capture_output=True, text=True, env=env)

    def test_always_silent_and_exit_zero(self) -> None:
        for stdin in (json.dumps(STOP), "not json", "", "[1,2,3]", json.dumps({"hook_event_name": "SubagentStop"})):
            out = self.run_hook(stdin)
            self.assertEqual((out.returncode, out.stdout, out.stderr), (0, "", ""), stdin[:20])

    def test_end_to_end_writes_one_line(self) -> None:
        self.run_hook(json.dumps(STOP))
        files = list((self.root / "plugins" / "ops" / "agent-runs").glob("*.jsonl"))
        self.assertEqual(len(files), 1)
        self.assertEqual(json.loads(files[0].read_text(encoding="utf-8"))["agent"], "cortex:verifier")

    def test_hooks_json_is_valid_and_non_blocking(self) -> None:
        cfg = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(set(cfg["hooks"]), {"SubagentStart", "SubagentStop"})
        for event in cfg["hooks"].values():
            hook = event[0]["hooks"][0]
            self.assertTrue(hook["async"])
            self.assertIn("exit 0", hook["command"])
            self.assertIn(">/dev/null 2>&1", hook["command"])


if __name__ == "__main__":
    unittest.main()
