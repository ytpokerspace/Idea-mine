# Direct Computation Lab — Research Concept

**Status:** proposed experiment; no performance claims have been measured yet  
**Goal:** identify cases where a direct solution can replace repeated simulation without sacrificing correctness or verifiability  
**Initial scope:** scalar affine recurrence only  
**Constraints:** standard-library Python, zero external API calls, reproducible tests and GitHub Actions

## 1. Research question

For the recurrence

`x[t+1] = a*x[t] + b`

can a direct formula compute `x[n]` faster than applying the transition `n` times, while agreeing with an independently implemented iterative reference within declared tolerances?

This is a deliberately small, falsifiable starting point. It does not claim that arbitrary computation can be performed without execution.

## 2. Competing methods

- **Baseline — iterative:** start from `x0` and apply `x = a*x + b` exactly `n` times.
- **Candidate — direct:** for `a != 1`, use `x[n] = a^n*x0 + b*(a^n - 1)/(a - 1)`; for `a == 1`, use `x[n] = x0 + n*b`.
- **Verifier:** compare candidate and reference with absolute and relative tolerances. Non-finite values fail closed. A failed check must be reported, not silently accepted.
- **Router (later milestone):** select a direct method only when its supported assumptions are satisfied; otherwise use a baseline or return “unsupported.”

## 3. Smallest falsifiable experiment

Run both methods over a fixed, published parameter set and step counts such as 10, 1,000, and 100,000. Repeat each timing several times and record all individual durations, medians, environment details, result values, and verification status.

### Hypotheses — not results

- **H1:** direct evaluation will generally be faster for sufficiently large step counts.
- **H2:** some inputs will expose floating-point disagreement, overflow, or numerical instability.
- **H3:** verification overhead can outweigh the savings for small step counts.

These are hypotheses until a benchmark is actually run. Do not publish expected values as measured outcomes.

## 4. Metrics

1. **Correctness:** absolute error and tolerance-pass rate against the iterative reference.
2. **Latency:** median wall-clock time per method, using a monotonic high-resolution timer.
3. **Speedup:** iterative median divided by direct median; report the raw timings as well.
4. **Reproducibility:** Python version, operating system/platform, parameters, step counts, repeat count, and raw samples.
5. **Verification overhead:** separately time verification in a later benchmark revision.

Timing results are machine- and runtime-dependent. Avoid claiming a universal speedup from one run.

## 5. Failure handling and limitations

- Reject negative or non-integer step counts and non-finite inputs.
- Record numerical disagreement; do not silently fall back and then report the candidate as successful.
- The iterative reference is an independent implementation path, not mathematical proof; both methods use floating-point arithmetic.
- Very large powers can overflow, and closed forms can suffer cancellation.
- The initial scope is deterministic and linear. Nonlinear, stochastic, chaotic, and physical systems are out of scope until separately specified and tested.
- A prediction is not evidence that an experiment’s real-world outcome is knowable in advance.

## 6. Repository implementation plan

1. Implement the recurrence, direct method, reference method, and verifier.
2. Add unit tests for a=1, zero steps, a small parameter grid, incorrect candidates, invalid inputs, and unsupported routing.
3. Add a dependency-free benchmark script that writes JSON containing raw data and environment metadata.
4. Add GitHub Actions to run tests and a small benchmark smoke test on pushes and pull requests; upload the JSON as an artifact.
5. Review failures and numerical edge cases before adding more problem families.

## 7. Acceptance criteria for milestone 1

- Automated tests pass on the supported Python version.
- The benchmark emits structured JSON with raw timings and verification results.
- Every benchmark case reports whether verification passed.
- Documentation distinguishes hypotheses from measurements.
- No external APIs, paid services, credentials, or network calls are required.
- CI success proves that the checks ran; it does not by itself prove a general performance advantage.

## 8. Next research extensions

Only after the first experiment is reproducible:
- add a finite-state transition problem with direct exponentiation of transition operators;
- compare exact arithmetic, floating-point arithmetic, and tolerance-based verification where practical;
- test router behavior on supported and unsupported cases;
- compare end-to-end cost including verification and fallback;
- add broader workloads only when each has a clear baseline and correctness oracle.

## 9. Evidence log

| Item | Status |
|---|---|
| Concept and hypotheses | Documented |
| Benchmark results | Not measured in this document |
| Automated CI run | Must be confirmed from GitHub Actions after implementation |
| General-purpose applicability | Not established |

The key research standard is simple: every claimed improvement must be paired with a baseline, a reproducible measurement, and a correctness check.
