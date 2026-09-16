---
name: reflect
description: Capture actionable lessons from current-task evidence when a reflection check finds a reusable improvement or the user asks to reflect.
---

# Reflect

Use one focused pass over the current conversation and evidence already collected,
with the bounded enforcement inspection below.
Follow a specific reference to an earlier incident when useful; do not scan broad
history, start a fresh investigation, or assemble a review panel. Preserve the
active task and its authorization.

## Decide what is reusable

Require a concrete incident and a change that would improve a future decision.
One serious incident is enough; repetition is not required. Distinguish:

- **Missed instruction:** inspect its existing trigger and use. Improve discovery
  if that caused the miss; do not duplicate an instruction merely because it was missed.
- **Unclear instruction:** correct the ambiguity at its existing owner.
- **Missing capability:** identify the smallest practical code constraint, native
  check or helper that prevents recurrence.
- **One-off failure:** discard it when no actionable improvement remains.

Before prescribing a remedy, inspect the enforcement relevant to the incident:
the repository's check commands, configuration and invocation path, including CI
or hooks where used. Establish whether a relevant check is absent, unwired, broken,
bypassed or insufficient for this failure. Distinguish configured enforcement from
evidence that it actually ran. Repair or extend an existing mechanism where
practical before proposing another. Keep this inspection scoped to the lesson.

Classify the failure as mechanical or requiring judgment. Prefer deterministic
enforcement for objectively detectable violations, such as banned APIs or fixed
file/import patterns, when it earns its maintenance cost; otherwise improve the
owning guidance or review criteria. Keep contextual choices there as well. For a
mixed failure, separate what a check can enforce from the judgment that remains.

Keep repository-specific lessons with the repository. Route reusable shared-skill
or Machine Profile improvements to their maintained source, not installed copies.
Respect separately owned upstream packages. Do not generalize a local preference
into a global rule without evidence and applicable authorization.

## Record and follow through

Record every accepted actionable lesson through the owning repository's issue
tracker guidance for deduplication, filing, readback and failure handling. Include
the incident, affected owner, proposed improvement and observable completion
criterion. Report the issue link; use the existing task issue when it already
covers the lesson.
Keep credentials and private transcript content out of tracker records.

Apply an in-scope fix through the global Planning before implementation rule and
existing review/delivery authority, reusing coverage; record its result in the
issue. Analysis and lesson filing can inform that planning before
implementation. Leave deferred work open. Filing does not admit or activate a
backlog, expand the current fix, or authorize shared guidance changes. Batch any
missing approval with concrete proposed changes; reuse consent already supplied.

Validate an approved change against the motivating incident with one relevant
real-use check where possible. Report future-dependent benefit as unverified until
that use occurs. Do not add an evaluation campaign to establish it.

Return a short list of accepted lessons, evidence, issue links and dispositions.
For an explicit reflection with nothing useful, say so. A routine check with no
qualifying lesson stays silent and creates no issue. Do not repeat completed
reflection on unchanged evidence or create a separate lesson ledger.
