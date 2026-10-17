"""Pi's native release acquisition and scoped configuration for reconciliation."""
from __future__ import annotations

import base64
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shlex
import shutil
import stat
import subprocess
import tarfile
import urllib.request
import zipfile

from reconcile import command_path, encoded, fingerprint, plain_path, path_within, same_path


def declaration(source):
    profile = (source / 'machine/PROFILE.md').read_text(encoding='utf-8')
    section = profile.split('## Optional Pi configuration\n')[1].split('## Experiment-to-test migration\n')[0]
    repository = re.search(r'^Release source: https://github.com/([\w.-]+/[\w.-]+)\.$', section, re.M)
    age = re.search(r'^Minimum release age: ([0-9]+) hours\.$', section, re.M)
    if not repository or not age:
        raise ValueError('Pi Profile requires a canonical release source and minimum age')
    platforms = re.findall(r'^\| (darwin|linux|win32) \| (arm64|x64) \| ([\w.-]+) \|$', section, re.M)
    targets = re.findall(r'^\| (pi/[\w.]+) \| ([\w./-]+) \| Whole file \|$', section, re.M)
    integration = re.search(r'^Herdr extension source: `([^`]+)`\.$', section, re.M)
    if not platforms or not targets or not integration:
        raise ValueError('Pi Profile lacks platform, file, or Herdr integration declarations')
    return profile, section, repository.group(1), int(age.group(1)), platforms, targets, integration.group(1)


def roots(source, explicit=None):
    environment = os.environ.get('PI_CODING_AGENT_DIR')
    if environment is not None and (not environment or not Path(environment).is_absolute()):
        raise ValueError('PI_CODING_AGENT_DIR must be an absolute directory')
    effective = plain_path(environment) if environment is not None else plain_path(Path.home() / '.pi/agent')
    requested = plain_path(explicit) if explicit else None
    if requested is not None and environment is not None and not same_path(requested, effective):
        raise ValueError('explicit Pi root disagrees with PI_CODING_AGENT_DIR')
    root = requested or effective
    _, section, _, _, _, _, _ = declaration(source)
    host = 'win32' if os.name == 'nt' else 'posix'
    matches = re.findall(r'^\| ' + host + r' \| ([^|]+) \| ([^|]+) \|$', section, re.M)
    if len(matches) != 1:
        raise ValueError('Pi Profile requires exact native runtime and launcher targets')
    def expand(value):
        value = value.strip().replace('$HOME', str(Path.home()))
        if '$LOCALAPPDATA' in value:
            local = os.environ.get('LOCALAPPDATA')
            if not local or not Path(local).is_absolute():
                raise ValueError('Pi requires an absolute LOCALAPPDATA')
            value = value.replace('$LOCALAPPDATA', local)
        return plain_path(value)
    runtime, launcher = map(expand, matches[0])
    return root, runtime, launcher


def receipt_targets(entries, source):
    """A distinctive instruction file anchors Pi; an absent opt-in preserves all scopes."""
    _, _, _, _, _, declarations, _ = declaration(source)
    anchors = [Path(target) for target, entry in entries.items()
               if Path(target).name == 'HERDR.md' and entry['scope'] == {'kind': 'file'}]
    if len(anchors) > 1:
        raise ValueError('multiple Pi receipt anchors require investigation')
    if not anchors:
        return None, set()
    root = plain_path(anchors[0].parent)
    _, runtime, launcher = roots(source)
    ordinary = {str(plain_path(root / relative)) for _, relative in declarations}
    ordinary.add(str(plain_path(root / 'extensions/herdr-agent-state.ts')))
    ordinary.add(str(plain_path(root / 'licenses/herdr-LICENSE')))
    expected = ordinary | {str(root / 'settings.json'), str(runtime), str(launcher)}
    targets = set()
    for target, entry in entries.items():
        path = Path(target)
        if target in expected:
            targets.add(target)
        elif path_within(path, root):
            raise ValueError('unexpected receipted target under Pi configuration root')
    return root, targets


