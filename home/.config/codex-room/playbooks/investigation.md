# Playbook: Investigation

A read-only question: how does X work, why was Y built this way, are we sure
about Z, should we do A or B. The deliverable is a cited answer. No code
changes.

1. Write the question as one answerable sentence, and the form of answer that
   helps Human decide (yes or no with evidence, a walkthrough, a list of
   call sites, a recommendation). If the question is vague, restate it and
   correct it with Human before dispatch.
2. Check what you already have: the room digest, the tracker, `GLOSSARY.md`,
   and ADRs. Do not re-gather what they show.
3. Send the question to the read-only scout. Split independent
   sub-questions across fresh read-only Peers, one each. Ask every Peer to
   label each claim: verified (with `path:line`, a commit, or command
   output), inferred (with the reasoning), or guess.
4. For "why was it built this way", the Peer reads history: `git log`,
   `git blame`, the commits and tickets that introduced it, ADRs.
5. When the answer depends on a fact you can observe by running something
   (behavior, timing, output, performance), a Peer runs it or builds a
   throwaway check outside the repository. Do not ask Human a question that
   an experiment can answer.
6. When the answer drives a decision with material uncertainty, send the
   question and the Peer digests to the Advisor for a second opinion.

Report to Human: the answer first, then the evidence for each claim with its
label, then what was not checked. If Human makes a decision from it, record
the decision and its reason in the tracker.
