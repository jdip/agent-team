# Local history

Use the package's `scripts/history.py` with Python 3.11+ from inside the actual
Agent Team checkout. It uses only the Python standard library and Git. Resolve the
script relative to the loaded `SKILL.md`, not a hardcoded machine path.

```sh
python3.13 <skill-directory>/scripts/history.py context --mode brief
python3.13 <skill-directory>/scripts/history.py context --mode audit
```

Select an available supported Python runtime; `python3.13` above is an example.
`context` is read-only. It resolves `<absolute-git-common-dir>/codex-engineering-brief/`
and returns the mode, UTC interval, previous report, latest report in each mode,
recent report paths, draft directory, and any cutoff gap. Inspect the resolved
location before writing. Git metadata is outside the tracked file set even when
the primary checkout's `.git` directory is physically inside its root.

## Coverage and continuity

For a **brief**, coverage ends at the captured run-start time and begins at the
later of the previous completed brief's coverage end and fourteen days earlier.
The first run covers fourteen days. Favor recent evidence inside that interval.
Disclose any older omitted interval after a long gap. Keep publication/event/update
dates distinct; historical context is labeled as context, not current news.

For an **audit**, inspect approximately thirty days. Audit completion never changes
the brief boundary. Read relevant recent briefs and the last audit for evidence
and unresolved source recommendations.

Read the previous reports to suppress unchanged claims, grouping aliases and
canonical source URLs. A materially changed claim may return with an explanation
of what is new. Carry unresolved watch questions and curation proposals into the
next report until resolved or explicitly retired. Archived reports own that
evolving history; tracked `references/sources.md` alone owns standing source policy.

## Save a completed report

Draft locally, preferably under the returned `drafts` directory, creating that
directory only when needed. Drafts have no completed-report header and are never
used to advance coverage. Preserve incomplete work if interrupted. Do not put
generated reports in the tracked checkout.

After research and citation/repo-impact checks, save using the exact interval
captured at run start:

```sh
python3.13 <skill-directory>/scripts/history.py save --mode brief \
  --start '<coverage_start>' --end '<coverage_end>' '<local-draft.md>'
```

Use `--mode audit` for an audit. The helper prefixes completion metadata to the
report and atomically publishes a uniquely named Markdown file. Only a successful
save creates completed history. Record repository revision, dirty-state caveats,
coverage limits, sources, report findings, and watch continuity in the report body.
Use the returned archive path for the conversation's report link.

Distinct/overlapping runs are retained; the greatest completed coverage end sets
the next brief boundary. An older run finishing late cannot move it backwards.
Quiet reports may complete when their checked coverage and limitations are honest.
Failed, interrupted, or incompletely saved runs do not advance coverage.

An unreadable, malformed, or future-dated existing report is an error, not first-run
evidence. Preserve it, inspect the specific problem, and report the limit. Do not
silently reset history or overwrite a completed report. A pending temporary save
is not a report. No scheduler, separate state ledger, database, or latest-pointer
file is needed. Report saving is not evidence that every possible source was read.

Linked worktrees share the Git common directory and therefore this archive;
separate clones/machines do not synchronize it. Preserve the archive as durable
local state during task cleanup. Clean only proven-owned, no-longer-needed drafts;
do not automatically delete reports. Private history stays local unless the
operator explicitly authorizes a particular sanitized publication.
