
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include "core.h"

int main(int argc, char *argv[]) {
    struct core_child child;
    int32_t code = 0;

    if (argc < 3) {
        printf("usage: run_child timeout_ms program [args...]\n");
        return 1;
    }

    int err = core_spawn(argv + 2, &child);

    if (err != 0) {
        printf("core_spawn: error %d\n", err);
        return 1;
    }

    printf("started pid %" PRId64 "\n", child.pid);

    err = core_wait(&child, atoi(argv[1]), &code);

    if (err != 0) {
        printf("core_wait: error %d, pid %" PRId64 " still running\n",
            err, child.pid);
        return 1;
    }

    printf("pid %" PRId64 " exited, code %d\n",
        child.pid, (int)code);

    return 0;
}
