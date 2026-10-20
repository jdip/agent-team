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
import sys
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


def cleanup_schedule_identity(identity):
    if not isinstance(identity, str):
        return False
    if identity.startswith('automation:'):
        name = identity.removeprefix('automation:')
        return (bool(name) and name not in ('.', '..') and '/' not in name
                and (os.name != 'nt' or ('\\' not in name and ':' not in name)))
    if identity.startswith('cron:'):
        return len(identity) > len('cron:')
    return bool(re.fullmatch(r'task-scheduler:\\AgentTeamCleanup-[0-9a-f]{64}', identity))


def _mountinfo_path(value):
    return re.sub(r'\\([0-7]{3})', lambda match: chr(int(match.group(1), 8)), value)


def _wsl_mounts():
    if sys.platform != 'linux' or 'microsoft' not in os.uname().release.casefold():
        return ()
    try:
        mountinfo = Path('/proc/self/mountinfo').read_text(encoding='utf-8')
    except OSError as error:
        raise ValueError('cannot inspect the WSL mount table') from error
    mounts = []
    for line in mountinfo.splitlines():
        before, separator, after = line.partition(' - ')
        fields = before.split()
        filesystem = after.split(maxsplit=2)
        if not separator or len(fields) < 5 or len(filesystem) < 3:
            raise ValueError('WSL mount table is malformed')
        mounts.append((Path(_mountinfo_path(fields[4])),
                       filesystem[0] == '9p' and 'aname=drvfs' in filesystem[2]))
    return tuple(mounts)


def _on_drvfs(path):
    path = Path(os.path.abspath(path))
    matches = [(mount, drvfs) for mount, drvfs in _wsl_mounts()
               if path == mount or mount in path.parents]
    return bool(matches) and max(matches, key=lambda item: len(item[0].parts))[1]


def plain_path(path):
    if os.name == 'nt':
        value = os.fspath(path)
        # Accept the ordinary extended-length local spelling, but never a
        # network, device, drive-relative, or other environment's root.
        if value.startswith('\\\\?\\') and re.match(r'^[A-Za-z]:[\\/]', value[4:]):
            value = value[4:]
        candidate = Path(value)
        if ((candidate.drive and not re.fullmatch(r'[A-Za-z]:', candidate.drive))
                or bool(candidate.drive) != bool(candidate.root)):
            raise ValueError(f'expected a local Windows path with an unambiguous root: {path}')
        path = candidate
    path = Path(os.path.abspath(path))
    if _on_drvfs(path):
        raise ValueError(f'path is on a Windows-mounted DrvFS volume: {path}')
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes

        drive_type = ctypes.WinDLL('kernel32', use_last_error=True).GetDriveTypeW
        drive_type.argtypes = [wintypes.LPCWSTR]
        drive_type.restype = wintypes.UINT
        if drive_type(path.anchor) not in (2, 3, 5, 6):
            raise ValueError(f'path is not on an established local drive: {path}')
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'symlink requires investigation: {part}')
        if os.name == 'nt':
            try:
                attributes = part.lstat().st_file_attributes
            except FileNotFoundError:
                continue
            if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError(f'reparse point requires investigation: {part}')
    # Resolve existing Windows spelling/aliases only after rejecting redirection.
    # Keep POSIX spelling unchanged so existing receipt identities stay valid.
    return path.resolve(strict=False) if os.name == 'nt' else path


def executable_path(path):
    """Validate a native command without resolving POSIX launcher symlinks."""
    executable = plain_path(path) if os.name == 'nt' else Path(os.path.abspath(path))
    if _on_drvfs(executable.resolve(strict=False)):
        raise ValueError(f'executable is on a Windows-mounted DrvFS volume: {executable}')
    return executable


def command_path(name):
    executable = shutil.which(name)
    if executable is None:
        raise ValueError(f'{name} executable is unavailable')
    return executable_path(executable)


def same_path(left, right):
    """Compare canonical paths without WindowsPath's unconditional case folding."""
    return str(left) == str(right)


def path_within(path, parent):
    return any(same_path(ancestor, parent) for ancestor in path.parents)


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


def projection(path, fields, kind='toml'):
    text = path.read_text(encoding='utf-8') if path.exists() else None
    document = (tomllib.loads(text) if kind == 'toml' else json.loads(text)) if text is not None else {}
    if not isinstance(document, dict):
        raise ValueError(f'expected a {kind} object: {path}')
    data = flatten(document)
    # Types matter: true, 1, and "1" must not compare equal.
    return {key: [type(data[tuple(key.split('.'))]).__name__, repr(data[tuple(key.split('.'))])]
            if tuple(key.split('.')) in data else ['absent'] for key in sorted(fields)}


