<!-- Adapted from pstack (github.com/backnotprop/pstack, MIT): the Perf issue
     playbook and the benchmark-checklist skill. -->

# Playbook: Perf issue

A measured slowness to improve against a baseline. Every fix ties to a
measurement. Reading source is not measuring.

One writable Peer can own steps 2 to 5 on one branch. You check its numbers
at two gates: the baseline and the result.

1. Frame it in the ticket: the slow path, the surface where it shows, the
   target if Human gave one, and the claim you expect to make in the words
   you would ship ("export is 30% faster at p50 on the 60k-row dataset").
2. Baseline first. Brief the Peer to measure the real path on the same
   surface, with the checks below. Gate: no vetted baseline, no fix.
3. Find the limiter. The Peer profiles in a run it does not report and maps
   the hot spot to source. It tries the cheapest change first, and stops at
   the first one that meets the target:
   1. Don't do it (cut work whose result nothing uses).
   2. Don't do it again (cache or reuse).
   3. Do less of it.
   4. Do it later, or when the user is not waiting.
   5. Do it concurrently.
   6. Do it cheaper.
4. Fix one change at a time. Measure after each change before the next. A
   change that does not move the number gets reverted.
5. Measure the result with the same script, data, and settings as the
   baseline. Gate: a vetted before and after.
6. Review and accept per the shared contract.

Checks for every number (the Peer answers each from a run, not a guess):

- Limiter: what stops it from going twice as fast. A change that did not
  move the number is explained by the limiter.
- Tuning: both sides run as production runs them (release build, flags,
  pools, caches, same data). If one side is untuned, there is no winner.
- Limits: the result fits disk, network, and core limits. Removing a piece
  that takes 10% of the run makes it at most about 11% faster.
- Errors: failures and wrong outputs are counted. Rejections are fast.
- Repeats: at least 5 runs per side, alternating A and B. Report the median
  and range. A gap smaller than the run-to-run range is no difference.
- Relevance: a micro result is reported as a share of the end-to-end path a
  user waits on.
- Work happened: the timed region did the work (rows written, results used,
  promises awaited).

Call the result inconclusive when the limiter is unknown, a side ran
untuned, or errors and "work happened" were not checked. Name the gap.

Report to Human: the verdict (faster, slower, no measurable difference,
inconclusive), baseline and result with unit, run count, range, and the
limiter, and where the raw runs are.