def semver(value):
    match = re.fullmatch(r'v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value) if isinstance(value, str) else None
    return tuple(map(int, match.groups())) if match else None


def utc(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (AttributeError, ValueError) as error:
        raise ValueError('invalid Pi release publication timestamp') from error
    if result.tzinfo is None or result.utcoffset() != timedelta(0):
        raise ValueError('Pi release publication timestamp must be UTC')
    return result


def api(endpoint):
    return json.loads(subprocess.check_output([str(command_path('gh')), 'api', endpoint]))


def select_release(source, run_start):
    _, _, repository, age, platforms, _, _ = declaration(source)
    architecture = {'aarch64': 'arm64', 'arm64': 'arm64', 'x86_64': 'x64', 'amd64': 'x64'}.get(platform.machine().lower())
    names = [asset for host, arch, asset in platforms if host == os.sys.platform and arch == architecture]
    if len(names) != 1:
        raise ValueError('Pi Profile has no unique native artifact for this platform')
    cutoff = utc(run_start) - timedelta(hours=age)
    eligible = []
    page = 1
    while True:
        releases = api(f'repos/{repository}/releases?per_page=100&page={page}')
        if not isinstance(releases, list):
            raise ValueError('Pi canonical release response is malformed')
        for release in releases:
            if not isinstance(release, dict) or release.get('draft') is not False or release.get('prerelease') is not False:
                continue
            version = semver(release.get('tag_name'))
            if version is None:
                continue
            published = utc(release.get('published_at'))
            if published <= cutoff:
                eligible.append((version, release))
        if len(releases) < 100:
            break
        page += 1
    if not eligible:
        raise ValueError('no stable Pi release meets the Profile minimum age')
    version, release = max(eligible, key=lambda item: item[0])
    if sum(item[0] == version for item in eligible) != 1:
        raise ValueError('ambiguous Pi semantic release version')
    assets = release.get('assets')
    if not isinstance(assets, list):
        raise ValueError('Pi release has no asset inventory')
    selected = {}
    for name in (names[0], 'SHA256SUMS'):
        if any(not isinstance(asset, dict) for asset in assets):
            raise ValueError('Pi asset inventory is malformed')
        matches = [asset for asset in assets if asset.get('name') == name]
        if len(matches) != 1:
            raise ValueError(f'eligible Pi release lacks one exact official asset: {name}')
        asset = matches[0]
        url = f'https://github.com/{repository}/releases/download/{release["tag_name"]}/{name}'
        if asset.get('browser_download_url') != url or type(asset.get('id')) is not int:
            raise ValueError('Pi official asset identity is invalid')
        advertised = asset.get('digest')
        if advertised is not None and not re.fullmatch(r'sha256:[0-9a-f]{64}', advertised):
            raise ValueError('Pi asset advertises an unsupported digest')
        selected[name] = {key: asset[key] for key in ('id', 'name', 'browser_download_url', 'digest') if key in asset}
    return {'version': '.'.join(map(str, version)), 'published_at': release['published_at'],
            'run_start': run_start, 'cutoff': cutoff.isoformat(), 'repository': repository,
            'tag': release['tag_name'], 'archive': selected[names[0]], 'sums': selected['SHA256SUMS']}


def download(asset, target):
    request = urllib.request.Request(asset['browser_download_url'], headers={'User-Agent': 'Agent-Team-Reconciliation'})
    with urllib.request.urlopen(request, timeout=60) as response, target.open('xb') as stream:
        shutil.copyfileobj(response, stream)
    with target.open('rb') as downloaded:
        actual = hashlib.file_digest(downloaded, 'sha256').hexdigest()
    if asset.get('digest') is not None and asset['digest'] != f'sha256:{actual}':
        raise ValueError('Pi asset differs from its advertised SHA-256 digest')
    return actual


def extract(archive, destination):
    """Accept complete ordinary bundles only, without links, devices, or path escapes."""
    seen = set()

    def path_for(name, directory):
        path = PurePosixPath(name)
        if (not name or '\\' in name or path.is_absolute() or '..' in path.parts
                or not path.parts or path.parts[0] != 'pi' or ':' in name):
            raise ValueError('unsafe path in Pi archive')
        key = path.as_posix().casefold() if os.name == 'nt' else path.as_posix()
        if key in seen:
            raise ValueError('duplicate path in Pi archive')
        seen.add(key)
        target = destination.joinpath(*path.parts)
        if target.exists() and not (directory and target.is_dir()):
            raise ValueError('conflicting path in Pi archive')
        return target

    if archive.name.endswith('.tar.gz'):
        with tarfile.open(archive, 'r:gz') as bundle:
            for member in bundle.getmembers():
                if not (member.isfile() or member.isdir()) or member.mode & 0o7000:
                    raise ValueError('unsupported type or privileged mode in Pi archive')
                target = path_for(member.name, member.isdir())
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.extractfile(member) as incoming, target.open('xb') as output:
                        shutil.copyfileobj(incoming, output)
                if os.name != 'nt':
                    target.chmod(member.mode & 0o777)
    elif archive.name.endswith('.zip'):
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                mode = member.external_attr >> 16
                if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR) or mode & 0o7000:
                    raise ValueError('unsupported type or privileged mode in Pi archive')
                target = path_for(member.filename, member.is_dir())
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.open(member) as incoming, target.open('xb') as output:
                        shutil.copyfileobj(incoming, output)
                if os.name != 'nt' and mode:
                    target.chmod(mode & 0o777)
    else:
        raise ValueError('unsupported Pi native archive')
    return destination / 'pi'


def native_version(runtime, timeout):
    executable = runtime / ('pi.exe' if os.name == 'nt' else 'pi')
    package = runtime / 'package.json'
    if not executable.is_file() or not package.is_file():
        raise ValueError('Pi runtime is missing its native executable or package resources')
    version = json.loads(package.read_text(encoding='utf-8')).get('version')
    if semver(version) is None:
        raise ValueError('Pi bundle package has no exact stable version')
    result = subprocess.run([str(executable), '--version'], capture_output=True, text=True,
                            stdin=subprocess.DEVNULL, timeout=timeout)
    if result.returncode or result.stdout.strip() != version:
        raise ValueError('Pi native executable version differs from its complete bundle')
    return version


def ensure_idle(runtime):
    """An upgrade never stops or replaces a running Pi task."""
    runtime = plain_path(runtime)
    if not runtime.exists():
        return  # A proven-absent installation has no mapped executable to replace.
    executable = str(runtime / ('pi.exe' if os.name == 'nt' else 'pi'))
    if os.name == 'nt':
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
                                 'Get-CimInstance Win32_Process | Select-Object ExecutablePath | ConvertTo-Json -Compress'],
                                capture_output=True, text=True, timeout=20)
        if result.returncode:
            raise ValueError('cannot inspect active native Pi processes; preserve runtime')
        processes = json.loads(result.stdout or '[]')
        processes = processes if isinstance(processes, list) else [processes]
        running = any(item.get('ExecutablePath', '').casefold() == executable.casefold()
                      for item in processes if item.get('ExecutablePath'))
    elif os.sys.platform == 'darwin':
        # lsof identifies the mapped executable even when argv[0] was relative.
        result = subprocess.run([str(command_path('lsof')), '-t', '--', executable],
                                capture_output=True, text=True, timeout=20)
        if result.returncode not in (0, 1) or result.stderr.strip():
            raise ValueError('cannot inspect active Pi executable mappings; preserve runtime')
        running = bool(result.stdout.strip())
    elif os.sys.platform == 'linux':
        running = False
        for process in Path('/proc').iterdir():
            if not process.name.isdigit():
                continue
            try:
                if process.stat().st_uid != os.getuid():
                    continue
                mapped = os.readlink(process / 'exe')
            except FileNotFoundError:
                continue  # Process exited while observing it.
            except PermissionError as error:
                raise ValueError('cannot inspect an owned process executable; preserve runtime') from error
            if mapped == executable:
                running = True
                break
    else:
        raise ValueError('cannot establish native Pi process safety on this platform')
    if running:
        raise ValueError('managed Pi runtime is active; preserve tasks and retry after they exit')


