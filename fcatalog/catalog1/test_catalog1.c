#include <stdio.h>
#include <string.h>
#include "catalog1.h"


#define NUM_PERMS 16

int print_dword_array(unsigned int* arr,unsigned int len) {
    // Print an array of dwords
    unsigned int i;
    for(unsigned int i=0; i<len; ++i) {
        printf("%04x ",arr[i]);
    }

}

int main() {
    unsigned int result[NUM_PERMS];
    char* my_data = "hello world!";
    sign(my_data,strlen(my_data),result,NUM_PERMS);

    // Print the signed result:
    print_dword_array(result,NUM_PERMS);
    return 0;
}
