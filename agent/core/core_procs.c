#include <windows.h>
#include <tlhelp32.h>
#include "core.h"

int core_list_procs(struct core_proc *out, int32_t max, int32_t *count) {
    PROCESSENTRY32W pe;
    int32_t found = 0;

    if (count == NULL || max < 0 || (out == NULL && max > 0))
        return ERROR_INVALID_PARAMETER;
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snap == INVALID_HANDLE_VALUE)
        return (int)GetLastError();

    pe.dwSize = sizeof pe;
    if (!Process32FirstW(snap, &pe)) {
        DWORD err = GetLastError();
        CloseHandle(snap);
        return (int)err;
    }
    do {
        if (found < max) {
            out[found].pid = pe.th32ProcessID;
            out[found].ppid = pe.th32ParentProcessID;
            if (WideCharToMultiByte(CP_UTF8, 0, pe.szExeFile, -1, out[found].name,
                                    sizeof out[found].name, NULL, NULL) == 0)
                out[found].name[sizeof out[found].name - 1] = '\0';
        }
        found++;
    } while (Process32NextW(snap, &pe));

    CloseHandle(snap);
    *count = found;
    return found > max ? ERROR_INSUFFICIENT_BUFFER : 0;
}