def acquire(source, stage, runtime, entries, run_start, timeout):
    release = select_release(source, run_start)
    root = stage / 'pi-native'
    root.mkdir()
    sums = root / 'SHA256SUMS'
    download(release['sums'], sums)
    matches = re.findall(r'^([0-9a-f]{64}) [ *]' + re.escape(release['archive']['name']) + r'$',
                         sums.read_text(encoding='utf-8'), re.M)
    if len(matches) != 1:
        raise ValueError('Pi SHA256SUMS does not identify the exact official archive once')
    release['sha256'] = matches[0]
    old = entries.get(str(runtime))
    if runtime.exists():
        if old is None or old['scope'] != {'kind': 'directory', 'modes': True} or fingerprint(runtime, old['scope']) != old['fingerprint']:
            raise ValueError('existing Pi runtime lacks unchanged ownership evidence; investigate before acquisition')
        installed = native_version(runtime, timeout)
        if semver(installed) >= semver(release['version']):
            print(json.dumps({'pi_release': release, 'installed_version': installed,
                              'result': 'preserved equal or newer owned runtime'}, sort_keys=True), flush=True)
            return runtime, installed
        ensure_idle(runtime)
    elif old is not None:
        raise ValueError('managed Pi runtime is missing; investigate before acquisition')
    archive = root / release['archive']['name']
    actual = download(release['archive'], archive)
    if actual != matches[0]:
        raise ValueError('Pi native archive differs from SHA256SUMS')
    bundle = extract(archive, root)
    if native_version(bundle, timeout) != release['version']:
        raise ValueError('Pi native archive does not match the selected release')
    release['sha256'] = actual
    print(json.dumps({'pi_release': release, 'result': 'verified complete native bundle'}, sort_keys=True), flush=True)
    return bundle, release['version']


