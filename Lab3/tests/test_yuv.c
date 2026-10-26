#include <stdio.h>
#include <stdlib.h>
#include "../lab3_starter/yuv_filter/yuv_filter.h"
static int clip(int x) { return x<0 ? 0 : x>255 ? 255 : x; }
int main(void) {
    image_t *in=(image_t*)calloc(1,sizeof(image_t));
    image_t *out=(image_t*)calloc(1,sizeof(image_t));
    const int dims[][2]={{1,1},{7,11},{200,200},{512,512}};
    const int scales[][3]={{128,128,128},{0,0,0},{64,128,32},{128,0,128}};
    unsigned state=48103;
    int d,s,x,y,errors=0,count=0,expected;
    FILE *fp;
    if(!in||!out) return 2;
    image_read(in);
    yuv_filter(in,out,128,128,128);
    image_write(out);
    fp=fopen("output.golden.dat","r");
    if(!fp) return 3;
    for(y=0;y<HEIGHT;++y) for(x=0;x<WIDTH;++x) {
        int got[3]={out->channels.ch1[x][y],out->channels.ch2[x][y],out->channels.ch3[x][y]};
        for(s=0;s<3;++s) { if(fscanf(fp,"%d",&expected)!=1 || got[s]!=expected) ++errors; ++count; }
    }
    fclose(fp);
    for(d=0;d<4;++d) for(s=0;s<4;++s) {
        in->width=dims[d][0]; in->height=dims[d][1];
        for(x=0;x<in->width;++x) for(y=0;y<in->height;++y) {
            state=1664525u*state+1013904223u;
            in->channels.ch1[x][y]=(unsigned char)(state>>24);
            state=1664525u*state+1013904223u;
            in->channels.ch2[x][y]=(unsigned char)(state>>24);
            state=1664525u*state+1013904223u;
            in->channels.ch3[x][y]=(unsigned char)(state>>24);
        }
        yuv_filter(in,out,scales[s][0],scales[s][1],scales[s][2]);
        if(out->width!=in->width || out->height!=in->height) ++errors;
        for(x=0;x<in->width;++x) for(y=0;y<in->height;++y) {
            int r=in->channels.ch1[x][y],g=in->channels.ch2[x][y],b=in->channels.ch3[x][y];
            int yy=((((66*r+129*g+25*b+128)>>8)+16)*scales[s][0])>>7;
            int u=((((-38*r-74*g+112*b+128)>>8)+128)*scales[s][1])>>7;
            int v=((((112*r-94*g-18*b+128)>>8)+128)*scales[s][2])>>7;
            int c=yy-16,dd=u-128,e=v-128;
            if(out->channels.ch1[x][y]!=clip((298*c+409*e+128)>>8) ||
               out->channels.ch2[x][y]!=clip((298*c-100*dd-208*e+128)>>8) ||
               out->channels.ch3[x][y]!=clip((298*c+516*dd+128)>>8)) ++errors;
            count+=3;
        }
    }
    printf("YUV: %d channel values, %d failures\n",count,errors);
    free(in);free(out);
    return errors!=0;
}
