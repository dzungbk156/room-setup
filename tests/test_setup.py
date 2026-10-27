from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOME_MIRROR = ROOT / "home"
ROOM = HOME_MIRROR / ".config" / "codex-room"
SYNC = HOME_MIRROR / ".local" / "bin" / "codex-room-sync"
LAUNCHER = HOME_MIRROR / ".local" / "bin" / "codex-room"
INSTALL_SLP = ROOT / "scripts" / "install-slp"
CATALOG = ROOT / "tests" / "fixtures" / "model-catalog.json"
PROVIDERS = ROOT / "paseo" / "room-providers.json.template"
PROFILES = ROOT / "paseo" / "room-profiles.json"


def snapshot(root: Path) -> list[tuple[str, bytes | str]]:
    result = []
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            result.append((relative, os.readlink(path)))
        elif path.is_file():
            result.append((relative, path.read_bytes()))
    return result


class RoomContractTests(unittest.TestCase):
    def test_repository_does_not_own_operator_homes(self) -> None:
        for name in (".codex", ".claude", ".paseo"):
            self.assertFalse((HOME_MIRROR / name).exists(), name)

    def test_no_private_state_or_machine_paths_are_tracked(self) -> None:
        forbidden = {"auth.json", "daemon-keypair.json", "push-tokens.json", "server-id", "cli-client-id"}
        for path in HOME_MIRROR.rglob("*"):
            self.assertNotIn(path.name, forbidden)
            if path.is_file():
                self.assertNotIn("/Users/", path.read_text(errors="ignore"), path)

    def test_paseo_templates_give_orchestration_tools_only_to_leads(self) -> None:
        providers = json.loads(PROVIDERS.read_text())
        self.assertEqual(sorted(providers),
                         ["room-advisor", "room-lead", "room-lead-claude", "room-peer", "room-peer-minimax"])
        for name, spec in providers.items():
            self.assertEqual(spec["paseoTools"]["enabled"], name.startswith("room-lead"), name)
        profiles = json.loads(PROFILES.read_text())
        self.assertTrue(all(profile["provider"] in providers for profile in profiles))
        lead_overlay = (ROOM / "overlays" / "lead.config.toml").read_text()
        default_lead = next(p for p in profiles if p["id"] == "room-lead")
        self.assertIn(f'model = "{default_lead["model"]}"', lead_overlay)
        advisor = next(p for p in profiles if p["id"] == "room-advisor")
        self.assertEqual(providers["room-advisor"]["command"][-1], "advisor")
        self.assertIn(f'model = "{advisor["model"]}"', (ROOM / "overlays" / "advisor.config.toml").read_text())
        self.assertNotIn("room-lead-sol61", [p["id"] for p in profiles])
        self.assertNotIn("gpt-6.1-sol", [m["id"] for m in providers["room-lead"]["models"]])

    def test_role_contracts(self) -> None:
        protocol = (ROOM / "workflow" / "WORKSPACE_PROTOCOL.md").read_text()
        lead = (ROOM / "overlays" / "lead.config.toml").read_text()
        peer = (ROOM / "roles" / "peer.md").read_text()
        for capability in (
            "Human owns product goals",
            "Lead owns project framing",
            "Peer owns one bounded outcome",
            "only with verified, accepted inputs and separate write scopes",
            "Give every moving write scope one owner",
            "immutable candidate",
            "REOPEN_REQUEST",
            "DEPENDENCY_REQUEST",
            "BLOCKED",
            "explicitly accepts or rejects",
            "repeatedly polling unchanged state",
            "A review Peer starts with zero context",
            "it never performs a review",
            "Spec review. After `to-spec` and before `to-tickets`",
            "Post-review prune",
            "default Peer provider\n  `room-peer-minimax`",
        ):
            self.assertIn(capability, protocol)
        for rule in (
            "Run writable Peers in parallel only",
            "Sequence changes to shared files or interfaces",
            "At session resumption",
            "create a duplicate tracker",
            "explicitly ACCEPT or REJECT",
            "Never send a review to the scout",
            "Create every Peer through Paseo with provider `room-peer-minimax`",
            "create a Kiro Peer (provider `room-peer`) in mode `room-peer-re`",
            "Use mode `build` for\nPeers that write and mode `plan` for read-only Peers",
            "Do not use your harness's built-in subagents",
            "Do not hand the build to another Lead",
            "provider `room-advisor`",
            "you still ACCEPT or REJECT every candidate yourself",
        ):
            self.assertIn(rule, lead)
        advisor = (ROOM / "overlays" / "advisor.config.toml").read_text()
        for rule in ("Room role: Advisor.", "Read only.", "do not address Human",
                     "You do not\naccept, reject, or approve anything"):
            self.assertIn(rule, advisor)
        self.assertIn("Advisor gives Lead second opinions and reviews", protocol)
        for rule in (
            "Peer (default): provider `room-peer-minimax`",
            "notify Lead before making those changes",
            "durable evidence locations",
            "Do not spawn, manage, or coordinate other agents",
        ):
            self.assertIn(rule, peer)
        for text in (protocol, lead, peer, advisor):
            self.assertNotIn("Supervisor", text)
        self.assertNotIn("Sol Lead", lead)


class InstallSlpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name).resolve() / "home"
        codex = self.home / ".codex"
        codex.mkdir(parents=True)
        (codex / "config.toml").write_text('model = "base-model"\n')
        (codex / "auth.json").write_text("{}\n")
        (codex / "AGENTS.md").write_text("")
        (codex / "skills").mkdir()
        (codex / "plugins").mkdir()
        bins = Path(self.temporary.name) / "bin"
        bins.mkdir()
        for name in ("codex", "claude", "kiro-cli", "opencode"):
            (bins / name).write_text("#!/bin/sh\nexit 0\n")
            (bins / name).chmod(0o755)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{bins}:/usr/bin:/bin",
            "CODEX_ROOM_MODEL_CATALOG": str(CATALOG),
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def install(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["python3", str(INSTALL_SLP), *args], env=self.env,
                              capture_output=True, text=True, check=True)

    def test_dry_run_writes_nothing(self) -> None:
        before = snapshot(self.home)
        out = self.install().stdout
        self.assertIn("would write  ~/.local/bin/room-digest", out)
        self.assertEqual(snapshot(self.home), before)

    def test_apply_installs_room_and_is_repeatable(self) -> None:
        codex_before = snapshot(self.home / ".codex")
        self.install("--apply")
        for rel in (".local/bin/codex-room", ".local/bin/codex-room-sync", ".local/bin/claude-room",
                    ".local/bin/room-digest"):
            self.assertTrue(os.access(self.home / rel, os.X_OK), rel)
        peer = json.loads((self.home / ".kiro/agents/room-peer.json").read_text())
        self.assertEqual(peer["prompt"], f"file://{self.home}/.config/codex-room/roles/peer.md")
        config = json.loads((self.home / ".paseo/config.json").read_text())
        providers = config["agents"]["providers"]
        self.assertTrue(providers["room-lead"]["paseoTools"]["enabled"])
        self.assertFalse(providers["codex"]["paseoTools"]["enabled"])
        self.assertTrue(providers["room-peer"]["command"][0].endswith("/kiro-cli"))
        runtime = (self.home / ".codex-runtime/lead/config.toml").read_text()
        self.assertIn('model = "gpt-6-astra"', runtime)
        self.assertIn("multi_agent = false", runtime)
        advisor_runtime = (self.home / ".codex-runtime/advisor/config.toml").read_text()
        self.assertIn('model = "gpt-6.1-sol"', advisor_runtime)
        self.assertIn("Room role: Advisor.", advisor_runtime)
        profile_ids = [p["id"] for p in config["daemon"]["agentProfiles"]]
        self.assertIn("room-advisor", profile_ids)
        self.assertNotIn("room-lead-sol61", profile_ids)
        self.assertFalse(providers["room-advisor"]["paseoTools"]["enabled"])
        self.assertEqual(snapshot(self.home / ".codex"), codex_before)

        second = self.install("--apply").stdout
        self.assertNotIn("write  ", second.replace("unchanged", ""))

    def test_hand_edited_file_is_kept_unless_forced(self) -> None:
        self.install("--apply")
        peer_role = self.home / ".config/codex-room/roles/peer.md"
        peer_role.write_text("my edit\n")
        self.assertIn("DRIFTED", self.install("--apply").stdout)
        self.assertEqual(peer_role.read_text(), "my edit\n")
        self.install("--apply", "--force")
        self.assertEqual(peer_role.read_text(), (ROOM / "roles/peer.md").read_text())

    def test_missing_codex_files_stop_before_writing(self) -> None:
        (self.home / ".codex/auth.json").unlink()
        completed = subprocess.run(["python3", str(INSTALL_SLP), "--apply"], env=self.env,
                                   capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("auth.json", completed.stderr)
        self.assertFalse((self.home / ".config").exists())


class LeadRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.canonical = self.root / "canonical"
        self.canonical.mkdir()
        (self.canonical / "config.toml").write_text(
            'model = "base-model"\nsandbox_mode = "read-only"\n\n'
            '[mcp_servers.example]\nurl = "https://example.invalid/mcp"\n\n'
            '[features]\nmulti_agent = true\nmulti_agent_v2 = true\n\n[agents]\nenabled = true\n'
        )
        for overlay in ("lead.config.toml", "advisor.config.toml"):
            (self.canonical / overlay).write_text((ROOM / "overlays" / overlay).read_text())
        for name in ("auth.json", "AGENTS.md", "hooks.json", "model-instructions.md"):
            (self.canonical / name).write_text("{}\n" if name.endswith(".json") else "fixture\n")
        for name in ("skills", "plugins"):
            (self.canonical / name).mkdir()
        self.env = {**os.environ, "CODEX_ROOM_LAB_ROOT": str(self.root), "CODEX_ROOM_MODEL_CATALOG": str(CATALOG)}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def sync(self, role: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["python3", str(SYNC), role], env=self.env, capture_output=True, text=True)

    def test_lead_runtime_is_isolated_and_disables_native_agents(self) -> None:
        self.assertEqual(self.sync("lead").returncode, 0)
        runtime = self.root / ".runtime" / "lead"
        config = (runtime / "config.toml").read_text()
        self.assertIn('model = "gpt-6-astra"', config)
        self.assertIn("multi_agent = false", config)
        self.assertIn("multi_agent_v2 = false", config)
        self.assertIn("[agents]\nenabled = false", config)
        self.assertIn("[mcp_servers.example]", config)
        self.assertIn("Room role: Lead.", config)
        for name in ("auth.json", "AGENTS.md", "hooks.json", "skills", "plugins", "model-instructions.md"):
            self.assertEqual((runtime / name).resolve(), (self.canonical / name).resolve())
        catalog = json.loads((runtime / "model-catalog.no-native-agents.json").read_text())
        self.assertTrue(all(model["multi_agent_version"] is None for model in catalog["models"]))
        first = (runtime / "config.toml").read_bytes()
        self.assertEqual(self.sync("lead").returncode, 0)
        self.assertEqual((runtime / "config.toml").read_bytes(), first)

    def test_advisor_runtime_is_separate_from_the_lead(self) -> None:
        self.assertEqual(self.sync("advisor").returncode, 0)
        config = (self.root / ".runtime" / "advisor" / "config.toml").read_text()
        self.assertIn('model = "gpt-6.1-sol"', config)
        self.assertIn("Room role: Advisor.", config)
        self.assertNotIn("Room role: Lead.", config)
        self.assertIn("[agents]\nenabled = false", config)

    def test_only_the_lead_and_advisor_roles_exist(self) -> None:
        for role in ("supervisor", "peer", "review"):
            with self.subTest(role=role):
                self.assertIn("usage:", self.sync(role).stderr)
                launched = subprocess.run([str(LAUNCHER), role], env=self.env, capture_output=True, text=True)
                self.assertEqual(launched.returncode, 2)
                self.assertIn("unknown role", launched.stderr)
        self.assertFalse((self.root / ".runtime").exists())

    def test_symlinked_runtime_is_refused_before_codex_starts(self) -> None:
        redirected = self.root / "redirected"
        redirected.mkdir()
        (self.root / ".runtime").mkdir()
        (self.root / ".runtime" / "lead").symlink_to(redirected, target_is_directory=True)
        marker = self.root / "codex-was-launched"
        fake_codex = self.root / "fake-codex"
        fake_codex.write_text(f"#!/bin/sh\ntouch '{marker}'\n")
        fake_codex.chmod(0o755)
        launched = subprocess.run([str(LAUNCHER), "lead"], env={**self.env, "CODEX_BIN": str(fake_codex)},
                                  capture_output=True, text=True)
        self.assertEqual(launched.returncode, 2)
        self.assertIn("must not be a symlink", launched.stderr)
        self.assertFalse(marker.exists())
        self.assertEqual(list(redirected.iterdir()), [])


class RoomDigestTests(unittest.TestCase):
    DIGEST = HOME_MIRROR / ".local" / "bin" / "room-digest"
    CLAUDE_ROOM = HOME_MIRROR / ".local" / "bin" / "claude-room"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name).resolve()
        self.project = root / "project"
        issues = self.project / ".scratch" / "feat" / "issues"
        issues.mkdir(parents=True)
        (self.project / "docs" / "agents").mkdir(parents=True)
        (self.project / "docs" / "agents" / "issue-tracker.md").write_text("# Issue tracker\n")
        (issues / "01-open.md").write_text("# 01 Open work\n\nStatus: ready-for-agent\n")
        (issues / "02-blocked.md").write_text("# 02 Blocked work\n\nStatus: needs-triage\nBlocked by: 01-open.md\n")
        (issues / "03-done.md").write_text("# 03 Finished work\n\nStatus: done\n")
        self.paseo = root / "paseo"
        store = self.paseo / "agents" / "ws"
        store.mkdir(parents=True)
        lead, gone = "a" * 36, "f" * 36

        def agent(agent_id: str, **fields: object) -> None:
            record = {"id": agent_id, "lastStatus": "idle", "lastActivityAt": "2026-10-26T10:00:00.000Z", **fields}
            (store / f"{agent_id}.json").write_text(json.dumps(record))

        agent(lead, provider="room-lead-claude", cwd=str(self.project), title="the lead", labels={})
        agent("b" * 36, provider="room-peer-minimax", cwd=str(root / "worktree"), title="labelled peer",
              labels={"paseo.parent-agent-id": lead, "room.ticket": ".scratch/feat/issues/01-open.md",
                      "room.scope": "src/", "room.branch": "feat/01"})
        agent("9" * 36, provider="room-advisor", cwd=str(self.project), title="the advisor",
              labels={"paseo.parent-agent-id": lead, "room.ticket": "none", "room.scope": "advisor"})
        agent("c" * 36, provider="room-peer", cwd=str(self.project), title="orphan peer",
              labels={"paseo.parent-agent-id": gone})
        agent("d" * 36, provider="room-peer", cwd=str(self.project), title="archived peer",
              archivedAt="2026-10-25T10:00:00.000Z", labels={})
        agent("e" * 36, provider="room-peer", cwd=str(root / "elsewhere"), title="unrelated peer", labels={})
        self.env = {**os.environ, "PASEO_HOME": str(self.paseo)}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_digest_lists_open_tickets_and_the_peer_ledger(self) -> None:
        completed = subprocess.run([str(self.DIGEST), str(self.project)], env=self.env,
                                   capture_output=True, text=True, check=True)
        out = completed.stdout
        self.assertIn(".scratch/feat/issues/01-open.md  [ready-for-agent]  01 Open work", out)
        self.assertIn("(blocked by: 01-open.md)", out)
        self.assertNotIn("03-done.md", out)
        self.assertIn("aaaaaaa room-lead-claude", out)
        self.assertIn("Advisors:\n- 9999999 room-advisor", out)
        self.assertNotIn("Leads are not archived", out)
        self.assertIn("ticket=.scratch/feat/issues/01-open.md scope=src/ branch=feat/01 lead=aaaaaaa", out)
        self.assertIn("lead=fffffff(missing)", out)
        self.assertIn("Peer ccccccc has no room.ticket label", out)
        self.assertIn("Peer ccccccc has no live Lead", out)
        self.assertNotIn("Peer bbbbbbb has", out)
        self.assertNotIn("archived peer", out)
        self.assertNotIn("unrelated peer", out)

    def test_digest_fails_soft_without_a_paseo_store(self) -> None:
        env = {**self.env, "PASEO_HOME": str(Path(self.temporary.name) / "absent")}
        completed = subprocess.run([str(self.DIGEST), str(self.project)], env=env,
                                   capture_output=True, text=True, check=True)
        self.assertIn("Paseo agent store not readable", completed.stdout)
        self.assertIn("01-open.md", completed.stdout)

    def test_claude_lead_session_context_includes_the_digest(self) -> None:
        completed = subprocess.run([str(self.CLAUDE_ROOM), "--session-context", "lead"], cwd=self.project,
                                   env={**self.env, "CODEX_ROOM_CONFIG_HOME": str(ROOM)},
                                   capture_output=True, text=True, check=True)
        context = json.loads(completed.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Room role: Lead.", context)
        self.assertIn(f"ROOM DIGEST for {self.project}", context)
        self.assertIn("01-open.md", context)

    def test_installer_and_lead_contract_ship_the_digest_and_ledger(self) -> None:
        self.assertIn('(".local/bin/room-digest", None, False, True)', (ROOT / "scripts" / "install-slp").read_text())
        lead = (ROOM / "overlays" / "lead.config.toml").read_text()
        for rule in ("`room-digest <project>`", "`room.ticket`", "`room.scope`", "`room.branch`",
                     "adopt the listed Peers", "`notifyOnFinish`"):
            self.assertIn(rule, lead)




if __name__ == "__main__":
    unittest.main()
