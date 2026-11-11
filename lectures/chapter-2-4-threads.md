# 2.4 Потоки

Глава справочника: [https://maximbytecamp.github.io/sysprog_makarov/temy/20-potoki/index.html](https://maximbytecamp.github.io/sysprog_makarov/temy/20-potoki/index.html)

## Разделы

1. Задача главы
2. Шаг 1. Объявить функцию в core.h
3. Шаг 2. Написать core_threads.c
4. Шаг 3. Запустить потоки из C
5. Шаг 4. Число потоков в Python
6. Шаг 5. Отправить в репозиторий
7. Запрос к помощнику ИИ

## Шпаргалка

| Что | Как |
|---|---|
| Число потоков | `core_proc_threads(pid, &count)`; (Windows: `cntThreads`); (macOS: `pti_threadnum`); (Linux: поле 20 `stat`) |
| Запуск потока | (Windows: `CreateThread` → дескриптор); (macOS и Linux: `pthread_create(&t, NULL, f, arg)`); (Windows: `WaitForMultipleObjects`, `CloseHandle`); (macOS и Linux: `pthread_join`) |
| Жизнь потоков | 1 → 5 → 1; главный есть всегда |
| Мозг | `proc_threads(pid)` — число или `None`; `most_threads(3)` — самые многопоточные |
| Гонка | `counter++` из потоков теряет прибавки; атомарная операция или замок |

## Итог главы

Ядро агента получило функцию `core_proc_threads`: по номеру процесса она возвращает число его потоков. (Windows: В Windows число берётся из поля `cntThreads` снимка процессов.) (macOS: В macOS — из поля `pti_threadnum` ответа `proc_pidinfo`.) (Linux: В Linux — из поля 20 файла `/proc/PID/stat`.) Программа `count_threads.c` запустила четыре потока функцией (Windows: `CreateThread`) (macOS и Linux: `pthread_create`) и показала их число: 1, 5 и снова 1. Мозг нашёл у ребёнка (Windows: 8) (macOS и Linux: 5) потоков и три самых многопоточных процесса. Программа `race.c` показала гонку: атомарная прибавка даёт 4 000 000, а `counter++` со словом `volatile` — каждый раз другое и меньшее число.
