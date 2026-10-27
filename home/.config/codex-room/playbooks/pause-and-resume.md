# Playbook: Pause and resume

## Pause

Use when Human asks to pause, before a planned handoff to another Lead, or
when your context is close to full. "Keep going" or "don't stop" is not a
pause.

1. Stop at a safe boundary. Dispatch nothing new. Tell each writable Peer to
   finish or back out of its current step, then stop.
2. Take no external or irreversible action to pause: no push, PR, or merge
   that was not already authorized.
3. Make work durable. Each writable Peer commits its uncommitted edits as one
   `wip:` commit on its own branch and says in the commit body if the tree is
   broken.
4. Clean the room. Archive finished Peers and update every remaining Peer's
   ledger labels, per the Lead rules.
5. Write the resume note at `<project>/.scratch/RESUME.md`. `room-digest`
   prints it at the next session start. It holds:
   - Intent: the goal, in one or two sentences.
   - Playbook and step: which playbook is running and the next step.
   - Verified: what is accepted, with evidence pointers (commits, paths).
   - In flight: each live Peer, its ticket, branch, and state.
   - Waiting on Human: open decisions, each with your recommendation.
   - Next action: the first thing to do on resume.
   - Gotchas: what you learned that the tracker does not show.
   Point at tickets and commits instead of copying them.

## Resume

1. Read the digest, including the resume note. Treat both as authoritative.
   Do not redo verified work or re-run the prior repro.
2. Adopt the listed Peers, per the Lead rules.
3. Compare done with pending: what each branch has against its base, and
   what the note and tracker still list.
4. Continue at the noted playbook step.
5. Before you accept a claim inherited from the prior session, check it on
   the real artifact. A prior self-report is not proof.
6. When the tracker reflects everything the note holds, delete
   `.scratch/RESUME.md` so a later digest does not show a stale note.
