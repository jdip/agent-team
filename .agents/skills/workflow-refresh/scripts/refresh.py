#!/usr/bin/env python3
"""Print an on-demand workflow reference from immutable public source blobs."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote

REPOSITORY = 'jdip/agent-team'
SOURCE_URL = f'https://github.com/{REPOSITORY}'


def command(*args, cwd=None):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                            encoding='utf-8', timeout=60)
    if result.returncode:
        # CLI diagnostics may include local paths or account details.
        raise ValueError(f'{args[0]} read failed; inspect access and source availability locally')
    return result.stdout


def api(endpoint):
    return json.loads(command('gh', 'api', endpoint))


def link(repository, revision, path):
    return f'https://github.com/{repository}/blob/{revision}/{quote(path, safe="/")}'


def cell(value):
    return html.escape(str(value)).replace('|', '&#124;').replace('\n', '<br>')


def scalar(value):
    value = value.strip()
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if not value or value[0] in '&*![{':
        raise ValueError('unsupported skill metadata scalar; read the authoritative source')
    return value


def metadata(text, policy=''):
    parts = text.split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError('skill frontmatter is missing')
    lines = parts[1].splitlines()
    values = {}
    for index, line in enumerate(lines):
        match = re.match(r'^(name|description|disable-model-invocation|user-invocable):\s*(.*)$', line)
        if not match:
            continue
        key, value = match.groups()
        if key in values:
            raise ValueError('duplicate skill metadata field')
        if value in ('>', '>-', '|', '|-'):
            block = []
            for following in lines[index + 1:]:
                if following and not following[0].isspace():
                    break
                block.append(following.strip())
            value = (' ' if value.startswith('>') else '\n').join(block).strip()
        values[key] = scalar(value)
    if not all(isinstance(values.get(key), str) and values[key] for key in ('name', 'description')):
        raise ValueError('skill name or description is missing')
    constraints = []
    if values.get('disable-model-invocation') == 'true':
        constraints.append('explicit user invocation')
    if values.get('user-invocable') == 'false':
        constraints.append('user invocation disabled')
    if re.search(r'^\s+allow_implicit_invocation:\s*false\s*$', policy, re.M):
        constraints.append('implicit invocation disabled by agents/openai.yaml')
    return values['name'], values['description'], '; '.join(constraints) or 'default discovery'


def profile_inventory(profile):
    # PROFILE.md owns these tables; use the same table layout as reconciliation.
    local_section = profile.split('## Copied local packages\n')[1].split('## Upstream packages\n')[0]
    local = [line.split('|')[1].strip() for line in local_section.splitlines()
             if line.startswith('| ') and not line.startswith('| ---')][1:]
    upstream_section = profile.split('## Upstream packages\n')[1].split('## Optional Claude Code configuration\n')[0]
    repository = re.search(r'Source: \[.*?\]\(https://github.com/([\w.-]+/[\w.-]+)\)', upstream_section)
    pin = re.search(r'Shared reviewed pin: `([0-9a-f]{40})`', upstream_section)
    upstream = re.findall(r'^\| ([\w-]+) \| (skills/[\w/-]+) \|$', upstream_section, re.M)
    if not local or len(set(local)) != len(local) or not repository or not pin or not upstream:
        raise ValueError('Machine Profile inventory is incomplete or has changed structure')
    return set(local), repository[1], pin[1], upstream


class Source:
    def __init__(self, root, revision):
        self.root = root
        self.revision = revision
        self.files = {}
        listing = command('git', 'ls-tree', '-rz', '--full-tree', revision, cwd=root)
        for entry in listing.split('\0'):
            if entry:
                info, path = entry.split('\t', 1)
                self.files[path] = info.split()[0]

    def read(self, path):
        if self.files.get(path) not in ('100644', '100755'):
            raise ValueError(f'regular source file unavailable: {path}')
        return command('git', 'show', f'{self.revision}:{path}', cwd=self.root)


def verified_test():
    revision = api(f'repos/{REPOSITORY}/git/ref/heads/test')['object']['sha']
    pages = json.loads(command('gh', 'api', '--paginate', '--slurp',
                               f'repos/{REPOSITORY}/commits/{revision}/check-runs?per_page=100'))
    checks = [check for page in pages for check in page['check_runs'] if check['name'] == 'validate']
    if not checks:
        raise ValueError('current test revision has no validate evidence; no verified snapshot produced')
    check = max(checks, key=lambda item: item['id'])
    if check['status'] != 'completed' or check['conclusion'] != 'success':
        raise ValueError('current test revision has not passed validate; no verified snapshot produced')
    return revision, check['html_url']


def skills(source, managed):
    rows = []
    found = set()
    for path in sorted(source.files):
        if not path.endswith('/SKILL.md') or not path.startswith(('machine/skills/', '.agents/skills/')):
            continue
        directory = path.rsplit('/', 1)[0]
        policy_path = f'{directory}/agents/openai.yaml'
        policy = source.read(policy_path) if policy_path in source.files else ''
        name, description, invocation = metadata(source.read(path), policy)
        if path.startswith('machine/skills/'):
            identity = directory.split('/')[2]
            found.add(identity)
            scope = 'managed portable' if identity in managed else 'portable source; outside Profile'
        else:
            scope = 'repository-local; outside Profile'
        helpers = [f'[{cell(p.rsplit("/", 1)[-1])}]({link(REPOSITORY, source.revision, p)})'
                   for p in sorted(source.files) if p.startswith(f'{directory}/scripts/')]
        if policy:
            invocation += f' ([policy]({link(REPOSITORY, source.revision, policy_path)}))'
        rows.append(f'| [{cell(name)}]({link(REPOSITORY, source.revision, path)}) | {scope} | '
                    f'{cell(description)} | {invocation} | {", ".join(helpers) or "—"} |')
    if managed - found:
        raise ValueError('a managed skill declared in the Machine Profile is missing from the source')
    return rows


def upstream_skills(repository, pin, packages):
    rows = []
    try:
        tree = api(f'repos/{repository}/git/trees/{pin}?recursive=1')
        if tree.get('truncated'):
            raise ValueError('upstream tree is truncated')
        files = {entry['path']: entry['mode'] for entry in tree['tree'] if entry['type'] == 'blob'}
    except (ValueError, KeyError):
        files = None
    for identity, directory in packages:
        path = f'{directory}/SKILL.md'
        try:
            if files is None or files.get(path) not in ('100644', '100755'):
                raise ValueError('upstream source inventory unavailable')
            def read(relative):
                content = api(f'repos/{repository}/contents/{relative}?ref={pin}')
                return base64.b64decode(content['content']).decode('utf-8')
            policy_path = f'{directory}/agents/openai.yaml'
            policy = read(policy_path) if policy_path in files else ''
            name, description, invocation = metadata(read(path), policy)
            if name != identity:
                raise ValueError('upstream identity differs from Profile')
            if policy:
                invocation += f' ([policy]({link(repository, pin, policy_path)}))'
            helpers = [f'[{cell(p.rsplit("/", 1)[-1])}]({link(repository, pin, p)})'
                       for p in sorted(files) if p.startswith(f'{directory}/scripts/')]
            detail = cell(description)
        except (ValueError, KeyError, UnicodeError):
            name, detail, invocation, helpers = identity, 'Metadata unavailable; read pinned source', 'unverified', []
        rows.append(f'| [{cell(name)}]({link(repository, pin, path)}) | {detail} | '
                    f'{invocation} | {", ".join(helpers) or "—"} |')
    return rows


def reference(source, revision, check_url, observed):
    profile = source.read('machine/PROFILE.md')
    managed, upstream_repository, pin, packages = profile_inventory(profile)
    rows = skills(source, managed)
    upstream = upstream_skills(upstream_repository, pin, packages)
    output = [
        '# Agent Team workflow reference', '',
        f'Source: [{REPOSITORY}]({SOURCE_URL}), commit `{revision}`.',
        f'Observed: {observed}.',
        f'Verification: [current test validate succeeded]({check_url}).' if check_url else
        'Verification: explicit candidate revision; test delivery and freshness are unverified.',
        '', 'This snapshot indexes instructions. Read the selected skill and its relevant companions '
        'before acting; its authorization and completion boundaries still apply. '
        'The entries describe source packages, not installation or session tool availability.',
        '', '## Authoritative entry points', '',
    ]
    entries = ['AGENTS.md', 'SECURITY.md', 'README.md', 'machine/AGENTS.md', 'machine/PROFILE.md',
               'docs/agents/issue-tracker.md', 'docs/development.md']
    entries += sorted(p for p in source.files if p.startswith('docs/workflows/') and p.endswith('.md'))
    for path in entries:
        text = source.read(path)
        headings = re.findall(r'^## (.+)$', text, re.M)
        output.append(f'- [{path}]({link(REPOSITORY, revision, path)}): {cell("; ".join(headings)) or "entry instructions"}.')
    output += ['', '## Repository skills', '',
               '| Skill | Source scope | Description and trigger | Invocation | Helpers |',
               '| --- | --- | --- | --- | --- |', *rows,
               '', f'## Upstream skills at `{pin}`', '',
               f'The [Machine Profile]({link(REPOSITORY, revision, "machine/PROFILE.md")}) owns '
               'these identities and their reviewed pin. Unavailable metadata is explicit; local installed copies are not substituted.',
               '', '| Skill | Description and trigger | Invocation | Helpers |',
               '| --- | --- | --- | --- |', *upstream,
               '', '## Repository workflow scripts', '']
    for path in sorted(source.files):
        if path.startswith('scripts/') and path.endswith(('.sh', '.py')):
            output.append(f'- [{path}]({link(REPOSITORY, revision, path)})')
    output += ['', '## Freshness and capability', '',
               'Refresh before a new orchestration decision or after a relevant workflow change. '
               'Compare the commit with a fresh test lookup; elapsed time alone does not establish freshness. '
               'An access failure leaves freshness unverified and does not authorize another identity or route.',
               '', 'Verify the executing session’s skill catalog, tools and permissions separately. '
               'Read relevant repository-local SKILL.md files even when absent from that catalog. '
               'Keep installation comparisons and private host details in local task context. '
               'This reference grants no machine reconciliation, main promotion or scheduling authority.', '']
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path.cwd(), help='Agent Team Git checkout')
    parser.add_argument('--candidate', help='explicit full commit SHA for local validation; never claims test verification')
    args = parser.parse_args()
    try:
        root = command('git', 'rev-parse', '--show-toplevel', cwd=args.repository).strip()
        remote = command('git', 'remote', 'get-url', 'origin', cwd=root).strip()
        if remote not in (f'{SOURCE_URL}.git', SOURCE_URL, f'git@github.com:{REPOSITORY}.git'):
            raise ValueError('origin is not the canonical Agent Team repository')
        if args.candidate:
            revision, check_url = args.candidate, None
        else:
            revision, check_url = verified_test()
        if not re.fullmatch(r'[0-9a-f]{40}', revision):
            raise ValueError('source must be an explicit full commit SHA')
        source = Source(root, revision)
        observed = datetime.now(timezone.utc).isoformat(timespec='seconds')
        result = reference(source, revision, check_url, observed)
        if check_url and api(f'repos/{REPOSITORY}/git/ref/heads/test')['object']['sha'] != revision:
            raise ValueError('test changed during refresh; inspect the new revision before refreshing again')
        print(result)
    except OSError:
        print('error: local source or required command unavailable; inspect the checkout and Git/gh locally',
              file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print('error: source read timed out; inspect repository access before refreshing again', file=sys.stderr)
        return 1
    except (ValueError, KeyError, IndexError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
