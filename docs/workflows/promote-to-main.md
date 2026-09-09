# Promote to main

Run only on a separate explicit promotion request. Issue implementation and
next-issue-loop do not request promotion. Use a clean checkout of the intended
origin/test revision, preserving existing task checkouts and unrelated work.
Requirements are the same Git/gh/Bash/Python 3.11+ tools as PR-to-test. Read actual
review and test-delivery evidence; review any changes not covered by it.

Run scripts/promote-to-main.sh, optionally supplying --title and --body-file.
It fetches origin and tags, verifies local source syntax, snapshots intended test
and main, creates/reuses the test-to-main PR, requires checks, merges the intended
head with a merge commit, and verifies that merged source in a temporary checkout.
It then creates/reuses a semver:none main-to-test synchronization PR, checks,
merges with a merge commit, and verifies the synchronized source. Branch drift
stops for investigation. No deployment, signing, notarization, or application
runtime exists in this repository; do not invent those completion requirements.

The version contribution comes from canonical task PR merge commits on test's
first-parent history that are not already in main, in oldest-first order. Count each
PR once; skip promotion and synchronization wrappers. Apply its major/minor/patch/none
label sequentially to the highest existing vMAJOR.MINOR.PATCH tag reachable from
the previous main. All-none makes no new tag. There is no fabricated initial version:
if no baseline exists and a bump is needed, report unresolved bookkeeping and ask
for the initial version after completing independent authorized work.

A resulting tag is created on the verified main merge and pushed without moving
existing tags. Missing/conflicting labels, unavailable metadata, or tag failures
are reported as incomplete bookkeeping rather than bypassing real gates or blocking
source delivery. The agent resolves routine label questions from evidence; do not
claim a tag was published without readback. Any future artifact pipeline that
requires a version must document that real prerequisite here before use.

The script is linear. Failures leave actual partial effects for the supervising
agent: inspect PR state, exact branch SHAs, checks, and local/remote tags before
recovery. Never blindly rerun after a merge. Complete remaining already-authorized
steps directly when their state is established. Do not add a journal, rollback
engine, release-state PR, or automatic main promotion.

Complete only after both applicable merged revisions and checks are verified.
Finish safe cleanup as in PR-to-test, retaining attached/shared/uncertain checkouts.
Promotion runtime verification requires an actual promotion request; syntax or
read-only version inspection does not claim a live promotion succeeded.
