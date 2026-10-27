# Playbook: Bug fix

A reported defect: something worked or should work, and does not. Every line
that ships traces to runtime evidence. A change that "might help" is a
hypothesis, not a fix, and does not ship.

One writable Peer can own steps 2 to 5 on one branch. You check its evidence
at three gates: the repro, the mechanism, and the fix. Do not move the Peer
past a gate until you accept the evidence for it.

1. Frame the defect in the ticket: observed behavior, expected behavior, the
   surface where it shows (browser, CLI, API, file output), and any repro
   steps, logs, or IDs Human gave. If the report is vague, write your
   restatement and correct it with Human before dispatch.
2. Reproduce first. Brief the Peer to reproduce on the same surface the
   report names: `browser-skill` with `bsk debug` capture for a web app, the
   real command for a CLI. Acceptance is a rerunnable repro (a failing test,
   a script, or exact steps) and its failing output. If it does not
   reproduce directly, the Peer narrows conditions, synthesizes the trigger,
   or adds instrumentation until it fires. It asks for Human help only with a
   specific reason the surface cannot be reached, after driving it as far as
   it goes. Gate: no accepted repro, no diagnosis.
3. Find the cause by elimination. The Peer lists candidate hypotheses (it may
   use `diagnosing-bugs`), then rules them out with runtime evidence: logs,
   instrumentation, `git bisect`, a smaller input. Each pass takes the split
   that removes the most remaining space. Gate: accept a mechanism only with
   runtime evidence that shows it, not an argument that it could be so.
   Consult the Advisor when the diagnosis is stuck or two mechanisms survive.
4. Fix the root cause. The smallest change the evidence justifies, made where
   the system first goes wrong (shared code, not each caller). The Peer
   reverts anything a disproved hypothesis motivated. When a cheap local test
   path exists, the failing test lands in its own commit before the fix
   commit (`tdd`). Otherwise the repro script ships in the handoff.
5. Verify on the same surface. The original repro from step 2 now passes.
   A different surface, a unit test alone, or "inconclusive" is not a pass;
   record it as unverified. Gate: failing-then-passing output from the same
   repro.
6. Review and accept. Use the cross-model review for a non-trivial or risky
   fix, then ACCEPT or REJECT per the shared contract.

Report to Human: what was broken, the root cause, the fix, and the
failing-then-passing repro output.
