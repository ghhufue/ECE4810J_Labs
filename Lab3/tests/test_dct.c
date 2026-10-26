#include <stdio.h>
#include "../lab3_starter/dct/dct.h"
#include "dct_vectors.h"

int main(void) {
    short input[64], output[64], recovered[64];
    int test, i, errors = 0;
    FILE *fp;
    for (test = 0; test < DCT_TEST_COUNT; ++test) {
        for (i=0; i<64; ++i) input[i]=dct_inputs[test][i];
        dct(input, output);
        idct(output, recovered);
        for (i=0; i<64; ++i) {
            if (output[i]!=dct_expected[test][i] || recovered[i]!=idct_expected[test][i]) {
                if (errors<10) printf("Mismatch: test=%d pixel=%d DCT %d/%d IDCT %d/%d\n",
                    test,i,output[i],dct_expected[test][i],recovered[i],idct_expected[test][i]);
                ++errors;
            }
        }
    }
    /* Required output.dat is the recovered top-left Lena block. */
    for(i=0;i<64;++i) input[i]=dct_inputs[2][i];
    dct(input,output); idct(output,recovered);
    fp=fopen("output.dat","w");
    if (!fp) return 2;
    for(i=0;i<64;++i) fprintf(fp,"%d\n",recovered[i]);
    fclose(fp);
    printf("DCT/IDCT: %d blocks, %d checked values, %d failures\n",
        DCT_TEST_COUNT,2*64*DCT_TEST_COUNT,errors);
    return errors!=0;
}
