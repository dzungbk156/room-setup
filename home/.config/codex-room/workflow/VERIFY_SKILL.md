<!-- Adapted from pstack (github.com/backnotprop/pstack, MIT): the
     create-verification-skill skill and its feature-map example. -->
# Build a project verification skill

A writable Peer follows this file when Lead briefs it to build a verification
skill for a project. The result is a project-local skill that drives the real
app the way a user does and captures evidence. Write it for the next Peer,
not for Human: a Peer with no history will read it in the middle of a task.

Output: `<project>/.agents/skills/verify-<app>/`, with `SKILL.md`, a
`features/` map, and any helper scripts. Use the path the brief names if it
names another one.

## 1. Read the repository, not Human

Answer these from the code, docs, and scripts. Ask Lead only for what you
cannot observe (credentials, a paid service, a device you cannot reach).

- Surface: what does a user touch? Web UI, CLI or TUI, desktop app, API,
  mobile app, library. Pick the primary one and list the others.
- Run: how does the app start locally? Use the repository's own documented
  command (package scripts, Makefile, README). Note ports, env vars, seed
  data, and auth.
- Drive: how can a Peer act on it? Use an existing harness first (test specs,
  expect scripts, PTY helpers, HTTP endpoints, a debug port). Otherwise: the
  `browser-skill` (`bsk` CLI) for web and Electron UIs, never Playwright; a
  tmux or PTY session for a CLI or TUI; plain HTTP for a service.
- Observe: what evidence can you capture? Screenshots, ARIA snapshots,
  terminal transcripts, response bodies, logs, exit codes, stored state.
- Isolate: can two instances run side by side (ports, data dirs, profiles)?
  If not, the skill says so and refuses to drive an instance it did not
  start.

If the checkout does not build or start as is, stop and return `BLOCKED`
with the exact command and error. Product code is outside this brief. One
exception: when a missing asset that the app does not use blocks startup (an
unused static dir, a sample config), the skill may create it as verification
scaffolding, say so, and remove it in Cleanup.

## 2. Write `SKILL.md`

Start with YAML frontmatter: `name: verify-<app>` and a `description` that
names the app, the surface, and when to use the skill. Then these sections,
each with real commands from this repository and no placeholders:

- Launch: the exact command that starts the app for verification, and the
  signal that it is ready (a log line, a prompt, a response). Launch reaches
  a usable state from an empty data dir, migrations and seed data included.
  Ready means usable, not only that a process answers. Include teardown. For
  a short-lived CLI or TUI: build once, then start each drive in its own
  isolated PTY or tmux session.
- Doctor: one read-only check that answers "is this instance worth
  driving?": process up, expected build or version, port owned by this run,
  auth valid. Run it before the first drive and again after any surprise.
- Drive: the harness recipe with this repository's real handles. Prefer
  stable handles (ARIA roles and names, data attributes, prompt strings,
  routes) over coordinates and tab order. `bsk` refs (`@eN`) change between
  views, so the skill names the role and accessible name, and the driver
  finds the matching ref in the current view. Each run opens its own
  scope (`bsk open "<url>" --scope <run-id>`) and ends with `bsk close`.
- Evidence: what to capture and where it goes. Name one location that
  Cleanup never deletes, by default `<project>/.scratch/verify/<run-id>/`.
  Copy the proof standards from step 5 into this section.
- Cleanup: stop what this run started and remove its scratch state. Never
  kill by process name. Never delete the evidence.
- Helpers: every script the skill ships is executable, and the skill shows
  how to call it.

## 3. Seed the feature map

Write `features/README.md` and one file per user-facing feature. Start with
the top 3 to 5 features you can find in routes, commands, menus, or docs.

`features/README.md` holds: the baseline preconditions (launch settings,
seed data, Doctor), the driving conventions, the proof rules, and an index
with one line per feature file.

Each feature file starts with an H1 title and one paragraph on what the user
sees. Then exactly these four H2 sections, in this order:

1. `Sub-features`: short stable IDs, one line each (`create-save`,
   `create-cli`). Briefs and handoffs cite these IDs.
2. `How to get to it (user POV)`: every entry point a user has (button,
   shortcut, command).
3. `Driving it with <harness>`: starts with `Preconditions:`, then one
   bullet per step that pairs the user action with the exact command and the
   result you can observe.
4. `Gotchas`: traps that waste or invalidate a run.

Keep implementation details out of the map: only user paths, stable handles,
required state, commands, and observable proof. If the seed data lacks a
precondition, the journey reports a failure and `Gotchas` gives the reason.
Never weaken a journey to make it pass.

Example step:

```markdown
- **Save note.** Choose `Save note`. `bsk click` the button named `Save note`.
  A status named `Note saved` appears and the heading reads `Release checklist`.
```

## 4. Prove the skill before handoff

Follow your own `SKILL.md` end to end once: Launch, Doctor, drive one mapped
feature, capture evidence, Cleanup. After Cleanup, check that the evidence is
still at the named location; a Cleanup that deletes the proof fails this
step. Fix what fails, and run Cleanup after every failed attempt so no
process or port is left behind. A skill you never ran is a draft, not a
candidate. If you proved it in a stand-in (a container for a fresh VM, a
local stack for a remote one), list each setup step the stand-in did that the
real target will not; those steps stay unverified.

## 5. Proof standards

These go into the skill's Evidence section and bind every later run:

- Drive the real user path, not internal setters or test-only endpoints.
- Capture the action and the state it produced, not only the final screen.
- Check side effects (files written, rows stored, messages sent) through a
  second, read-only view.
- Use mocks only where a production boundary already isolates the external
  system.
- A dry-run or test mode: observe what it really skips (files, network, git
  refs); do not trust its name.
- Record the feature ID and entry point with every artifact. An entry point
  you did not drive is not verified through another one.
- When a check fails, suspect the observation method before the app.

## Handoff

Report: the skill path, the feature driven in step 4 and its evidence path,
the features mapped, surfaces you saw but did not map, stand-in gaps, and
anything Lead must decide (credentials, a paid service, product breakage you
saw).
