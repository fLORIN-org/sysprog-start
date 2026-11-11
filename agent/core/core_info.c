#include "core.h"

#ifdef _WIN32
#include <windows.h>

int core_get_info(struct core_info *out) {
    if (out == NULL) {
        return ERROR_INVALID_PARAMETER;
    }

    ZeroMemory(out, sizeof(*out));

    out->pid = (int64_t)GetCurrentProcessId();

    SYSTEM_INFO si;
    GetNativeSystemInfo(&si);
    out->cpus = (int32_t)si.dwNumberOfProcessors;
    out->page_size = (int32_t)si.dwPageSize;

    WCHAR name[CORE_HOST_MAX];
    DWORD size = CORE_HOST_MAX;
    if (!GetComputerNameW(name, &size)) {
        return (int)GetLastError();
    }

    if (WideCharToMultiByte(CP_UTF8, 0, name, -1, out->host, CORE_HOST_MAX, NULL, NULL) == 0) {
        return (int)GetLastError();
    }

    return 0;
}

#else
#include <unistd.h>
#include <string.h>
#include <errno.h>

int core_get_info(struct core_info *out) {
    if (out == NULL) {
        return EINVAL;
    }

    memset(out, 0, sizeof(*out));

    out->pid = (int64_t)getpid();
    out->cpus = (int32_t)sysconf(_SC_NPROCESSORS_ONLN);
    out->page_size = (int32_t)sysconf(_SC_PAGESIZE);

    if (gethostname(out->host, CORE_HOST_MAX) != 0) {
        return errno;
    }
    out->host[CORE_HOST_MAX - 1] = '\0';

    return 0;
}

#endif
