#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void null_write(void) {
    int *p = NULL;
    printf("writing to address %p\n", (void *)p);
    *p = 42;
    printf("not reached\n");
}

static void overflow(void) {
    struct { int data[4]; int limit; } s = {{0, 0, 0, 0}, 100};
    printf("limit before: %d\n", s.limit);
    for (int i = 0; i <= 4; i++)
        s.data[i] = 7;
    printf("limit after:  %d\n", s.limit);
}

static void heap_overflow(void) {
    int *data = malloc(4 * sizeof(int));
    int i;
    for (i = 0; i <= 4; i++)
        data[i] = 7;
    printf("wrote %d numbers into room for 4\n", i);
    free(data);
}

static void use_after_free(void) {
    char *name = malloc(16);
    strcpy(name, "agent");
    free(name);
    printf("name after free: %s\n", name);
}

int main(int argc, char *argv[]) {
    const char *mode = argc > 1 ? argv[1] : "";
    if (strcmp(mode, "null") == 0)
        null_write();
    else if (strcmp(mode, "overflow") == 0)
        overflow();
    else if (strcmp(mode, "heap") == 0)
        heap_overflow();
    else if (strcmp(mode, "uaf") == 0)
        use_after_free();
    else {
        printf("usage: crash null|overflow|heap|uaf\n");
        return 1;
    }
    return 0;
}
