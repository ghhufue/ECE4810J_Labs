#include <cstdio>
#include "../lab3_starter/fir/fir.h"
int main() {
    FILE *in=std::fopen("input.dat","r"), *gold=std::fopen("out.gold.dat","r"), *out=std::fopen("out.dat","w");
    int sample,expected,result,errors=0;
    if(!in||!gold||!out)return 2;
    fir_reset();
    for(int i=0;i<600;++i) {
        if(std::fscanf(in,"%d",&sample)!=1 || std::fscanf(gold,"%d",&expected)!=1)return 3;
        fir(&result,sample);
        std::fprintf(out,"%d\n",result);
        if(result!=expected)++errors;
    }
    std::fclose(in);std::fclose(gold);std::fclose(out);
    std::printf("FIR supplied golden: 600 samples, %d failures\n",errors);
    return errors!=0;
}
