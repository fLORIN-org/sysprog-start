#include <math.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    double x = argc + 1;
    printf("%s: sqrt(%.0f) = %f\n", argv[0], x, sqrt(x));
    return 0;
}
