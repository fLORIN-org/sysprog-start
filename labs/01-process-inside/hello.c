#include <windows.h>
#include <stdio.h>

int main(void) {
    DWORD pid = GetCurrentProcessId();
    printf("agent v0, pid=%lu\n", pid);
    printf("Press Enter to exit\n");
    getchar();
    return 0;
}
