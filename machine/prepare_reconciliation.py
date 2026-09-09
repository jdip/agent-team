#!/usr/bin/env python3
"""Prepare, preflight, and optionally apply one Machine Reconciliation."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time
import copy
import importlib
import tomllib

sys.dont_write_bytecode = True

def command(*args, cwd=None, env=None):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode:
        detail = '\n'.join(part for part in (result.stdout.strip(), result.stderr.strip()) if part) or 'command failed'
        raise ValueError(f"{' '.join(args[:2])}: {detail}")
    return result.stdout.strip()


def plain_path(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'symlink requires investigation: {part}')
    return path


class AppServer:
    """Small bounded JSON-RPC client for the installed Codex app-server."""

    def __init__(self, executable, codex_home, timeout):
        environment = os.environ.copy()
        if codex_home:
            environment['CODEX_HOME'] = str(codex_home)
        self.process = subprocess.Popen([str(executable), 'app-server', '--stdio'],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, env=environment)
        self.timeout = timeout
        self.next_id = 1
        self.buffer = bytearray()

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

    def request(self, method, params):
        identifier = self.next_id
        self.next_id += 1
        self._send({'id': identifier, 'method': method, 'params': params})
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ValueError(f'Codex app-server timed out waiting for {method}')
            message = self._read_message(method, remaining)
            if message.get('id') != identifier:
                continue
            if 'error' in message:
                raise ValueError(f"Codex app-server {method} failed: {message['error']}")
            if 'result' not in message:
                raise ValueError(f'Codex app-server returned no result for {method}')
            return message['result']

    def notify(self, method, params):
        self._send({'method': method, 'params': params})

    def _send(self, message):
        if self.process.poll() is not None:
            raise ValueError('Codex app-server exited before request')
        self.process.stdin.write((json.dumps(message, separators=(',', ':')) + '\n').encode())
        self.process.stdin.flush()

    def _read_message(self, method, remaining):
        while b'\n' not in self.buffer:
            ready, _, _ = select.select([self.process.stdout.fileno()], [], [], remaining)
            if not ready:
                raise ValueError(f'Codex app-server timed out waiting for {method}')
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk:
                raise ValueError(f'Codex app-server stopped while handling {method}')
            self.buffer.extend(chunk)
        line, _, remaining_data = self.buffer.partition(b'\n')
        self.buffer = bytearray(remaining_data)
        return json.loads(line.decode())


def app_server_data(executable, requested_home, source, timeout):
    server = AppServer(executable, requested_home, timeout)
    try:
        initialized = server.request('initialize', {
            'clientInfo': {'name': 'agent-team-reconciliation', 'version': '1'},
            'capabilities': {'experimentalApi': True},
        })
        server.notify('initialized', {})
        if initialized.get('platformOs') not in ('macos', 'linux'):
            raise ValueError(f"unsupported reconciliation host: {initialized.get('platformOs')!r}")
        skills = server.request('skills/list', {'cwds': [str(source)], 'forceReload': True})
        models = []
        cursor = None
        while True:
            result = server.request('model/list', {'includeHidden': True, 'cursor': cursor})
            models.extend(result.get('data', []))
            cursor = result.get('nextCursor')
            if cursor is None:
                break
        return initialized, skills, models
    finally:
        server.close()


def select_source(repository, work_root):
    repository = plain_path(repository)
    if not (repository / '.git').exists():
        raise ValueError(f'not a Git checkout: {repository}')
    branch = command('git', 'symbolic-ref', '--quiet', '--short', 'HEAD', cwd=repository)
    remote = command('git', 'config', '--get', f'branch.{branch}.remote', cwd=repository)
    merge = command('git', 'config', '--get', f'branch.{branch}.merge', cwd=repository)
    if remote == '.' or not merge.startswith('refs/heads/'):
        raise ValueError(f'{branch}: upstream identity is ambiguous; inspect branch tracking')
    remote_branch = merge.removeprefix('refs/heads/')
    fresh = command('git', 'ls-remote', '--exit-code', remote, f'refs/heads/{remote_branch}',
                    cwd=repository).split()[0]
    if not re.fullmatch(r'[0-9a-f]{40}', fresh):
        raise ValueError(f'{branch}: remote returned an invalid revision')
    command('git', 'fetch', '--no-tags', '--no-write-fetch-head', remote, fresh, cwd=repository)
    head = command('git', 'rev-parse', 'HEAD', cwd=repository)
    if head != fresh:
        ahead = subprocess.run(['git', 'merge-base', '--is-ancestor', fresh, head], cwd=repository)
        behind = subprocess.run(['git', 'merge-base', '--is-ancestor', head, fresh], cwd=repository)
        if ahead.returncode == 0:
            raise ValueError(f'{branch}: local commits are unpublished; publish or select their authority explicitly')
        if behind.returncode != 0:
            raise ValueError(f'{branch}: local and {remote}/{remote_branch} have diverged; investigate source authority')
    root = Path(tempfile.mkdtemp(prefix='agent-team-source-', dir=work_root))
    checkout = root / 'source'
    try:
        command('git', 'worktree', 'add', '--detach', str(checkout), fresh, cwd=repository)
    except Exception:
        root.rmdir()
        raise
    return branch, remote, fresh, root, checkout


def source_skill_names(source):
    from reconcile import table

    profile = (source / 'machine/PROFILE.md').read_text()
    local = profile.split('## Copied local packages\n')[1].split('## Upstream packages\n')[0]
    upstream = profile.split('## Upstream packages\n')[1].split('## Optional Claude Code configuration\n')[0]
    return set(table(local)), {name for name, _ in re.findall(r'^\| ([\w-]+) \| (skills/[\w/-]+) \|$', upstream, re.M)}


def probe_claude(timeout):
    executable = shutil.which('claude')
    if executable is None:
        return None
    executable = Path(os.path.abspath(executable))
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError(f'Claude executable is unavailable: {executable}')
    try:
        result = subprocess.run([str(executable), '--version'], stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        raise ValueError('Claude executable version probe timed out') from error
    if result.returncode:
        raise ValueError('Claude executable version probe failed; investigate availability')
    return executable


def verify_claude_settings_root(root, platform):
    default_root = plain_path(Path.home() / '.claude')
    paths = {base / name for base in (default_root, root)
             for name in ('settings.json', 'settings.local.json', 'managed-settings.json')}
    if platform == 'macos':
        managed = Path('/Library/Application Support/ClaudeCode')
    elif platform == 'linux':
        managed = Path('/etc/claude-code')
    else:
        raise ValueError(f'unsupported Claude settings platform: {platform!r}')
    paths.add(managed / 'managed-settings.json')
    fragments = managed / 'managed-settings.d'
    if fragments.exists() or fragments.is_symlink():
        fragments = plain_path(fragments)
        if not fragments.is_dir():
            raise ValueError(f'Claude managed settings path is not a directory: {fragments}')
        paths.update(path for path in fragments.glob('*.json') if not path.name.startswith('.'))
    for path in sorted(paths):
        if not path.exists() and not path.is_symlink():
            continue
        path = plain_path(path)
        if not path.is_file():
            raise ValueError(f'Claude settings path is not an ordinary file: {path}')
        try:
            settings = json.loads(path.read_text())
        except json.JSONDecodeError as error:
            raise ValueError('Claude settings cannot establish a configuration root') from error
        if not isinstance(settings, dict):
            raise ValueError('Claude settings must contain a JSON object')
        environment = settings.get('env')
        if environment is not None and not isinstance(environment, dict):
            raise ValueError('Claude settings environment must contain a JSON object')
        if environment is not None and 'CLAUDE_CONFIG_DIR' in environment:
            configured_root = environment['CLAUDE_CONFIG_DIR']
            if (not isinstance(configured_root, str) or not configured_root
                    or not Path(configured_root).is_absolute()):
                raise ValueError('Claude settings configuration root is malformed')
            try:
                settings_root = plain_path(configured_root)
            except (ValueError, OSError) as error:
                raise ValueError('Claude settings configuration root requires investigation') from error
            if settings_root != root:
                raise ValueError('Claude settings configuration root disagrees with the effective Claude root')


def resolve_claude_root(explicit, platform):
    environment = os.environ.get('CLAUDE_CONFIG_DIR')
    if environment is not None and (not environment or not Path(environment).is_absolute()):
        raise ValueError('CLAUDE_CONFIG_DIR is malformed')
    environment_root = plain_path(environment) if environment is not None else None
    explicit_root = plain_path(explicit) if explicit else None
    effective_root = environment_root or plain_path(Path.home() / '.claude')
    if explicit_root is not None and explicit_root != effective_root:
        raise ValueError('explicit Claude configuration root disagrees with the effective Claude root')
    root = effective_root
    verify_claude_settings_root(root, platform)
    return root


def existing_ancestor(path):
    path = plain_path(path)
    while not path.exists():
        path = path.parent
    if not path.is_dir():
        raise ValueError(f'destination ancestor is not a directory: {path}')
    return path


def resolve_root(label, explicit, names, receipt, discovered):
    roots = set()
    for target, entry in receipt.items():
        if entry['scope'].get('kind') == 'directory' and Path(target).name in names:
            roots.add(str(Path(target).parent))
    for group in discovered.get('data', []):
        for skill in group.get('skills', []):
            path = skill.get('path')
            if skill.get('scope') == 'user' and skill.get('name') in names and path:
                skill_file = Path(path)
                if skill_file.name != 'SKILL.md':
                    raise ValueError(f'native skill discovery returned an unsupported path: {skill_file}')
                roots.add(str(skill_file.parent.parent))
    if explicit:
        requested = str(plain_path(explicit))
        if roots and roots != {requested}:
            raise ValueError(f'{label} disagrees with receipt/native discovery: {sorted(roots)}')
        return Path(requested)
    if len(roots) != 1:
        detail = 'none' if not roots else ', '.join(sorted(roots))
        raise ValueError(f'cannot resolve {label} from receipt/native discovery ({detail}); supply it explicitly')
    return Path(roots.pop())


def models_for_profile(source):
    config = tomllib.loads((source / 'machine/config.toml').read_text())
    required = {(config['model'], config['model_reasoning_effort']),
                (config['agents']['default_subagent_model'],
                 config['agents']['default_subagent_reasoning_effort'])}
    for path in (source / 'machine/agents').glob('*.toml'):
        role = tomllib.loads(path.read_text())
        required.add((role['model'], role['model_reasoning_effort']))
    return required


def verify_models(required, advertised):
    available = {
        item.get('model'): {effort.get('reasoningEffort') for effort in item.get('supportedReasoningEfforts', [])}
        for item in advertised if isinstance(item.get('model'), str)
    }
    missing = sorted(f'{model}/{effort}' for model, effort in required
                     if effort not in available.get(model, set()))
    if missing:
        raise ValueError(f'installed Codex does not support declared model/effort: {", ".join(missing)}')


TOMLKIT_VERSION = '0.15.1'


def provision_tomlkit(stage):
    dependency_root = stage / 'candidate-dependencies'
    pip = subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True)
    if pip.returncode == 0:
        install = [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check']
    else:
        candidates = [shutil.which('uv'), Path.home() / '.local/bin/uv']
        uv = next((Path(candidate) for candidate in candidates
                   if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK)), None)
        if uv is None:
            raise ValueError('neither Python pip nor uv is available for isolated TOML candidate preparation')
        install = [str(uv), 'pip', 'install', '--python', sys.executable]
    try:
        command(*install, '--index-url', 'https://pypi.org/simple', '--target', str(dependency_root), '--no-deps',
                f'tomlkit=={TOMLKIT_VERSION}')
    except ValueError as error:
        raise ValueError(f'isolated tomlkit acquisition failed: {error}') from error
    sys.path.insert(0, str(dependency_root))
    tomlkit = importlib.import_module('tomlkit')
    if tomlkit.__version__ != TOMLKIT_VERSION:
        raise ValueError('isolated tomlkit version differs from the approved pin')
    return tomlkit


def table_at(document, path, create, tomlkit):
    table = document
    for key in path:
        if key not in table:
            if not create:
                return None
            table.add(key, tomlkit.table())
        table = table[key]
        if not hasattr(table, 'items'):
            raise ValueError(f'owned config table is a non-table value: {".".join(path)}')
    return table


def item_at(document, path):
    table = table_at(document, path[:-1], False, None)
    return None if table is None or path[-1] not in table else table[path[-1]]


def unwrapped(item):
    return item.unwrap() if hasattr(item, 'unwrap') else item


def build_candidate(source, actual, output, scope, prior_scope, tomlkit):
    from reconcile import verify_candidate_config

    needed = {tuple(field.split('.')) for field in scope['fields']}
    source_bytes = source.read_bytes()
    source_document = tomlkit.parse(source_bytes.decode('utf-8'))
    previous = {tuple(field.split('.')) for field in prior_scope}
    actual_bytes = actual.read_bytes() if actual.exists() else b''
    document = tomlkit.parse(actual_bytes.decode('utf-8')) if actual_bytes else tomlkit.document()
    newline = '\r\n' if b'\r\n' in (actual_bytes or source_bytes) else '\n'
    for path in previous - needed:
        table = table_at(document, path[:-1], False, tomlkit)
        if table is not None and path[-1] in table:
            del table[path[-1]]
    for path in needed:
        source_item = item_at(source_document, path)
        if source_item is None:
            raise ValueError(f'source config lacks owned value: {".".join(path)}')
        table = table_at(document, path[:-1], True, tomlkit)
        if path[-1] in table and (type(unwrapped(table[path[-1]])) is type(unwrapped(source_item))
                                  and unwrapped(table[path[-1]]) == unwrapped(source_item)):
            continue
        replacement = copy.deepcopy(source_item) if hasattr(source_item, 'trivia') else tomlkit.item(source_item)
        if path[-1] not in table:
            replacement.trivia.trail = newline
        table[path[-1]] = replacement
    output.write_bytes(tomlkit.dumps(document).encode('utf-8'))
    verify_candidate_config(output, source, actual, scope, prior_scope)


def verify_installed(source, skills_root, upstream_root, executable, home, timeout):
    _, discovered, models = app_server_data(executable, home, source, timeout)
    verify_models(models_for_profile(source), models)
    local, upstream = source_skill_names(source)
    expected = {name: skills_root / name / 'SKILL.md' for name in local}
    expected.update({name: upstream_root / name / 'SKILL.md' for name in upstream})
    visible = {(skill['name'], Path(skill['path'])): skill
               for group in discovered['data'] for skill in group['skills']
               if skill['scope'] == 'user'}
    missing = [name for name, path in expected.items() if (name, path) not in visible]
    disabled = [name for name, path in expected.items()
                if (name, path) in visible and visible[name, path].get('enabled') is not True]
    if missing or disabled:
        details = []
        if missing:
            details.append(f'missing expected paths: {", ".join(sorted(missing))}')
        if disabled:
            details.append(f'disabled expected skills: {", ".join(sorted(disabled))}')
        raise ValueError(f'fresh Codex skill discovery is unusable ({"; ".join(details)})')


def run_prepared(args):
    from reconcile import claude_receipt_root, inventory, read_receipt, verify_upstream

    source = plain_path(args.prepared_source)
    executable = Path(args.codex) if args.codex else shutil.which('codex')
    if not executable:
        raise ValueError('Codex executable is unavailable; supply --codex')
    executable = Path(executable)
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError(f'Codex executable is unavailable: {executable}')
    stage = None
    verified_stage = False
    try:
        initialized, discovered, models = app_server_data(executable, args.codex_home, source, args.timeout)
        home = plain_path(initialized['codexHome'])
        if args.codex_home and home != plain_path(args.codex_home):
            raise ValueError(f'Codex app-server resolved a different CODEX_HOME: {home}')
        _, receipt = read_receipt(home / '.agent-team/reconciliation-receipts-v1.json')
        claude_executable = probe_claude(args.timeout)
        if args.claude_config_root and claude_executable is None:
            raise ValueError('explicit Claude configuration root requires a Claude executable on PATH')
        claude_root = (resolve_claude_root(args.claude_config_root, initialized['platformOs'])
                       if claude_executable else None)
        anchored_claude_root, anchored_claude_targets = claude_receipt_root(receipt)
        if claude_root is not None and anchored_claude_root is not None and claude_root != anchored_claude_root:
            raise ValueError('Claude configuration root disagrees with the receipt anchor; investigate before writes')
        codex_receipt = {target: entry for target, entry in receipt.items()
                         if target not in anchored_claude_targets}
        local_names, upstream_names = source_skill_names(source)
        skills_root = resolve_root('copied skill destination', args.skills_root, local_names, codex_receipt, discovered)
        upstream_root = resolve_root('upstream installer destination', args.upstream_root, upstream_names,
                                     codex_receipt, discovered)
        verify_models(models_for_profile(source), models)
        rows, pin, packages = inventory(source, home, skills_root, Path('/upstream-stage'), upstream_root,
                                        claude_root)
        stage_parent = Path(args.staging_root) if args.staging_root else skills_root.parent
        stage_parent = plain_path(stage_parent)
        stage_parent.mkdir(parents=True, exist_ok=True)
        staging_roots = [skills_root, upstream_root]
        if claude_root is not None:
            staging_roots.append(claude_root / 'skills')
        for root in staging_roots:
            if stage_parent.stat().st_dev != existing_ancestor(root).stat().st_dev:
                raise ValueError(f'staging root is not on the destination filesystem: {root}')
        discovery_roots = [skills_root, upstream_root, home / 'skills']
        if claude_root is not None:
            discovery_roots.append(claude_root / 'skills')
        if any(stage_parent == root or root in stage_parent.parents for root in discovery_roots):
            raise ValueError('staging root is inside a skill discovery root')
        stage = Path(tempfile.mkdtemp(prefix='agent-team-upstream-', dir=stage_parent))
        installer = home / 'skills/.system/skill-installer/scripts/install-skill-from-github.py'
        installer = plain_path(installer)
        if not installer.is_file():
            raise ValueError(f'supported skill installer is unavailable: {installer}')
        command(sys.executable, str(installer), '--repo', 'mattpocock/skills', '--ref', pin,
                '--dest', str(stage), '--path', *(path for _, path in packages))
        verify_upstream(stage, pin, packages)
        verified_stage = True
        tomlkit = provision_tomlkit(stage)
        config_target = home / 'config.toml'
        config_scope = rows[0][2]
        previous_scope = receipt.get(str(config_target), {}).get('scope', {}).get('fields', [])
        candidate = stage / 'candidate-config.toml'
        build_candidate(source / 'machine/config.toml', config_target, candidate, config_scope,
                        previous_scope, tomlkit)
        preflight = [sys.executable, str(source / 'machine/reconcile.py'), '--source', str(source),
                     '--codex-home', str(home), '--skills-root', str(skills_root),
                     '--upstream-root', str(upstream_root), '--upstream-stage', str(stage)]
        if claude_root is not None:
            preflight.extend(['--claude-config-root', str(claude_root)])
        for target, observation in args.resolve:
            preflight.extend(['--resolve', f'{target}={observation}'])
        command(*preflight, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        if args.apply:
            apply = [*preflight, '--candidate-config', str(candidate), '--models-verified', '--apply']
            publication = command(*apply, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}).splitlines()
            for line in publication:
                print(line, flush=True)
            try:
                verify_installed(source, skills_root, upstream_root, executable, home, args.timeout)
            except Exception as error:
                raise ValueError(f'publication completed; fresh verification failed: {error}') from error
        print(json.dumps({'codex_home': str(home), 'skills_root': str(skills_root),
                          'upstream_root': str(upstream_root),
                          'claude_config_root': str(claude_root) if claude_root else None,
                          'claude_available': claude_executable is not None,
                          'platform': initialized['platformOs'],
                          'result': 'reconciled and verified' if args.apply else 'prepared and preflighted; no managed writes'},
                         sort_keys=True))
    except Exception:
        if stage is not None and not verified_stage:
            print(f'Preparation staging retained for inspection: {stage}', file=sys.stderr)
            stage = None
        raise
    finally:
        if stage is not None:
            shutil.rmtree(stage)


def cleanup_source(repository, source_root, source):
    removal = subprocess.run(['git', 'worktree', 'remove', str(source)], cwd=repository,
                             capture_output=True, text=True)
    if removal.returncode:
        print(f'Prepared source retained for inspection: {source}', file=sys.stderr)
        return
    try:
        source_root.rmdir()
    except OSError:
        print(f'Preparation root retained for inspection: {source_root}', file=sys.stderr)


def run_bootstrap(args):
    repository = plain_path(args.repository)
    work_root = plain_path(args.work_root) if args.work_root else repository.parent
    work_root.mkdir(parents=True, exist_ok=True)
    source_root = source = None
    try:
        branch, remote, revision, source_root, source = select_source(repository, work_root)
        print(json.dumps({'branch': branch, 'remote': remote, 'revision': revision,
                          'result': 'selected clean reconciliation source'}, sort_keys=True), flush=True)
        helper = source / 'machine/prepare_reconciliation.py'
        if not helper.is_file():
            raise ValueError(f'selected revision lacks the canonical preparation script: {helper}')
        child = [sys.executable, str(helper), '--prepared-source', str(source),
                 '--timeout', str(args.timeout)]
        for name in ('codex_home', 'skills_root', 'upstream_root', 'staging_root', 'codex',
                     'claude_config_root'):
            value = getattr(args, name)
            if value:
                child.extend(['--' + name.replace('_', '-'), str(value)])
        if args.apply:
            child.append('--apply')
        for target, observation in args.resolve:
            child.extend(['--resolve', f'{target}={observation}'])
        report = command(*child, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        if report:
            print(report)
    finally:
        if source_root is not None:
            cleanup_source(repository, source_root, source)


def run(args):
    if args.prepared_source:
        run_prepared(args)
    else:
        run_bootstrap(args)


def main():
    from reconcile import parse_resolution

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', default='.', help='current-branch Agent Team checkout')
    parser.add_argument('--prepared-source', help=argparse.SUPPRESS)
    parser.add_argument('--codex-home')
    parser.add_argument('--skills-root')
    parser.add_argument('--upstream-root')
    parser.add_argument('--staging-root')
    parser.add_argument('--work-root')
    parser.add_argument('--codex')
    parser.add_argument('--claude-config-root')
    parser.add_argument('--resolve', action='append', type=parse_resolution, default=[],
                        metavar='TARGET=OBSERVED_SHA256_OR_absent')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--timeout', type=float, default=20)
    args = parser.parse_args()
    try:
        if args.timeout <= 0:
            raise ValueError('--timeout must be positive')
        run(args)
    except (ValueError, OSError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        outcome = 'Managed writes may have preceded this failure; inspect actual state and receipts.' if args.apply else 'No managed writes were made.'
        parser.exit(1, f'Reconciliation preparation stopped: {error}\n{outcome} Investigate the reported source, native capability, staging, or preflight evidence.\n')


if __name__ == '__main__':
    main()
