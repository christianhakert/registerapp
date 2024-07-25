#include "data.h"
// #include <stdio.h>

typedef unsigned long uint64_t;
typedef long int64_t;

void print_system(double **system, double *right, uint64_t range);

void solve_system(double **system, double *right, uint64_t range);

int main() {
    double local_system[RANGE][RANGE];

    double *system_ptr[RANGE];
    for (uint64_t i = 0; i < RANGE; i++) {
        system_ptr[i] = local_system[i];
    }

    // print_system(system_ptr, right, RANGE);
    for (unsigned long i = 0; i < 150; i++) {
        for (unsigned long x = 0; x < RANGE; x++) {
            for (unsigned long y = 0; y < RANGE; y++) {
                local_system[x][y] = system[x][y];
            }
        }
        // printf("DOne copy\n");
        solve_system(system_ptr, right, RANGE);
    }

    // print_system(system_ptr, right, RANGE);
}

void substract_lines(double **system, double *right, uint64_t target,
                     uint64_t src, double fac, uint64_t range) {
    double *target_line = system[target];
    double *src_line = system[src];
    for (uint64_t i = 0; i < range; i++) {
        target_line[i] -= src_line[i] * fac;
    }
    right[target] -= right[src] * fac;
}

void swap_lines(double **system, double *right, uint64_t target, uint64_t src,
                uint64_t range) {
    double *target_line = system[target];
    double *src_line = system[src];
    for (uint64_t i = 0; i < range; i++) {
        double acc = target_line[i];
        target_line[i] = src_line[i];
        src_line[i] = acc;
    }
    double acc = right[target];
    right[target] = right[src];
    right[src] = acc;
}

void solve_system(double **system, double *right, uint64_t range) {
    // Outer loop over range
    for (uint64_t range_reduce = 0; range_reduce < range; range_reduce++) {
        // First check if line can be used to reduce
        if (system[range_reduce][range_reduce] == 0) {
            for (uint64_t left_over = range_reduce + 1; left_over < range;
                 left_over++) {
                if (system[left_over][range_reduce] != 0) {
                    swap_lines(system, right, range_reduce, left_over, range);
                    break;
                }
            }
            if (system[range_reduce][range_reduce] == 0) {
                // printf("System is not solvable\n");
                return;
            }
        }

        // Now eliminate the current column everywhere
        for (uint64_t left_over = range_reduce + 1; left_over < range;
             left_over++) {
            double reduce_fac = system[left_over][range_reduce] /
                                system[range_reduce][range_reduce];
            substract_lines(system, right, left_over, range_reduce, reduce_fac,
                            range);
        }
    }

    // Now insert solved variables and eliminate them all
    for (int64_t left_line = range - 1; left_line >= 0; left_line--) {
        // Insert variables first
        for (int64_t i = left_line + 1; i < (int64_t)range; i++) {
            right[left_line] -= system[left_line][i] * right[i];
            system[left_line][i] = 0;
        }

        right[left_line] /= system[left_line][left_line];
        system[left_line][left_line] = 1;
    }
}

// void print_system(double **system, double *right, uint64_t range) {
//     printf("Printing equation system:\n");
//     for (uint64_t y = 0; y < range; y++) {
//         for (uint64_t x = 0; x < range; x++) {
//             if (system[y][x] > 0.00001 || system[y][x] < -0.00001) {
//                 if (system[y][x] == 1) {
//                 } else if (system[y][x] == -1) {
//                     printf("-");
//                 } else {
//                     printf("%f ", system[y][x]);
//                 }
//                 printf("x %d\t", x);
//             }
//         }
//         printf("=\t %f\n", right[y]);
//     }
// }