def skill_paths(source, skills, upstream):
    from reconcile import claude_packages

    profile = (source / 'machine/PROFILE.md').read_text(encoding='utf-8')
    # Pi uses the same relevant complete package inventory as optional Claude.
    copied, packages = claude_packages(profile)
    return [str(plain_path(skills / name)) for name in copied] + [
        str(plain_path(upstream / name)) for name, _ in packages]


def settings_scope(source, paths):
    defaults = json.loads((source / 'machine/pi/settings.json').read_text(encoding='utf-8'))
    return {'kind': 'json', 'fields': sorted(defaults),
            'resources': {'skills': sorted(paths)}}


def settings_projection(document, scope):
    result = {key: [type(document[key]).__name__, repr(document[key])] if key in document else ['absent']
              for key in sorted(scope['fields'])}
    for field, paths in scope.get('resources', {}).items():
        values = document.get(field, [])
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ValueError('Pi resource settings must contain arrays of paths')
        result[field] = {path: values.count(path) for path in paths}
    return result


def prepare_settings(source, actual, output, scope, prior_scope):
    defaults = json.loads((source / 'machine/pi/settings.json').read_text(encoding='utf-8'))
    if set(defaults) != set(scope['fields']) or any(not isinstance(value, str) for value in defaults.values()):
        raise ValueError('Pi source settings must declare exactly its owned scalar fields')
    document = json.loads(actual.read_text(encoding='utf-8')) if actual.exists() else {}
    if not isinstance(document, dict):
        raise ValueError('Pi settings must be a JSON object')
    for field in set(prior_scope.get('fields', [])) - set(scope['fields']):
        document.pop(field, None)
    document.update(defaults)
    prior = prior_scope.get('resources', {})
    for field in prior.keys() | scope['resources'].keys():
        paths = scope['resources'].get(field, [])
        values = document.get(field, [])
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ValueError('Pi resource settings must contain arrays of paths')
        document[field] = [value for value in values if value not in set(prior.get(field, [])) | set(paths)] + paths
    output.write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    verify_settings(output, source, actual, scope, prior_scope)


