#!/usr/bin/env python3
"""Agent Team's linear GitHub delivery path; local effects live in the runbooks."""
import argparse
import json
import shutil
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'machine'))

from reconcile import command_path, executable_path, plain_path


class DeliveryContext:
    """Local, per-run evidence; never a recovery plan or persisted retry state."""

    def __init__(self):
        self.flow = 'delivery'
        self.repository = 'not yet resolved'
        self.revision = 'not yet resolved'
        self.stage = 'preflight'
        self.operation = 'validate checkout and tools'
        self.completed = []
        self.uncertain = []
        self.retained = []

    def enter(self, stage, operation):
        self.stage, self.operation = stage, operation

    def attempt(self, effect):
        self.uncertain.append(effect)

    def confirm(self, effect):
        if effect in self.uncertain:
            self.uncertain.remove(effect)
        self.completed.append(effect)

    def report(self, error, terminal=True):
        if isinstance(error, subprocess.CalledProcessError):
            cause = f'{Path(error.cmd[0]).name} exited {error.returncode}; native stderr remains above'
        elif isinstance(error, subprocess.TimeoutExpired):
            cause = f'{Path(error.cmd[0]).name} exceeded its {error.timeout:g}s bound; native output remains above'
        else:
            cause = str(error)
        status = 'Delivery stopped' if terminal else 'Advisory failure'
        print(f'{status} at {self.stage}: {self.operation}\n'
              f'Identity: {self.flow}; repository {self.repository}; revision {self.revision}\n'
              f'Cause: {cause}\n'
              f'Confirmed effects: {"; ".join(self.completed) or "none recorded"}\n'
              f'Attempted effects requiring inspection: {"; ".join(self.uncertain) or "none recorded"}\n'
              f'Retained diagnostics: {"; ".join(self.retained) or "native output above"}\n'
              'Next: inspect actual refs, PR/check state and retained local evidence before recovery.\n'
              'Review local diagnostics before public sharing.', file=sys.stderr, flush=True)
        if terminal:
            print('Primary handoff pending: reconcile actual effects and local required completion, '
                  'then apply one Reflection screen before resolution.', file=sys.stderr, flush=True)


run = DeliveryContext()


