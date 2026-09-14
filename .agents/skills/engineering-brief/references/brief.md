# Brief format

Lead with the coverage interval, inspected repository revision, research coverage
and limits, and any gap excluded by the fourteen-day cutoff. Bias selection toward
recent evidence. Make repository relevance prominent in each leading finding and
in REPO IMPACT; it is the purpose of the report.

Retain the following sections. Use up to five leading developments, not five
mandatory slots. For a quiet section distinguish no meaningful findings in the
checked material from material not checked. Cross-reference a recurring topic
rather than duplicating its story and controls. Aim for an 8–12 minute read without
padding; include the initial architecture baseline in the report body.

## 1. TOP 5

For each: what happened; why it matters; claim type, evidence grade, and impact;
who should care; direct source; relevance to Agent Team; and whether it challenges
or reinforces something the repo currently does. Include its repo comparison and
topic action. Explain what changed if revisiting a previously reported claim.

## 2. RELEASES & PRODUCT CHANGES

Meaningful behavioral, architectural, or workflow deltas. Explain the implications
rather than reproducing marketing copy or version-number churn.

## 3. NEW TECHNIQUES & WORKFLOWS

Explain promising practices sufficiently to reproduce them, then compare actual
Agent Team behavior. Examples include planner/implementer/reviewer separation,
parallel investigation, worktree isolation, verification contracts, runtime proof,
context engineering, repository knowledge, fresh-context review, routing,
autonomous debugging, and long-running execution.

## 4. SKILLS / PLUGINS / MCP

For promising items: what it does, relevance here, architectural compatibility,
supply-chain/security implications, and whether to read, test, adopt, or ignore.
Those are recommendations; adopting/installing remains a separately selected action.

## 5. PRACTITIONER RADAR

Include a watched practitioner only for relevant substance actually published.
Explain the demonstrated workflow or claim and its evidence, not that a new video
or post appeared. Discover production-software maintainers beyond the seed list.

## 6. PROJECTS TO WATCH

Prefer novel architecture, practical workflows, reproducibility, good documentation,
and code worth learning from. Stars and rapid popularity do not establish quality.

## 7. RESEARCH / EVALS

Apply the eval dimensions in [evidence](evidence.md). Explain what the methodology
teaches about real engineering and where generalization stops.

## 8. DEBATES & COUNTERPOINTS

Present positions A and B, supporting evidence for each, and what experiment could
resolve the uncertainty. Preserve disagreement rather than inventing consensus.

## 9. REPO IMPACT

Group evidenced conclusions under **Already doing this**, **Potential gap**,
**Possible improvement**, **Possible experiment**, and **No action**. Include
repo paths/revision and the comparison classification from the evidence rubric.
Unknowns remain explicit. A new technique need not be a useful change here.

## 10. TRY THIS

Recommend **zero to three** experiments. For each state the actual uncertainty,
small reversible intervention, baseline/comparison or A/B design, measurement and
success criterion, cost/scope, and stopping/rollback condition. Favor real tasks
and outcomes over merely proving that a feature can be invoked. A useful proposal
could compare defect discovery from independent and same-context reviews on five
real tasks; “adopt multi-agent review” alone is not an experiment.

## 11. WATCHLIST

Carry forward unresolved questions, early projects, and developing patterns with
why and when to revisit. Link the earlier report when helpful. Record resolutions
or contrary evidence rather than repeating unchanged stories in TOP 5.

## 12. SOURCE QUALITY CHECK

Record highest-value sources in this run, observed noise, newly discovered
engineers/repos, and emerging blind spots. Separate unvisited sources from low-value
ones. Link curation proposals to their supporting observations.
