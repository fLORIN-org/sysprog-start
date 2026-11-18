# core

Ядро агента-сторожа на C. Функция `core_get_info` собирает сведения о процессе и компьютере (pid, число процессоров, размер страницы памяти, имя компьютера) и записывает их в структуру `struct core_info` из `core.h`.

## Файлы

- `core.h` — структура `core_info` и объявление функции
- `core_info.c` — реализация для Windows (WinAPI) и POSIX (macOS/Linux)
- `show_info.c` — проверочная программа, печатает поля структуры

## Сборка

Windows (x64 Native Tools Command Prompt):

```
cl /nologo /W4 /LD core_info.c /Fe:sentry_core.dll
cl /nologo /W4 core_info.c show_info.c /Fe:show_info.exe
show_info.exe
```

macOS:

```
clang -Wall -Wextra -shared -fPIC -o libsentry_core.dylib core_info.c
clang -Wall -Wextra -o show_info core_info.c show_info.c
./show_info
```

Linux:

```
gcc -Wall -Wextra -shared -fPIC -o libsentry_core.so core_info.c
gcc -Wall -Wextra -o show_info core_info.c show_info.c
./show_info
```