def call(*args, capture=True):
    result = subprocess.run([str(command_path(args[0])), *args[1:]], check=True, text=True, encoding='utf-8',
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def bash():
    if sys.platform != 'win32':
        return str(command_path('bash'))
    git = shutil.which('git')
    if git:
        for root in Path(git).resolve().parents:
            candidate = root / 'bin' / 'bash.exe'
            if candidate.is_file():
                return str(candidate)
    raise ValueError('Git Bash is required for native Windows delivery')


def github(*args):
    return json.loads(call('gh', *args))


def sha(ref):
    return call('git', 'rev-parse', ref)


def verify(revision):
    run.enter('merged-source proof', f'verify merged revision {revision}')
    temporary_root = Path(tempfile.gettempdir())
    if sys.platform != 'win32':
        temporary_root = temporary_root.resolve()
    root = Path(tempfile.mkdtemp(prefix='agent-team-delivery-', dir=plain_path(temporary_root)))
    checkout = root / 'checkout'
    run.retained.append(str(root))
    effect = 'add local verification checkout'
    run.attempt(effect)
    call('git', 'worktree', 'add', '--detach', str(checkout), revision, capture=False)
    run.confirm(effect)
    try:
        subprocess.run([bash(), 'scripts/check.sh'], cwd=checkout, check=True)
    except Exception:
        print(f'Verification checkout retained for investigation: {checkout}', flush=True)
        raise
    run.confirm(f'source checks passed on {revision}')
    effect = 'remove local verification checkout'
    run.attempt(effect)
    call('git', 'worktree', 'remove', str(checkout), capture=False)
    run.confirm(effect)
    root.rmdir()
    run.retained.remove(str(root))
    print(f'Verified source on {revision}; no deployed application exists in this repository.', flush=True)


def pr(base, head, title, body_file, semver):
    run.enter('push/PR', f'resolve PR to {base}')
    matches = github('pr', 'list', '--base', base, '--head', head, '--state', 'open',
                     '--json', 'number')
    if len(matches) > 1:
        raise ValueError('multiple matching PRs; inspect before proceeding')
    if matches:
        number = str(matches[0]['number'])
    else:
        args = ['gh', 'pr', 'create', '--base', base, '--head', head, '--title', title]
        args += ['--body-file', body_file] if body_file else ['--body', f'Canonical {head} to {base} delivery. Semver: {semver}.']
        effect = f'create PR to {base}'
        run.attempt(effect)
        url = call(*args)
        print(f'Created {url}', flush=True)
        number = url.rsplit('/', 1)[1]
        run.confirm(effect)
    run.confirm(f'PR {number} available to {base}')
    effect = f'update PR {number} version labels'
    try:
        labels = github('pr', 'view', number, '--json', 'labels')['labels']
        run.attempt(effect)
        for label in labels:
            if label['name'].startswith('semver:') and label['name'] != f'semver:{semver}':
                call('gh', 'pr', 'edit', number, '--remove-label', label['name'])
        call('gh', 'pr', 'edit', number, '--add-label', f'semver:{semver}')
        run.confirm(effect)
    except subprocess.CalledProcessError as error:
        run.report(error, terminal=False)
        print(f'Version label update incomplete for PR {number}; inspect metadata. Delivery gates remain required.', flush=True)
    return number


def merge(number, expected_head, expected_base):
    run.enter('check/readiness', f'check PR {number} at expected head/base')
    account = github('api', 'user')
    author_email = f'{account["id"]}+{account["login"]}@users.noreply.github.com'
    info = github('pr', 'view', number, '--json', 'headRefOid,state,url')
    if info['state'] != 'OPEN' or info['headRefOid'] != expected_head:
        raise ValueError(f'PR revision/state changed: {info["url"]}')
    print(f'Waiting for checks: {info["url"]}', flush=True)
    deadline = time.monotonic() + 900
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError(f'PR {number} did not become ready within 15 minutes; inspect required checks and branch policy')
        subprocess.run([str(command_path('gh')), 'pr', 'checks', number, '--watch', '--fail-fast', '--interval', '10'],
                       check=True, timeout=remaining)
        fresh = github('pr', 'view', number, '--json',
                       'state,headRefOid,baseRefOid,mergeStateStatus,reviewDecision,isDraft')
        if (fresh['state'] != 'OPEN' or fresh['headRefOid'] != expected_head
                or fresh['baseRefOid'] != expected_base):
            raise ValueError(f'PR {number} state/head/base changed while waiting; reassess scope before merging')
        readiness = fresh['mergeStateStatus']
        if fresh['isDraft'] or fresh['reviewDecision'] in ('REVIEW_REQUIRED', 'CHANGES_REQUESTED'):
            raise ValueError(f'PR {number} needs draft/review policy resolution before merging')
        if readiness == 'CLEAN':
            break
        if readiness not in ('BLOCKED', 'UNKNOWN'):
            raise ValueError(f'PR {number} merge readiness is {readiness}; inspect branch policy and conflicts')
        # Older passing runs can precede registration of the new PR checks.
        print(f'PR {number} checks passed but merge readiness is {readiness}; waiting for GitHub.', flush=True)
        time.sleep(min(10, max(0, deadline - time.monotonic())))
    run.enter('merge', f'merge PR {number} at {expected_head}')
    effect = f'merge PR {number}'
    run.attempt(effect)
    call('gh', 'pr', 'merge', number, '--merge', '--match-head-commit', expected_head,
         '--author-email', author_email, capture=False)
    result = github('pr', 'view', number, '--json', 'state,mergeCommit')
    if result['state'] != 'MERGED':
        raise ValueError(f'PR {number} is not merged; inspect external gates')
    revision = result['mergeCommit']['oid']
    run.confirm(effect)
    run.revision = revision
    print(f'Merged PR {number} as {revision}', flush=True)
    call('git', 'fetch', 'origin', capture=False)
    author = call('git', 'show', '-s', '--format=%an%n%ae', revision).splitlines()
    if (len(author) != 2 or author[1] != author_email
            or author[0] not in (account['login'], account.get('name'))):
        raise ValueError(f'PR {number} merge author differs from the approved account/no-reply identity; preserve repository state and investigate')
    parents = call('git', 'show', '-s', '--format=%P', revision).split()
    if parents != [expected_base, expected_head]:
        raise ValueError(f'PR {number} merged with unexpected parents; merge exists but verification/tagging stopped')
    run.confirm(f'merge parents and author verified on {revision}')
    verify(revision)
    return revision


def version_for_promotion(repository, old_main, intended_test):
    """Use existing tags and canonical test PR merge commits, without a ledger."""
    tags = call('git', 'tag', '--merged', old_main, '--sort=-version:refname').splitlines()
    versions = [tag for tag in tags if re.fullmatch(r'v\d+\.\d+\.\d+', tag)]
    baseline = versions[0] if versions else None
    contributions = []
    for commit in call('git', 'rev-list', '--first-parent', '--reverse', f'{old_main}..{intended_test}').splitlines():
        for item in github('api', f'repos/{repository}/commits/{commit}/pulls'):
            if item['base']['ref'] != 'test' or item['head']['ref'] == 'main' or item['merge_commit_sha'] != commit:
                continue
            labels = [label['name'][7:] for label in item['labels'] if label['name'].startswith('semver:')]
            if len(labels) != 1 or labels[0] not in ('major', 'minor', 'patch', 'none'):
                raise ValueError(f'PR {item["number"]} needs semver metadata review')
            contributions.append(labels[0])
    if not any(item != 'none' for item in contributions):
        print(f'All-none promotion: retain {baseline or "no existing version"}; no new tag.', flush=True)
        return None
    if baseline is None:
        raise ValueError('no established initial version; report bookkeeping for a human decision')
    major, minor, patch = map(int, baseline[1:].split('.'))
    for bump in contributions:
        if bump == 'major':
            major, minor, patch = major + 1, 0, 0
        elif bump == 'minor':
            minor, patch = minor + 1, 0
        elif bump == 'patch':
            patch += 1
    return f'v{major}.{minor}.{patch}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('flow', choices=['pr-to-test', 'promote-to-main'])
    parser.add_argument('--title')
    parser.add_argument('--body-file')
    parser.add_argument('--semver', choices=['major', 'minor', 'patch', 'none'], default='none')
    args = parser.parse_args()
    run.flow = args.flow
    executable_path(sys.executable)
    plain_path(Path.cwd())
    plain_path(call('git', 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    run.revision = sha('HEAD')
    if call('git', 'status', '--porcelain'):
        raise ValueError('use a clean committed checkout; preserve unrelated work elsewhere')
    call('git', 'fetch', '--no-tags', 'origin', capture=False)
    tags_current = True
    if args.flow == 'promote-to-main':
        run.enter('promotion bookkeeping', 'refresh existing version tags')
        try:
            call('git', 'fetch', 'origin', '--tags', capture=False)
        except subprocess.CalledProcessError as error:
            tags_current = False
            run.report(error, terminal=False)
            print('Tag refresh incomplete; inspect version metadata separately from delivery gates.', flush=True)
    run.enter('preflight', 'resolve repository identity')
    repository = github('repo', 'view', '--json', 'nameWithOwner')['nameWithOwner']
    run.repository = repository
    run.enter('source gate', 'run source syntax and staged privacy checks')
    call(bash(), 'scripts/check.sh', capture=False)
    run.confirm(f'source gate passed on {run.revision}')
    run.enter('preflight', 'validate delivery branch and intended revision')
    if args.flow == 'pr-to-test':
        branch = call('git', 'branch', '--show-current')
        if not branch or branch in ('main', 'test'):
            raise ValueError('PR-to-test requires a named task branch')
        intended = sha('HEAD')
        run.enter('push/PR', f'push intended revision {intended}')
        effect = f'push intended revision {intended}'
        run.attempt(effect)
        call('git', 'push', 'origin', f'HEAD:refs/heads/{branch}', capture=False)
        run.confirm(effect)
        number = pr('test', branch, args.title or f'Deliver {branch}', args.body_file, args.semver)
        merge(number, intended, sha('origin/test'))
    else:
        old_main, intended = sha('origin/main'), sha('origin/test')
        if sha('HEAD') != intended:
            raise ValueError('promotion requires a clean checkout of the intended origin/test revision')
        tag = None
        run.enter('promotion bookkeeping', 'classify version from existing tags and test PRs')
        try:
            if tags_current:
                tag = version_for_promotion(repository, old_main, intended)
        except (ValueError, subprocess.CalledProcessError) as error:
            run.report(error, terminal=False)
            print('Version bookkeeping unresolved. Continuing actual delivery gates.', flush=True)
        number = pr('main', 'test', args.title or 'Promote verified test to main', args.body_file, 'none')
        merged = merge(number, intended, old_main)
        if tag:
            run.enter('tag', f'publish version {tag}')
            try:
                effect = f'create local tag {tag} on {merged}'
                run.attempt(effect)
                call('git', 'tag', tag, merged)
                run.confirm(effect)
                effect = f'publish tag {tag}'
                run.attempt(effect)
                call('git', 'push', 'origin', f'refs/tags/{tag}', capture=False)
                run.confirm(effect)
                print(f'Published {tag}', flush=True)
            except subprocess.CalledProcessError as error:
                run.report(error, terminal=False)
                print(f'Tag {tag} publication incomplete; inspect local/remote tags. No tag was moved.', flush=True)
        run.enter('synchronization', 'verify promoted branch state before main-to-test synchronization')
        if sha('origin/test') != intended or sha('origin/main') != merged:
            raise ValueError('branch drift after promotion; inspect before main-to-test synchronization')
        number = pr('test', 'main', 'Synchronize main back to test', None, 'none')
        merge(number, merged, intended)
    print('Delivery verified. Primary handoff pending: finish local required completion, issue bookkeeping '
          'and safe associated-artifact cleanup; apply one consolidated Reflection screen before resolution.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        run.report(error)
        sys.exit(1)
