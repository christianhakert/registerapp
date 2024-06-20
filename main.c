// #include <stdio.h>

int main(){
    asm volatile(".global __main_start_mark;"
                "__main_start_mark: nop");
    int a;
    // printf("Starting benchmark\n");
    asm volatile("add x1,x2, x3");
    for(int i=0;i<12345;i++){
        a++;
    }

    test();

    asm volatile(".global __main_stop_mark;"
                "__main_stop_mark: nop;");
}

void test(){

}