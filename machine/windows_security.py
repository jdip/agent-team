"""Native Windows DACL preservation for reconciliation publication.

The directory API deliberately starts before ``copytree``.  The empty staging
wrapper receives an exact, protected copy of the intended target parent's DACL,
so objects subsequently created below it inherit the same ACEs they would have
in the live location.  Existing path-specific DACLs are then overlaid on the
prepared tree before the live tree is removed.

Only discretionary access control is written here.  Owner, primary group, and
mandatory integrity label are observed and must already match on replacement
objects; other SACL information remains outside reconciliation ownership.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass, replace
import os
from pathlib import Path
import stat


_OWNER_SECURITY_INFORMATION = 0x00000001
_GROUP_SECURITY_INFORMATION = 0x00000002
_DACL_SECURITY_INFORMATION = 0x00000004
_LABEL_SECURITY_INFORMATION = 0x00000010
_UNPROTECTED_DACL_SECURITY_INFORMATION = 0x20000000
_PROTECTED_DACL_SECURITY_INFORMATION = 0x80000000
_SE_DACL_PRESENT = 0x0004
_SE_SACL_PRESENT = 0x0010
_SE_DACL_PROTECTED = 0x1000
_SE_FILE_OBJECT = 1
_ACL_SIZE_INFORMATION_CLASS = 2
_FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
_INHERITED_ACE = 0x10
_GENERIC_WRITE = 0x40000000
_DELETE = 0x00010000
_CREATE_NEW = 1
_FILE_ATTRIBUTE_NORMAL = 0x00000080
_FILE_DISPOSITION_INFO_CLASS = 4
_SECURITY_DESCRIPTOR_REVISION = 1


class _ACL_SIZE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('AceCount', wintypes.DWORD),
        ('AclBytesInUse', wintypes.DWORD),
        ('AclBytesFree', wintypes.DWORD),
    ]


class _SECURITY_DESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ('Revision', ctypes.c_ubyte),
        ('Sbz1', ctypes.c_ubyte),
        ('Control', wintypes.WORD),
        ('Owner', ctypes.c_void_p),
        ('Group', ctypes.c_void_p),
        ('Sacl', ctypes.c_void_p),
        ('Dacl', ctypes.c_void_p),
    ]


class _SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('nLength', wintypes.DWORD),
        ('lpSecurityDescriptor', ctypes.c_void_p),
        ('bInheritHandle', wintypes.BOOL),
    ]


class _FILE_DISPOSITION_INFO(ctypes.Structure):
    _fields_ = [('DeleteFile', wintypes.BOOL)]


@dataclass(frozen=True, repr=False)
class _ObjectSecurity:
    kind: str
    owner: bytes
    group: bytes
    dacl: bytes | None
    label: bytes | None
    protected: bool


@dataclass(frozen=True, repr=False)
class DirectorySecurityState:
    """Opaque, in-memory evidence for one prepared directory publication."""

    target: str
    wrapper: str
    parent: _ObjectSecurity
    live: dict[str, _ObjectSecurity] | None
    parent_anchor: str
    parent_anchor_security: _ObjectSecurity
    parent_chain: tuple[tuple[str, _ObjectSecurity], ...]
    prepared: str | None = None
    staged: dict[str, _ObjectSecurity] | None = None
    final: dict[str, _ObjectSecurity] | None = None


@dataclass(frozen=True)
class _WindowsApi:
    get_named_security_info: object
    set_named_security_info: object
    get_security_descriptor_control: object
    get_acl_information: object
    get_length_sid: object
    initialize_security_descriptor: object
    set_security_descriptor_dacl: object
    set_security_descriptor_control: object
    local_free: object
    create_file: object
    close_handle: object
    set_file_information: object
    replace_file: object


_WINDOWS_API = None


def _api():
    global _WINDOWS_API
    if os.name != 'nt':
        raise OSError('native Windows security APIs are unavailable on this platform')
    if _WINDOWS_API is not None:
        return _WINDOWS_API

    advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    get_named = advapi32.GetNamedSecurityInfoW
    get_named.argtypes = [
        wintypes.LPWSTR, ctypes.c_int, wintypes.DWORD,
        ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    get_named.restype = wintypes.DWORD

    set_named = advapi32.SetNamedSecurityInfoW
    set_named.argtypes = [
        wintypes.LPWSTR, ctypes.c_int, wintypes.DWORD,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
    ]
    set_named.restype = wintypes.DWORD

    get_control = advapi32.GetSecurityDescriptorControl
    get_control.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(wintypes.WORD),
        ctypes.POINTER(wintypes.DWORD),
    ]
    get_control.restype = wintypes.BOOL

    get_acl_information = advapi32.GetAclInformation
    get_acl_information.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.c_int,
    ]
    get_acl_information.restype = wintypes.BOOL

    get_length_sid = advapi32.GetLengthSid
    get_length_sid.argtypes = [ctypes.c_void_p]
    get_length_sid.restype = wintypes.DWORD

    initialize_descriptor = advapi32.InitializeSecurityDescriptor
    initialize_descriptor.argtypes = [ctypes.c_void_p, wintypes.DWORD]
    initialize_descriptor.restype = wintypes.BOOL

    set_descriptor_dacl = advapi32.SetSecurityDescriptorDacl
    set_descriptor_dacl.argtypes = [
        ctypes.c_void_p, wintypes.BOOL, ctypes.c_void_p, wintypes.BOOL,
    ]
    set_descriptor_dacl.restype = wintypes.BOOL

    set_descriptor_control = advapi32.SetSecurityDescriptorControl
    set_descriptor_control.argtypes = [ctypes.c_void_p, wintypes.WORD, wintypes.WORD]
    set_descriptor_control.restype = wintypes.BOOL

    local_free = kernel32.LocalFree
    local_free.argtypes = [ctypes.c_void_p]
    local_free.restype = ctypes.c_void_p

    create_file = kernel32.CreateFileW
    create_file.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(_SECURITY_ATTRIBUTES), wintypes.DWORD,
        wintypes.DWORD, wintypes.HANDLE,
    ]
    create_file.restype = wintypes.HANDLE

    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [wintypes.HANDLE]
    close_handle.restype = wintypes.BOOL

    set_file_information = kernel32.SetFileInformationByHandle
    set_file_information.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
    ]
    set_file_information.restype = wintypes.BOOL

    replace_file = kernel32.ReplaceFileW
    replace_file.argtypes = [
        wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR,
        wintypes.DWORD, ctypes.c_void_p, ctypes.c_void_p,
    ]
    replace_file.restype = wintypes.BOOL

    _WINDOWS_API = _WindowsApi(
        get_named, set_named, get_control, get_acl_information, get_length_sid,
        initialize_descriptor, set_descriptor_dacl, set_descriptor_control,
        local_free, create_file, close_handle, set_file_information, replace_file)
    return _WINDOWS_API


def _path_text(path):
    value = os.path.abspath(os.fspath(path))
    if value.startswith('\\\\'):
        raise ValueError(f'UNC path is outside native reconciliation: {path}')
    if not os.path.isabs(value) or not os.path.splitdrive(value)[0]:
        raise ValueError(f'expected an absolute local Windows path: {path}')
    return value if value.startswith('\\\\?\\') else '\\\\?\\' + value


def _same_path(left, right):
    return os.path.abspath(os.fspath(left)) == os.path.abspath(os.fspath(right))


def _kind(path):
    try:
        status = os.lstat(path)
    except FileNotFoundError:
        return None
    attributes = getattr(status, 'st_file_attributes', 0)
    if attributes & _FILE_ATTRIBUTE_REPARSE_POINT:
        raise ValueError(f'reparse point requires investigation: {path}')
    if stat.S_ISDIR(status.st_mode):
        return 'directory'
    if stat.S_ISREG(status.st_mode):
        return 'file'
    raise ValueError(f'unsupported filesystem object: {path}')


def _security(path, kind=None):
    kind = kind or _kind(path)
    if kind is None:
        raise FileNotFoundError(path)
    api = _api()
    owner = ctypes.c_void_p()
    group = ctypes.c_void_p()
    dacl = ctypes.c_void_p()
    label = ctypes.c_void_p()
    descriptor = ctypes.c_void_p()
    status = api.get_named_security_info(
        _path_text(path), _SE_FILE_OBJECT,
        (_OWNER_SECURITY_INFORMATION | _GROUP_SECURITY_INFORMATION
         | _DACL_SECURITY_INFORMATION | _LABEL_SECURITY_INFORMATION),
        ctypes.byref(owner), ctypes.byref(group), ctypes.byref(dacl),
        ctypes.byref(label), ctypes.byref(descriptor))
    if status:
        raise ctypes.WinError(status)
    try:
        control = wintypes.WORD()
        revision = wintypes.DWORD()
        if not api.get_security_descriptor_control(
                descriptor, ctypes.byref(control), ctypes.byref(revision)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not control.value & _SE_DACL_PRESENT:
            raise ValueError(f'filesystem object has no present DACL: {path}')
        def acl_bytes(pointer):
            if not pointer.value:
                return None
            details = _ACL_SIZE_INFORMATION()
            if not api.get_acl_information(
                    pointer, ctypes.byref(details), ctypes.sizeof(details),
                    _ACL_SIZE_INFORMATION_CLASS):
                raise ctypes.WinError(ctypes.get_last_error())
            # Ignore allocator slack, but make the retained ACL self-contained:
            # the ACL header's size must not still cover discarded free bytes.
            compact = bytearray(ctypes.string_at(pointer, details.AclBytesInUse))
            compact[2:4] = details.AclBytesInUse.to_bytes(2, 'little')
            return bytes(compact)

        def sid_bytes(pointer):
            length = api.get_length_sid(pointer)
            if not length:
                raise ctypes.WinError(ctypes.get_last_error())
            return ctypes.string_at(pointer, length)

        if not owner.value or not group.value:
            raise ValueError(f'filesystem object lacks owner or group identity: {path}')
        raw_label = acl_bytes(label)
        if not control.value & _SE_SACL_PRESENT and raw_label is not None:
            raise ValueError(f'inconsistent mandatory-label security descriptor: {path}')
        return _ObjectSecurity(
            kind=kind,
            owner=sid_bytes(owner),
            group=sid_bytes(group),
            dacl=acl_bytes(dacl),
            label=raw_label,
            protected=bool(control.value & _SE_DACL_PROTECTED))
    finally:
        if descriptor.value:
            api.local_free(descriptor)


def _set_security(path, security, *, protected=None):
    actual_kind = _kind(path)
    if actual_kind != security.kind:
        raise ValueError(
            f'filesystem kind changed while applying DACL: expected '
            f'{security.kind}, observed {actual_kind}: {path}')
    protected = security.protected if protected is None else protected
    backing = None
    dacl = None
    if security.dacl is not None:
        backing = ctypes.create_string_buffer(security.dacl)
        dacl = ctypes.cast(backing, ctypes.c_void_p)
    information = _DACL_SECURITY_INFORMATION | (
        _PROTECTED_DACL_SECURITY_INFORMATION if protected
        else _UNPROTECTED_DACL_SECURITY_INFORMATION)
    status = _api().set_named_security_info(
        _path_text(path), _SE_FILE_OBJECT, information,
        None, None, dacl, None)
    if status:
        raise ctypes.WinError(status)


def _without_inherited_ace_flags(dacl):
    if dacl is None:
        return None
    explicit = bytearray(dacl)
    if len(explicit) < 8:
        raise ValueError('invalid ACL header')
    ace_count = int.from_bytes(explicit[4:6], 'little')
    offset = 8
    for _ in range(ace_count):
        if offset + 4 > len(explicit):
            raise ValueError('invalid ACE header')
        size = int.from_bytes(explicit[offset + 2:offset + 4], 'little')
        if size < 4 or offset + size > len(explicit):
            raise ValueError('invalid ACE size')
        explicit[offset + 1] &= ~_INHERITED_ACE
        offset += size
    if offset != len(explicit):
        raise ValueError('unexpected trailing ACL data')
    return bytes(explicit)


def _protected_copy(security):
    """Represent the DACL Windows stores when a copied ACL is protected.

    SetNamedSecurityInfo makes transplanted inherited ACEs explicit, clearing
    only INHERITED_ACE.  Their effective and propagation flags are retained.
    An already-protected descriptor carrying inherited ACE provenance cannot be
    represented exactly through this API, so stop instead of changing its
    future unprotect behavior.
    """
    explicit = _without_inherited_ace_flags(security.dacl)
    if security.protected and explicit != security.dacl:
        raise ValueError('protected DACL with inherited ACEs is unsupported')
    return replace(security, dacl=explicit, protected=True)


def _key(parts):
    return os.path.join(*parts) if parts else ''


def _tree_paths(root):
    root = Path(root)
    if _kind(root) != 'directory':
        raise ValueError(f'expected ordinary directory: {root}')
    result = {'': (root, 'directory')}
    pending = [(root, ())]
    while pending:
        parent, relative = pending.pop()
        children = []
        with os.scandir(parent) as entries:
            for entry in entries:
                path = Path(entry.path)
                kind = _kind(path)
                parts = relative + (entry.name,)
                key = _key(parts)
                if key in result:
                    raise ValueError(f'ambiguous case-insensitive path in directory tree: {path}')
                result[key] = (path, kind)
                if kind == 'directory':
                    children.append((path, parts))
        pending.extend(reversed(sorted(children, key=lambda item: item[0].name.casefold())))
    return result


def _tree_security(root):
    return {key: _security(path, kind) for key, (path, kind) in _tree_paths(root).items()}


def _assert_tree(expected, actual, description):
    if expected != actual:
        raise ValueError(f'{description} security metadata changed; investigate before continuing')


def _matching_live_key(target, candidate_key, live):
    """Resolve a differently-cased spelling only when Windows resolves it.

    Exact spelling stays authoritative for case-sensitive directories.  On an
    ordinary case-insensitive directory, ``samefile`` maps a case-only candidate
    rename back to the old object whose access restrictions must be retained.
    """
    if candidate_key in live:
        return candidate_key
    requested = Path(target) / candidate_key
    if _kind(requested) is None:
        return None
    matches = []
    for old_key in live:
        if not old_key:
            continue
        try:
            if os.path.samefile(requested, Path(target) / old_key):
                matches.append(old_key)
        except FileNotFoundError:
            continue
    if len(matches) != 1:
        raise ValueError(
            f'ambiguous relative path identity while preserving DACL: {candidate_key}')
    return matches[0]


def create_file(path: Path, reference: Path):
    """Atomically create an empty file with a protected reference DACL.

    ``CREATE_NEW`` and ``SECURITY_ATTRIBUTES`` attach the DACL during object
    creation, before another process can acquire a handle under staging-parent
    permissions.  The returned file descriptor owns the native handle.
    """
    import msvcrt

    path, reference = Path(path), Path(reference)
    if _same_path(path, reference):
        raise ValueError('staging file and security reference must be distinct')
    if _kind(reference) != 'file':
        raise ValueError('file security reference must be an ordinary existing file')
    reference_security = _security(reference, 'file')
    protected = _protected_copy(reference_security)

    dacl_backing = None
    dacl = None
    if protected.dacl is not None:
        dacl_backing = ctypes.create_string_buffer(protected.dacl)
        dacl = ctypes.cast(dacl_backing, ctypes.c_void_p)
    descriptor = _SECURITY_DESCRIPTOR()
    api = _api()
    if not api.initialize_security_descriptor(
            ctypes.byref(descriptor), _SECURITY_DESCRIPTOR_REVISION):
        raise ctypes.WinError(ctypes.get_last_error())
    if not api.set_security_descriptor_dacl(
            ctypes.byref(descriptor), True, dacl, False):
        raise ctypes.WinError(ctypes.get_last_error())
    if not api.set_security_descriptor_control(
            ctypes.byref(descriptor), _SE_DACL_PROTECTED, _SE_DACL_PROTECTED):
        raise ctypes.WinError(ctypes.get_last_error())
    attributes = _SECURITY_ATTRIBUTES(
        ctypes.sizeof(_SECURITY_ATTRIBUTES),
        ctypes.cast(ctypes.byref(descriptor), ctypes.c_void_p),
        False)

    ctypes.set_last_error(0)
    handle = api.create_file(
        _path_text(path), _GENERIC_WRITE | _DELETE, 0,
        ctypes.byref(attributes), _CREATE_NEW, _FILE_ATTRIBUTE_NORMAL, None)
    invalid_handle = ctypes.c_void_p(-1).value
    if handle == invalid_handle:
        raise ctypes.WinError(ctypes.get_last_error())

    def discard_created_file():
        disposition = _FILE_DISPOSITION_INFO(True)
        removed = bool(api.set_file_information(
            handle, _FILE_DISPOSITION_INFO_CLASS, ctypes.byref(disposition),
            ctypes.sizeof(disposition)))
        removal_error = ctypes.get_last_error() if not removed else None
        api.close_handle(handle)
        if not removed:
            raise OSError(
                removal_error,
                f'empty protected staging file retained for investigation: {path}')

    try:
        if _security(path, 'file') != protected:
            raise ValueError('new staging file security does not match the protected reference')
        if path.stat().st_size != 0:
            raise ValueError('new protected staging file is unexpectedly nonempty')
        if _security(reference, 'file') != reference_security:
            raise ValueError('reference file security changed during staging creation')
        descriptor_fd = msvcrt.open_osfhandle(handle, os.O_WRONLY | os.O_BINARY)
        handle = None
        return descriptor_fd
    except BaseException:
        if handle is not None:
            discard_created_file()
        raise


def replace_file(temporary: Path, target: Path):
    """Atomically replace an existing file without losing its DACL.

    ``ReplaceFileW`` is called with flags zero: ACL merge errors are never
    ignored.  The replacement is also pre-secured so its descriptor is no more
    permissive even before the replace operation completes.
    """
    temporary, target = Path(temporary), Path(target)
    if not _same_path(temporary.parent, target.parent):
        raise ValueError('replacement file must be staged in the target directory')
    if _kind(temporary) != 'file' or _kind(target) != 'file':
        raise ValueError('ReplaceFileW requires ordinary existing files')
    before = _security(target, 'file')
    _set_security(temporary, before)
    if _security(temporary, 'file') != before:
        raise ValueError('replacement file security metadata does not match the target')
    if _security(target, 'file') != before:
        raise ValueError('target file security changed immediately before replacement')
    ctypes.set_last_error(0)
    if not _api().replace_file(
            _path_text(target), _path_text(temporary), None, 0, None, None):
        error = ctypes.get_last_error()
        raise ctypes.WinError(error)
    if _security(target, 'file') != before:
        raise ValueError('ReplaceFileW completed without preserving the target DACL')


def prepare_directory_start(wrapper: Path, target: Path):
    """Secure an empty staging wrapper before ``copytree`` creates its package."""
    wrapper, target = Path(wrapper), Path(target)
    if _kind(wrapper) != 'directory':
        raise ValueError(f'expected an ordinary staging wrapper: {wrapper}')
    with os.scandir(wrapper) as entries:
        if next(entries, None) is not None:
            raise ValueError('directory staging wrapper must be empty before ACL preparation')
    target_kind = _kind(target)
    if target_kind not in (None, 'directory'):
        raise ValueError(f'directory target has incompatible kind: {target}')
    live = _tree_security(target) if target_kind == 'directory' else None

    # A first installation may not yet have its immediate target parent.  Model
    # each missing directory beneath the nearest existing ancestor so Windows
    # performs the real inheritance algorithm once per level, including
    # NO_PROPAGATE and creator mappings.  The package remains wrapper/package.
    missing = []
    anchor = target.parent
    while _kind(anchor) is None:
        missing.append(anchor)
        if anchor.parent == anchor:
            raise ValueError(f'no existing local ancestor for directory target: {target}')
        anchor = anchor.parent
    if _kind(anchor) != 'directory':
        raise ValueError(f'target ancestor is not an ordinary directory: {anchor}')
    missing.reverse()
    anchor_security = _security(anchor, 'directory')
    initial_wrapper = _security(wrapper, 'directory')
    if initial_wrapper.label != anchor_security.label:
        raise ValueError(
            'staging and target ancestors have different mandatory integrity labels')

    # Protection keeps the copied parent DACL from inheriting unrelated ACEs
    # from the off-discovery staging location.  Its inheritable ACEs still flow
    # to children created beneath the wrapper.
    wrapper_security = replace(_protected_copy(anchor_security), kind='directory')
    _set_security(wrapper, wrapper_security)
    secured_wrapper = _security(wrapper, 'directory')
    if (secured_wrapper.dacl != wrapper_security.dacl
            or secured_wrapper.protected != wrapper_security.protected):
        raise ValueError('staging wrapper did not accept the intended parent DACL exactly')

    emulator = wrapper
    chain = []
    for index, missing_path in enumerate(missing):
        emulator = emulator / f'.agent-team-parent-{index}'
        emulator.mkdir()
        inherited = _security(emulator, 'directory')
        chain.append((os.path.abspath(os.fspath(missing_path)), inherited))
    parent_security = chain[-1][1] if chain else anchor_security
    if chain:
        # Make package a direct child while retaining the DACL the actual final
        # parent will receive after mkdir creates the same number of levels.
        emulated_parent = replace(_protected_copy(parent_security), kind='directory')
        _set_security(wrapper, emulated_parent)
        secured_wrapper = _security(wrapper, 'directory')
        if (secured_wrapper.dacl != emulated_parent.dacl
                or secured_wrapper.protected != emulated_parent.protected):
            raise ValueError('staging wrapper did not accept the emulated parent DACL')
    return DirectorySecurityState(
        target=os.path.abspath(os.fspath(target)),
        wrapper=os.path.abspath(os.fspath(wrapper)),
        parent=parent_security,
        live=live,
        parent_anchor=os.path.abspath(os.fspath(anchor)),
        parent_anchor_security=anchor_security,
        parent_chain=tuple(chain))


def prepare_directory_finish(prepared: Path, target: Path, state: DirectorySecurityState):
    """Overlay existing path DACLs after ``copytree``, before live mutation."""
    prepared, target = Path(prepared), Path(target)
    if not _same_path(target, state.target) or not _same_path(prepared.parent, state.wrapper):
        raise ValueError('directory security state does not match the prepared publication')
    paths = _tree_paths(prepared)
    created_root = _security(prepared, 'directory')
    if state.live is None:
        if created_root.protected:
            raise ValueError('new directory root unexpectedly disabled parent inheritance')
        final_root = created_root
    else:
        final_root = state.live['']

    # Freeze the exact root DACL while it resides under the unrelated staging
    # path.  Descendants are then restored top-down so parent inheritance is in
    # place before each child descriptor is applied.
    protected_root = _protected_copy(final_root)
    _set_security(prepared, protected_root)
    if state.live is not None:
        matches = []
        for key in paths:
            if key:
                old_key = _matching_live_key(target, key, state.live)
                if old_key is not None:
                    matches.append((key, old_key))
        matches.sort(key=lambda item: (item[0].count(os.sep), item[0]))
        for key, old_key in matches:
            path, kind = paths[key]
            old = state.live[old_key]
            if old.kind != kind:
                raise ValueError(f'filesystem kind changed at managed relative path: {path}')
            _set_security(path, old)

    staged = _tree_security(prepared)
    staged_root = staged['']
    if staged_root != protected_root:
        raise ValueError('prepared directory root DACL is not safely frozen')
    if state.live is not None:
        for key, old_key in matches:
            if staged[key] != state.live[old_key]:
                raise ValueError(
                    'prepared directory did not preserve an existing child DACL exactly')
    final = dict(staged)
    final[''] = final_root
    return replace(
        state,
        prepared=os.path.abspath(os.fspath(prepared)),
        staged=staged,
        final=final)


def verify_directory(target: Path, state: DirectorySecurityState):
    """Recheck live, parent, and staged DACL evidence immediately before removal."""
    target = Path(target)
    if not _same_path(target, state.target) or state.prepared is None or state.staged is None:
        raise ValueError('directory security preparation is incomplete or for another target')
    if _security(Path(state.parent_anchor), 'directory') != state.parent_anchor_security:
        raise ValueError('target ancestor security changed after directory preparation')
    for parent_path, expected in state.parent_chain:
        if _security(Path(parent_path), 'directory') != expected:
            raise ValueError('created target parent has unexpected security metadata')
    if _security(target.parent, 'directory') != state.parent:
        raise ValueError('target parent security differs from prepared inheritance')
    target_kind = _kind(target)
    if state.live is None:
        if target_kind is not None:
            raise ValueError('absent directory target appeared after security preparation')
    else:
        if target_kind != 'directory':
            raise ValueError('directory target disappeared or changed kind after preparation')
        _assert_tree(state.live, _tree_security(target), 'live directory')
    _assert_tree(state.staged, _tree_security(Path(state.prepared)), 'prepared directory')


def finish_directory(path: Path, state: DirectorySecurityState):
    """Restore final-parent inheritance after rename and verify the complete tree."""
    path = Path(path)
    if (not _same_path(path, state.target) or state.staged is None
            or state.final is None):
        raise ValueError('directory security state is incomplete or for another target')
    if _security(path.parent, 'directory') != state.parent:
        raise ValueError('target parent DACL changed before inheritance restoration')
    _assert_tree(state.staged, _tree_security(path), 'renamed directory')
    final_root = state.final['']
    if not final_root.protected:
        _set_security(path, final_root)
    _assert_tree(state.final, _tree_security(path), 'published directory')
