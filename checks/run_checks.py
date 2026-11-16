"""Проверки репозитория по дисциплине «Системное программирование».

Запускается в GitHub Actions на трёх системах (Windows, macOS, Linux) после каждой
отправки кода и локально командой: python checks/run_checks.py

Что проверяется:
1. Лабораторные работы, у которых есть код: программа собирается и печатает
   ожидаемую строку. Код для другой системы пропускается (hello.c с windows.h
   собирается только в Windows, с unistd.h — только в macOS и Linux).
   Снимки экрана лабораторных: заглушки в screenshots/ заменены своими снимками.
2. Проверки агента-сторожа. Каждая открывается на своей паре; до этого она
   отмечена как «ещё не открыта» и на результат не влияет.

Файл ведёт преподаватель: при обновлении материалов он заменяется новой версией.
"""
import os
import platform
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM = {"Windows": "win", "Darwin": "mac", "Linux": "linux"}[platform.system()]
SYSTEM_NAME = {"win": "Windows", "mac": "macOS", "linux": "Linux"}[SYSTEM]

# Проверки агента: номер, пара, на которой открывается, название.
AGENT_CHECKS = [
    (1, 4, "Список процессов совпадает с системным"),
    (2, 6, "Процесс загружает процессор больше 80%"),
    (3, 8, "Память процесса растёт без остановки"),
    (4, 10, "Изменён файл hosts"),
    (5, 11, "Новый файл в папке автозагрузки пользователя"),
    (6, 12, "Новая запись в системной автозагрузке"),
    (7, 13, "Пять неудачных входов подряд"),
    (8, 14, "Открыт новый порт"),
    (9, 15, "Модель ИИ занимает больше заданной памяти"),
    (10, 18, "В отправленных данных нет имени пользователя"),
    (11, 20, "Ядро работает в фоне и отвечает"),
    (12, 21, "Подключено новое устройство"),
    (13, 22, "Запущена программа без подписи или не из пакета"),
]
OPENED = 2  # сколько проверок агента уже открыто; растёт с каждой парой

PID_LINE = re.compile(r"agent v0(?: \(python\))?, pid= ?\d+")


def target_of_c(text):
    return "win" if "windows.h" in text else "posix"


def target_of_py(text):
    return "win" if "windll" in text else "posix"


def fits(target):
    return target == "win" if SYSTEM == "win" else target == "posix"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60, **kw)


def build_c(src, out_dir):
    exe = Path(out_dir) / ("hello.exe" if SYSTEM == "win" else "hello")
    if SYSTEM == "win":
        r = run(["cl", "/nologo", str(src), f"/Fe:{exe}", f"/Fo:{out_dir}\\"])
    else:
        cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
        r = run([cc, "-o", str(exe), str(src)])
    return exe, r


