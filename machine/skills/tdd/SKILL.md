---
name: tdd
description: Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
---

# Test-Driven Development

TDD is the red → green loop. This skill is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle: consult them before and during the loop, not after.

When exploring the codebase, read `CONTEXT.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists, and it survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams: where tests go

Apply the global Planning before implementation rule before tests or code
intended to ship. Reuse the implementing workflow's covering map/spec; a direct
test-first request enters planning when coverage is missing.

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

Select seams from the approved behavior, supplied acceptance criteria, and established public interfaces. State the boundary under test and proceed within that scope; prior approval does not need a second seam-confirmation round. Ask only when choosing a boundary would settle an unresolved interface or scope decision. Complete independent inspection before presenting that decision.

When the interface itself is in question, read the available `codebase-design` skill for the module, interface, depth, seam, adapter, leverage and locality vocabulary. Use it as a reference, not a new planning session.

Apply the repository's classification before adding tests. For Application Code, use meaningful behavioral tests and actual local gates. For Tooling maintained through real-use verification, exercise the actual operation and source checks; this skill does not require a new coverage suite or simulated infrastructure.

## Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological**: the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec.
- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage (see the `code-review` skill), not the red → green implementation cycle.

## Attribution

Adapted by Agent Team from [Matt Pocock’s tdd](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/tdd), revision `3cca18b368ae95cdbdebbff572ccafa662551015`. The [MIT notice](LICENSE) covers reused upstream material. Agent Team owns this adaptation.
