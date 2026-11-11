#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include "core.h"

#define MAX 4096

int main(int argc, char *argv[]) {
    static struct core_proc procs[MAX];
    int32_t max = argc > 1 ? atoi(argv[1]) : MAX;
    int32_t count = 0;

    if (max < 0 || max > MAX)
        max = MAX;
    int err = core_list_procs(procs, max, &count);
    if (err != 0) {
        printf("core_list_procs: error %d, need %d places, have %d\n", err, (int)count, (int)max);
        return 1;
    }
    for (int32_t i = 0; i < count; i++)
        printf("%7" PRId64 " %7" PRId64 "  %s\n", procs[i].pid, procs[i].ppid, procs[i].name);
    printf("processes %d, sizeof %zu\n", (int)count, sizeof procs[0]);
    return 0;
}
