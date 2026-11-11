
import ctypes
import errno
import json
import os
import platform
import sys
import urllib.request


def _lib_name():
    system = platform.system()
    if system == "Windows":
        return "sentry_core.dll"
    if system == "Darwin":
        return "libsentry_core.dylib"
    return "libsentry_core.so"


CORE_HOST_MAX = 256


class CoreInfo(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_int64),
        ("cpus", ctypes.c_int32),
        ("page_size", ctypes.c_int32),
        ("host", ctypes.c_char * CORE_HOST_MAX),
    ]


_lib = ctypes.CDLL(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "core",
        _lib_name()
    )
)

_lib.core_get_info.argtypes = [ctypes.POINTER(CoreInfo)]
_lib.core_get_info.restype = ctypes.c_int


def error_text(err):
    if sys.platform == "win32":
        return ctypes.FormatError(err).strip()
    return os.strerror(err)


def get_info():
    info = CoreInfo()

    err = _lib.core_get_info(ctypes.byref(info))

    if err != 0:
        raise OSError(err, "core_get_info failed")

    return {
        "pid": info.pid,
        "cpus": info.cpus,
        "page_size": info.page_size,
        "host": info.host.decode("utf-8"),
    }


# ---- Глава 2.1: список процессов ----

class CoreProc(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_int64),
        ("ppid", ctypes.c_int64),
        ("name", ctypes.c_char * 64),
    ]


_lib.core_list_procs.argtypes = [
    ctypes.POINTER(CoreProc),
    ctypes.c_int32,
    ctypes.POINTER(ctypes.c_int32)
]

_lib.core_list_procs.restype = ctypes.c_int

TOO_SMALL = 122 if sys.platform == "win32" else errno.ERANGE


def list_procs(room=256):
    while True:
        buf = (CoreProc * room)()
        count = ctypes.c_int32()

        err = _lib.core_list_procs(
            buf,
            room,
            ctypes.byref(count)
        )

        if err == 0:
            return [
                {
                    "pid": p.pid,
                    "ppid": p.ppid,
                    "name": p.name.decode("utf-8", "replace")
                }
                for p in buf[:count.value]
            ]

        if err != TOO_SMALL:
            raise OSError(err, error_text(err))

        room = count.value + 64


def parents(procs, pid):
    by_pid = {p["pid"]: p for p in procs}
    chain = []

    while pid in by_pid and len(chain) < 64:
        p = by_pid[pid]
        chain.append(p)

        if p["ppid"] == pid:
            break

        pid = p["ppid"]

    return chain


# ---- Глава 2.2: запуск процесса ----

class CoreChild(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_int64),
        ("handle", ctypes.c_int64),
    ]


_lib.core_spawn.argtypes = [
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(CoreChild),
]

_lib.core_spawn.restype = ctypes.c_int


_lib.core_wait.argtypes = [
    ctypes.POINTER(CoreChild),
    ctypes.c_int32,
    ctypes.POINTER(ctypes.c_int32),
]

_lib.core_wait.restype = ctypes.c_int


def spawn(args):
    if not args:
        raise ValueError("Не указана программа для запуска")

    encoded = [
        str(arg).encode("utf-8")
        for arg in args
    ]

    argv = (ctypes.c_char_p * (len(encoded) + 1))()

    for i, arg in enumerate(encoded):
        argv[i] = arg

    argv[len(encoded)] = None

    child = CoreChild()

    err = _lib.core_spawn(
        argv,
        ctypes.byref(child)
    )

    if err != 0:
        raise OSError(err, error_text(err))

    return child


def wait(child, timeout_ms=-1):
    code = ctypes.c_int32()

    err = _lib.core_wait(
        ctypes.byref(child),
        timeout_ms,
        ctypes.byref(code)
    )

    if err == 258 and sys.platform == "win32":
        raise TimeoutError("Процесс ещё выполняется")

    if err != 0:
        raise OSError(err, error_text(err))

    return code.value


# ---- Отправка данных ----

def send(message, url):
    data = json.dumps(
        message,
        ensure_ascii=False
    ).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.status, resp.read().decode("utf-8")


# ---- Запуск агента ----

if __name__ == "__main__":
    info = get_info()

    procs = list_procs()

    chain = parents(procs, os.getpid())

    message = {
        "type": "agent_started",
        "pid": info["pid"],
        "cpus": info["cpus"],
        "page_size": info["page_size"],
        "host": info["host"],
        "procs": len(procs),
        "parents": [p["name"] for p in chain],
    }

    print(
        json.dumps(
            message,
            ensure_ascii=False,
            indent=2
        )
    )

    if len(sys.argv) > 1:
        status, body = send(message, sys.argv[1])
        print(f"status={status} body={body}")
