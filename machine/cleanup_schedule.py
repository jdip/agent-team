#!/usr/bin/env python3
"""Narrow native-automation observations and dedicated user-cron operations."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tomllib

from reconcile import (atomic_file, cleanup_schedule_entry, cleanup_schedule_fingerprint,
                       cleanup_schedule_identity, cleanup_schedule_preflight, command_path, encoded,
                       executable_path, fingerprint, parse_resolution, plain_path, read_receipt, same_path)

DESKTOP_FIELDS = ('kind', 'name', 'prompt', 'status', 'rrule', 'model',
                  'reasoning_effort', 'execution_environment', 'target', 'cwds')
CRON_ID = 'cron:agent-team-cleanup'
CRON_MARKER = ' # agent-team-cleanup'
CRON_MAX_LINE_BYTES = 1000


def receipt_hash(raw):
    return hashlib.sha256(raw).hexdigest() if raw is not None else 'absent'


def task_scheduler_identity(home):
    from windows_scheduler import identity
    return identity(home)


def desktop(home, identity):
    if not identity.startswith('automation:') or not cleanup_schedule_identity(identity):
        raise ValueError('expected native automation identity')
    name = identity.split(':', 1)[1]
    path = plain_path(home / 'automations' / name / 'automation.toml')
    if not path.exists():
        return None
    data = tomllib.loads(path.read_text(encoding='utf-8'))
    if data.get('version') != 1 or data.get('id') != name or data.get('kind') != 'cron':
        raise ValueError('unknown native automation schema/identity')
    result = {key: data[key] for key in DESKTOP_FIELDS}
    result['rrule'] = ';'.join(sorted(result['rrule'].removeprefix('RRULE:').split(';')))
    # Native timestamps and user notification preferences are not managed fields.
    return result


def crontab():
    result = subprocess.run([str(command_path('crontab')), '-l'], capture_output=True, text=True,
                            encoding='utf-8', env={**os.environ, 'LC_ALL': 'C'})
    if result.returncode == 1 and 'no crontab for' in result.stderr:
        return ''
    if result.returncode:
        raise ValueError(f'cannot read user crontab: {result.stderr.strip()}')
    return result.stdout


def is_cleanup_cron_line(line):
    return not line.lstrip().startswith('#') and line.rstrip('\r\n').endswith(CRON_MARKER)


def cron_configuration(text):
    matches = [line for line in text.splitlines() if is_cleanup_cron_line(line)]
    if len(matches) > 1:
        raise ValueError('multiple managed cleanup cron entries; investigate')
    return {'line': matches[0]} if matches else None


def observe(home, identity):
    if identity.startswith('automation:'):
        return desktop(home, identity)
    if identity == CRON_ID:
        return cron_configuration(crontab())
    if identity.startswith('task-scheduler:'):
        from windows_scheduler import observe as observe_task
        return observe_task(home)
    raise ValueError('unknown cleanup schedule identity')


def preflight_other_entries(home, entries, identity, resolutions=None):
    for target, entry in entries.items():
        if target == identity:
            continue
        if entry['scope'] == {'kind': 'cleanup-schedule'}:
            raise ValueError('another cleanup schedule is already receipted; resolve retirement first')
        current = fingerprint(Path(target), entry['scope'])
        if current != entry['fingerprint'] and (resolutions or {}).get(target) != (current or 'absent'):
            raise ValueError(f'receipted target changed: {target}; no schedule write')


def stable_source(path):
    stable = plain_path(path)
    if not (stable / '.git').exists():
        raise ValueError(f'not a Git checkout: {stable}')
    result = subprocess.run([str(command_path('git')), '-C', str(stable), 'rev-parse',
                             '--path-format=absolute', '--git-common-dir'],
                            capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise ValueError(f'cannot resolve stable source Git common directory: {result.stderr.strip()}')
    common = result.stdout.strip()
    if not common:
        raise ValueError('stable source Git common directory is empty')
    plain_path(common)
    return stable


def cleanup_prompt(home, stable, project_roots=()):
    home, stable = plain_path(home), plain_path(stable)
    python = executable_path(sys.executable)
    roots = tuple(plain_path(root) for root in project_roots)
    skill = stable / 'machine/skills/cleanup-task-artifacts/SKILL.md'
    if not skill.is_file():
        raise ValueError(f'stable cleanup skill is unavailable: {skill}')
    roots_text = ('Use only supported known project roots.' if not roots else
                  f'Use only these explicitly supplied project roots: {", ".join(map(str, roots))}.')
    return (f'Use the cleanup-task-artifacts skill at {skill}. Use {python} to run its discovery script. '
            f'{roots_text} Skip archival/removal when task lifecycle evidence is unavailable. '
            f'Preserve the stable source checkout at {stable} and Codex home at {home}. '
            'Notify only meaningful cleanup, failures, or required action; stay quiet on no-op runs. '
            'Do not reconcile or update machines.')


def cleanup_output_path(home, path):
    if path is None:
        return None
    output = plain_path(path)
    expected = plain_path(home / '.agent-team/cleanup-last-message.txt')
    if not same_path(output, expected):
        raise ValueError('cleanup output must be the private cleanup-last-message.txt file')
    return output


def cleanup_command(home, stable, executable, project_roots=(), output_last_message=None):
    home, stable, executable = plain_path(home), plain_path(stable), executable_path(executable)
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError('Codex executable is unavailable')
    command = [str(executable), 'exec']
    output = cleanup_output_path(home, output_last_message)
    if output is not None:
        command.extend(['--output-last-message', str(output)])
    command.extend(['-C', str(stable), cleanup_prompt(home, stable, project_roots)])
    return command


def cleanup_runner_arguments(home, stable, executable, project_roots=(), output_last_message=None):
    home, stable, executable = plain_path(home), stable_source(stable), executable_path(executable)
    cleanup_command(home, stable, executable, project_roots, output_last_message)
    helper = plain_path(stable / 'machine/cleanup_schedule.py')
    if not helper.is_file():
        raise ValueError(f'stable cleanup scheduler is unavailable: {helper}')
    arguments = [str(helper), 'run-cleanup', '--codex-home', str(home),
                 '--stable-checkout', str(stable), '--codex', str(executable)]
    for root in project_roots:
        arguments.extend(['--project-root', str(plain_path(root))])
    output = cleanup_output_path(home, output_last_message)
    if output is not None:
        arguments.extend(['--output-last-message', str(output)])
    return arguments


def cron_path():
    path = os.environ.get('PATH', '/usr/bin:/bin')
    if sys.platform != 'linux' or 'microsoft' not in os.uname().release.casefold():
        return path
    native = []
    for entry in path.split(':'):
        try:
            executable_path(entry)
        except ValueError as error:
            if 'Windows-mounted DrvFS volume' not in str(error):
                raise
            continue
        native.append(entry)
    if not native:
        raise ValueError('WSL PATH contains no native executable directories')
    return ':'.join(native)


def cron_command(home, stable, executable, project_roots=(), output_last_message=None):
    runner = [str(executable_path(sys.executable)),
              *cleanup_runner_arguments(home, stable, executable, project_roots, output_last_message)]
    return (f'CODEX_HOME={shlex.quote(str(home))} PATH={shlex.quote(cron_path())} '
            + shlex.join(runner))


def run_cleanup(home, stable, executable, project_roots=(), output_last_message=None):
    command = cleanup_command(home, stable, executable, project_roots, output_last_message)
    subprocess.run(command, cwd=stable, check=True, env={**os.environ, 'CODEX_HOME': str(home)})


def windows_action(home, stable, executable, project_roots=(), output_last_message=None):
    home, stable = plain_path(home), stable_source(stable)
    arguments = cleanup_runner_arguments(home, stable, executable, project_roots, output_last_message)
    return {'command': str(executable_path(sys.executable)),
            'arguments': subprocess.list2cmdline(arguments),
            'working_directory': str(stable)}


def save(home, identity, configuration, expected_receipt):
    path = home / '.agent-team/reconciliation-receipts-v1.json'
    raw, entries = read_receipt(path)
    if receipt_hash(raw) != expected_receipt:
        raise ValueError('receipt changed since preflight; inspect actual schedule write before recovery')
    if configuration is None:
        if identity not in entries:
            raise ValueError('retirement has no prior receipt evidence')
        entries.pop(identity)
    else:
        entries[identity] = cleanup_schedule_entry(identity, configuration)
    atomic_file(path, encoded({'version': 1, 'entries': list(entries.values())}) + b'\n')
    print(f'Recorded observed schedule result for {identity}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['inspect', 'record-desktop', 'install-cron', 'retire-cron',
                                              'install-windows', 'retire-windows', 'run-cleanup'])
    parser.add_argument('--codex-home', required=True)
    parser.add_argument('--identity')
    parser.add_argument('--resolve', action='append', type=parse_resolution, default=[],
                        metavar='TARGET=OBSERVED_SHA256_OR_absent', help='approved other target=observation conflict, preserving its receipt')
    parser.add_argument('--approve', help='explicitly authorized conflicting observation fingerprint or absent')
    parser.add_argument('--receipt-hash')
    parser.add_argument('--observed-hash')
    parser.add_argument('--observed-write', action='store_true')
    parser.add_argument('--removed', action='store_true')
    parser.add_argument('--stable-checkout')
    parser.add_argument('--codex')
    parser.add_argument('--project-root', action='append', default=[])
    parser.add_argument('--output-last-message')
    parser.add_argument('--hour', type=int, default=9)
    parser.add_argument('--minute', type=int, default=0)
    args = parser.parse_args()
    home = plain_path(args.codex_home)
    if args.operation == 'run-cleanup':
        if not args.stable_checkout or not args.codex:
            raise ValueError('supply actual stable checkout and Codex executable')
        stable = stable_source(args.stable_checkout)
        run_cleanup(home, stable, args.codex, args.project_root, args.output_last_message)
        return
    windows_operation = args.operation in ('install-windows', 'retire-windows')
    identity = args.identity or (task_scheduler_identity(home)
                                 if windows_operation or (args.operation == 'inspect' and os.name == 'nt')
                                 else CRON_ID)
    if windows_operation and identity != task_scheduler_identity(home):
        raise ValueError('Windows schedule operation requires the canonical Task Scheduler identity')
    if identity.startswith('task-scheduler:') and identity != task_scheduler_identity(home):
        raise ValueError('task scheduler identity does not match the canonical Codex home')
    path = home / '.agent-team/reconciliation-receipts-v1.json'
    raw, entries = read_receipt(path)
    preflight_other_entries(home, entries, identity, dict(args.resolve))
    current = observe(home, identity)
    observed = cleanup_schedule_fingerprint(current)
    if args.operation == 'record-desktop':
        if not identity.startswith('automation:') or not args.observed_write:
            raise ValueError('record only after an observed authorized native API write')
        if args.receipt_hash is None or args.observed_hash != (observed or 'absent'):
            raise ValueError('actual native state differs from the observed write')
        if args.removed != (current is None):
            raise ValueError('native removal/publication state does not match the operation')
        save(home, identity, current, args.receipt_hash)
        return
    cleanup_schedule_preflight(entries.get(identity), identity, current, args.approve)
    if args.operation == 'inspect':
        print(json.dumps({'identity': identity, 'configuration': current,
                          'fingerprint': observed, 'receipt_hash': receipt_hash(raw)}))
        return
    if args.operation == 'install-windows':
        if os.name != 'nt' or not args.stable_checkout or not args.codex:
            raise ValueError('Windows installation requires actual stable checkout and Codex executable')
        action = windows_action(home, args.stable_checkout, args.codex, args.project_root,
                                args.output_last_message)
        if receipt_hash(read_receipt(path)[0]) != receipt_hash(raw):
            raise ValueError('receipt changed immediately before Task Scheduler write')
        from windows_scheduler import install
        actual = install(home, action, args.hour, args.minute, current)
        save(home, identity, actual, receipt_hash(raw))
        return
    if args.operation == 'retire-windows':
        if os.name != 'nt':
            raise ValueError('Windows retirement is only for the actual native Windows target')
        if identity not in entries:
            raise ValueError('task scheduler retirement requires prior receipt evidence')
        if receipt_hash(read_receipt(path)[0]) != receipt_hash(raw):
            raise ValueError('receipt changed immediately before Task Scheduler write')
        from windows_scheduler import retire
        retire(home, current)
        if observe(home, identity) is not None:
            raise ValueError('Task Scheduler task remains after retirement')
        save(home, identity, None, receipt_hash(raw))
        return
    if sys.platform != 'linux' or identity != CRON_ID:
        raise ValueError('cron installation/retirement is only for the actual headless Linux target')
    original = crontab()
    if cron_configuration(original) != current:
        raise ValueError('cron state changed since preflight')
    lines = [line for line in original.splitlines(keepends=True) if not is_cleanup_cron_line(line)]
    if args.operation == 'install-cron':
        if not args.stable_checkout or not args.codex or not 0 <= args.hour <= 23 or not 0 <= args.minute <= 59:
            raise ValueError('supply actual stable checkout, Codex executable, and valid hour/minute')
        stable, executable = stable_source(args.stable_checkout), executable_path(args.codex)
        if not os.access(executable, os.X_OK):
            raise ValueError('stable cleanup source or Codex executable is unavailable')
        command = cron_command(home, stable, executable, args.project_root, args.output_last_message)
        if any(char in command for char in ('\n', '\r', '%')):
            raise ValueError('cron command needs supervised escaping before installation')
        line = f'{args.minute} {args.hour} * * * {command}{CRON_MARKER}\n'
        if len(line.encode('utf-8')) > CRON_MAX_LINE_BYTES:
            raise ValueError(f'generated cron line is too long ({len(line.encode("utf-8"))} bytes; '
                             f'limit {CRON_MAX_LINE_BYTES})')
        if lines and not lines[-1].endswith('\n'):
            raise ValueError('existing crontab lacks final newline; investigate without altering unrelated bytes')
        lines.append(line)
        expected = {'line': line.rstrip('\n')}
    else:
        expected = None
        if identity not in entries:
            raise ValueError('cron retirement requires prior receipt evidence')
    desired = ''.join(lines)
    if crontab() != original or receipt_hash(read_receipt(path)[0]) != receipt_hash(raw):
        raise ValueError('crontab or receipt changed immediately before write')
    subprocess.run([str(command_path('crontab')), '-'], input=desired, text=True, encoding='utf-8', check=True)
    print(f'Wrote {identity}; verification and receipt pending', flush=True)
    actual = crontab()
    if actual != desired or cron_configuration(actual) != expected:
        raise ValueError('crontab readback differs; inspect partial effects without retrying')
    save(home, identity, expected, receipt_hash(raw))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        sys.exit(f'Cleanup schedule stopped: {error}. Actual writes may precede receipt publication; inspect before recovery.')
