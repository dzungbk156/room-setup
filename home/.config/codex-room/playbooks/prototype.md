<!-- Adapted from pstack (github.com/backnotprop/pstack, MIT): the Prototype
     playbook. -->

# Playbook: Prototype

A throwaway sketch that settles one design or behavior choice by observing
it, instead of asking Human or arguing it. The output is a decision, not
shippable code. The real build follows the Feature route.

1. Write the one choice the prototype must settle (which layout, which
   interaction, which approach is faster, does this library do X). No choice
   to settle means no prototype: route to Feature.
2. Brief one writable Peer to build it in a scratch folder outside the
   project source (`.scratch/proto-<name>/` or a temp folder). Speed over
   polish: no tests, no abstractions, the lightest stack that shows the idea.
   Ponytail's test rule does not apply here.
3. For two or more options, the Peer builds each one, labeled, behind one
   switch (a button, a flag, an argument), so they compare side by side. Ask
   for one option Human did not name when the space is open.
4. The Peer observes the thing being decided: screenshots per option with
   `browser-skill` for a visual choice, printed output or timing for a
   behavior choice. The observation is the evidence.
5. Decide, or take the choice to Human with the evidence when it is a
   product or preference call. Record the decision and its reason in the
   tracker, and start the Feature route from it.

Report to Human: the options tried, the evidence for each, the tradeoffs,
your recommendation, and the scratch path. Say that the prototype is
throwaway.
