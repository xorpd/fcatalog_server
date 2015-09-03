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
    printf("\n");

}

// Count the amount of similar entries between arr1 and arr2 arrays:
unsigned int count_similars(unsigned int* arr1, unsigned int* arr2,
        unsigned int len) {

    unsigned int count = 0;
    for(unsigned int i=0; i<len; ++i) {
        if(arr1[i] == arr2[i]) {
            count += 1;
        }
    }
    return count;
}


int test_simple_sign() {
    // Sign a simple chunk of data, and make sure we don't crash.
    
    unsigned int result[NUM_PERMS];
    char* my_data = "hello world!";

    printf("Testing simple signing of data:");
    sign(my_data,strlen(my_data),result,NUM_PERMS);
    printf("Result:");
    // Print the signed result:
    print_dword_array(result,NUM_PERMS);
    return 0;
}

int test_sign_similarity() {
    // Check the similarity properties of the sign function.
    unsigned int result[NUM_PERMS];
    unsigned int s1[NUM_PERMS];
    unsigned int s2[NUM_PERMS];
    char digits1[] = "948259038450923823094850923845092384598234532452908345";
    char digits2[] = "948259038450923823094850924845092384598234532452908345";
    char letters1[] = "kldfgjlksdmklvcamsdkcjaslkfjalskdjfklasdmklsajflkas";
    char letters2[] = "kldfgjlksdmklvcatsdkcjaslkfjalskdjfklasdmklsajflkas";

    sign(letters1,strlen(letters1),s1,NUM_PERMS);
    sign(letters2,strlen(letters2),s2,NUM_PERMS);

    return 0;

}



int main() {
    int res = 0;

    res |= test_simple_sign();
    res |= test_sign_similarity();

    if(0 == res) {
        printf("All tests pass successfuly!");
    }

    return 0;
}
