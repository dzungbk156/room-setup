# Room Setup

Configuration for an agent "room" that runs inside [Paseo](https://github.com/getpaseo/paseo):
one **Lead** agent frames the work and accepts results, and short-lived **Peer**
agents each own one bounded task. Human keeps product, cost, external-effect,
and irreversible decisions.

The repository has two layers:

| Layer | Installer | What it sets up |
| --- | --- | --- |
| Multi-provider room (current) | `scripts/install-slp` | Lead on Codex or Claude Code, Peers on Kiro CLI or OpenCode, as Paseo providers and agent profiles |
| Core room | `./install` | Builds the pinned Paseo release and the original three-role Codex room (`codex-supervisor`, `codex-lead`, `codex-peer`) |

Most users want the multi-provider room. The core installer is only needed if
you also want this repo to build Paseo from source.

## Multi-provider room

```text
Paseo
  ├─ room-lead          Codex (gpt-6-astra or gpt-6.1-sol) via codex-room lead
  ├─ room-lead-claude   Claude Code (claude-opus-5-5) via claude-room lead
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
| Lead (Astra) | `room-lead` | `gpt-6-astra` | Default Codex Lead |
| Lead (Sol 6.1) | `room-lead` | `gpt-6.1-sol` | Build phase: dispatch, acceptance, review |
| Lead (Opus) | `room-lead-claude` | `claude-opus-5-5` | Thinking with Human: grilling, specs, tickets |
| Peer (MiniMax) | `room-peer-minimax` | MiniMax M3.1 Flash | Every Peer by default |
| Peer | `room-peer` | `claude-opus-4.5` | Only when Human asks |
| Peer (REA) | `room-peer` (mode `room-peer-re`) | `claude-opus-4.5` | Reverse engineering only |

Start one Lead per project from the Paseo app. The Lead creates Peers itself.

At session start the Lead reads `room-digest` for its project: git state, open
`.scratch` tickets, and the room's Leads and Peers. The Claude Lead gets it in
its session context; the Codex Lead runs it first. The Lead labels each Peer
with `room.ticket`, `room.scope`, and `room.branch`, so the digest shows who
owns what after a restart or a Lead handoff. The digest reads Paseo's on-disk
agent records (`~/.paseo/agents`), which is Paseo's internal format; recheck
it after a Paseo upgrade.
Role rules live in `home/.config/codex-room/overlays/lead.config.toml` (shared by
both Lead seats), `home/.config/codex-room/roles/peer.md`, and the shared
contract `home/.config/codex-room/workflow/WORKSPACE_PROTOCOL.md`.

### Prerequisites

- macOS (Linux is untested for this layer), Python 3.11+, `jq` at `/usr/bin/jq`.
- Paseo app installed and running (official release, or `./install` below).
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

### Install

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

### Uninstall

There is no uninstaller for this layer yet. Remove the `room-*` entries from
`agents.providers` and `daemon.agentProfiles` in `~/.paseo/config.json` (or
restore it from the latest `~/.codex-room-backups/slp-*`), then delete the files
listed above.

## Core room and Paseo build

The rest of this document covers `./install`, which builds Paseo and the
original three-role Codex room:

```text
Paseo provider
  -> codex-room <supervisor|lead|peer>
  -> codex-room-sync
  -> isolated ~/.codex-runtime/<role>
  -> Codex app-server
```

This layer deliberately does **not** own `~/.codex`. Each operator installs and
authenticates Codex independently. The sync script reads the operator's existing
`~/.codex/config.toml` as its base and shares their auth, skills, plugins, and
global `AGENTS.md` by symlink. Hooks are shared only when `hooks.json` exists.

### What gets installed

The `home/` directory mirrors `$HOME`:

| Repository source | Local destination |
| --- | --- |
| `home/.config/codex-room/` | `~/.config/codex-room/` |
| `home/.local/bin/codex-room*` | `~/.local/bin/` |
| `home/.paseo/config.json.template` | `~/.paseo/config.json` |

The public installer creates this checkout-aware symlink:

```text
~/.local/bin/paseo
  -> ~/projects/supervisors/paseo/packages/cli/bin/paseo
```

`@@HOME@@` placeholders are rendered during installation. Runtime databases, sessions, logs, auth files, keypairs, tokens, worktrees, and backups are never installed from or exported into Git.

### Install

Prerequisites:

- macOS or another Unix-like environment with Bash, Python 3.11 or newer,
  Git, Node 22, npm, and jq.
- Codex CLI installed and authenticated, with an existing `~/.codex/config.toml`,
  `auth.json`, `AGENTS.md`, `skills/`, and `plugins/` available for runtime
  sharing. `hooks.json` is optional: an existing file is shared, while an
  absent file is skipped without creating anything in the operator home.
- `~/.local/bin` on `PATH`.

```bash
git clone https://github.com/dzungbk156/room-setup.git room-setup
cd room-setup

./install                         # read-only plan and prerequisite check
./install --apply                 # transactional Paseo/config/runtime install
./install --verify                # installed checks plus live provider inventory
```

The root command preflights the pinned Paseo checkout, installs dependencies,
builds the Paseo server/CLI bundles, renders managed HOME files, stages all
three role runtimes, and publishes the complete transition with rollback on a
dependency, build, generation, or final verification failure. It does not
install or authenticate Codex, touch `~/.codex`, start a daemon, or build
Paseo Desktop. Start and reach the local provider daemon explicitly before
live verification:

```bash
paseo daemon start
paseo daemon status
./install --verify
```

`./install --verify` is read-only and fails when the live Paseo provider
inventory cannot be reached. Use `scripts/verify` for an installed-only
diagnostic while the daemon is stopped. Repeating `./install --apply` is the
upgrade path: it regenerates the three managed runtimes, preserves operator
Codex files and existing runtime/session data, and retires only recognized,
unchanged legacy artifacts.

### Disposable container acceptance test

With Docker available, one command exercises the public installer twice against
a fresh, fake operator home:

```bash
make test-container
```

The test uses a digest-pinned Node 22 base with Debian's Python 3.11, mounts
this checkout read-only, and supplies `tests/fixtures/model-catalog.json` so it
does not need Codex API authentication. It downloads the pinned Paseo source
and npm dependencies (excluding untested Electron/Playwright GUI binaries),
but never mounts or copies the host's `~/.codex`, auth,
sessions, plugins, or other operator data. A successful run prints the exact
Codex role inventory, Paseo MCP recipients, runtime tree, and
`CONTAINER_ACCEPTANCE_OK`.

This Linux container checks installer topology, legacy-role rejection,
repeatability, preservation, and real Paseo daemon startup with a provider RPC.
Authenticated Codex sessions, Paseo Desktop/GUI behavior, and macOS
signing/TCC/application restart remain operator checks.

The Paseo source manifest pins official stable release **v0.8.0** and its immutable commit.
It never installs a daily main build or beta. See [release selection and fork migration](docs/paseo-release.md). The public installer
preflights Paseo in a disposable location before changing live state. Paseo uses
`npm ci` and refuses custom Git hooks because its audited `prepare` lifecycle
installs lefthook. The public transaction makes the audited tag authoritative for
a clean checkout on the configured branch and official origin, including when
the checkout is ahead or divergent; the standalone helper remains
fast-forward-only. Fork checkouts and other remote layouts are refused.

The installer backs up every replaced managed file and the Paseo checkout under
`~/.codex-room-backups/core3-<UTC timestamp>-<pid>-<nanoseconds>/` with
owner-only permissions. The coordinator owns the CLI-link backup as part of
the same transaction; the delegated Paseo helper does not create a second
backup. Customized obsolete files are preserved with a warning; only
recognized, unchanged legacy artifacts are retired after backup.

If `Ctrl-C` or `SIGTERM` arrives during apply, the installer settles its
owned helper process group and rolls back the published state. A power loss or
`SIGKILL` can interrupt before rollback and remains an operating-system
durability limit; inspect the restricted transaction backup before retrying.

It never writes to `~/.codex`.

### Paseo Desktop

After the stable checkout exists at `~/projects/supervisors/paseo`:

```bash
paseo daemon start
paseo daemon status
paseo-local-update
```

That command validates provenance and hook/lock safety, advances only to the
audited commit, runs `npm ci`, builds and ad-hoc signs the local Desktop app,
backs up the prior `/Applications/Paseo.app`, installs the new build, and
restarts Paseo.

### Roles

| Role | Default model | Reasoning | Paseo MCP injection |
| --- | --- | --- | --- |
| Supervisor | `gpt-5.6-sol` | medium | yes |
| Lead | `gpt-6-astra` | medium | yes |
| Peer | `gpt-5.6-sol` | medium | no |

The Lead overlay is shared with the multi-provider room, so its model and
instructions follow that layer.

Human retains product, cost, external-effect, and irreversible-risk decisions.
Supervisor routes Human intent and bounded recovery. Lead owns technical
framing, dependency order, verification, and explicit candidate acceptance.
Peer owns one bounded outcome and returns an immutable candidate or a concrete
block signal. Lead may request a fresh read-only Peer review when independent
judgment can change a technical decision. All role overlays currently request
`danger-full-access` with `approval_policy = "never"`. Read
[docs/architecture.md](docs/architecture.md) before changing these boundaries.

### Common operations

```bash
# Lower-level maintenance: regenerate all role runtimes after changing an overlay
./scripts/sync-all

# Validate source only, without requiring installed runtimes
./scripts/verify --source

# Verify installed state and the live Paseo provider inventory
./install --verify

# Optional sanitized runtime summaries for local comparison
./scripts/export-runtime-snapshots

```

The lower-level scripts are maintenance interfaces used by the public
lifecycle and are not alternate fresh-install commands. See
[docs/operations.md](docs/operations.md) for scope-owned parallel work and handoff,
candidate acceptance, and maintenance runbooks.

Official Codex configuration precedence is documented by OpenAI in the [Codex config basics](https://learn.chatgpt.com/docs/config-file/config-basic.md). `codex-room` uses a separate `CODEX_HOME` per role; this is a local orchestration layer, not a replacement for the operator's Codex installation.
