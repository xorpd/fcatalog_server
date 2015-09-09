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

    printf("\n* Testing simple signing of data:\n");
    sign(my_data,strlen(my_data),result,NUM_PERMS);
    return 0;
}

int test_short_input() {
    // Try to sign a short input, and expect a return value of -1.
    
    unsigned int result[NUM_PERMS];
    char* short_data = "123";
    char* exact_data = "1234";
    int res;

    printf("\n* Testing signing of short data:\n");
    res = sign(short_data,strlen(short_data),result,NUM_PERMS);
    if (res != -1) {
        printf("\n sign() didn't report that input was too short.\n");
        return -1;
    }
    res = sign(exact_data,strlen(exact_data),result,NUM_PERMS);
    if (res != 0) {
        printf("\n sign() reported incorrectly that input was too short.\n");
        return -1;
    }
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

    unsigned int sims;

    printf("\n* Testing similarity properties of catalog1:\n");

    sign(letters1,strlen(letters1),s1,NUM_PERMS);
    sign(letters2,strlen(letters2),s2,NUM_PERMS);
    // Count similars:
    sims = count_similars(s1,s2,NUM_PERMS);
    if(sims < NUM_PERMS/2) {
        printf("letters1 is not so similar to letters2.\n");
        return -1;
    }

    sign(digits1,strlen(digits1),s1,NUM_PERMS);
    sign(digits2,strlen(digits2),s2,NUM_PERMS);
    sims = count_similars(s1,s2,NUM_PERMS);
    if(sims < NUM_PERMS/2) {
        printf("digits1 is not so similar to digits2.\n");
        return -1;
    }

    sign(letters1,strlen(letters1),s1,NUM_PERMS);
    sign(digits2,strlen(digits2),s2,NUM_PERMS);
    sims = count_similars(s1,s2,NUM_PERMS);
    if(sims > 0) {
        printf("A similarity was found between letters1 and digits2\n");
        return -1;
    }

    return 0;
}



int main() {
    int res = 0;

    res |= test_simple_sign();
    res |= test_short_input();
    res |= test_sign_similarity();

    if(0 == res) {
        printf("\n===========================\n");
        printf("All tests passed successfuly!\n");
        printf("===========================\n");
    } else {
        printf("\n@@@@@@@@@@@@@@@@@@@@@@@@\n");
        printf("Some tests have failed!\n");
        printf("@@@@@@@@@@@@@@@@@@@@@@@@\n");
    }

    return 0;
}