def fingerprint(path, scope):
    if scope.get('kind') not in ('file', 'directory', 'toml', 'json', 'shell-hook'):
        raise ValueError('unknown scope requires its target-specific adapter before filesystem inspection')
    path = plain_path(path)
    if not path.exists():
        return None
    if scope['kind'] == 'shell-hook':
        from shell_integration import hook_fingerprint
        return hook_fingerprint(path, scope)
    if scope['kind'] == 'file':
        if not path.is_file():
            raise ValueError(f'expected ordinary file: {path}')
        content = path.read_bytes()
        if scope.get('executable') and os.name != 'nt':
            return digest(encoded({'sha256': digest(content), 'mode': stat.S_IMODE(path.stat().st_mode)}))
        return digest(content)
    if scope['kind'] == 'directory':
        if not path.is_dir():
            raise ValueError(f'expected directory: {path}')
        contents = files(path)
        if scope.get('modes') and os.name != 'nt':
            entries = {name: {'sha256': digest(data), 'mode': stat.S_IMODE((path / name).stat().st_mode)}
                       for name, data in contents.items()}
            directories = {p.relative_to(path).as_posix(): stat.S_IMODE(p.stat().st_mode)
                           for p in (path, *path.rglob('*')) if p.is_dir()}
            return digest(encoded({'files': entries, 'directories': directories}))
        return digest(encoded({name: digest(data) for name, data in contents.items()}))
    if scope['kind'] == 'json' and 'resources' in scope:
        from pi_runtime import settings_projection
        document = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(document, dict):
            raise ValueError('Pi settings must be a JSON object')
        return digest(encoded(settings_projection(document, scope)))
    if scope['kind'] in ('toml', 'json'):
        return digest(encoded(projection(path, scope['fields'], scope['kind'])))
    raise ValueError(f'unsupported scope requires its target-specific adapter: {path}')


