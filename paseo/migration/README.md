# Initial survey: fork vs. upstream (2026-09-15)

> This records the survey done before the migration. The current configuration
> and process have moved to **stable v0.8.0**, not the main-branch tip surveyed
> below. See the [current release guide](../../docs/paseo-release.md).

## Conclusion

The fork's per-provider MCP extension can be replaced by the official
`agents.providers.<id>.paseoTools` feature. The current role split does not need
a list of forbidden tools: set `enabled: false` on every provider other than
Supervisor and Lead.

This was a survey plus a candidate config. It did not change the origin,
checkout, installer, running config, or restart the daemon.

## Revisions compared

- Checkout `~/projects/supervisors/paseo`: branch `main`, origin
  `git@github.com:example/paseo-fork.git`, upstream `git@github.com:getpaseo/paseo.git`.
- HEAD and origin/main after fetch: `8511089eaeb06cddd049b629562926822020de5c`,
  2026-08-28, describe `v0.7.0-beta.1-13-g8511089ea`. Matches the pin in
  `paseo/source.toml`.
- upstream/main after fetch: `cb90806045eb636a176c46b30b9e16cb5fa0a120`,
  describe `v0.8.0-34-gcb9080604`, package version `0.8.0`.
- The branches had diverged: the fork had 12 commits of its own (including
  repeated merges/commits), upstream had 193. No fast-forward from the current HEAD.
- Fetching tags hit an old `v0.4.0-beta.2` tag whose content differed locally;
  it was not overwritten. Fetching upstream/main alone with `--no-tags` succeeded.
- `~/.paseo/config.json` matched the template exactly after `@@HOME@@` substitution.

## Config changes needed

1. Keep `daemon.mcp.enabled: true` and `daemon.mcp.injectIntoAgents: true`.
2. Remove `daemon.mcp.injectIntoProviders` (fork-only field). Upstream does not
   use it to block tools, and the schema accepts unknown fields, so leaving it
   in may fail silently.
3. Add `paseoTools: { "enabled": true }` to `codex-supervisor` and `codex-lead`.
4. Add `paseoTools: { "enabled": false }` to `codex-peer` and every other
   provider to keep the old scope.

Full config: [current template](../../home/.paseo/config.json.template). It was
built from the user's in-progress template and keeps models, thinking, command,
params, and other settings unchanged; only the MCP policy moved. It explicitly
disables the built-in providers `claude`, `codex`, `copilot`, `opencode`, `pi`,
`omp` and the custom providers `grok`, `hermes`.

### Important behavior differences

- Upstream enables the full tool set when a provider has no `paseoTools`. The
  fork used an allowlist, so new providers were excluded by default. Set an
  explicit policy whenever you add a provider; upstream has no global
  default-deny equivalent to the old allowlist.
- `extends: "codex"` does not inherit the tool policy. Each provider ID has its own.
- `paseoTools.enabled` controls only Paseo's tool set; `providers.<id>.enabled`
  controls the provider itself. They are not interchangeable.
- `paseoTools.disabledTools` is only needed to keep part of the tool set; use
  exact tool IDs. Do not confuse it with the provider runtime's `disallowedTools`.
- Upstream applies the policy to both MCP and native tools. Voice `speak` is
  handled separately; the current config has voice off.
- After switching builds: reload config, then create new agents or reload
  existing ones. A running session keeps the tool set it received at startup.
- `extends`, `command`, `env`, `params`, `models`, `additionalModels`,
  `thinkingOptions`, and `isDefault` still exist in the upstream schema; the
  current profiles need no config-level change.

## Room setup changes needed at the same time

Changing the remote URL and JSON is not enough:

| Component | Required change |
| --- | --- |
| `paseo/source.toml` | Point the primary source at getpaseo; update the audited commit/version |
| `scripts/install-paseo-fork` | Support the upstream source and switching a diverged checkout; it currently accepts only no-op or fast-forward and checks the fork topology |
| `scripts/install-room` | Align remote/provenance checks and the checkout switch/rollback flow |
| `home/.local/bin/paseo-local-update` | Drop the hardcoded fork URL and old pin; fix source, topology, and update-selection checks |
| `scripts/verify`, `scripts/doctor` | Check the upstream source and the `paseoTools` policy |
| `scripts/export-current` | Replace the old allowlist condition with the new provider policy |
| `tests/test_setup.py`, `tests/container/accept`, related tests | Update expectations for source, pin, migration, and MCP |
| README, `paseo/notes/*`, `docs/paseo-fork.md` | Update guidance and actual behavior |

Recommendation: drop the fork but keep pinning an audited upstream revision.
The updater should have an explicit step to choose a new upstream revision and
test the build before moving the pin. The current tooling requires the branch
tip to equal the pin, so a one-time pin does not solve convenient updates as
main keeps moving.

For the first switch, keep the fork checkout as a fallback, build upstream in a
separate checkout, and switch the running setup after verification. Do not
merge upstream into the fork for this migration.

## One other fork-only change

Fork patch `c81cb8473` let a loopback client without a bearer token connect even
when the daemon has a password. Current upstream still checks the token when a
password is set (`websocket-server.ts`, `attachAuthenticatedSocket`); that
exception is not kept. The compared config declares no password, but check the
actual environment/CLI settings and Desktop/CLI connectivity before switching
builds. Do not infer connection compatibility from a valid MCP schema alone.

## Verification done and limits

- Fetched origin and upstream; compared HEAD, branch, version, divergent
  history, and upstream source.
- Ran upstream's `ProviderOverridesSchema` against all 11 providers in the
  candidate config: PASS.
- Ran upstream's policy functions on the 11 providers: only Supervisor/Lead get
  the tool set and `create_agent`: PASS. Confirmed undeclared providers default to enabled.
- Read the agent launch path to confirm the same gate covers MCP and native
  tools, plus upstream's test for per-session policy snapshots.
- Did not build all of upstream, run the upstream daemon, test data migration,
  or test Desktop/CLI connectivity. Conclusions are at the config/source level,
  not proof that a build switch succeeds.

## Upstream sources

- [Official feature #4277, merged 2026-09-03](https://github.com/getpaseo/paseo/commit/53c96074791089949f6917cfa55db1d11f212521)
- [MCP docs at the audited commit](https://github.com/getpaseo/paseo/blob/cb90806045eb636a176c46b30b9e16cb5fa0a120/public-docs/mcp.md)
- [Provider schema](https://github.com/getpaseo/paseo/blob/cb90806045eb636a176c46b30b9e16cb5fa0a120/packages/protocol/src/provider-config.ts)
- [Policy selection by provider ID](https://github.com/getpaseo/paseo/blob/cb90806045eb636a176c46b30b9e16cb5fa0a120/packages/server/src/server/agent/paseo-tool-policy.ts)
