# Playbook: Refactoring

A change to structure or shape that keeps behavior the same: rename,
extract, inline, dedupe, move, replace an internal API.

1. Write in the ticket the target shape, why it is better, and the
   observable behavior that must not change.
2. Pin the behavior before any change. A Peer lists the tests that cover the
   affected behavior. Where coverage is missing, it adds characterization
   tests that assert what callers observe, not internals, and lands them in
   their own commit. Gate: the pinned tests pass on the original code.
3. Subtract first. Remove dead code, one-caller wrappers, and stale
   references in the scope before reshaping what is left.
4. Write the throughput checkpoint. For a sweep across many call sites, brief
   the Peer to build a script or codemod that does the change, and keep it
   as rerunnable evidence. Migrate every internal caller and delete the old
   API in the same change. Keep a compatibility layer only for external
   consumers, and only when Human asks for it.
5. Each commit ends green: the pinned tests pass at every commit, in small
   ordered steps.
6. Verify. The pinned tests pass unchanged. A test whose assertion changed
   (beyond following a renamed symbol) signals a behavior change: the Peer
   flags it and you decide. Check the public interface diff when one exists.
7. Review with `ponytail-review` and the Standards axis. Use the
   cross-model review when the change is wide or touches shared contracts.
   Then ACCEPT or REJECT per the shared contract.

Report to Human: the old and new shape, what was deleted, the evidence that
behavior is unchanged, and any flagged behavior changes.
