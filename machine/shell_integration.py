"""The declared Codex shell helper and exact startup-hook scopes."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

from reconcile import digest, executable_path, plain_path, same_path


def declaration(source):
    profile = (source / 'machine/PROFILE.md').read_text(encoding='utf-8')
    section = profile.split('## Shared Codex shell integration\n')[1].split('\n## ', 1)[0]
    helper = re.search(r'^Helper source: `([^`]+)`\.$', section, re.M)
    destination = re.search(r'^Helper destination: `\$CODEX_HOME/([^`]+)`\.$', section, re.M)
    marker = re.search(r'^Hook marker: `([^`]+)`\.$', section, re.M)
    targets = dict(re.findall(r'^\| (bash|bash-login|zsh) \| ([^|]+) \|$', section, re.M))
    if not helper or not destination or not marker or set(targets) != {'bash', 'bash-login', 'zsh'}:
        raise ValueError('Profile requires one shell helper, marker and native startup declarations')
    return helper.group(1), destination.group(1), marker.group(1), {key: value.strip() for key, value in targets.items()}


def markers(scope):
    if (set(scope) != {'kind', 'shell', 'marker'} or scope['kind'] != 'shell-hook'
            or scope['shell'] not in ('bash', 'zsh')
            or not re.fullmatch(r'[a-z0-9 -]+', scope['marker'])):
        raise ValueError('unknown shell hook scope; preserve and investigate')
    identity = f"{scope['marker']} {scope['shell']}"
    return f'# >>> {identity} >>>'.encode(), f'# <<< {identity} <<<'.encode()


def split_hook(data, scope):
    """Return exact unowned prefix, owned block, suffix; never parse shell syntax."""
    begin, end = markers(scope)
    family = scope['marker'].encode()
    marker_lines = [line.rstrip(b'\r\n') for line in data.splitlines(keepends=True)
                    if family in line and (b'# >>>' in line or b'# <<<' in line)]
    if not marker_lines:
        return data, None, b''
    if marker_lines != [begin, end] or data.count(begin) != 1 or data.count(end) != 1:
        raise ValueError('duplicate or malformed shell hook markers; preserve and investigate')
    start = data.index(begin)
    finish = data.index(end) + len(end)
    # The leading and trailing LF belong to the hook, including on first creation.
    if start == 0 or data[start - 1:start] != b'\n' or data[finish:finish + 1] != b'\n':
        raise ValueError('shell hook boundary changed; preserve and investigate')
    if data[start - 1:finish + 1].count(b'\r'):
        raise ValueError('shell hook newline representation changed; preserve and investigate')
    return data[:start - 1], data[start - 1:finish + 1], data[finish + 1:]


def raw_file(path):
    path = plain_path(path)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError('shell startup target is not an ordinary file')
    return path.read_bytes()


def hook_fingerprint(path, scope):
    raw = raw_file(path)
    if raw is None:
        return None
    _, block, _ = split_hook(raw, scope)
    return digest(block) if block is not None else None


def hook_bytes(helper, scope):
    begin, end = markers(scope)
    version = 'BASH_VERSION' if scope['shell'] == 'bash' else 'ZSH_VERSION'
    body = (f'\n{begin.decode()}\n'
            f'if [ -n "${{{version}-}}" ]; then\n'
            '    case $- in\n'
            '        *i*)\n'
            '            if ! alias codex >/dev/null 2>&1 && ! typeset -f codex >/dev/null 2>&1; then\n'
            f'                . {shlex.quote(str(helper))}\n'
            '            fi\n'
            '            ;;\n'
            '    esac\n'
            'fi\n'
            f'{end.decode()}\n')
    return body.encode('utf-8')


def reject_competing_definition(raw, scope):
    before, _, after = split_hook(raw or b'', scope)
    # Recognize direct declarations only; native hook/helper guards preserve any
    # alias/function supplied later by other startup code without interpreting it.
    declaration = re.compile(rb'(?m)^[ \t]*(?:function[ \t]+codex(?:[ \t{(]|$)|'
                             rb'codex[ \t]*\([ \t]*\)|'
                             rb'alias[ \t]+(?:[^\n]*[ \t])?codex[ \t]*=)')
    if declaration.search(before + after):
        raise ValueError('startup file declares a competing codex alias/function; preserve and investigate')


def candidate_path(stage, target):
    return stage / ('shell-hook-' + digest(str(target).encode()) + '.sh')


def validate_candidate(candidate, actual, helper, scope):
    proposed = raw_file(candidate)
    original = raw_file(actual)
    before, _, after = split_hook(original or b'', scope)
    proposed_before, block, proposed_after = split_hook(proposed or b'', scope)
    if block != hook_bytes(helper, scope) or before + after != proposed_before + proposed_after:
        raise ValueError('shell hook candidate changes unowned bytes or differs from the declared hook')
    reject_competing_definition(original, scope)


def available_shells():
    if sys.platform not in ('darwin', 'linux'):
        return {}
    result = {}
    for shell in ('bash', 'zsh'):
        executable = shutil.which(shell)
        if executable is None:
            continue
        executable = str(executable_path(executable))
        probe = subprocess.run([executable, '--version'], stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, timeout=20)
        if probe.returncode:
            raise ValueError(f'available {shell} version probe failed')
        if shell == 'bash':
            version = re.search(r'version ([0-9]+)\.([0-9]+)', probe.stdout)
            if not version or tuple(map(int, version.groups())) < (3, 2):
                raise ValueError('available Bash must support version 3.2 or newer')
        result[shell] = executable
    return result


def startup_probe(executable, shell, mode):
    # Native provenance identifies sourced definitions without exposing bodies.
    command = r'''
_agent_team_kind=none
_agent_team_source=
if alias codex >/dev/null 2>&1; then
    _agent_team_kind=alias
elif typeset -f codex >/dev/null 2>&1; then
    _agent_team_kind=function
    if [ -n "${BASH_VERSION-}" ]; then
        shopt -s extdebug
        _agent_team_source=$(declare -F codex)
    else
        zmodload zsh/parameter || exit 1
        _agent_team_source=${functions_source[codex]-}
    fi
fi
printf '\036agent-team-shell\037%s\037%s\037%s' "$_agent_team_kind" "$_agent_team_source" "${ZDOTDIR-$HOME}"
'''
    result = subprocess.run([executable, mode, command], stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=20)
    marker = b'\x1eagent-team-shell\x1f'
    if result.returncode or result.stdout.count(marker) != 1:
        raise ValueError(f'native {shell} startup cannot establish shell routing provenance')
    payload = result.stdout.split(marker, 1)[1].split(b'\x1f')
    if len(payload) != 3 or payload[0] not in (b'none', b'alias', b'function'):
        raise ValueError(f'native {shell} startup provenance is ambiguous')
    kind, origin, root = (os.fsdecode(value) for value in payload)
    if kind == 'function' and shell == 'bash':
        fields = origin.split(' ', 2)
        if len(fields) != 3 or fields[0] != 'codex' or not fields[1].isdigit():
            raise ValueError('Bash cannot establish its Codex function source')
        origin = fields[2]
    return kind, origin, root


def inspect_startup(shells, helper, entries):
    old = entries.get(str(helper))
    managed = (old is not None and old['scope'] == {'kind': 'file'}
               and (raw := raw_file(helper)) is not None and digest(raw) == old['fingerprint'])
    roots = set()
    for shell, executable in shells.items():
        modes = ('-c', '-ic', '-lic') if shell == 'zsh' else ('-ic', '-lic')
        for mode in modes:
            kind, origin, root = startup_probe(executable, shell, mode)
            if kind != 'none' and (kind != 'function' or not managed
                                   or not origin or not same_path(plain_path(origin), helper)):
                raise ValueError(f'native {shell} startup has a competing codex alias/function; preserve it')
            if shell == 'zsh':
                if not root or not Path(root).is_absolute() or '\n' in root or '\r' in root:
                    raise ValueError('effective ZDOTDIR is not an unambiguous absolute root')
                roots.add(str(plain_path(root)))
    if 'zsh' in shells and len(roots) != 1:
        raise ValueError('Zsh startup modes disagree on effective ZDOTDIR; preserve and investigate')
    return Path(roots.pop()) if roots else None


def inventory(source, home, entries, stage, prepare=False):
    relative, destination, marker, declarations = declaration(source)
    helper_source = plain_path(source / 'machine' / relative)
    helper_target = plain_path(home / destination)
    shells = available_shells()
    effective_zsh_root = inspect_startup(shells, helper_target, entries)
    hooks = {}
    if 'bash' in shells:
        startup = declarations['bash']
        logins = [value.strip() for value in declarations['bash-login'].split(',')]
        if (not startup or Path(startup).name != startup or not logins
                or any(not value or Path(value).name != value for value in logins)):
            raise ValueError('Profile Bash startup declarations are malformed')
        login = None
        for value in logins:
            candidate = plain_path(Path.home() / value)
            if candidate.exists():
                login = candidate
                break
        login = login or plain_path(Path.home() / logins[0])
        hooks['bash'] = [plain_path(Path.home() / startup), login]
    if 'zsh' in shells:
        suffix = declarations['zsh'].removeprefix('$ZDOTDIR/')
        if suffix == declarations['zsh'] or not suffix or Path(suffix).name != suffix:
            raise ValueError('Profile Zsh startup declaration is malformed')
        hooks['zsh'] = [plain_path(effective_zsh_root / suffix)]
    preserved = set()
    for target, entry in entries.items():
        scope = entry['scope']
        if scope.get('kind') == 'shell-hook':
            markers(scope)
            shell = scope['shell']
            if shell not in shells:
                preserved.add(target)
            elif scope['marker'] != marker or target not in {str(path) for path in hooks[shell]}:
                raise ValueError('shell startup root or login precedence differs from its receipt anchor')
        elif Path(target).parts[-2:] == Path(destination).parts[-2:]:
            if not same_path(plain_path(target), helper_target) or scope != {'kind': 'file'}:
                raise ValueError('shell helper destination differs from its receipt anchor')
            if not shells:
                preserved.add(target)
    if not shells:
        return [], preserved
    for shell, executable in shells.items():
        syntax = subprocess.run([executable, '-n', str(helper_source)], stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=20)
        if syntax.returncode:
            raise ValueError(f'{shell} rejected the declared shell helper syntax')
    rows = [(helper_source, helper_target, {'kind': 'file'})]
    for shell, targets in hooks.items():
        for target in targets:
            scope = {'kind': 'shell-hook', 'shell': shell, 'marker': marker}
            candidate = candidate_path(stage, target)
            if prepare:
                original = raw_file(target)
                before, _, after = split_hook(original or b'', scope)
                reject_competing_definition(original, scope)
                candidate.write_bytes(before + hook_bytes(helper_target, scope) + after)
            validate_candidate(candidate, target, helper_target, scope)
            syntax = subprocess.run([shells[shell], '-n', str(candidate)], stdin=subprocess.DEVNULL,
                                    capture_output=True, timeout=20)
            if syntax.returncode:
                raise ValueError(f'{shell} rejected the complete startup candidate syntax')
            rows.append((candidate, target, scope))
    return rows, preserved
