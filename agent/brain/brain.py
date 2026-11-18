import ctypes
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


_lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "..", "core", _lib_name()))
_lib.core_get_info.argtypes = [ctypes.POINTER(CoreInfo)]
_lib.core_get_info.restype = ctypes.c_int


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


def send(message, url):
    data = json.dumps(message, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.status, resp.read().decode("utf-8")


if __name__ == "__main__":
    info = get_info()
    message = {
        "type": "agent_started",
        "pid": info["pid"],
        "cpus": info["cpus"],
        "page_size": info["page_size"],
        "host": info["host"],
    }
    print(json.dumps(message, ensure_ascii=False))

    if len(sys.argv) > 1:
        status, body = send(message, sys.argv[1])
        print(f"status={status} body={body}")
