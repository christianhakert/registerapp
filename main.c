#include <stdio.h>

int main(){
    asm volatile(".global __main_start_mark;"
                "__main_start_mark: nop");
    int a;
    printf("Starting benchmark\n");
    for(int i=0;i<12345;i++){
        a++;
    }
    asm volatile(".global __main_stop_mark;"
                "__main_stop_mark: nop;");
}