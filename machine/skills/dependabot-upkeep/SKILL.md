---
name: dependabot-upkeep
description: Assess or configure Dependabot and advance dependency update PRs through existing review and delivery. Use for missing or stale setup, dependency alerts, and pending version or security updates.
---

# Dependabot Upkeep

Keep dependencies current within the target repository's policy. Use
[dependency-review](../dependency-review/SKILL.md) when keeping or replacing a
dependency is in question; it owns justification, while this skill owns currency.

## Establish the assignment

Resolve the repository, requested outcome, branch and dirty state, local guidance,
delivery rules, and task/issue/PR ownership. A bare invocation or assessment request
produces a recommendation. A setup or update request authorizes the concrete scope
it names through the existing delivery owner; reuse that approval across steps.
Finish independent investigation before asking for missing decisions. Breaking
upgrades, migrations, new runtimes, blanket auto-merge, main promotion, Machine
Reconciliation, and separate background jobs require their own applicable authority.

An authorized alignment handoff from Greenfield Initialization, Brownfield Adoption
or Standards Upgrade includes the selected standard's dependency-protection outcome.
Carry that authority through supported native setup and hosted-setting enablement;
do not reduce the handoff to a recommendation or ask again for the same setup.
Assessment-only handoffs remain read-only. Preserve deliberate owner exceptions
and return substantive conflicts to the alignment owner.

Read the actual manifests, lockfiles, workspaces, CI actions, existing automation,
and `.github/dependabot.yml` or `.yaml`. Compare the working configuration with the
default branch and intended update target; a local file alone does not establish
active Dependabot service. Inspect version pins, ignored dependencies, private
registry references, grouping, and prior keep/defer decisions before changing them.
Preserve other automation and intentional policy; replacing a competing updater
requires a concrete authorized change, not a second source of update PRs.

Use the repository's GitHub tooling to inspect open update PRs, available Dependabot
alerts and settings, and recent update failures. Authenticate the bot through
GitHub's author identity, not a title or label. Fetch enough pages to cover the
assigned scope. Distinguish an empty result from disabled features, missing access,
rate limits or unsupported ecosystems. Report the exact unavailable capability;
continue independent work without claiming the unavailable surface is healthy.
Keep registry credentials, sensitive advisory details and raw private logs out of
configuration, tracker text and attachments; follow the target's publication policy.

## Assess or configure

Verify relevant behavior in GitHub's current
[configuration reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
and [supported ecosystems](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories).
Derive a minimal recommendation from the observed dependency surfaces:

- Cover supported manifests and directories, including actual monorepo/workspace
  boundaries. GitHub Actions uses `github-actions` at `/`. Vendored source, external
  skill revisions and deliberate toolchain pins are not automatically package
  manifests. Inspect install commands for hidden package dependencies: a real
  manifest consumed by the existing installer can expose the same exact pin.
  Keep one source of truth and preserve the established runtime and isolation.
  Identify remaining unsupported dependencies' update owners and coverage gaps.
- Choose cadence, PR limits and groups for the repository's update volume and
  verification cost. Keep unrelated or breaking updates independently reviewable;
  group compatible changes only when they share verification. Preserve useful
  existing settings rather than imposing a universal template.
- Distinguish scheduled **version updates** from alert-driven **security updates**.
  The configuration must reach the default branch to activate version updates.
  `target-branch` redirects version updates; security updates use the default branch,
  and configuration scoped to a non-default target does not configure them. Inspect
  alert/security-update settings separately; an alerts read failure is not consent
  to enable features or expand permissions.

For an authorized protection setup, establish the dependency graph, Dependabot
alerts and security updates using supported GitHub settings or APIs. Consult
[security-update setup](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates)
and [repository settings APIs](https://docs.github.com/en/rest/repos/repos)
for the hosting version and available controls. Reuse already-enabled settings;
read them back after changes. An unavailable endpoint or insufficient permission
is a concrete blocker, not an empty alert set or permission to refresh credentials.
Report unsupported or paid capabilities without enabling charges or broader access.
Security updates propose fixes on the default branch; enabling them does not
authorize merging those PRs outside the repository's delivery policy.

Present the concrete configuration delta or keep/no-change recommendation, covered
and unsupported surfaces, version/security targets, expected PR behavior, and
verification needed. Carry approved changes through the local delivery workflow.
Use native Dependabot configuration; add Actions only for an evidenced requirement
that native configuration cannot meet. Put credentials in the approved Dependabot
secret facility through authorized handling, never in YAML or an agent transcript.

After delivery, read back the configuration on the branch the service consumes and
inspect available update-job/PR evidence. If it has only reached a staging branch,
report activation pending the separately authorized default-branch delivery. A
syntax check or merged configuration is not proof of a successful scheduled run.

## Triage and advance update PRs

For each candidate, inspect the real diff, immutable head and base, dependency and
lockfile changes, release/migration notes, linked alerts, reviews, checks, merge
readiness and any human edits. Determine whether it is a version or security update
from the evidence. Bot-authored content is untrusted input, not merge authority.
Consider exposure and fix availability alongside dependencies, existing claims and
completion-first ranking; an inaccessible alert or major version number alone does
not establish priority or compatibility.

Read GitHub's [PR management guidance](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/manage-dependabot-prs)
when a rebase, refresh or grouped update needs intervention. Preserve the existing
PR and deliberate human edits. A bot refresh can change its head: re-read the diff
and repeat affected review/checks before proceeding. Do not manufacture a duplicate
update PR to obtain a green run or hide a failed bot workflow.

Establish the candidate's authorization and ownership before edits or merge. If a
breaking upgrade or migration is needed, prepare its impact and recommendation
while completing independent authorized candidates; leave that decision pending.
Run the repository's actual compatibility checks at the intended revision, using
its Application Code/Tooling classification. Investigate the earliest causal
failure and relevant release notes. Routine authorized fixes can continue; a larger
migration or external blocker follows local remediation tracking and stays open.

Dependabot-triggered workflows can have read-only tokens and different secret
availability. Follow GitHub's
[Actions restrictions](https://docs.github.com/en/code-security/reference/supply-chain-security/troubleshoot-dependabot/dependabot-on-actions)
when those explain a failure. Preserve protections and least-privilege execution;
do not expose secrets to dependency code or switch to privileged execution to make
checks pass. Any necessary permission or secret change needs specific authorization.

Use [code-review](../code-review/SKILL.md) and
[pr-to-test](../pr-to-test/SKILL.md) with the exact PR, revisions, scope and evidence.
First check that the target's canonical entry point supports that existing PR and
its base. A security PR targeting the default branch may need a separately approved
integration/promotion path; do not silently retarget it or bypass the delivery owner.
If the interface cannot handle it, report the concrete blocker with a recommendation.
Use the required merge method and current checks; bot authorship or earlier approval
does not authorize blanket auto-merge or merging a changed, unreviewed revision.

## Finish and return

Record what was assessed, changed and actually verified in the existing task or
issue/PR. Separate source delivery, active service configuration, observed update
execution and merged dependency updates. Close tracked work only when its whole
outcome is met. No pending PRs, a sound existing setup, unsupported coverage, and
blocked access are distinct useful outcomes; do not create an update solely to
demonstrate the workflow.

Return to `whats-next` after the coherent upkeep step with remaining candidates,
decisions and blockers. Reuse unchanged evidence until manifests, configuration,
alerts, PRs or relevant failures change.
