#!/usr/bin/env python3
"""Narrow filesystem helpers for supervised Machine Reconciliation (Python 3.11+)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import tomllib


def parse_resolution(value):
    target, separator, observation = value.rpartition('=')
    if not separator or not target or not (
            observation == 'absent' or re.fullmatch(r'[0-9a-f]{64}', observation)):
        raise argparse.ArgumentTypeError(
            'expected --resolve TARGET=OBSERVED_SHA256_OR_absent '
            '(nonempty target and a lowercase SHA256 or absent); no managed writes were made')
    return target, observation


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()



def cleanup_schedule_fingerprint(configuration):
    """Hash only the normalized owned configuration supplied by the schedule adapter."""
    return None if configuration is None else digest(encoded(configuration))


def cleanup_schedule_preflight(entry, identity, configuration, approved_observation=None):
    """The schedule adapter calls this before the shared all-target write gate."""
    current = cleanup_schedule_fingerprint(configuration)
    if entry is not None and (entry['target'] != identity or entry['scope'] != {'kind': 'cleanup-schedule'}):
        raise ValueError('cleanup schedule identity/scope changed; investigate')
    conflict = (entry is None and current is not None) or (entry is not None and current != entry['fingerprint'])
    if conflict and approved_observation != (current or 'absent'):
        raise ValueError(f'cleanup schedule {identity}: observed={current}; supervised decision required')
    return current


def cleanup_schedule_entry(identity, observed_after_write):
    """Call only after the adapter observes its authorized successful write."""
    if observed_after_write is None:
        raise ValueError('cannot receipt a missing cleanup schedule')
    return {'target': identity, 'scope': {'kind': 'cleanup-schedule'},
            'algorithm': 'sha256', 'fingerprint': cleanup_schedule_fingerprint(observed_after_write)}

def plain_path(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'symlink requires investigation: {part}')
    return path


def files(path):
    plain_path(path)
    result = {}
    for p in sorted(path.rglob('*')):
        plain_path(p)
        if p.is_file():
            result[p.relative_to(path).as_posix()] = p.read_bytes()
        elif not p.is_dir():
            raise ValueError(f'unsupported directory entry: {p}')
    return result


def flatten(value, prefix=()):
    result = {}
    for key, item in value.items():
        name = prefix + (key,)
        if isinstance(item, dict) and item:
            result.update(flatten(item, name))
        else:
            result[name] = item
    return result


def projection(path, fields):
    data = flatten(tomllib.loads(path.read_text())) if path.exists() else {}
    # Types matter: true, 1, and "1" must not compare equal.
    return {key: [type(data[tuple(key.split('.'))]).__name__, repr(data[tuple(key.split('.'))])]
            if tuple(key.split('.')) in data else ['absent'] for key in sorted(fields)}


def fingerprint(path, scope):
    if scope.get('kind') not in ('file', 'directory', 'toml'):
        raise ValueError('unknown scope requires its target-specific adapter before filesystem inspection')
    path = plain_path(path)
    if not path.exists():
        return None
    if scope['kind'] == 'file':
        if not path.is_file():
            raise ValueError(f'expected ordinary file: {path}')
        return digest(path.read_bytes())
    if scope['kind'] == 'directory':
        if not path.is_dir():
            raise ValueError(f'expected directory: {path}')
        return digest(encoded({name: digest(data) for name, data in files(path).items()}))
    if scope['kind'] == 'toml':
        return digest(encoded(projection(path, scope['fields'])))
    raise ValueError(f'unsupported scope requires its target-specific adapter: {path}')


def atomic_file(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.reconcile-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def table(section):
    return [line.split('|')[1].strip() for line in section.splitlines()
            if line.startswith('| ') and not line.startswith('| ---')][1:]


def claude_packages(profile):
    copied = profile.split('### Claude copied packages\n')[1].split('### Claude upstream packages\n')[0]
    upstream = profile.split('### Claude upstream packages\n')[1].split('## Preflight, publication, and retirement\n')[0]
    return table(copied), re.findall(r'^\| ([\w-]+) \| (skills/[\w/-]+) \|$', upstream, re.M)


def claude_receipt_root(entries):
    anchors = [target for target, entry in entries.items()
               if entry['scope'] == {'kind': 'file'}
               and Path(target).name == 'agent-team.md' and Path(target).parent.name == 'rules']
    if not anchors:
        return None, set()
    if len(anchors) != 1:
        raise ValueError('multiple Claude receipt anchors require investigation')
    anchor = anchors[0]
    root = plain_path(Path(anchor).parent.parent)
    skills = root / 'skills'
    targets = set()
    for target, entry in entries.items():
        path = Path(target)
        if root not in path.parents:
            continue
        valid = (path == root / 'rules/agent-team.md' and entry['scope'] == {'kind': 'file'}) or (
            path.parent == skills and entry['scope'] == {'kind': 'directory'})
        if not valid:
            raise ValueError(f'{target}: unexpected receipted target under Claude configuration root')
        targets.add(target)
    if anchor not in targets:
        raise ValueError('Claude receipt anchor requires investigation')
    return root, targets


def inventory(source, home, skills, upstream, upstream_root=None, claude_root=None):
    profile = (source / 'machine/PROFILE.md').read_text()
    config = source / 'machine/config.toml'
    fields = sorted('.'.join(key) for key in flatten(tomllib.loads(config.read_text())))
    rows = [(config, home / 'config.toml', {'kind': 'toml', 'fields': fields})]
    section = profile.split('## Shared configuration and whole files\n')[1].split('## Copied local packages\n')[0]
    for name in table(section):
        rows.append((source / 'machine' / name, home / name, {'kind': 'file'}))
    section = profile.split('## Copied local packages\n')[1].split('## Upstream packages\n')[0]
    for name in table(section):
        rows.append((source / 'machine/skills' / name, skills / name, {'kind': 'directory'}))
    section = profile.split('## Upstream packages\n')[1].split('## Optional Claude Code configuration\n')[0]
    pin = re.search(r'Shared reviewed pin: `([0-9a-f]{40})`', section).group(1)
    packages = re.findall(r'^\| ([\w-]+) \| (skills/[\w/-]+) \|$', section, re.M)
    for name, _ in packages:
        rows.append((upstream / name if upstream else None, (upstream_root or skills) / name, {'kind': 'directory'}))
    if claude_root is not None:
        copied, claude_upstream = claude_packages(profile)
        codex_upstream = dict(packages)
        if any(codex_upstream.get(name) != path for name, path in claude_upstream):
            raise ValueError('Claude upstream package is not an exact subset of the staged Codex upstream inventory')
        rows.append((source / 'machine/AGENTS.md', claude_root / 'rules/agent-team.md', {'kind': 'file'}))
        for name in copied:
            rows.append((source / 'machine/skills' / name, claude_root / 'skills' / name, {'kind': 'directory'}))
        for name, _ in claude_upstream:
            rows.append((upstream / name if upstream else None, claude_root / 'skills' / name, {'kind': 'directory'}))
    targets = [str(plain_path(row[1])) for row in rows]
    if len(set(targets)) != len(targets):
        raise ValueError('duplicate profile target')
    if len(fields) != 9:
        raise ValueError('expected nine managed configuration fields; inspect the declaration')
    return rows, pin, packages


def verify_upstream(stage, pin, packages):
    tree = json.loads(subprocess.check_output([
        'gh', 'api', f'repos/mattpocock/skills/git/trees/{pin}?recursive=1']))
    if tree.get('truncated'):
        raise ValueError('upstream tree response is truncated')
    for name, prefix in packages:
        expected = {item['path'][len(prefix)+1:]: item for item in tree['tree']
                    if item['path'].startswith(prefix + '/') and item['type'] != 'tree'}
        actual = files(stage / name)
        if 'SKILL.md' not in actual or actual.keys() != expected.keys():
            raise ValueError(f'incomplete staged package: {name}')
        for relative, data in actual.items():
            item = expected[relative]
            blob = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
            if item['type'] != 'blob' or item['mode'] not in ('100644', '100755') or blob != item['sha']:
                raise ValueError(f'staged package differs from pin: {name}/{relative}')


def read_receipt(path):
    plain_path(path)
    raw = path.read_bytes() if path.exists() else None
    receipt = json.loads(raw) if raw is not None else {'version': 1, 'entries': []}
    if receipt.get('version') != 1 or set(receipt) != {'version', 'entries'}:
        raise ValueError('unknown receipt format')
    entries = {}
    for entry in receipt['entries']:
        if set(entry) != {'target', 'scope', 'algorithm', 'fingerprint'} or entry['algorithm'] != 'sha256':
            raise ValueError('unknown receipt entry')
        if entry['scope'] == {'kind': 'cleanup-schedule'}:
            target = entry['target']
            if not isinstance(target, str) or not target.startswith(('automation:', 'cron:')):
                raise ValueError('unknown cleanup schedule identity')
        else:
            target = str(plain_path(entry['target']))
        if target != entry['target'] or target in entries:
            raise ValueError('ambiguous receipt target')
        entries[target] = entry
    return raw, entries


def unmanaged_projection(data, managed, retired):
    """Return the unowned TOML values while ignoring empty owned containers."""
    owned = {tuple(field.split('.')) for field in managed | retired}
    containers = {key[:i] for key in owned for i in range(1, len(key))}
    return {key: [type(value).__name__, repr(value)] for key, value in data.items()
            if key not in owned and not (key in containers and value == {})}


def verify_candidate_config(candidate, source, original, scope, previous_scope=()):
    """Prove a complete candidate changes only the owned configuration fields."""
    candidate_data = flatten(tomllib.loads(candidate.read_text()))
    original_data = flatten(tomllib.loads(original.read_text())) if original.exists() else {}
    managed = set(scope['fields'])
    retired = set(previous_scope) - managed
    if any(tuple(key.split('.')) in candidate_data for key in retired):
        raise ValueError('candidate config retains retired managed fields')
    if projection(candidate, managed) != projection(source, managed):
        raise ValueError('candidate config does not have the declared managed values')
    if unmanaged_projection(candidate_data, managed, retired) != unmanaged_projection(original_data, managed, retired):
        raise ValueError('candidate config changes unmanaged configuration')


def run(args):
    source = plain_path(args.source)
    home = plain_path(args.codex_home)
    skills = plain_path(args.skills_root)
    upstream_root = plain_path(args.upstream_root) if args.upstream_root else skills
    stage = plain_path(args.upstream_stage) if args.upstream_stage else None
    claude_root = plain_path(args.claude_config_root) if args.claude_config_root else None
    receipt_path = home / '.agent-team/reconciliation-receipts-v1.json'
    raw_receipt, entries = read_receipt(receipt_path)
    anchored_claude_root, preserved_claude_targets = claude_receipt_root(entries)
    if claude_root is not None and anchored_claude_root is not None and claude_root != anchored_claude_root:
        raise ValueError('Claude configuration root disagrees with the receipt anchor; investigate before writes')
    if claude_root is not None:
        preserved_claude_targets = set()
    rows, pin, packages = inventory(source, home, skills, stage, upstream_root, claude_root)
    approvals = dict(args.resolve)
    errors, observed, desired = [], {}, {}
    if (home / 'AGENTS.override.md').exists() or (home / 'AGENTS.override.md').is_symlink():
        errors.append('AGENTS.override.md interferes with global instructions; preserve and investigate')
    for candidate, target, scope in rows:
        target = plain_path(target)
        desired[str(target)] = (candidate, scope)
        if candidate is None or not candidate.exists():
            errors.append(f'missing declared source: {candidate or "upstream staging"}')
        else:
            fingerprint(candidate, scope)
    # Retired entries remain in the same all-target gate, with their old scope.
    for target in desired.keys() | entries.keys():
        old = entries.get(target)
        if old and old['scope'] == {'kind': 'cleanup-schedule'}:
            continue
        scope = old['scope'] if old else desired[target][1]
        current = fingerprint(Path(target), scope)
        observed[target] = (scope, current)
        expected = old['fingerprint'] if old else None
        conflict = (old is not None and current != expected) or (old is None and current is not None)
        gate_scope = scope
        if old and target in desired and old['scope'] != desired[target][1]:
            new_scope = desired[target][1]
            if scope['kind'] != 'toml' or new_scope['kind'] != 'toml':
                errors.append(f'{target}: ownership kind changed; investigate before migration')
            else:
                added = set(new_scope['fields']) - set(scope['fields'])
                if any(v != ['absent'] for v in projection(Path(target), added).values()):
                    conflict = True
                gate_scope = {'kind': 'toml', 'fields': sorted(set(scope['fields']) | set(new_scope['fields']))}
        gate_current = fingerprint(Path(target), gate_scope)
        observed[target] = (gate_scope, gate_current)
        if conflict and approvals.get(target) != (gate_current or 'absent'):
            errors.append(f'{target}: scope={scope} saved={expected} observed={gate_current}; supervised decision required')
        if target not in desired and scope['kind'] == 'toml':
            errors.append(f'{target}: retired config target requires supervised relocation; no writes')
    targets = [Path(target) for target in observed]
    if any(a != b and a in b.parents for a in targets for b in targets):
        errors.append('overlapping current or retired scopes require investigation')
    if any(receipt_path == path or path in receipt_path.parents for path in targets):
        errors.append('receipt metadata overlaps a managed target')
    unknown = approvals.keys() - observed.keys()
    if unknown:
        errors.append(f'authorization refers to unknown targets: {sorted(unknown)}')
    preserved_approvals = approvals.keys() & preserved_claude_targets
    if preserved_approvals:
        errors.append('Claude is absent; preserved receipt scopes cannot be resolved or retired')
    if errors:
        raise ValueError('\n'.join(errors))
    if not args.apply:
        print('All declared sources and live target/retirement scopes passed preflight; no writes.')
        return
    if not args.models_verified:
        raise ValueError('supervisor must verify target model/effort availability before applying')
    if stage is None:
        raise ValueError('verified upstream staging is required')
    discovery_roots = [skills, upstream_root, home / 'skills']
    if claude_root is not None:
        discovery_roots.append(claude_root / 'skills')
    if any(stage == root or root in stage.parents or stage.parent == root for root in discovery_roots):
        raise ValueError('upstream staging must be outside skill discovery')
    verify_upstream(stage, pin, packages)
    config_target = str(home / 'config.toml')
    candidate_config = plain_path(args.candidate_config) if args.candidate_config else None
    if candidate_config is None:
        raise ValueError('supply the supervisor-prepared complete candidate config')
    source_config, config_scope = desired[config_target]
    original_config = home / 'config.toml'
    original_config_bytes = (home / 'config.toml').read_bytes() if (home / 'config.toml').exists() else None
    previously_managed = set(entries.get(config_target, {}).get('scope', {}).get('fields', []))
    verify_candidate_config(candidate_config, source_config, original_config, config_scope,
                            previously_managed)
    desired[config_target] = (candidate_config, config_scope)
    # Snapshot candidates before mutation. The source worktree must represent the
    # single revision selected by the supervisor, with no uncommitted edits.
    if subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain']):
        raise ValueError('source checkout has uncommitted changes; select a clean revision')
    prepared_files = {target: candidate.read_bytes() for target, (candidate, scope) in desired.items()
                      if scope['kind'] != 'directory'}
    prepared = {}
    try:
        # Prepare complete copies off discovery before any live target is touched.
        for target, (candidate, scope) in desired.items():
            if candidate == Path(target) or Path(target) in candidate.parents:
                raise ValueError(f'candidate overlaps live target: {target}')
            if scope['kind'] == 'directory':
                root = stage.parent
                nearest = Path(target).parent
                while not nearest.exists():
                    nearest = nearest.parent
                if root.stat().st_dev != nearest.stat().st_dev:
                    raise ValueError(f'staging is not on destination filesystem: {target}')
                temporary = Path(tempfile.mkdtemp(prefix='.agent-team-publish-', dir=root))
                prepared[target] = temporary / 'package'
                shutil.copytree(candidate, prepared[target], symlinks=False)
                if fingerprint(prepared[target], scope) != fingerprint(candidate, scope):
                    raise ValueError(f'prepared copy mismatch: {target}')
        for target in observed:
            scope, expected = observed[target]
            if fingerprint(Path(target), scope) != expected:
                raise ValueError(f'target changed after preflight: {target}')
        def publication_order(target):
            path = Path(target)
            if claude_root is not None and path == claude_root / 'rules/agent-team.md':
                return 0, target
            if claude_root is not None and claude_root / 'skills' in path.parents:
                return 2, target
            return 1, target

        for target in sorted(observed, key=publication_order):
            path = Path(target)
            scope, expected = observed[target]
            now_raw, _ = read_receipt(receipt_path)
            if now_raw != raw_receipt or fingerprint(path, scope) != expected:
                raise ValueError(f'state changed immediately before write: {target}')
            if target == config_target and (path.read_bytes() if path.exists() else None) != original_config_bytes:
                raise ValueError('shared config changed, including unmanaged fields; prepare it again')
            if target in preserved_claude_targets:
                continue
            if target not in desired:
                if scope['kind'] == 'toml':
                    raise ValueError('retiring TOML fields requires a reviewed candidate config and scope migration')
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink(missing_ok=True)
                if path.exists():
                    raise ValueError(f'retirement incomplete: {target}')
                entries.pop(target, None)
                print(f'Retired {target}', flush=True)
            else:
                candidate, new_scope = desired[target]
                if new_scope['kind'] == 'directory':
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if path.exists():
                        shutil.rmtree(path)
                        print(f'Removed old directory {target}; replacement and receipt pending', flush=True)
                    os.rename(prepared[target], path)
                    print(f'Published directory {target}; verification and receipt pending', flush=True)
                else:
                    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
                    atomic_file(path, prepared_files[target], mode)
                    print(f'Replaced file {target}; verification and receipt pending', flush=True)
                actual = fingerprint(path, new_scope)
                if actual != fingerprint(candidate, new_scope):
                    raise ValueError(f'installed result mismatch: {target}')
                entries[target] = {'target': target, 'scope': new_scope,
                                   'algorithm': 'sha256', 'fingerprint': actual}
                print(f'Wrote {target}', flush=True)
            atomic_file(receipt_path, encoded({'version': 1, 'entries': list(entries.values())}) + b'\n')
            raw_receipt = receipt_path.read_bytes()
    finally:
        for path in prepared.values():
            shutil.rmtree(path.parent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--codex-home', required=True)
    parser.add_argument('--skills-root', required=True)
    parser.add_argument('--upstream-root', help='resolved installer destination, if different from copied skills')
    parser.add_argument('--claude-config-root', help='proven effective Claude configuration root')
    parser.add_argument('--upstream-stage')
    parser.add_argument('--candidate-config')
    parser.add_argument('--models-verified', action='store_true')
    parser.add_argument('--resolve', action='append', type=parse_resolution, default=[],
                        metavar='TARGET=OBSERVED_SHA256_OR_absent')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        run(args)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        outcome = ('Printed removals/publications are partial effects; receipt publication may be incomplete. '
                   'Inspect actual state before retrying.' if args.apply else 'No managed writes were made.')
        parser.exit(1, f'Reconciliation stopped: {error}\n{outcome}\n')


if __name__ == '__main__':
    main()
