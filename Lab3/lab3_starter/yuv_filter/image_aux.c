#include <stdio.h>
#include <stdlib.h>
#include "image_aux.h"

void image_read(image_t *in_image) {
    image_dim_t width, height;
    int x, y;
    FILE        *fp;

    fp = fopen("input.dat","r");
    if (!fp) { perror("input.dat"); exit(1); }
    int tmp;
    // fscanf(fp, "%d", &tmp);
    width = WIDTH;
    // fscanf(fp, "%d", &tmp);
    height = HEIGHT;

    in_image->width  = width;
    in_image->height = height;
    for (y = 0; y < height; y++) {
        for (x = 0; x < width; x++) {
            if (fscanf(fp, "%d", &tmp)!=1) exit(2);
            in_image->channels.ch1[x][y] = tmp;
            if (fscanf(fp, "%d", &tmp)!=1) exit(2);
            in_image->channels.ch2[x][y] = tmp;
            if (fscanf(fp, "%d", &tmp)!=1) exit(2);
            in_image->channels.ch3[x][y] = tmp;
        }
    }
    fclose(fp);
}


void image_write(image_t *out_image) {
    FILE *fp;
    int x, y;
    image_dim_t width, height;
    image_pix_t tmp;

    fp = fopen("output.dat","w");
    if (!fp) { perror("output.dat"); exit(1); }

    width = out_image->width;
    // fprintf(fp, "%d \n", width);

    height = out_image->height;
    // fprintf(fp, "%d \n", height);

    for (y = 0; y < height; y++) {
        /* Scan-line: */
        for (x = 0; x < width; x++) {
            tmp = out_image->channels.ch1[x][y];
            fprintf(fp, "%d\n", tmp);
            tmp = out_image->channels.ch2[x][y];
            fprintf(fp, "%d\n", tmp);
            tmp = out_image->channels.ch3[x][y];
            fprintf(fp, "%d\n", tmp);
        }
    }
    fclose(fp);
}