def verify_settings(candidate, source, actual, scope, prior_scope):
    proposed = json.loads(candidate.read_text(encoding='utf-8'))
    original = json.loads(actual.read_text(encoding='utf-8')) if actual.exists() else {}
    defaults = json.loads((source / 'machine/pi/settings.json').read_text(encoding='utf-8'))
    expected = {**defaults, **scope['resources']}
    if settings_projection(proposed, scope) != settings_projection(expected, scope):
        raise ValueError('Pi settings candidate differs from declared owned values')
    retired = set(prior_scope.get('fields', [])) - set(scope['fields'])
    if retired & proposed.keys():
        raise ValueError('Pi settings candidate retains retired scalar fields')
    owned = set(scope['fields']) | set(prior_scope.get('fields', []))
    def unmanaged(document):
        document = dict(document)
        for key in owned:
            document.pop(key, None)
        for key in scope['resources'].keys() | prior_scope.get('resources', {}).keys():
            paths = set(scope['resources'].get(key, [])) | set(prior_scope.get('resources', {}).get(key, []))
            document[key] = [value for value in document.get(key, []) if value not in paths]
        return encoded(document)
    if unmanaged(proposed) != unmanaged(original):
        raise ValueError('Pi settings candidate changes unmanaged values or resources')


def prepare_integration(source, stage, herdr_ref):
    _, _, _, _, _, _, relative = declaration(source)
    blob = api(f'repos/herdrdev/herdr/contents/{relative}?ref={herdr_ref}')
    if blob.get('type') != 'file' or blob.get('encoding') != 'base64':
        raise ValueError('native Herdr Pi extension is unavailable')
    content = base64.b64decode(blob['content'], validate=False)
    actual = hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()
    if blob.get('sha') != actual:
        raise ValueError('native Herdr Pi extension differs from upstream Git blob')
    destination = stage / 'herdr-agent-state.ts'
    destination.write_bytes(content)
    license_blob = api(f'repos/herdrdev/herdr/contents/LICENSE?ref={herdr_ref}')
    license_data = base64.b64decode(license_blob['content'])
    if hashlib.sha1(f'blob {len(license_data)}\0'.encode() + license_data).hexdigest() != license_blob.get('sha'):
        raise ValueError('Herdr integration license differs from upstream Git blob')
    (stage / 'herdr-LICENSE').write_bytes(license_data)
    return destination


def prepare_launcher(stage, runtime, root, codex_home):
    executable = runtime / ('pi.exe' if os.name == 'nt' else 'pi')
    destination = stage / ('pi.cmd' if os.name == 'nt' else 'pi-launcher')
    if os.name == 'nt':
        if any(character in str(path) for path in (executable, root, codex_home) for character in '%\r\n"'):
            raise ValueError('Pi Windows paths cannot be safely represented in a native launcher')
        content = ('@echo off\r\nsetlocal DisableDelayedExpansion\r\n'
                   f'set "PI_CODING_AGENT_DIR={root}"\r\n'
                   f'set "CODEX_HOME={codex_home}"\r\n"{executable}" %*\r\n')
    else:
        content = ('#!/bin/sh\n'
                   f'export PI_CODING_AGENT_DIR={shlex.quote(str(root))}\n'
                   f'export CODEX_HOME={shlex.quote(str(codex_home))}\n'
                   f'exec {shlex.quote(str(executable))} "$@"\n')
    destination.write_bytes(content.encode('utf-8'))
    destination.chmod(0o755)
    return destination


def inventory(source, root, runtime, launcher, bundle, stage, skills, upstream):
    _, _, _, _, _, declarations, _ = declaration(source)
    rows = [(source / 'machine' / candidate, root / target, {'kind': 'file'})
            for candidate, target in declarations]
    rows.extend([(bundle, runtime, {'kind': 'directory', 'modes': True}),
                 (stage / ('pi.cmd' if os.name == 'nt' else 'pi-launcher'), launcher,
                  {'kind': 'file', 'executable': True}),
                 (stage / 'herdr-agent-state.ts', root / 'extensions/herdr-agent-state.ts', {'kind': 'file'}),
                 (stage / 'herdr-LICENSE', root / 'licenses/herdr-LICENSE', {'kind': 'file'}),
                 (stage / 'candidate-pi-settings.json', root / 'settings.json',
                  settings_scope(source, skill_paths(source, skills, upstream)))])
    return rows
