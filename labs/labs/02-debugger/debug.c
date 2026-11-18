#include <stdio.h>
#include <string.h>

struct point {
    int x;
    int y;
};

int area(struct point p) {
    int s = p.x * p.y;
    return s;
}

int main(void) {
    struct point p = {3, 4};
    char name[8];
    int total = 0;

    strcpy(name, "agent");
    for (int i = 1; i <= 3; i++)
        total += i;
    int a = area(p);
    printf("%s: total=%d area=%d\n", name, total, a);
    return 0;
}
