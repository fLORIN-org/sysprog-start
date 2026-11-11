#ifndef SENTRY_CORE_H
#define SENTRY_CORE_H

#include <stdint.h>

#define CORE_HOST_MAX 256
#define CORE_NAME_MAX 64

#ifdef _WIN32
#define CORE_API __declspec(dllexport)
#else
#define CORE_API
#endif

struct core_info {
    int64_t pid;
    int32_t cpus;
    int32_t page_size;
    char    host[CORE_HOST_MAX];
};

struct core_proc {
    int64_t pid;
    int64_t ppid;
    char    name[CORE_NAME_MAX];
};

CORE_API int core_get_info(struct core_info *out);
CORE_API int core_list_procs(struct core_proc *out, int32_t max, int32_t *count);

#endif