def atomic_file(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    secured_reference = os.name == 'nt' and path.exists()
    if secured_reference:
        temporary = path.parent / f'.reconcile-{os.urandom(16).hex()}'
        fd = None
    else:
        fd, temporary = tempfile.mkstemp(prefix='.reconcile-', dir=path.parent)
    created_temporary = not secured_reference
    retain_temporary = False
    try:
        if secured_reference:
            from windows_security import create_file

            fd = create_file(temporary, path)
            created_temporary = True
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if os.name == 'nt' and path.exists():
            from windows_security import replace_file

            # ReplaceFileW can report partial effects. Retain any surviving
            # replacement on failure so the supervisor can inspect actual state.
            retain_temporary = True
            replace_file(Path(temporary), path)
            retain_temporary = False
        else:
            if os.name != 'nt':
                os.chmod(temporary, mode)
            os.replace(temporary, path)
    finally:
        if created_temporary and not retain_temporary:
            Path(temporary).unlink(missing_ok=True)
        elif retain_temporary and Path(temporary).exists():
            print(f'File replacement retained for investigation: {temporary}', flush=True)


def table(section):
    return [line.split('|')[1].strip() for line in section.splitlines()
            if line.startswith('| ') and not line.startswith('| ---')][1:]


def upstream_sources(profile):
    section = profile.split('## Upstream packages\n')[1].split('## Optional Claude Code configuration\n')[0]
    sources = []
    for group in section.split('\n### '):
        packages = re.findall(r'^\| ([\w-]+) \| (skills/[\w/-]+) \|$', group, re.M)
        if not packages:
            continue
        repository = re.search(r'^Source: \[[^\]]+\]\(https://github.com/([\w.-]+/[\w.-]+)\)\.$', group, re.M)
        pin = re.search(r'Shared reviewed pin: `([0-9a-f]{40})`', group)
        if not repository or (not pin and 'Update policy: latest default-branch commit on each reconciliation.' not in group):
            raise ValueError('upstream declaration requires a repository and reviewed pin or explicit latest policy')
        sources.append((repository.group(1), pin.group(1) if pin else None, packages))
    names = [name for _, _, packages in sources for name, _ in packages]
    floating = [packages for _, ref, packages in sources if ref is None]
    if len(names) != len(set(names)) or len(floating) != 1 or [name for name, _ in floating[0]] != ['herdr']:
        raise ValueError('expected unique upstream identities and Herdr as the sole latest source')
    return sources


def parse_commit_ref(value):
    if not re.fullmatch(r'[0-9a-f]{40}', value):
        raise argparse.ArgumentTypeError('expected a full lowercase Git commit SHA')
    return value


def claude_packages(profile):
    copied = profile.split('### Claude copied packages\n')[1].split('### Claude upstream packages\n')[0]
    upstream = profile.split('### Claude upstream packages\n')[1].split('## Preflight, publication, and retirement\n')[0]
    return table(copied), re.findall(r'^\| ([\w-]+) \| (skills/[\w/-]+) \|$', upstream, re.M)


def claude_receipt_root(entries, migration_scopes=None):
    anchors = []
    for target, entry in entries.items():
        if entry['scope'] != {'kind': 'file'}:
            continue
        path = Path(target)
        if path.name == 'agent-team.md' and path.parent.name == 'rules':
            anchors.append(target)
        elif (os.name == 'nt' and path.name.casefold() == 'agent-team.md'
              and path.parent.name.casefold() == 'rules'):
            expected = plain_path(path.parent.parent / 'rules/agent-team.md')
            if not same_path(path, expected):
                raise ValueError('ambiguous Claude receipt anchor spelling; preserve and investigate')
            anchors.append(target)
    if not anchors:
        return None, set()
    if len(anchors) != 1:
        raise ValueError('multiple Claude receipt anchors require investigation')
    anchor = anchors[0]
    root = plain_path(Path(anchor).parent.parent)
    skills = plain_path(root / 'skills')
    rule = plain_path(root / 'rules/agent-team.md')
    targets = set()
    for target, entry in entries.items():
        path = Path(target)
        if not path_within(path, root):
            continue
        valid = (same_path(path, rule) and entry['scope'] == {'kind': 'file'}) or (
            same_path(path.parent, skills) and entry['scope'] == {'kind': 'directory'})
        if migration_scopes:
            relative = path.relative_to(root).as_posix()
            valid |= migration_scopes.get(relative) == entry['scope']
        if not valid:
            raise ValueError(f'{target}: unexpected receipted target under Claude configuration root')
        targets.add(target)
    if anchor not in targets:
        raise ValueError('Claude receipt anchor requires investigation')
    return root, targets



def experiment_migration_scopes(source):
    """Read the explicitly releasable prior ownership from the canonical Profile."""
    profile = (source / 'machine/PROFILE.md').read_text(encoding='utf-8')
    section = profile.split('## Experiment-to-test migration\n')[1].split('## Preflight, publication, and retirement\n')[0]
    scopes = {'Claude': {}, 'Claude desktop': {}}
    rows = [line.split('|')[1:-1] for line in section.splitlines()
            if line.startswith('| ') and not line.startswith('| ---')][1:]
    for row in rows:
        host, relative, kind, fields = (item.strip() for item in row)
        if host not in scopes or Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise ValueError('invalid experiment migration declaration')
        scope = {'kind': kind}
        if kind == 'json':
            scope['fields'] = sorted(item.strip() for item in fields.split(','))
        elif kind != 'file' or fields != '-':
            raise ValueError('unsupported experiment migration scope')
        if relative in scopes[host]:
            raise ValueError('duplicate experiment migration declaration')
        scopes[host][relative] = scope
    return scopes


def experiment_release_targets(scopes, entries, claude_root):
    """Match only exact prior receipt scopes at their established native roots."""
    roots = {'Claude': claude_root, 'Claude desktop': None}
    if sys.platform == 'darwin':
        roots['Claude desktop'] = Path.home() / 'Library/Application Support/Claude'
    elif os.name == 'nt' and os.environ.get('APPDATA'):
        roots['Claude desktop'] = Path(os.environ['APPDATA']) / 'Claude'
    released = set()
    for host, declarations in scopes.items():
        root = roots[host]
        if root is None:
            continue
        for relative, scope in declarations.items():
            target = str(plain_path(root / relative))
            if target in entries:
                if entries[target]['scope'] != scope:
                    raise ValueError(f'{target}: prior scope differs from the approved migration declaration')
                released.add(target)
    return released


def preserve_installation_record(receipt_path, raw_receipt):
    """Keep the original installation evidence before releasing any ownership."""
    record = plain_path(receipt_path.parent / f'receipt-before-test-migration-{digest(raw_receipt)}.json')
    if record.exists():
        if record.read_bytes() != raw_receipt:
            raise ValueError('existing installation record differs; preserve and investigate')
    else:
        atomic_file(record, raw_receipt)
    if record.read_bytes() != raw_receipt:
        raise ValueError('original installation record verification failed')
    print(f'Preserved original installation record: {record}', flush=True)

def inventory(source, home, skills, upstream, upstream_root=None, claude_root=None):
    profile = (source / 'machine/PROFILE.md').read_text(encoding='utf-8')
    config = source / 'machine/config.toml'
    fields = sorted('.'.join(key) for key in flatten(tomllib.loads(config.read_text(encoding='utf-8'))))
    rows = [(config, home / 'config.toml', {'kind': 'toml', 'fields': fields})]
    section = profile.split('## Shared configuration and whole files\n')[1].split('## Copied local packages\n')[0]
    for name in table(section):
        rows.append((source / 'machine' / name, home / name, {'kind': 'file'}))
    section = profile.split('## Copied local packages\n')[1].split('## Upstream packages\n')[0]
    for name in table(section):
        rows.append((source / 'machine/skills' / name, skills / name, {'kind': 'directory'}))
    sources = upstream_sources(profile)
    packages = [package for _, _, group in sources for package in group]
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
    if len(fields) != 13:
        raise ValueError('expected thirteen managed configuration fields; inspect the declaration')
    return rows, sources


def verify_upstream(stage, sources, herdr_ref):
    if not herdr_ref or not re.fullmatch(r'[0-9a-f]{40}', herdr_ref):
        raise ValueError('supply the single resolved Herdr commit with --herdr-ref; use canonical preparation')
    for repository, pin, packages in sources:
        ref = pin or herdr_ref
        tree = json.loads(subprocess.check_output([
            str(command_path('gh')), 'api', f'repos/{repository}/git/trees/{ref}?recursive=1']))
        if tree.get('truncated'):
            raise ValueError(f'upstream tree response is truncated: {repository}')
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
                    raise ValueError(f'staged package differs from {repository}@{ref}: {name}/{relative}')


def read_receipt(path):
    plain_path(path)
    raw = path.read_bytes() if path.exists() else None
    receipt = json.loads(raw) if raw is not None else {'version': 1, 'entries': []}
    if (not isinstance(receipt, dict) or set(receipt) != {'version', 'entries'}
            or type(receipt['version']) is not int or receipt['version'] != 1
            or not isinstance(receipt['entries'], list)):
        raise ValueError('unknown receipt format')
    entries = {}
    for entry in receipt['entries']:
        if (not isinstance(entry, dict)
                or set(entry) != {'target', 'scope', 'algorithm', 'fingerprint'}
                or entry['algorithm'] != 'sha256'
                or not isinstance(entry['target'], str)
                or not isinstance(entry['scope'], dict)):
            raise ValueError('unknown receipt entry')
        if (not isinstance(entry['fingerprint'], str)
                or re.fullmatch(r'[0-9a-f]{64}', entry['fingerprint']) is None):
            raise ValueError('invalid receipt SHA-256 fingerprint')
        if entry['scope'] == {'kind': 'cleanup-schedule'}:
            target = entry['target']
            if not cleanup_schedule_identity(target):
                raise ValueError('unknown cleanup schedule identity')
        else:
            target = str(plain_path(entry['target']))
        if target != entry['target'] or target in entries:
            raise ValueError('ambiguous receipt target')
        entries[target] = entry
    return raw, entries


PRESERVED_MODEL_FIELDS = ('model', 'model_reasoning_effort')


def root_model_settings(path):
    """Read the existing root pair that --preserve-model-settings keeps for one run."""
    path = plain_path(path)
    data = tomllib.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    pair = tuple(data.get(field) for field in PRESERVED_MODEL_FIELDS)
    if any(not isinstance(value, str) or not value.strip() for value in pair):
        raise ValueError('--preserve-model-settings requires existing nonblank root model '
                         'and model_reasoning_effort strings')
    return pair


def managed_projection(source, fields, preserved=None):
    """Return the desired owned values, substituting an explicitly preserved root pair."""
    values = projection(source, fields)
    if preserved is not None:
        if not set(PRESERVED_MODEL_FIELDS) <= set(fields):
            raise ValueError('preserved model settings require managed root model fields')
        values.update({field: ['str', repr(value)] for field, value in zip(PRESERVED_MODEL_FIELDS, preserved)})
    return values


def unmanaged_projection(data, managed, retired):
    """Return the unowned TOML values while ignoring empty owned containers."""
    owned = {tuple(field.split('.')) for field in managed | retired}
    containers = {key[:i] for key in owned for i in range(1, len(key))}
    return {key: [type(value).__name__, repr(value)] for key, value in data.items()
            if key not in owned and not (key in containers and value == {})}


def verify_candidate_config(candidate, source, original, scope, previous_scope=(), preserved=None):
    """Prove a complete candidate changes only the owned configuration fields."""
    candidate_data = flatten(tomllib.loads(candidate.read_text(encoding='utf-8')))
    original_data = flatten(tomllib.loads(original.read_text(encoding='utf-8'))) if original.exists() else {}
    managed = set(scope['fields'])
    retired = set(previous_scope) - managed
    if any(tuple(key.split('.')) in candidate_data for key in retired):
        raise ValueError('candidate config retains retired managed fields')
    if preserved is not None and root_model_settings(original) != preserved:
        raise ValueError('existing root model settings changed after they were frozen and verified; prepare again')
    if projection(candidate, managed) != managed_projection(source, managed, preserved):
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
    receipt_path = plain_path(home / '.agent-team/reconciliation-receipts-v1.json')
    config_target = str(plain_path(home / 'config.toml'))
    preserved = tuple(args.preserve_model_settings) if args.preserve_model_settings else None
    raw_receipt, entries = read_receipt(receipt_path)
    migration = experiment_migration_scopes(source) if args.migrate_experiment else None
    anchored_claude_root, preserved_claude_targets = claude_receipt_root(
        entries, migration['Claude'] if migration else None)
    if claude_root is not None and anchored_claude_root is not None and not same_path(claude_root, anchored_claude_root):
        raise ValueError('Claude configuration root disagrees with the receipt anchor; investigate before writes')
    if claude_root is not None:
        preserved_claude_targets = set()
    from pi_runtime import (inventory as pi_inventory, receipt_targets as pi_receipt_targets,
                            roots as pi_roots, verify_settings, verify_fast_extension, native_version, ensure_idle)
    anchored_pi_root, preserved_pi_targets = pi_receipt_targets(entries, source)
    pi_root = plain_path(args.pi_config_root) if args.pi_config_root else None
    pi_runtime = pi_launcher = None
    if pi_root is not None:
        effective_pi_root, pi_runtime, pi_launcher = pi_roots(source, pi_root)
        if not same_path(effective_pi_root, pi_root) or (anchored_pi_root is not None
                and not same_path(pi_root, anchored_pi_root)):
            raise ValueError('Pi root disagrees with its effective root or prior receipt anchor')
        if stage is None or not args.pi_runtime_stage or not args.pi_version:
            raise ValueError('Pi requires canonical verified native staging and exact version')
        pi_bundle = plain_path(args.pi_runtime_stage)
        if native_version(pi_bundle, 20) != args.pi_version:
            raise ValueError('Pi staged runtime version changed after preparation')
        preserved_pi_targets = set()
    elif args.pi_runtime_stage or args.pi_version:
        raise ValueError('Pi runtime arguments require an effective Pi root')
    rows, sources = inventory(source, home, skills, stage, upstream_root, claude_root)
    if pi_root is not None:
        rows.extend(pi_inventory(source, pi_root, pi_runtime, pi_launcher, pi_bundle,
                                 stage, skills, upstream_root))
    from shell_integration import (inventory as shell_inventory, raw_file, split_hook,
                                   validate_candidate as validate_shell_candidate)
    if stage is None:
        raise ValueError('verified upstream and shell candidate staging is required')
    shell_rows, preserved_shell_targets = shell_inventory(source, home, entries, stage)
    rows.extend(shell_rows)
    shell_helper = shell_rows[0][1] if shell_rows else None
    shell_originals = {target: raw_file(Path(target)) for target, entry in entries.items()
                       if entry['scope']['kind'] == 'shell-hook'}
    shell_originals.update({str(target): raw_file(target) for _, target, scope in shell_rows
                            if scope['kind'] == 'shell-hook'})
    for candidate, target, scope in shell_rows:
        if scope['kind'] == 'shell-hook':
            validate_shell_candidate(candidate, target, shell_helper, scope)
    all_target_names = [str(plain_path(target)) for _, target, _ in rows]
    if len(set(all_target_names)) != len(all_target_names):
        raise ValueError('duplicate profile target across hosts')
    preserved_targets = preserved_claude_targets | preserved_pi_targets | preserved_shell_targets
    json_originals = {str(target): target.read_bytes() if target.exists() else None
                      for _, target, scope in rows if scope['kind'] == 'json'}
    if pi_root is not None:
        pi_settings = plain_path(pi_root / 'settings.json')
        pi_settings_row = next(row for row in rows if same_path(row[1], pi_settings))
        previous = entries.get(str(pi_settings), {}).get('scope', {})
        verify_settings(pi_settings_row[0], source, pi_settings, pi_settings_row[2], previous)
    releasing = experiment_release_targets(migration, entries, anchored_claude_root) if migration else set()
    preserved_targets -= releasing
    approvals = dict(args.resolve)
    errors, observed, desired = [], {}, {}
    if (home / 'AGENTS.override.md').exists() or (home / 'AGENTS.override.md').is_symlink():
        errors.append('AGENTS.override.md interferes with global instructions; preserve and investigate')
    if pi_root is not None and ((pi_root / 'AGENTS.override.md').exists()
                                or (pi_root / 'AGENTS.override.md').is_symlink()):
        errors.append('Pi AGENTS.override.md suppresses managed instructions; preserve and investigate')
    if preserved is not None and root_model_settings(home / 'config.toml') != preserved:
        errors.append('existing root model settings changed after they were frozen and verified; prepare again')
    for candidate, target, scope in rows:
        target = plain_path(target)
        desired[str(target)] = (candidate, scope)
        if candidate is None or not candidate.exists():
            errors.append(f'missing declared source: {candidate or "upstream staging"}')
        else:
            fingerprint(candidate, scope)
    if releasing & desired.keys():
        raise ValueError('migration release overlaps a current profile target')
    # Retired and released entries remain in the same all-target gate, with their old scope.
    for target in desired.keys() | entries.keys():
        old = entries.get(target)
        if old and old['scope'] == {'kind': 'cleanup-schedule'}:
            continue
        scope = old['scope'] if old else desired[target][1]
        if scope['kind'] == 'json' and target not in releasing and target not in preserved_pi_targets and (
                target not in desired or desired[target][1]['kind'] != 'json'):
            errors.append(f'{target}: JSON scope requires its declared migration owner; no writes')
        current = fingerprint(Path(target), scope)
        observed[target] = (scope, current)
        expected = old['fingerprint'] if old else None
        conflict = (old is not None and current != expected) or (old is None and current is not None)
        gate_scope = scope
        if old and target in desired and old['scope'] != desired[target][1]:
            new_scope = desired[target][1]
            if scope['kind'] == 'json' and new_scope['kind'] == 'json' and 'resources' in new_scope:
                fields = sorted(set(scope['fields']) | set(new_scope['fields']))
                resources = {key: sorted(set(scope.get('resources', {}).get(key, [])) | set(new_scope.get('resources', {}).get(key, [])))
                             for key in scope.get('resources', {}).keys() | new_scope.get('resources', {}).keys()}
                gate_scope = {'kind': 'json', 'fields': fields, 'resources': resources}
                added = set(new_scope['fields']) - set(scope['fields'])
                if any(v != ['absent'] for v in projection(Path(target), added, 'json').values()):
                    conflict = True
                document = json.loads(Path(target).read_text(encoding='utf-8')) if Path(target).exists() else {}
                for key, paths in new_scope.get('resources', {}).items():
                    if any(path in document.get(key, []) for path in set(paths) - set(scope.get('resources', {}).get(key, []))):
                        conflict = True
            elif scope['kind'] != 'toml' or new_scope['kind'] != 'toml':
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
        if target not in desired and target not in releasing and target not in preserved_targets and scope['kind'] in ('toml', 'json'):
            errors.append(f'{target}: retired config target requires supervised relocation; no writes')
    targets = [Path(target) for target in observed]
    if any(not same_path(a, b) and path_within(b, a) for a in targets for b in targets):
        errors.append('overlapping current or retired scopes require investigation')
    if any(same_path(receipt_path, path) or path_within(receipt_path, path) for path in targets):
        errors.append('receipt metadata overlaps a managed target')
    unknown = approvals.keys() - observed.keys()
    if unknown:
        errors.append(f'authorization refers to unknown targets: {sorted(unknown)}')
    preserved_approvals = approvals.keys() & preserved_targets
    if preserved_approvals:
        errors.append('inactive host scopes cannot be resolved or retired')
    if errors:
        raise ValueError('\n'.join(errors))
    if pi_runtime is not None:
        runtime_row = desired[str(pi_runtime)]
        if fingerprint(runtime_row[0], runtime_row[1]) != fingerprint(pi_runtime, runtime_row[1]):
            ensure_idle(pi_runtime)
    if stage is None:
        raise ValueError('verified upstream staging is required')
    discovery_roots = [skills, upstream_root, plain_path(home / 'skills')]
    if claude_root is not None:
        discovery_roots.append(plain_path(claude_root / 'skills'))
    if pi_root is not None:
        discovery_roots.append(plain_path(pi_root / 'skills'))
    if any(same_path(stage, root) or path_within(stage, root) or same_path(stage.parent, root)
           for root in discovery_roots):
        raise ValueError('upstream staging must be outside skill discovery')
    verify_upstream(stage, sources, args.herdr_ref)
    if pi_root is not None:
        verify_fast_extension(source, stage)
    print(f'Herdr resolved commit: {args.herdr_ref}', flush=True)

    def agrees(target):
        """Receipt scope, gate-verified live state and desired content already match."""
        old, (candidate, scope) = entries.get(target), desired[target]
        # A preserved root pair is part of the desired config without altering its source.
        wanted = (digest(encoded(managed_projection(candidate, scope['fields'], preserved)))
                  if preserved is not None and target == config_target else fingerprint(candidate, scope))
        return (old is not None and old['scope'] == scope
                and observed[target] == (scope, old['fingerprint'])
                and wanted == old['fingerprint'])

    for target in sorted(observed) if not args.apply else ():
        if target in releasing:
            print(f'Would release ownership without changing the file: {target}', flush=True)
        elif target not in desired and target not in preserved_targets:
            print(f'Would retire {target}', flush=True)
        elif target in desired and not agrees(target):
            print(f'Would publish {target}', flush=True)
    if not args.apply:
        print('All declared sources and live target/retirement scopes passed preflight; no writes.')
        return
    if not args.models_verified:
        raise ValueError('supervisor must verify target model/effort availability before applying')
    candidate_config = plain_path(args.candidate_config) if args.candidate_config else None
    if candidate_config is None:
        raise ValueError('supply the supervisor-prepared complete candidate config')
    source_config, config_scope = desired[config_target]
    original_config = home / 'config.toml'
    original_config_bytes = (home / 'config.toml').read_bytes() if (home / 'config.toml').exists() else None
    previously_managed = set(entries.get(config_target, {}).get('scope', {}).get('fields', []))
    verify_candidate_config(candidate_config, source_config, original_config, config_scope,
                            previously_managed, preserved)
    desired[config_target] = (candidate_config, config_scope)
    # Snapshot candidates before mutation. The source worktree must represent the
    # single revision selected by the supervisor, with no uncommitted edits.
    if subprocess.check_output([str(command_path('git')), '-C', str(source), 'status', '--porcelain']):
        raise ValueError('source checkout has uncommitted changes; select a clean revision')
    # Agreeing targets keep their live bytes, metadata and receipt entry untouched.
    unchanged = {target for target in desired if agrees(target)}
    prepared_files = {target: candidate.read_bytes() for target, (candidate, scope) in desired.items()
                      if scope['kind'] != 'directory' and target not in unchanged}
    release_originals = {target: Path(target).read_bytes() if Path(target).exists() else None
                         for target in releasing}
    prepared = {}
    directory_security = {}
    completed = False
    try:
        # Prepare complete copies off discovery before any live target is touched.
        for target, (candidate, scope) in desired.items():
            if target in unchanged:
                continue
            if same_path(candidate, Path(target)) or path_within(candidate, Path(target)):
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
                if os.name == 'nt':
                    from windows_security import prepare_directory_start, prepare_directory_finish

                    directory_security[target] = prepare_directory_start(temporary, Path(target))
                shutil.copytree(candidate, prepared[target], symlinks=False)
                if os.name == 'nt':
                    directory_security[target] = prepare_directory_finish(
                        prepared[target], Path(target), directory_security[target])
                if fingerprint(prepared[target], scope) != fingerprint(candidate, scope):
                    raise ValueError(f'prepared copy mismatch: {target}')
        for target in observed:
            scope, expected = observed[target]
            if fingerprint(Path(target), scope) != expected:
                raise ValueError(f'target changed after preflight: {target}')
        for target, original in shell_originals.items():
            if raw_file(Path(target)) != original:
                raise ValueError('shell startup changed, including unowned bytes; prepare it again')
        for target, original in release_originals.items():
            if (Path(target).read_bytes() if Path(target).exists() else None) != original:
                raise ValueError(f'released file changed after preparation: {target}')
        if releasing:
            now_raw, _ = read_receipt(receipt_path)
            if now_raw != raw_receipt:
                raise ValueError('receipt changed before preserving installation evidence')
            preserve_installation_record(receipt_path, raw_receipt)
        def publication_order(target):
            path = Path(target)
            if shell_helper is not None and same_path(path, shell_helper):
                return -2, target
            if pi_root is not None and same_path(path, pi_root / 'HERDR.md'):
                return -1, target
            if pi_runtime is not None and same_path(path, pi_runtime):
                return 0, target
            if pi_launcher is not None and same_path(path, pi_launcher):
                return 3, target
            if claude_root is not None and same_path(path, plain_path(claude_root / 'rules/agent-team.md')):
                return 0, target
            if claude_root is not None and path_within(path, plain_path(claude_root / 'skills')):
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
            if target in shell_originals and raw_file(path) != shell_originals[target]:
                raise ValueError('shell startup changed, including unowned bytes; prepare it again')
            if target in json_originals and (path.read_bytes() if path.exists() else None) != json_originals[target]:
                raise ValueError('Pi settings changed, including unmanaged values; prepare it again')
            if target in releasing:
                if (path.read_bytes() if path.exists() else None) != release_originals[target]:
                    raise ValueError(f'released file changed immediately before ownership release: {target}')
                entries.pop(target)
                print(f'Released to Unmanaged Local State; file preserved: {target}', flush=True)
            elif target in preserved_targets or target in unchanged:
                continue
            elif target not in desired:
                if scope['kind'] in ('toml', 'json'):
                    raise ValueError('retiring TOML fields requires a reviewed candidate config and scope migration')
                if scope['kind'] == 'shell-hook':
                    original = shell_originals[target]
                    before, _, after = split_hook(original or b'', scope)
                    if original is not None:
                        atomic_file(path, before + after, stat.S_IMODE(path.stat().st_mode))
                        if raw_file(path) != before + after:
                            raise ValueError('shell hook retirement changed unowned startup bytes')
                elif path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink(missing_ok=True)
                if (scope['kind'] == 'shell-hook' and fingerprint(path, scope) is not None) or (
                        scope['kind'] != 'shell-hook' and path.exists()):
                    raise ValueError(f'retirement incomplete: {target}')
                entries.pop(target, None)
                print(f'Retired {target}', flush=True)
            else:
                candidate, new_scope = desired[target]
                if new_scope['kind'] == 'directory':
                    if pi_runtime is not None and same_path(path, pi_runtime):
                        ensure_idle(pi_runtime)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if os.name == 'nt':
                        from windows_security import verify_directory, finish_directory

                        verify_directory(path, directory_security[target])
                    if path.exists():
                        shutil.rmtree(path)
                        print(f'Removed old directory {target}; replacement and receipt pending', flush=True)
                    os.rename(prepared[target], path)
                    print(f'Published directory {target}; verification and receipt pending', flush=True)
                    if os.name == 'nt':
                        finish_directory(path, directory_security[target])
                else:
                    mode = (0o755 if new_scope.get('executable') else
                            stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600)
                    atomic_file(path, prepared_files[target], mode)
                    print(f'Replaced file {target}; verification and receipt pending', flush=True)
                if new_scope['kind'] == 'shell-hook' and raw_file(path) != prepared_files[target]:
                    raise ValueError('installed shell startup differs from its complete candidate')
                actual = fingerprint(path, new_scope)
                if actual != fingerprint(candidate, new_scope):
                    raise ValueError(f'installed result mismatch: {target}')
                entries[target] = {'target': target, 'scope': new_scope,
                                   'algorithm': 'sha256', 'fingerprint': actual}
                print(f'Wrote {target}', flush=True)
            atomic_file(receipt_path, encoded({'version': 1, 'entries': list(entries.values())}) + b'\n')
            raw_receipt = receipt_path.read_bytes()
        print(f'Retained {len(unchanged)} unchanged targets and their receipt entries', flush=True)
        completed = True
    finally:
        for path in prepared.values():
            if os.name == 'nt' and not completed and path.exists():
                print(f'Directory preparation retained for investigation: {path.parent}', flush=True)
            else:
                shutil.rmtree(path.parent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--codex-home', required=True)
    parser.add_argument('--skills-root', required=True)
    parser.add_argument('--upstream-root', help='resolved installer destination, if different from copied skills')
    parser.add_argument('--claude-config-root', help='proven effective Claude configuration root')
    parser.add_argument('--upstream-stage')
    parser.add_argument('--pi-config-root', help='proven opted-in Pi configuration root')
    parser.add_argument('--pi-runtime-stage')
    parser.add_argument('--pi-version')
    parser.add_argument('--herdr-ref', type=parse_commit_ref,
                        help='single immutable Herdr commit resolved by canonical preparation')
    parser.add_argument('--candidate-config')
    parser.add_argument('--models-verified', action='store_true')
    parser.add_argument('--preserve-model-settings', nargs=2, metavar=('MODEL', 'EFFORT'),
                        help='existing root pair frozen and verified by canonical preparation')
    parser.add_argument('--resolve', action='append', type=parse_resolution, default=[],
                        metavar='TARGET=OBSERVED_SHA256_OR_absent')
    parser.add_argument('--migrate-experiment', action='store_true',
                        help='explicitly authorized experiment-to-test ownership migration; preserve prior files and receipt record')
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
