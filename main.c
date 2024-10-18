#include "data.h"

typedef unsigned char uint8_t;

void quick_sort(uint8_t *begin, uint8_t *end);

void main() {
    unsigned int sort_size = 8000;

    quick_sort(random_number, random_number + sort_size);
}

void quick_sort(unsigned char *begin, unsigned char *end) {
    // printf("Beginning of qsort\n");
    if (begin + 2 >= end) {
        return;
    }
    unsigned char *pivot_element = end - 1;

    unsigned char *li = begin;
    unsigned char *ri = end - 1;

    // printf("Resorting loop\n");
    while (li < ri) {
        while (li < end - 2 && *li < *pivot_element) li++;
        while (ri > begin && *ri >= *pivot_element) ri--;

        if (li < ri) {
            unsigned char buffer = *li;
            *li = *ri;
            *ri = buffer;
        }
    }

    // printf("Resorting loop end\n");

    if (*li > *pivot_element) {
        unsigned char buffer = *li;
        *li = *pivot_element;
        *pivot_element = buffer;
    }

    // printf("LCalling qsort at 0x%lx\n", quick_sort);
    quick_sort(begin, li);
    // printf("RCalling qsort at 0x%lx\n", quick_sort);
    quick_sort(li + 1, end);
}