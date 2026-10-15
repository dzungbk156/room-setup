# Paseo stable release

`./install --apply` owns the Paseo checkout and Room configuration transition.
The authoritative source is [`paseo/source.toml`](../paseo/source.toml):

- Official repository: `https://github.com/getpaseo/paseo.git`.
- Stable release: [`v0.8.0`](https://github.com/getpaseo/paseo/releases/tag/v0.8.0), published 2026-09-10, not a draft or prerelease.
- Commit: `b8e24677e12b226c7c38c1c3a40649daa9f1152f`.
- Checkout: `~/projects/supervisors/paseo`, local branch `main`, only remote `origin`.

## Release selection

The installer fetches the named release tag and verifies its peeled commit against
the pin. Both lightweight and annotated tags are supported. Beta/prerelease names,
missing tags, and changed tag targets are refused before dependency installation.
The fetched object is checked again to catch a tag moving after the remote lookup.

The local branch retains normal origin/main tracking, but install/update commands
never pull or select the head of main. A newer main or a newer beta does not change
the installed version. A newer stable release is adopted deliberately by updating
the manifest and the installed updater template together, then validating it.

## Installation and migration

A fresh install builds in a sibling staging directory before publication. It runs
`npm ci` and `npm run build:server:clean`, requires both CLI and daemon bundles,
and smoke-tests `paseo --help`. Custom hooks/core.hooksPath and lockfile mutation
are refused. The public coordinator snapshots the checkout and CLI link before
publishing; dependency/build/runtime/final-verification failures restore that snapshot.

Existing official checkouts must be clean, on the expected branch, and use only
the configured official `origin`. The public transaction backs up the checkout
and makes the audited tag authoritative even when the current commit is ahead or
divergent. The standalone helper accepts only the exact pin or an ancestor of it,
so a history replacement cannot occur without the coordinator's backup and
rollback boundary. Untracked operator state is preserved.

Fork checkouts and custom remote layouts are refused; re-clone from the
official source instead.

The install does not restart a running daemon or replace Desktop. After reviewing
and applying, restart/reload Paseo when existing agent work has finished. New or
reloaded sessions receive the new tool policy; an already-running session keeps
its launch-time tools. Run `./install --verify` against the restarted daemon.

## Provider tools

Keep `daemon.mcp.enabled` and `daemon.mcp.injectIntoAgents` true. Configure
`agents.providers.<id>.paseoTools.enabled` true for Supervisor/Lead and false for
Peer and every other known provider. The old `injectIntoProviders` field is removed.

This gates both MCP and native Paseo tools. Peer receives neither catalog. Model,
thinking, command, and runtime settings are retained. `disabledTools` is available
for partial restrictions, but is unnecessary for this all-or-nothing split.

Upstream defaults to enabled for an unspecified provider and does not inherit this
policy through `extends`. Add an explicit policy whenever adding a provider.
`scripts/verify` and `scripts/export-current` reject missing policies or unexpected
recipients. Voice-only `speak` is separate; voice is disabled in this setup.
This controls tool delivery, not what an agent with shell access can discover.

## Desktop

`scripts/update-paseo` delegates to the installed `paseo-local-update`. It checks
the same stable tag/commit, builds and signs Desktop, backs up the previous app,
and restarts Paseo. See
[`paseo/notes/desktop-build.md`](../paseo/notes/desktop-build.md).

Official Paseo requires a bearer token for every client when the daemon has a
password. The Room template does not configure a password; check Desktop/CLI
connectivity if the daemon receives one through other settings.
