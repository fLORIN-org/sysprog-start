
#include <string.h>
#include <windows.h>
#include "core.h"

#define CMD_MAX 1024

int core_spawn(char *const argv[], struct core_child *out) {
    WCHAR cmd[CMD_MAX];
    int used = 0;
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;

    if (argv == NULL || argv[0] == NULL || out == NULL)
        return ERROR_INVALID_PARAMETER;

    for (int i = 0; argv[i] != NULL; i++) {
        int quote = strchr(argv[i], ' ') != NULL;

        if (used + 3 >= CMD_MAX)
            return ERROR_INSUFFICIENT_BUFFER;

        if (i > 0)
            cmd[used++] = L' ';

        if (quote)
            cmd[used++] = L'"';

        int n = MultiByteToWideChar(
            CP_UTF8, 0, argv[i], -1,
            cmd + used, CMD_MAX - used - 2
        );

        if (n == 0)
            return ERROR_INSUFFICIENT_BUFFER;

        used += n - 1;

        if (quote)
            cmd[used++] = L'"';
    }

    cmd[used] = L'\0';

    ZeroMemory(&si, sizeof si);
    si.cb = sizeof si;

    if (!CreateProcessW(
        NULL, cmd, NULL, NULL, FALSE, 0,
        NULL, NULL, &si, &pi
    ))
        return (int)GetLastError();

    CloseHandle(pi.hThread);

    out->pid = pi.dwProcessId;
    out->handle = (int64_t)(intptr_t)pi.hProcess;

    return 0;
}

int core_wait(
    struct core_child *child,
    int32_t timeout_ms,
    int32_t *exit_code
) {
    DWORD code;

    if (child == NULL || child->handle == 0 || exit_code == NULL)
        return ERROR_INVALID_PARAMETER;

    HANDLE h = (HANDLE)(intptr_t)child->handle;

    DWORD r = WaitForSingleObject(
        h,
        timeout_ms < 0 ? INFINITE : (DWORD)timeout_ms
    );

    if (r == WAIT_TIMEOUT)
        return WAIT_TIMEOUT;

    if (r != WAIT_OBJECT_0)
        return (int)GetLastError();

    if (!GetExitCodeProcess(h, &code))
        return (int)GetLastError();

    CloseHandle(h);

    child->handle = 0;
    *exit_code = (int32_t)code;

    return 0;
}
