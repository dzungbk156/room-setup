# Workspace Protocol

This is the small shared contract for a room workspace. Human
instructions and owner decisions remain authoritative. A repository may add
project-local detail, but cannot change role authority or safety boundaries.

All roles read this shared contract from
`~/.config/codex-room/workflow/WORKSPACE_PROTOCOL.md` before project work, then
read `docs/WORKSPACE_PROTOCOL.md` relative to the actual target project when
present. The local document supplements this contract. Report a missing or
unreadable shared contract rather than silently assuming it was loaded.

## Authority

- Human owns product goals, priority, material cost, external effects, and
  irreversible risk decisions.
- Lead owns project framing, technical decisions, integration, verification,
  and explicit candidate acceptance.
- Peer owns one bounded outcome delegated by Lead.

## Ownership and dispatch

Project instructions carry outcomes, constraints, and existing authority, not
private conversation transcripts or attribution about who spoke to whom.
Keep briefs self-contained. Preserve the meaning of an authorized decision;
an evidence-based question does not grant new authority or revoke existing
permission. Resolve a coordination question against current ownership and
evidence, then continue ready work without creating another approval gate.

- Give every moving write scope one owner. Run writable Peers in parallel
  only with verified, accepted inputs and separate write scopes.
- Agree on shared contracts before dispatch. Sequence changes to shared files
  or interfaces; use separate branches or worktrees when needed. Do not start
  blocked work merely to increase parallel activity. Continue each ready
  branch without waiting for unrelated assignments.
- A Peer must notify Lead before changing a shared contract or writing outside
  its owned scope; it must not expand ownership or coordinate other Peers.
- A Lead brief states the observable outcome, dependencies, write scope,
  relevant contract or invariants, acceptance evidence, and when to reopen the
  decision. Implementation file lists remain provisional.
- A writable Peer returns an immutable candidate or deterministic snapshot,
  original base, complete changed paths, verification, and residual risk.
- Preserve unrelated work and existing private notebooks, runtime/session
  state, and operator-owned `.codex` bytes. The setup must not silently take
  ownership of them.

## Ready inputs and continuity

At session resumption, Lead inspects project instructions, actual state, the
latest handoff, and current ownership before assigning work, starting from
the `room-digest` output. Lead records each Peer's ticket, write scope, and
branch as Paseo labels on the Peer (`room.ticket`, `room.scope`,
`room.branch`); those labels and the tracker are the ownership record. Verify required
inputs exist, are accepted, and are available in the working context; a closed
task or completion message alone does not establish readiness. Give each
assignment enough context to start without the preceding conversation.

After acceptance, Lead updates the existing work-status source, records
remaining limits and usable downstream inputs, and reconciles affected
assumptions and dependencies before choosing next work. When a decision changes
the plan, update the existing issue or project document, including outdated
task descriptions and completion criteria. Record the decision and its reason
there; do not leave it only in chat or create a duplicate tracker.

## Evidence and handoff

Identify the exact candidate, verification environment, reproduction steps,
actual results, and durable evidence locations. Separate verified behavior,
untested scope, failed checks, and unknowns. Match proof to the promised
outcome: passing tests or valid data alone do not establish usable UI, playback
quality, or save/reopen behavior.

A handoff states what is usable, how to try it, remaining limits, and usable
downstream inputs. Permission to proceed with a limitation does not turn an
unmet criterion into a pass.

## Independent judgment

Peer may return `REOPEN_REQUEST` for a failed premise,
`DEPENDENCY_REQUEST` for an unowned prerequisite, or `BLOCKED` when no safe
in-scope progress remains. Each signal includes evidence, consequence, and the
decision or dependency needed.

When architecture or an exact candidate carries material uncertainty, Lead may
request a fresh read-only Peer review of the stable candidate or snapshot. The
review uses the flexible Peer profile and a bounded question; no dedicated
review role, mandatory form, or reviewer count is
required.

A review Peer starts with zero context. Its brief names the candidate or
document, the bounded question, and the paths it may read. It carries no Lead
reasoning, preferred answer, earlier findings, or conversation history; those
bias the reviewer toward what Lead already believes. The reusable read-only
scout accumulates context, so it never performs a review: each review gets a
fresh Peer, archived when its report is accepted.

## Acceptance and waiting

Every actionable Peer response closes a loop with its original Lead brief.
Peer addresses the assigned outcome and requested evidence, distinguishes
complete/missing/failed/unverified claims, and states write ownership. A
read-only review supplies findings and limits for the bounded question; a
blocker supplies evidence, consequence, and the decision needed.

Lead must answer the question, resolve dependencies or ownership, request
specific missing evidence, or explicitly accept/reject the identified
candidate with a reason. Communicate decisions that affect the Peer and
record them in the existing project status source. A deferral identifies an
owner and return event/checkpoint. Silence, DONE, or test results do not close
the loop. Keep dependent work waiting for resolution while unrelated ready
work continues.

Writer proof, passing tests, completion messages, and lifecycle status are
evidence. Lead inspects the exact artifact and explicitly accepts or rejects
the candidate with a technical reason. Human alone decides product scope,
material cost, external effects, and irreversible risk.

Use finish, error, attention, and decision events to advance work. Wait for an
event instead of repeatedly polling unchanged state. Keep handoffs concise and
decision-ready; add detail only when it changes the route or acceptance.

## Engineering skills (mattpocock/skills)

The room uses Matt Pocock's engineering skills for its align, plan, build, and
review loop. These rules adapt them to room authority; where a skill and this
contract disagree, this contract wins.

