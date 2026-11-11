# Агент-сторож компьютера

Сквозной проект дисциплины: программа, которая следит за состоянием компьютера и сообщает о нарушениях.
Устройство агента — в [главе 0.4](https://maximbytecamp.github.io/sysprog_makarov/temy/04-kak-ustroena-disciplina/index.html#s3).

| Папка | Часть | Язык | Что делает |
|---|---|---|---|
| [`core`](core/README.md) | ядро | C | вызывает функции системы и возвращает факты: процессы, память, файлы, порты |
| [`brain`](brain/README.md) | мозг | Python | по расписанию вызывает ядро, сравнивает снимки, отправляет тревоги в n8n, отвечает ИИ-агенту |

Код агента появляется с пары 2. С пары 4 в [проверках](../checks/README.md) открываются проверки агента:
к концу курса их 13.

## Какие файлы здесь появляются

Файлы агента студент создаёт сам по шагам глав. Каждая следующая глава опирается на файлы предыдущей.
Если глава пропущена или репозиторий создан заново, в начале следующей главы есть раскрывающийся блок
«Если файлов прошлых глав нет» с полным кодом нужных файлов и командой сборки.

| Файл | Появляется | Меняется |
|---|---|---|
| `core/core.h` | [1.1, шаг 5](https://maximbytecamp.github.io/sysprog_makarov/temy/06-c-dlya-sistemnogo-programmista/index.html#s6) | [1.2, шаг 1](https://maximbytecamp.github.io/sysprog_makarov/temy/07-c-i-python-vmeste/index.html) — `CORE_API`; [задание модуля 1](https://maximbytecamp.github.io/sysprog_makarov/temy/11-zadanie-modulya-1/index.html) — `uptime_s`; [2.1, шаг 1](https://maximbytecamp.github.io/sysprog_makarov/temy/14-spisok-processov/index.html#s2) — `struct core_proc`; [2.2, шаг 1](https://maximbytecamp.github.io/sysprog_makarov/temy/16-zapusk-processa/index.html#s2) — `struct core_child`; [2.3, шаг 1](https://maximbytecamp.github.io/sysprog_makarov/temy/18-processornoe-vremya/index.html#s2) — `struct core_cpu`; [2.4, шаг 1](https://maximbytecamp.github.io/sysprog_makarov/temy/20-potoki/index.html#s2) — `core_proc_threads` |
| `core/core_info.c` | [1.1, шаг 6](https://maximbytecamp.github.io/sysprog_makarov/temy/06-c-dlya-sistemnogo-programmista/index.html#s7) | задание модуля 1 — `uptime_s` |
| `core/show_info.c` | [1.1, шаг 7](https://maximbytecamp.github.io/sysprog_makarov/temy/06-c-dlya-sistemnogo-programmista/index.html#s8) | — |
| `core/core_procs.c` | [2.1, шаг 2](https://maximbytecamp.github.io/sysprog_makarov/temy/14-spisok-processov/index.html#s3) | — |
| `core/list_procs.c` | [2.1, шаг 3](https://maximbytecamp.github.io/sysprog_makarov/temy/14-spisok-processov/index.html#s4) | — |
| `core/core_spawn.c` | [2.2, шаг 2](https://maximbytecamp.github.io/sysprog_makarov/temy/16-zapusk-processa/index.html#s3) | — |
| `core/run_child.c` | [2.2, шаг 3](https://maximbytecamp.github.io/sysprog_makarov/temy/16-zapusk-processa/index.html#s4) | — |
| `core/core_cpu.c` | [2.3, шаг 2](https://maximbytecamp.github.io/sysprog_makarov/temy/18-processornoe-vremya/index.html#s3) | — |
| `core/cpu_top.c` | [2.3, шаг 3](https://maximbytecamp.github.io/sysprog_makarov/temy/18-processornoe-vremya/index.html#s4) | — |
| `core/core_threads.c` | [2.4, шаг 2](https://maximbytecamp.github.io/sysprog_makarov/temy/20-potoki/index.html#s3) | — |
| `core/count_threads.c` | [2.4, шаг 3](https://maximbytecamp.github.io/sysprog_makarov/temy/20-potoki/index.html#s4) | — |
| `brain/brain.py` | [1.2, шаги 3–8](https://maximbytecamp.github.io/sysprog_makarov/temy/07-c-i-python-vmeste/index.html) | [1.3, шаг 4](https://maximbytecamp.github.io/sysprog_makarov/temy/08-n8n-i-ollama/index.html#s5) — `send`; задание модуля 1 — `uptime_s`; [2.1, шаг 6](https://maximbytecamp.github.io/sysprog_makarov/temy/14-spisok-processov/index.html#s7) — `list_procs`, `parents`; [2.2, шаг 5](https://maximbytecamp.github.io/sysprog_makarov/temy/16-zapusk-processa/index.html#s6) — `spawn`, `wait`; [2.3, шаг 5](https://maximbytecamp.github.io/sysprog_makarov/temy/18-processornoe-vremya/index.html#s6) — `proc_cpu`, `cpu_load`; [2.4, шаг 4](https://maximbytecamp.github.io/sysprog_makarov/temy/20-potoki/index.html#s5) — `proc_threads`, `most_threads` |
| `n8n/agent-uptime.json`, `n8n/ai-log.md` | [задание модуля 1](https://maximbytecamp.github.io/sysprog_makarov/temy/11-zadanie-modulya-1/index.html#s3) | — |

Собранная библиотека (`sentry_core.dll`, `libsentry_core.dylib`, `libsentry_core.so`) в репозиторий не кладётся:
она собирается из `core_info.c`, `core_procs.c`, `core_spawn.c`, `core_cpu.c` и `core_threads.c` на любой системе.
