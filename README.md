# Room Setup

Configuration for an agent "room" that runs inside [Paseo](https://github.com/getpaseo/paseo):
one **Lead** agent frames the work and accepts results, an **Advisor** gives the
Lead second opinions and reviews, and short-lived **Peer** agents each own one
bounded task. Human keeps product, cost, external-effect, and irreversible
decisions.

## Layout

```text
Paseo
  ├─ room-lead-claude   Claude Code (claude-opus-5-5) via claude-room lead
  ├─ room-lead          Codex (gpt-6-astra) via codex-room lead
  ├─ room-advisor       Codex (gpt-6.1-sol) via codex-room advisor
  ├─ room-peer-minimax  OpenCode (MiniMax M3.1 Flash), default Peer
  └─ room-peer          Kiro CLI (claude-opus-4.5), modes room-peer / room-peer-re
```

Only the Lead providers get Paseo's orchestration tools (create/message/archive
agents). Peers get none. Paseo gives these tools to any provider without an
explicit policy, so the installer sets `paseoTools.enabled = false` on every
other provider: the built-ins (`claude`, `codex`, `opencode`, `kiro`, ...) and
any custom providers already in your config.

| Profile | Provider | Model | Use |
| --- | --- | --- | --- |
| Lead (Opus) | `room-lead-claude` | `claude-opus-5-5` | The Lead Human works with: grilling, specs, tickets, build, acceptance |
| Lead (Astra) | `room-lead` | `gpt-6-astra` | Codex Lead, when Human starts one instead |
| Advisor (Sol 6.1) | `room-advisor` | `gpt-6.1-sol` | Second opinions and reviews for the Lead; reads only |
| Peer (MiniMax) | `room-peer-minimax` | MiniMax M3.1 Flash | Every Peer by default |
| Peer | `room-peer` | `claude-opus-4.5` | Only when Human asks |
| Peer (REA) | `room-peer` (mode `room-peer-re`) | `claude-opus-4.5` | Reverse engineering only |

Start one Lead per project from the Paseo app. The Lead creates Peers and the
Advisor itself. The Advisor has no orchestration tools and its role forbids
writes; Paseo's Codex modes have no read-only option, so it runs in
`full-access` and the read-only limit is a role rule, not a sandbox.

At session start the Lead reads `room-digest` for its project: git state, open
`.scratch` tickets, and the room's Leads, Advisors, and Peers. The Claude Lead gets it in
its session context; the Codex Lead runs it first. The Lead labels each Peer
with `room.ticket`, `room.scope`, and `room.branch`, so the digest shows who
owns what after a restart or a Lead handoff. The digest reads Paseo's on-disk
agent records (`~/.paseo/agents`), which is Paseo's internal format; recheck
it after a Paseo upgrade.
Role rules live in `home/.config/codex-room/overlays/lead.config.toml` (shared by
both Lead seats), `home/.config/codex-room/overlays/advisor.config.toml`,
`home/.config/codex-room/roles/peer.md`, and the shared
contract `home/.config/codex-room/workflow/WORKSPACE_PROTOCOL.md`.

## Prerequisites

- macOS (Linux is untested), Python 3.11+, `jq` at `/usr/bin/jq`.
- Paseo app installed and running (official release from [paseo.sh](https://paseo.sh)).
  The app bundles the CLI at `/Applications/Paseo.app/Contents/Resources/bin/paseo`
  but does not put it on `PATH`; add it, or use that full path below.
- Each agent CLI installed **and logged in** with your own account:
  - `codex` logged in (`codex login`) with access to the `gpt-6-astra` /
    `gpt-6.1-sol` models. The installer needs `config.toml`, `auth.json`,
    `AGENTS.md`, `skills/`, and `plugins/` in `~/.codex` and stops before
    writing anything if one is missing; an empty `AGENTS.md` or directory is fine.
  - `claude` (Claude Code) logged in to a Claude subscription. `claude-room`
    unsets `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` on purpose.
  - `opencode` logged in to the MiniMax coding plan, for the default MiniMax Peer.
  - `kiro-cli` on `PATH` with access to `claude-opus-4.5`, for the Kiro and REA
    Peers. The installer records that path in the Paseo provider; re-run it if
    Kiro moves.
- Optional skills the room refers to by name. Missing skills are skipped by the
  agents, but the workflow assumes them:
  - Lead: [mattpocock/skills](https://github.com/mattpocock/skills)
    (`grill-with-docs`, `to-spec`, `to-tickets`, `implement-spec`, ...),
    `humanizer`, `browser-skill`, and the Paseo skills, in `~/.claude/skills`
    or `~/.agents/skills`.
  - Peers: `~/.kiro/skills/browser-skill/SKILL.md`; the REA Peer also needs
    `~/.claude/skills/reverse-engineer-anything/SKILL.md` and Node from
    `~/.local/opt/node24/bin` or Homebrew for `npx rea-agents`.

## Install

```bash
git clone https://github.com/dzungbk156/room-setup.git room-setup
cd room-setup

scripts/install-slp            # dry run: prints every file and Paseo config change
scripts/install-slp --apply    # writes files, backs up what it replaces
paseo restart                  # or quit and reopen the Paseo app
```

`install-slp` writes:

- `~/.config/codex-room/` (Lead overlay, Peer role, workspace protocol,
  `PONYTAIL.md`, OpenCode Peer config)
- `~/.local/bin/codex-room`, `codex-room-sync`, `claude-room`, `room-digest`
- `~/.kiro/agents/room-peer.json`, `room-peer-re.json`
- the room providers and agent profiles in `~/.paseo/config.json`, merged into
  your existing config, `paseoTools.enabled = false` on non-room providers, and
  `daemon.mcp.enabled/injectIntoAgents = true`
- `~/.codex-runtime/lead/`, generated by `codex-room-sync lead`

It never touches `~/.codex`, `~/.claude`, or Kiro auth. Every replaced file is
copied to `~/.codex-room-backups/slp-<timestamp>/` first. A hash manifest at
`~/.config/codex-room/.install-slp-manifest.json` detects installed files you
edited by hand; those are skipped unless you pass `--force`. Re-running the
script is the upgrade path; it also removes the retired `room-supervisor`
provider, profile, and role file from earlier versions.

**All seats run without permission prompts** (Codex `danger-full-access` +
`approval_policy = "never"`, Claude `bypassPermissions`, Kiro
`--trust-all-tools`, OpenCode `allow`). Only use the room on machines and
repositories where that is acceptable.

## Uninstall

There is no uninstaller yet. Remove the `room-*` entries from
`agents.providers` and `daemon.agentProfiles` in `~/.paseo/config.json` (or
restore it from the latest `~/.codex-room-backups/slp-*`), then delete the files
listed above.

## Development

```bash
python3 -m unittest discover -s tests
```

The tests use a fake `$HOME` and fake agent CLIs; they never touch your real
`~/.codex`, `~/.claude`, or `~/.paseo`.

`codex-room lead` regenerates the Codex Lead runtime in `~/.codex-runtime/lead`
from your `~/.codex/config.toml` plus `overlays/lead.config.toml` on every
launch, with Codex's native multi-agent features turned off. Edit the overlay,
then re-run `scripts/install-slp --apply`.
