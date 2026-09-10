"""Narrow Windows Task Scheduler publication for cleanup-task-artifacts."""

import ctypes
from ctypes import wintypes
from datetime import datetime
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET

from reconcile import command_path, plain_path


_TASK_PREFIX = r"\AgentTeamCleanup-"
_TASK_NAMESPACE = "http://schemas.microsoft.com/windows/2004/02/mit/task"
_DESCRIPTION = "Agent Team cleanup-task-artifacts"
_ERROR_FILE_NOT_FOUND = 0x80070002
_ACTION_FIELDS = frozenset(("command", "arguments", "working_directory"))


def _home(home):
    value = plain_path(home)
    if not value.is_dir():
        raise ValueError(f"Codex home is unavailable: {value}")
    return value


def task_name(home):
    """Return the one Task Scheduler name owned for this canonical Codex home."""
    value = _home(home)
    suffix = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return _TASK_PREFIX + suffix


def identity(home):
    return "task-scheduler:" + task_name(home)


def _current_user_sid():
    if os.name != "nt":
        raise ValueError("Windows Task Scheduler is available only on native Windows")
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    open_process_token = advapi32.OpenProcessToken
    open_process_token.argtypes = (wintypes.HANDLE, wintypes.DWORD,
                                   ctypes.POINTER(wintypes.HANDLE))
    open_process_token.restype = wintypes.BOOL
    get_token_information = advapi32.GetTokenInformation
    get_token_information.argtypes = (wintypes.HANDLE, ctypes.c_int,
                                      wintypes.LPVOID, wintypes.DWORD,
                                      ctypes.POINTER(wintypes.DWORD))
    get_token_information.restype = wintypes.BOOL
    convert_sid = advapi32.ConvertSidToStringSidW
    convert_sid.argtypes = (wintypes.LPVOID, ctypes.POINTER(wintypes.LPWSTR))
    convert_sid.restype = wintypes.BOOL
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (wintypes.HANDLE,)
    close_handle.restype = wintypes.BOOL
    local_free = kernel32.LocalFree
    local_free.argtypes = (wintypes.HLOCAL,)
    local_free.restype = wintypes.HLOCAL
    get_current_process = kernel32.GetCurrentProcess
    get_current_process.argtypes = ()
    get_current_process.restype = wintypes.HANDLE

    token = wintypes.HANDLE()
    if not open_process_token(get_current_process(), 0x0008,
                              ctypes.byref(token)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        size = wintypes.DWORD()
        get_token_information(token, 1, None, 0, ctypes.byref(size))
        if ctypes.get_last_error() != 122 or not size.value:
            raise ctypes.WinError(ctypes.get_last_error())
        buffer = ctypes.create_string_buffer(size.value)
        if not get_token_information(token, 1, buffer, size.value,
                                     ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        sid_pointer = ctypes.cast(buffer, ctypes.POINTER(wintypes.LPVOID))[0]
        text = wintypes.LPWSTR()
        if not convert_sid(sid_pointer, ctypes.byref(text)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return text.value
        finally:
            local_free(text)
    finally:
        close_handle(token)


def _decode(raw):
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("mbcs")


def _run(arguments, *, allow_absent=False):
    try:
        result = subprocess.run(
            [str(command_path("schtasks.exe")), *arguments, "/HRESULT"],
            capture_output=True, timeout=30)
    except subprocess.TimeoutExpired as error:
        raise ValueError("Task Scheduler command timed out; inspect exact task state") from error
    code = result.returncode & 0xFFFFFFFF
    if allow_absent and code == _ERROR_FILE_NOT_FOUND:
        return None
    if result.returncode:
        operation = arguments[0].removeprefix("/").lower()
        raise ValueError(f"Task Scheduler {operation} failed with HRESULT 0x{code:08x}")
    return _decode(result.stdout)


def _query_xml(name):
    return _run(["/Query", "/TN", name, "/XML", "ONE"], allow_absent=True)


def _tag(element):
    prefix = "{" + _TASK_NAMESPACE + "}"
    if not element.tag.startswith(prefix):
        raise ValueError("Task Scheduler XML has an unknown namespace")
    return element.tag[len(prefix):]


def _children(element, allowed):
    result = {}
    for child in element:
        name = _tag(child)
        if name not in allowed or name in result:
            raise ValueError(f"Task Scheduler XML has unsupported {name} topology")
        result[name] = child
    return result


def _required(children, name):
    if name not in children or children[name].text is None:
        raise ValueError(f"Task Scheduler XML lacks {name}")
    return children[name].text


def _boolean(children, name):
    value = _required(children, name).strip().lower()
    if value not in ("true", "false"):
        raise ValueError(f"Task Scheduler XML has invalid {name}")
    return value == "true"


def _action(action):
    if set(action) != _ACTION_FIELDS or not all(isinstance(action[key], str) and action[key]
                                                for key in _ACTION_FIELDS):
        raise ValueError("Task Scheduler action must contain exact nonempty string fields")
    if any("\0" in action[key] for key in _ACTION_FIELDS):
        raise ValueError("Task Scheduler action contains a NUL")
    return {key: action[key] for key in sorted(_ACTION_FIELDS)}


def _text_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _action_hashes(action):
    action = _action(action)
    return {f"{key}_sha256": _text_hash(value) for key, value in action.items()}


def _validate_time(hour, minute):
    if not isinstance(hour, int) or isinstance(hour, bool) or not 0 <= hour <= 23:
        raise ValueError("invalid Task Scheduler hour")
    if not isinstance(minute, int) or isinstance(minute, bool) or not 0 <= minute <= 59:
        raise ValueError("invalid Task Scheduler minute")


def _expected(action, hour, minute, start_boundary):
    _validate_time(hour, minute)
    return {
        "kind": "task-scheduler",
        "schedule": "daily",
        "hour": hour,
        "minute": minute,
        "second": 0,
        "start_boundary": start_boundary,
        "start_boundary_zone": "local",
        "trigger_enabled": True,
        "principal": "current-user",
        "logon_type": "InteractiveToken",
        "run_level": "LeastPrivilege",
        "multiple_instances": "IgnoreNew",
        "disallow_start_on_batteries": False,
        "stop_if_going_on_batteries": False,
        "allow_hard_terminate": True,
        "start_when_available": True,
        "run_only_if_network_available": False,
        "allow_start_on_demand": True,
        "enabled": True,
        "hidden": False,
        "run_only_if_idle": False,
        "wake_to_run": False,
        "execution_time_limit": "PT2H",
        "priority": 7,
        "idle_stop_on_end": False,
        "idle_restart": False,
        "registration_description": True,
        "registration_uri": True,
        "action_context": True,
        **_action_hashes(action),
    }


def _parse(name, raw):
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        raise ValueError("Task Scheduler returned malformed XML") from error
    if _tag(root) != "Task" or root.attrib.get("version") not in {
            "1.2", "1.3", "1.4", "1.5", "1.6"} or len(root.attrib) != 1:
        raise ValueError("Task Scheduler XML has an unsupported root schema")
    top = _children(root, {"RegistrationInfo", "Triggers", "Principals",
                           "Settings", "Actions"})
    if set(top) != {"RegistrationInfo", "Triggers", "Principals", "Settings", "Actions"}:
        raise ValueError("Task Scheduler XML lacks required owned sections")

    registration = _children(top["RegistrationInfo"], {
        "Author", "Date", "Description", "Documentation", "Source", "URI", "Version"})
    description = registration.get("Description")
    uri = registration.get("URI")

    trigger_nodes = list(top["Triggers"])
    if len(trigger_nodes) != 1 or _tag(trigger_nodes[0]) != "CalendarTrigger":
        raise ValueError("Task Scheduler task must have exactly one daily trigger")
    trigger = _children(trigger_nodes[0], {"StartBoundary", "Enabled", "ScheduleByDay"})
    if set(trigger) != {"StartBoundary", "Enabled", "ScheduleByDay"}:
        raise ValueError("Task Scheduler daily trigger has unsupported topology")
    schedule = _children(trigger["ScheduleByDay"], {"DaysInterval"})
    if set(schedule) != {"DaysInterval"}:
        raise ValueError("Task Scheduler daily schedule has unsupported topology")
    try:
        start = datetime.fromisoformat(_required(trigger, "StartBoundary"))
        days = int(_required(schedule, "DaysInterval"))
    except ValueError as error:
        raise ValueError("Task Scheduler daily trigger is malformed") from error

    principal_nodes = list(top["Principals"])
    if len(principal_nodes) != 1 or _tag(principal_nodes[0]) != "Principal":
        raise ValueError("Task Scheduler task must have exactly one principal")
    principal_node = principal_nodes[0]
    if principal_node.attrib != {"id": "Author"}:
        raise ValueError("Task Scheduler principal identity is unsupported")
    principal = _children(principal_node, {"UserId", "LogonType", "RunLevel"})
    if set(principal) != {"UserId", "LogonType", "RunLevel"}:
        raise ValueError("Task Scheduler principal has unsupported topology")

    settings = _children(top["Settings"], {
        "MultipleInstancesPolicy", "DisallowStartIfOnBatteries",
        "StopIfGoingOnBatteries", "AllowHardTerminate", "StartWhenAvailable",
        "RunOnlyIfNetworkAvailable", "IdleSettings", "AllowStartOnDemand",
        "Enabled", "Hidden", "RunOnlyIfIdle", "WakeToRun",
        "ExecutionTimeLimit", "Priority"})
    expected_settings = {
        "MultipleInstancesPolicy", "DisallowStartIfOnBatteries",
        "StopIfGoingOnBatteries", "AllowHardTerminate", "StartWhenAvailable",
        "RunOnlyIfNetworkAvailable", "IdleSettings", "AllowStartOnDemand",
        "Enabled", "Hidden", "RunOnlyIfIdle", "WakeToRun",
        "ExecutionTimeLimit", "Priority"}
    if set(settings) != expected_settings:
        raise ValueError("Task Scheduler settings have unsupported topology")
    idle = _children(settings["IdleSettings"], {"StopOnIdleEnd", "RestartOnIdle"})
    if set(idle) != {"StopOnIdleEnd", "RestartOnIdle"}:
        raise ValueError("Task Scheduler idle settings have unsupported topology")

    actions_node = top["Actions"]
    if actions_node.attrib != {"Context": "Author"}:
        raise ValueError("Task Scheduler action context is unsupported")
    actions = list(actions_node)
    if len(actions) != 1 or _tag(actions[0]) != "Exec":
        raise ValueError("Task Scheduler task must have exactly one Exec action")
    action_nodes = _children(actions[0], {"Command", "Arguments", "WorkingDirectory"})
    if set(action_nodes) != {"Command", "Arguments", "WorkingDirectory"}:
        raise ValueError("Task Scheduler Exec action has unsupported topology")
    actual_action = {
        "command": _required(action_nodes, "Command"),
        "arguments": _required(action_nodes, "Arguments"),
        "working_directory": _required(action_nodes, "WorkingDirectory"),
    }
    user_id = _required(principal, "UserId")
    return {
        "kind": "task-scheduler",
        "schedule": "daily" if days == 1 else f"every-{days}-days",
        "hour": start.hour,
        "minute": start.minute,
        "second": start.second,
        "start_boundary": start.isoformat(),
        "start_boundary_zone": "local" if start.tzinfo is None else "fixed-offset",
        "trigger_enabled": _boolean(trigger, "Enabled"),
        "principal": "current-user" if user_id == _current_user_sid() else "other-user",
        "logon_type": _required(principal, "LogonType"),
        "run_level": _required(principal, "RunLevel"),
        "multiple_instances": _required(settings, "MultipleInstancesPolicy"),
        "disallow_start_on_batteries": _boolean(settings, "DisallowStartIfOnBatteries"),
        "stop_if_going_on_batteries": _boolean(settings, "StopIfGoingOnBatteries"),
        "allow_hard_terminate": _boolean(settings, "AllowHardTerminate"),
        "start_when_available": _boolean(settings, "StartWhenAvailable"),
        "run_only_if_network_available": _boolean(settings, "RunOnlyIfNetworkAvailable"),
        "allow_start_on_demand": _boolean(settings, "AllowStartOnDemand"),
        "enabled": _boolean(settings, "Enabled"),
        "hidden": _boolean(settings, "Hidden"),
        "run_only_if_idle": _boolean(settings, "RunOnlyIfIdle"),
        "wake_to_run": _boolean(settings, "WakeToRun"),
        "execution_time_limit": _required(settings, "ExecutionTimeLimit"),
        "priority": int(_required(settings, "Priority")),
        "idle_stop_on_end": _boolean(idle, "StopOnIdleEnd"),
        "idle_restart": _boolean(idle, "RestartOnIdle"),
        "registration_description": description is not None and description.text == _DESCRIPTION,
        "registration_uri": uri is not None and uri.text == name,
        "action_context": True,
        **_action_hashes(actual_action),
    }


def observe(home):
    name = task_name(home)
    raw = _query_xml(name)
    return None if raw is None else _parse(name, raw)


def _element(parent, name, text=None, **attributes):
    child = ET.SubElement(parent, "{" + _TASK_NAMESPACE + "}" + name, attributes)
    if text is not None:
        child.text = str(text)
    return child


def _document(home, action, start_boundary):
    name = task_name(home)
    action = _action(action)
    ET.register_namespace("", _TASK_NAMESPACE)
    root = ET.Element("{" + _TASK_NAMESPACE + "}Task", {"version": "1.4"})
    registration = _element(root, "RegistrationInfo")
    _element(registration, "Description", _DESCRIPTION)
    _element(registration, "URI", name)
    triggers = _element(root, "Triggers")
    trigger = _element(triggers, "CalendarTrigger")
    _element(trigger, "StartBoundary", start_boundary)
    _element(trigger, "Enabled", "true")
    schedule = _element(trigger, "ScheduleByDay")
    _element(schedule, "DaysInterval", "1")
    principals = _element(root, "Principals")
    principal = _element(principals, "Principal", id="Author")
    _element(principal, "UserId", _current_user_sid())
    _element(principal, "LogonType", "InteractiveToken")
    _element(principal, "RunLevel", "LeastPrivilege")
    settings = _element(root, "Settings")
    for key, value in (
            ("MultipleInstancesPolicy", "IgnoreNew"),
            ("DisallowStartIfOnBatteries", "false"),
            ("StopIfGoingOnBatteries", "false"),
            ("AllowHardTerminate", "true"),
            ("StartWhenAvailable", "true"),
            ("RunOnlyIfNetworkAvailable", "false")):
        _element(settings, key, value)
    idle = _element(settings, "IdleSettings")
    _element(idle, "StopOnIdleEnd", "false")
    _element(idle, "RestartOnIdle", "false")
    for key, value in (
            ("AllowStartOnDemand", "true"),
            ("Enabled", "true"),
            ("Hidden", "false"),
            ("RunOnlyIfIdle", "false"),
            ("WakeToRun", "false"),
            ("ExecutionTimeLimit", "PT2H"),
            ("Priority", "7")):
        _element(settings, key, value)
    actions = _element(root, "Actions", Context="Author")
    execute = _element(actions, "Exec")
    _element(execute, "Command", action["command"])
    _element(execute, "Arguments", action["arguments"])
    _element(execute, "WorkingDirectory", action["working_directory"])
    return ET.tostring(root, encoding="utf-16", xml_declaration=True)


def install(home, expected_action, hour, minute, expected_current):
    """Create/update the exact owned task and return its verified observation."""
    home = _home(home)
    expected_action = _action(expected_action)
    _validate_time(hour, minute)
    today = datetime.now().astimezone().date()
    start_boundary = f"{today.isoformat()}T{hour:02d}:{minute:02d}:00"
    desired = _expected(expected_action, hour, minute, start_boundary)
    if observe(home) != expected_current:
        raise ValueError("Task Scheduler state changed immediately before publication")
    name = task_name(home)
    document = _document(home, expected_action, start_boundary)
    temporary_directory = plain_path(tempfile.gettempdir())
    if not temporary_directory.is_dir():
        raise ValueError("native temporary directory is unavailable")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix="agent-team-task-", suffix=".xml",
                                         dir=temporary_directory, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(document)
        arguments = ["/Create", "/TN", name, "/XML", str(temporary)]
        if expected_current is not None:
            arguments.append("/F")
        _run(arguments)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    actual = observe(home)
    if actual != desired:
        raise ValueError("Task Scheduler readback differs after publication")
    return actual


class _GUID(ctypes.Structure):
    _fields_ = (("data1", wintypes.DWORD), ("data2", wintypes.WORD),
                ("data3", wintypes.WORD), ("data4", ctypes.c_ubyte * 8))


class _BRECORD(ctypes.Structure):
    _fields_ = (("record", wintypes.LPVOID), ("record_info", wintypes.LPVOID))


class _VARIANT_VALUE(ctypes.Union):
    _fields_ = (("long", wintypes.LONG), ("pointer", wintypes.LPVOID),
                ("long_long", ctypes.c_longlong), ("brecord", _BRECORD))


class _VARIANT(ctypes.Structure):
    _anonymous_ = ("value",)
    _fields_ = (("vt", wintypes.USHORT), ("reserved1", wintypes.USHORT),
                ("reserved2", wintypes.USHORT), ("reserved3", wintypes.USHORT),
                ("value", _VARIANT_VALUE))


def _guid(value):
    return _GUID.from_buffer_copy(uuid.UUID(value).bytes_le)


def _method(interface, index, result, *arguments):
    table = ctypes.cast(interface,
                        ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return ctypes.WINFUNCTYPE(result, ctypes.c_void_p, *arguments)(table[index])


def _check_hresult(result, operation):
    code = result & 0xFFFFFFFF
    if code & 0x80000000:
        raise ValueError(f"Task Scheduler {operation} failed with HRESULT 0x{code:08x}")


def _release(interface):
    if interface:
        _method(interface, 2, wintypes.ULONG)(interface)


def _state_and_instances(name):
    """Read numeric state and current-user running instances through narrow COM calls."""
    ole32 = ctypes.WinDLL("ole32", use_last_error=True)
    oleaut32 = ctypes.WinDLL("oleaut32", use_last_error=True)
    co_initialize = ole32.CoInitializeEx
    co_initialize.argtypes = (wintypes.LPVOID, wintypes.DWORD)
    co_initialize.restype = wintypes.LONG
    co_uninitialize = ole32.CoUninitialize
    co_uninitialize.argtypes = ()
    co_uninitialize.restype = None
    co_create = ole32.CoCreateInstance
    co_create.argtypes = (ctypes.POINTER(_GUID), wintypes.LPVOID, wintypes.DWORD,
                          ctypes.POINTER(_GUID), ctypes.POINTER(ctypes.c_void_p))
    co_create.restype = wintypes.LONG
    allocate_bstr = oleaut32.SysAllocString
    allocate_bstr.argtypes = (wintypes.LPCWSTR,)
    allocate_bstr.restype = ctypes.c_void_p
    free_bstr = oleaut32.SysFreeString
    free_bstr.argtypes = (ctypes.c_void_p,)
    free_bstr.restype = None

    initialized = co_initialize(None, 0)
    _check_hresult(initialized, "COM initialization")
    service = ctypes.c_void_p()
    folder = ctypes.c_void_p()
    task = ctypes.c_void_p()
    instances = ctypes.c_void_p()
    root = task_path = None
    try:
        class_id = _guid("0f87369f-a4e5-4cfc-bd3e-73e6154572dd")
        interface_id = _guid("2faba4c7-4da9-4013-9697-20cc3fd40f85")
        _check_hresult(co_create(ctypes.byref(class_id), None, 1,
                                 ctypes.byref(interface_id), ctypes.byref(service)),
                       "COM activation")
        empty = _VARIANT()
        connect = _method(service, 10, wintypes.LONG,
                          _VARIANT, _VARIANT, _VARIANT, _VARIANT)
        _check_hresult(connect(service, empty, empty, empty, empty), "connection")
        root = allocate_bstr("\\")
        if not root:
            raise MemoryError("cannot allocate Task Scheduler root path")
        get_folder = _method(service, 7, wintypes.LONG, ctypes.c_void_p,
                             ctypes.POINTER(ctypes.c_void_p))
        _check_hresult(get_folder(service, root, ctypes.byref(folder)), "root lookup")
        task_path = allocate_bstr(name)
        if not task_path:
            raise MemoryError("cannot allocate Task Scheduler task path")
        get_task = _method(folder, 13, wintypes.LONG, ctypes.c_void_p,
                           ctypes.POINTER(ctypes.c_void_p))
        _check_hresult(get_task(folder, task_path, ctypes.byref(task)), "task lookup")
        state = wintypes.LONG()
        get_state = _method(task, 9, wintypes.LONG, ctypes.POINTER(wintypes.LONG))
        _check_hresult(get_state(task, ctypes.byref(state)), "state query")
        get_instances = _method(task, 14, wintypes.LONG, wintypes.LONG,
                                ctypes.POINTER(ctypes.c_void_p))
        _check_hresult(get_instances(task, 0, ctypes.byref(instances)),
                       "running-instance query")
        count = wintypes.LONG()
        get_count = _method(instances, 7, wintypes.LONG,
                            ctypes.POINTER(wintypes.LONG))
        _check_hresult(get_count(instances, ctypes.byref(count)),
                       "running-instance count")
        if count.value < 0:
            raise ValueError("Task Scheduler returned an invalid instance count")
        return state.value, count.value
    finally:
        if task_path:
            free_bstr(task_path)
        if root:
            free_bstr(root)
        for interface in (instances, task, folder, service):
            _release(interface)
        co_uninitialize()


def retire(home, expected_current):
    """Disable and delete a receipt-proven task only while no instance is active."""
    home = _home(home)
    if expected_current is None or observe(home) != expected_current:
        raise ValueError("Task Scheduler state changed immediately before retirement")
    if (expected_current.get("principal") != "current-user"
            or expected_current.get("logon_type") != "InteractiveToken"
            or expected_current.get("run_level") != "LeastPrivilege"):
        raise ValueError("Task Scheduler task has an unsupported retirement security context")
    name = task_name(home)
    state, instances = _state_and_instances(name)
    if state not in (1, 3) or instances:
        raise ValueError(
            "Task Scheduler retirement requires a disabled or ready task with no instances")
    _run(["/Change", "/TN", name, "/Disable"])
    state, instances = _state_and_instances(name)
    if state != 1 or instances:
        raise ValueError(
            "Task Scheduler task is not disabled and instance-free; retirement stopped")
    _run(["/Delete", "/TN", name, "/F"])
    if _query_xml(name) is not None:
        raise ValueError("Task Scheduler task remains after retirement")