def check_lab01():
    rows = []
    lab = ROOT / "labs" / "01-process-inside"
    c, py = lab / "hello.c", lab / "hello.py"
    if not c.exists() and not py.exists():
        return [("ЛР 1", "hello.c, hello.py", "не сдано", "")], True
    ok = True
    if c.exists():
        text = c.read_text(encoding="utf-8", errors="replace")
        if not fits(target_of_c(text)):
            rows.append(("ЛР 1", "hello.c", "пропущено", f"код для другой системы, {SYSTEM_NAME} его не собирает"))
        else:
            with tempfile.TemporaryDirectory() as d:
                exe, r = build_c(c, d)
                if r.returncode != 0:
                    ok = False
                    rows.append(("ЛР 1", "hello.c", "ошибка", "не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150]))
                else:
                    out = run([str(exe)], input="\n").stdout
                    if PID_LINE.search(out):
                        rows.append(("ЛР 1", "hello.c", "пройдено", PID_LINE.search(out).group(0)))
                    else:
                        ok = False
                        rows.append(("ЛР 1", "hello.c", "ошибка", "нет строки «agent v0, pid=…» в выводе"))
    if py.exists():
        text = py.read_text(encoding="utf-8", errors="replace")
        if not fits(target_of_py(text)):
            rows.append(("ЛР 1", "hello.py", "пропущено", f"код для другой системы, в {SYSTEM_NAME} не запускается"))
        else:
            r = run([sys.executable, str(py)], input="\n")
            m = PID_LINE.search(r.stdout)
            if r.returncode == 0 and m:
                rows.append(("ЛР 1", "hello.py", "пройдено", m.group(0)))
            else:
                ok = False
                tail = (r.stderr.strip().splitlines() or ["нет строки «agent v0 (python), pid=…» в выводе"])[-1]
                rows.append(("ЛР 1", "hello.py", "ошибка", tail[:150]))
    return rows, ok


LAB02_LINE = "agent: total=6 area=12"


def check_lab02():
    """ЛР 2: debug.c собирается с отладочными сведениями и печатает ту же строку, что на кадрах."""
    src = ROOT / "labs" / "02-debugger" / "debug.c"
    if not src.exists():
        return [("ЛР 2", "debug.c", "не сдано", "")], True
    with tempfile.TemporaryDirectory() as d:
        exe = Path(d) / ("debug.exe" if SYSTEM == "win" else "debug")
        if SYSTEM == "win":
            r = run(["cl", "/nologo", "/Zi", "/Od", str(src), f"/Fe:{exe}", f"/Fo:{d}\\", f"/Fd:{d}\\"])
        else:
            cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
            r = run([cc, "-g", "-O0", "-o", str(exe), str(src)])
        if r.returncode != 0:
            return [("ЛР 2", "debug.c", "ошибка", "не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150])], False
        out = run([str(exe)]).stdout
    if LAB02_LINE in out:
        return [("ЛР 2", "debug.c", "пройдено", LAB02_LINE)], True
    return [("ЛР 2", "debug.c", "ошибка", f"нет строки «{LAB02_LINE}» в выводе")], False


LAB03_LINE = "sqrt(2) = 1.414214"


def check_lab03():
    """ЛР 3: libs.c собирается (в Linux — с -lm) и печатает корень из 2."""
    src = ROOT / "labs" / "03-libraries" / "libs.c"
    if not src.exists():
        return [("ЛР 3", "libs.c", "не сдано", "")], True
    with tempfile.TemporaryDirectory() as d:
        exe = Path(d) / ("libs.exe" if SYSTEM == "win" else "libs")
        if SYSTEM == "win":
            r = run(["cl", "/nologo", str(src), f"/Fe:{exe}", f"/Fo:{d}\\"])
        else:
            cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
            r = run([cc, "-o", str(exe), str(src), "-lm"])
        if r.returncode != 0:
            return [("ЛР 3", "libs.c", "ошибка", "не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150])], False
        out = run([str(exe)]).stdout
    if LAB03_LINE in out:
        return [("ЛР 3", "libs.c", "пройдено", LAB03_LINE)], True
    return [("ЛР 3", "libs.c", "ошибка", f"нет строки «{LAB03_LINE}» в выводе")], False


LABS = ("01-process-inside", "02-debugger", "03-libraries", "04-process-tree", "05-process-birth", "06-cpu-load", "07-python-threads", "08-memory-map", "09-crash")
PLACEHOLDER = b"sysprog-placeholder"  # метка в заглушках шаблона, у снимка её нет
IMAGE_START = (b"\x89PNG", b"\xff\xd8\xff")


def check_screenshots():
    """Снимки лабораторных: каждый файл screenshots/*.png — картинка, и не заглушка из шаблона."""
    rows, ok = [], True
    for n, lab in enumerate(LABS, 1):
        files = sorted((ROOT / "labs" / lab / "screenshots").glob("*.png"))
        if not files:
            continue
        data = {f.name: f.read_bytes() for f in files}
        broken = [name for name, b in data.items() if not b.startswith(IMAGE_START)]
        left = [name[:2] for name, b in data.items() if PLACEHOLDER in b]
        if broken:
            ok = False
            rows.append((f"ЛР {n}", "screenshots/", "ошибка", "файл не картинка: " + ", ".join(broken)))
        elif len(left) == len(files):
            rows.append((f"ЛР {n}", "screenshots/", "не сдано", f"снимков 0 из {len(files)}"))
        elif left:
            rows.append((f"ЛР {n}", "screenshots/", "не сдано", f"снимков {len(files) - len(left)} из {len(files)}, остались заглушки " + ", ".join(left)))
        else:
            rows.append((f"ЛР {n}", "screenshots/", "пройдено", f"снимков {len(files)} из {len(files)}"))
    return rows, ok


def system_uptime():
    """Секунды с запуска системы — тем способом, которым их не считает агент студента."""
    if SYSTEM == "win":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.GetTickCount64.restype = ctypes.c_uint64
        return k32.GetTickCount64() // 1000
    if SYSTEM == "mac":
        import time
        boot = int(re.search(r"sec = (\d+)", run(["sysctl", "-n", "kern.boottime"]).stdout).group(1))
        return int(time.time()) - boot
    return int(float(Path("/proc/uptime").read_text().split()[0]))


CORE = ROOT / "agent" / "core"
LIB_NAME = {"win": "sentry_core.dll", "mac": "libsentry_core.dylib", "linux": "libsentry_core.so"}[SYSTEM]


def target_of_core(text):
    """Для какой системы файл ядра: core_info.c общий для macOS и Linux, core_procs.c у каждой свой."""
    if "windows.h" in text:
        return "win"
    if "libproc.h" in text:
        return "mac"
    if "/proc" in text:
        return "linux"
    return "posix"


def fits_core(target):
    return target == SYSTEM or (target == "posix" and SYSTEM != "win")


_core = {}


def build_core():
    """Собирает библиотеку ядра из всех agent/core/*.c без main — так же, как в главах.

    Возвращает (функции ядра в исходниках, ошибка): ошибка — None, если библиотека собрана,
    иначе строка таблицы. Собирается один раз за запуск.
    """
    if "result" in _core:
        return _core["result"]
    texts = {f: f.read_text(encoding="utf-8", errors="replace") for f in sorted(CORE.glob("*.c"))}
    texts = {f: t for f, t in texts.items() if "int main" not in t}
    funcs = {name for name in ("core_get_info", "core_list_procs", "core_proc_cpu") if any(name in t for t in texts.values())}
    other = [f.name for f, t in texts.items() if not fits_core(target_of_core(t))]
    if not texts:
        err = ("agent/core", "не сдано", "нет файлов ядра agent/core/*.c")
    elif other:
        err = (", ".join(other), "пропущено", f"ядро для другой системы, {SYSTEM_NAME} его не собирает")
    else:
        src = [f.name for f in texts]
        if SYSTEM == "win":
            r = run(["cl", "/nologo", "/LD", *src, f"/Fe:{LIB_NAME}"], cwd=CORE)
        elif SYSTEM == "mac":
            r = run(["clang", "-shared", "-fPIC", "-o", LIB_NAME, *src], cwd=CORE)
        else:
            r = run(["gcc", "-shared", "-fPIC", "-o", LIB_NAME, *src], cwd=CORE)
        err = None if r.returncode == 0 else (
            " ".join(src), "ошибка", "ядро не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150])
    _core["result"] = funcs, err
    return funcs, err


def check_module1_agent():
    """Модуль 1, задание «Агент»: ядро собирается в библиотеку, brain.py печатает JSON с полем uptime_s."""
    brain = ROOT / "agent" / "brain" / "brain.py"
    funcs, err = build_core()
    if "core_get_info" not in funcs or not brain.exists():
        return [("Модуль 1", "agent", "не сдано", "нет agent/core/*.c с core_get_info или agent/brain/brain.py")], True
    if err:
        return [("Модуль 1", *err)], err[1] != "ошибка"
    r = run([sys.executable, str(brain)])
    try:
        msg = json.loads(r.stdout)
    except ValueError:
        tail = (r.stderr.strip().splitlines() or ["brain.py не напечатал JSON"])[-1]
        return [("Модуль 1", "brain.py", "ошибка", tail[:150])], False
    if "uptime_s" not in msg and "pid" in msg:
        return [("Модуль 1", "brain.py", "не сдано", "ядро из глав 1.1–1.2 работает, поля uptime_s ещё нет")], True
    missing = [k for k in ("event", "pid", "cpus", "page_size", "host", "uptime_s") if k not in msg]
    if missing:
        return [("Модуль 1", "brain.py", "ошибка", "в JSON нет полей: " + ", ".join(missing))], False
    real = system_uptime()
    if not isinstance(msg["uptime_s"], int) or abs(msg["uptime_s"] - real) > 60:
        return [("Модуль 1", "brain.py", "ошибка", f"uptime_s = {msg['uptime_s']}, система работает {real} с")], False
    return [("Модуль 1", "agent", "пройдено", f"uptime_s = {msg['uptime_s']}, система — {real} с")], True


def check_module1_ai():
    """Модуль 1, задание «ИИ»: сценарий n8n с вебхуком и моделью Ollama и журнал проверки ответов."""
    flow, log = ROOT / "agent" / "n8n" / "agent-uptime.json", ROOT / "agent" / "n8n" / "ai-log.md"
    if not flow.exists():
        return [("Модуль 1", "agent/n8n", "не сдано", "нет agent-uptime.json — выгрузки сценария из n8n")], True
    if not log.exists():
        return [("Модуль 1", "agent/n8n", "ошибка", "нет ai-log.md — журнала проверки ответов модели")], False
    try:
        nodes = [n.get("type", "") for n in json.loads(flow.read_text(encoding="utf-8")).get("nodes", [])]
    except ValueError:
        return [("Модуль 1", "agent-uptime.json", "ошибка", "файл не разбирается как JSON — экспорт из n8n")], False
    need = {"вебхук": "webhook", "модель Ollama": "ollama"}
    lost = [name for name, part in need.items() if not any(part in n.lower() for n in nodes)]
    if lost:
        return [("Модуль 1", "agent-uptime.json", "ошибка", "в сценарии нет узлов: " + ", ".join(lost))], False
    if log.read_text(encoding="utf-8").count("___"):
        return [("Модуль 1", "ai-log.md", "ошибка", "в журнале остались пропуски ___")], False
    return [("Модуль 1", "agent/n8n", "пройдено", f"узлов в сценарии: {len(nodes)}")], True


def system_procs():
    """PID → PPID всех процессов по программе системы, а не по ядру студента."""
    if SYSTEM == "win":
        cmd = ["powershell", "-NoProfile", "-Command",
               "Get-CimInstance Win32_Process | ForEach-Object { \"$($_.ProcessId) $($_.ParentProcessId)\" }"]
        name = "Win32_Process"
    else:
        cmd, name = ["ps", "-A", "-o", "pid=,ppid="], "ps"
    pairs = [line.split() for line in run(cmd).stdout.splitlines()]
    return {int(p[0]): int(p[1]) for p in pairs if len(p) == 2}, name


def check_agent1():
    """Проверка агента 1 (пара 4): core_list_procs находит те же процессы, что программа системы.

    Возвращает (результат, подробности, ok); результат — «пройдена», «не пройдена», «не сдано», «пропущено».
    """
    import ctypes
    funcs, err = build_core()
    if "core_list_procs" not in funcs:
        return "не сдано", "нет agent/core/*.c с core_list_procs", True
    if err:
        return ("пропущено", err[2], True) if err[1] == "пропущено" else ("не пройдена", err[2], False)

    class CoreProc(ctypes.Structure):
        _fields_ = [("pid", ctypes.c_int64), ("ppid", ctypes.c_int64), ("name", ctypes.c_char * 64)]

    try:
        lib = ctypes.CDLL(str(CORE / LIB_NAME))
        lib.core_list_procs.argtypes = [ctypes.POINTER(CoreProc), ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
        lib.core_list_procs.restype = ctypes.c_int
    except (OSError, AttributeError) as e:
        return "не пройдена", f"библиотека не загружается: {e}"[:150], False
    too_small = 122 if SYSTEM == "win" else 34  # ERROR_INSUFFICIENT_BUFFER / ERANGE

    one, count = (CoreProc * 1)(), ctypes.c_int32()
    code = lib.core_list_procs(one, 1, ctypes.byref(count))
    if code != too_small or count.value <= 1:
        return "не пройдена", f"при max = 1 ядро вернуло {code} и count = {count.value}, ждали {too_small} и число процессов", False
    room = count.value + 64
    buf = (CoreProc * room)()
    code = lib.core_list_procs(buf, room, ctypes.byref(count))
    if code != 0:
        return "не пройдена", f"при max = {room} ядро вернуло {code}", False
    core = {p.pid: (p.ppid, p.name.decode("utf-8", "replace")) for p in buf[:count.value]}
    real, tool = system_procs()

    me = core.get(os.getpid())
    if me is None:
        return "не пройдена", f"в списке ядра нет процесса проверки, pid = {os.getpid()}", False
    if me[0] != os.getppid() or "python" not in me[1].lower():
        return "не пройдена", f"процесс проверки: ppid = {me[0]}, name = «{me[1]}», ждали ppid = {os.getppid()} и имя python", False
    common = core.keys() & real.keys()
    same_parent = sum(core[pid][0] == real[pid] for pid in common)
    detail = f"ядро {len(core)}, {tool} {len(real)}, общих {len(common)}, родитель совпал у {same_parent}"
    # Списки сняты с разницей в доли секунды: часть процессов успевает появиться или завершиться.
    spare = max(5, len(real) // 10)
    if len(real.keys() - core.keys()) > spare:
        return "не пройдена", detail + " — ядро находит не все процессы", False
    if len(core.keys() - real.keys()) > spare:
        return "не пройдена", detail + " — в списке ядра процессы, которых нет в системе", False
    if same_parent < 0.95 * len(common):
        return "не пройдена", detail + " — ppid отличается от системного", False
    return "пройдена", detail, True


BUSY = "import time\nend = time.time() + 7\nwhile time.time() < end: pass"
IDLE = "import time\ntime.sleep(7)"
NO_PID = 2147483646  # такого номера нет ни в одной системе: в Windows номера кратны 4, в macOS и Linux не доходят до него


def check_agent2():
    """Проверка агента 2 (пара 6): по core_proc_cpu нагрузка процесса-нагрузчика больше 80%, спящего — меньше 10%.

    Возвращает (результат, подробности, ok), как check_agent1.
    """
    import ctypes
    import time
    funcs, err = build_core()
    if "core_proc_cpu" not in funcs:
        return "не сдано", "нет agent/core/*.c с core_proc_cpu", True
    if err:
        return ("пропущено", err[2], True) if err[1] == "пропущено" else ("не пройдена", err[2], False)

    class CoreCpu(ctypes.Structure):
        _fields_ = [("user_us", ctypes.c_int64), ("kernel_us", ctypes.c_int64)]

    try:
        lib = ctypes.CDLL(str(CORE / LIB_NAME))
        lib.core_proc_cpu.argtypes = [ctypes.c_int64, ctypes.POINTER(CoreCpu)]
        lib.core_proc_cpu.restype = ctypes.c_int
    except (OSError, AttributeError) as e:
        return "не пройдена", f"библиотека не загружается: {e}"[:150], False

    def used(pid):
        cpu = CoreCpu()
        code = lib.core_proc_cpu(pid, ctypes.byref(cpu))
        return None if code != 0 else cpu.user_us + cpu.kernel_us

    busy = subprocess.Popen([sys.executable, "-c", BUSY])
    idle = subprocess.Popen([sys.executable, "-c", IDLE])
    try:
        time.sleep(1)
        b0, i0, start = used(busy.pid), used(idle.pid), time.monotonic()
        time.sleep(3)
        b1, i1, wall = used(busy.pid), used(idle.pid), time.monotonic() - start
    finally:
        busy.kill(); idle.kill()
        busy.wait(); idle.wait()
    if None in (b0, b1, i0, i1):
        return "не пройдена", "core_proc_cpu вернула ошибку для работающего процесса", False
    if used(NO_PID) is not None:
        return "не пройдена", f"для несуществующего процесса {NO_PID} core_proc_cpu вернула 0, ждали код ошибки", False
    load_busy = round((b1 - b0) / (wall * 10_000))
    load_idle = round((i1 - i0) / (wall * 10_000))
    detail = f"нагрузка {load_busy}%, спящий процесс {load_idle}% за {wall:.1f} с"
    if load_busy < 80:
        return "не пройдена", detail + " — у нагрузки меньше 80%: проверьте единицы времени", False
    if load_busy > 120 or load_idle > 10:
        return "не пройдена", detail + " — числа больше настоящих: проверьте единицы времени", False
    return "пройдена", detail, True


def main():
    # Консоль Windows по умолчанию в cp1252: русский текст выводится в UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    rows, ok = check_lab01()
    rows2, ok2 = check_lab02()
    rows3, ok3 = check_lab03()
    rows4, ok4 = check_module1_agent()
    rows5, ok5 = check_module1_ai()
    rows6, ok6 = check_screenshots()
    rows += rows2 + rows3 + rows6 + rows4 + rows5
    ok = ok and ok2 and ok3 and ok4 and ok5 and ok6
    agent = {1: check_agent1()}
    if OPENED >= 2:
        agent[2] = check_agent2()
    ok = ok and all(a_ok for _, _, a_ok in agent.values())
    passed = sum(state == "пройдена" for state, _, _ in agent.values())
    lines = [f"## Проверки · {SYSTEM_NAME}", "",
             "| Работа | Файл | Результат | Подробности |", "|---|---|---|---|"]
    lines += [f"| {a} | `{b}` | {c} | {d} |" for a, b, c, d in rows]
    lines += ["", f"### Агент-сторож: проверок пройдено {passed} / {len(AGENT_CHECKS)}", "",
              "| № | Пара | Проверка | Результат | Подробности |", "|---|---|---|---|---|"]
    for n, pair, name in AGENT_CHECKS:
        state, detail, _ = agent.get(n, ("ещё не открыта" if n > OPENED else "не сдано", "", True))
        lines.append(f"| {n} | {pair} | {name} | {state} | {detail} |")
    report = "\n".join(lines)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