- Tracker. Each project runs `setup-matt-pocock-skills` once, with the
  local-markdown tracker. `docs/agents/issue-tracker.md` then names where
  tickets live; that tracker is the project's status source. Record tickets,
  blocking edges, dispositions, and plan changes there, not only in chat. If
  the file is missing, Lead asks Human to run setup (local markdown) before
  creating tickets.
- Align and plan belong to Lead, working directly with Human: `grill-with-docs`
  (with `grilling` and `domain-modeling`), `to-spec`, `to-tickets`,
  `wayfinder`, `triage`, `improve-codebase-architecture`, `ask-matt`,
  `implement-spec` (orchestration, see below), and `retro` after a session.
- Spec review. After `to-spec` and before `to-tickets`, Lead sends the spec to
  fresh read-only Peers, one lens each: zoom-out (is the design larger than
  the problem; does the codebase, a dependency, or the platform already
  provide it), naive reader (can someone with no project history follow it;
  which terms, assumptions, or background are missing), and codebase auditor
  (do the named paths, functions, signatures, and APIs exist as described).
  Lead may drop a lens that cannot apply, such as the auditor for a spec that
  names no existing code, and records why. Lead marks each finding fix or
  contest in the spec or tracker, citing evidence for a contest, updates the
  spec, and writes tickets only from the updated spec. Human may waive the
  step for a small spec.
- Build belongs to Peers: `implement`, `tdd`, `diagnosing-bugs`, `prototype`,
  `wizard`, and the reading part of `research`. Merge and rebase conflicts are
  ordinary Peer work (no dedicated skill).
  Peers use `codebase-design` vocabulary and read `GLOSSARY.md` and ADRs as
  consumers; they change them only when the brief grants that scope. Peers do
  not run Lead-side skills unless the brief asks.
- Dispatch. A ticket in the ready-for-agent state is a Peer brief. Lead
  dispatches in blocking-edge order: a ticket is ready only when every blocker
  is accepted. The brief carries the ticket path, branch or worktree, write
  scope, and acceptance evidence.
- Sub-agents. When a skill says to spawn a sub-agent, background agent, or
  parallel agents: Lead creates Paseo Peers with the default Peer provider
  `room-peer-minimax` (mode `plan` for read-only, `build` when the step
  writes); a Peer performs those steps itself,
  sequentially, without spawning agents.
- `implement` commits only to the branch or worktree named in the brief. The
  commit is a candidate: the Peer reports its hash, base, changed paths, and
  verification. A Peer's own `code-review` is evidence, not acceptance.
- `implement-spec`. Lead runs it as the room's spec-wide build loop: the
  "integration branch" is created by Lead; each "implementer subagent" is a
  writable Peer on its own branch and worktree based on the integration
  branch, briefed with the ticket path and building it with `tdd`; the
  "exploration subagent" is the read-only scout, saving notes outside the repo
  at a path named in the brief; the "merger subagent" is a Peer that merges an
  accepted candidate into the integration branch. Lead accepts each candidate
  before it is merged and dispatches the next frontier. A draft PR is an
  external effect: open one only when the tracker closes work through PRs or
  Human asks.
- `pr` shapes any PR body. Writing one is in scope for whoever was asked;
  opening, pushing, or merging a PR needs Human authority.
- `code-review`. Lead runs it by dispatching two fresh read-only Peers against
  the same fixed point, one for the Standards axis and one for the Spec axis,
  then reads both reports and explicitly accepts or rejects the candidate.
- Ponytail. Every Peer carries `PONYTAIL.md`: before writing code it reuses
  what the codebase, standard library, platform, or installed dependencies
  already provide, writes the smallest complete change, never cuts validation,
  error handling, security, or accessibility, and ends its handoff with what it
  skipped or did not check. A brief that asks for more (`tdd`, broader tests)
  wins. A deliberate shortcut carries a `ponytail:` comment naming its limit.
- `ponytail-review` is the third review axis: for a non-trivial or risky
  candidate, Lead adds a fresh read-only Peer that runs it beside the Standards
  and Spec Peers (bugs outside the diff, security, real load, untested risky
  logic, what to cut). Its findings are evidence; Lead still decides.
- Post-review prune. Fixes for review findings tend to add guards, options,
  and sections the finding did not need. When fixes change a spec or
  candidate beyond a few lines, Lead sends the fix delta (diff against the
  reviewed point) to one more fresh read-only Peer before acceptance: the
  zoom-out lens for a spec, `ponytail-review` for code. It asks what the
  fixes added that their findings did not require, and does not reopen
  decisions Lead already accepted.
- `ponytail-audit` (whole repo, ranked) and `ponytail-debt` (ledger of
  `ponytail:` shortcuts) are read-only Peer tasks run at Human's request or
  before planning a cleanup; Lead turns accepted findings into tracker tickets.
- REA (reverse engineering). A Kiro Peer (provider `room-peer`) in mode
  `room-peer-re` carries the REA MCP
  tools and `reverse-engineer-anything` skill for shipped targets without
  source: native binaries, Electron/JavaScript bundles, .NET assemblies,
  websites, app packages. The brief names the target path or URL and the
  question; the handoff returns findings with REA's evidence and stated
  unknowns. Native disassembly needs Hopper, Ghidra, or IDA configured; without
  one the Peer reports that limit instead of guessing.
- `retro` runs after a session at Human's request, usually with Lead. It
  proposes environment changes (navigation pointers, automated checks, coding
  standards, steering files); applying them is ordinary scoped work.
- Domain docs are `GLOSSARY.md` / `GLOSSARY-MAP.md` (formerly `CONTEXT.md` /
  `CONTEXT-MAP.md`). If a project still has the old names, Lead proposes a
  `git mv` to the new names before relying on the skills.
