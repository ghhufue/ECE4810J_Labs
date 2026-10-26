
#include "dct.h"

void dct_1d(dct_data_t src[DCT_SIZE], dct_data_t dst[DCT_SIZE])
{
   unsigned int k, n;
   int tmp;
   const dct_data_t dct_coeff_table[DCT_SIZE][DCT_SIZE] = {
#include "dct_coeff_table.txt"
   };

DCT_Outer_Loop:
   for (k = 0; k < DCT_SIZE; k++) {
DCT_Inner_Loop:
      for(n = 0, tmp = 0; n < DCT_SIZE; n++) {
         int coeff = (int)dct_coeff_table[k][n];
         tmp += src[n] * coeff;
      }
      dst[k] = DESCALE(tmp, CONST_BITS);
   }
}

void dct_2d(dct_data_t in_block[DCT_SIZE][DCT_SIZE],
      dct_data_t out_block[DCT_SIZE][DCT_SIZE])
{
   dct_data_t row_outbuf[DCT_SIZE][DCT_SIZE];
   dct_data_t col_outbuf[DCT_SIZE][DCT_SIZE], col_inbuf[DCT_SIZE][DCT_SIZE];
   unsigned i, j;

   // DCT rows
Row_DCT_Loop:
   for(i = 0; i < DCT_SIZE; i++) {
      dct_1d(in_block[i], row_outbuf[i]);
   }
   // Transpose data in order to re-use 1D DCT code
Xpose_Row_Outer_Loop:
   for (j = 0; j < DCT_SIZE; j++)
Xpose_Row_Inner_Loop:
      for(i = 0; i < DCT_SIZE; i++)
         col_inbuf[j][i] = row_outbuf[i][j];
   // DCT columns
Col_DCT_Loop:
   for (i = 0; i < DCT_SIZE; i++) {
      dct_1d(col_inbuf[i], col_outbuf[i]);
   }
   // Transpose data back into natural order
Xpose_Col_Outer_Loop:
   for (j = 0; j < DCT_SIZE; j++)
Xpose_Col_Inner_Loop:
      for(i = 0; i < DCT_SIZE; i++)
         out_block[j][i] = col_outbuf[i][j];
}

void read_data(short input[N], short buf[DCT_SIZE][DCT_SIZE])
{
   int r, c;

RD_Loop_Row:
   for (r = 0; r < DCT_SIZE; r++) {
RD_Loop_Col:
      for (c = 0; c < DCT_SIZE; c++)
         buf[r][c] = input[r * DCT_SIZE + c];
   }
}

void write_data(short buf[DCT_SIZE][DCT_SIZE], short output[N])
{
   int r, c;

WR_Loop_Row:
   for (r = 0; r < DCT_SIZE; r++) {
WR_Loop_Col:
      for (c = 0; c < DCT_SIZE; c++)
         output[r * DCT_SIZE + c] = buf[r][c];
   }
}

void dct(short input[N], short output[N])
{

   short buf_2d_in[DCT_SIZE][DCT_SIZE];
   short buf_2d_out[DCT_SIZE][DCT_SIZE];

   // Read input data. Fill the internal buffer.
   read_data(input, buf_2d_in);

   dct_2d(buf_2d_in, buf_2d_out);

   // Write out the results.
   write_data(buf_2d_out, output);
}

/* C=round(2^(CONST_BITS+1.5)*T). Forward C/2^13 is inverted by
 * C-transpose/2^16. Match the manual's floor shift in each inverse pass. */
void idct_1d(dct_data_t src[DCT_SIZE], dct_data_t dst[DCT_SIZE])
{
   const dct_data_t coeff[DCT_SIZE][DCT_SIZE] = {
#include "dct_coeff_table.txt"
   };
   int k, n;
IDCT_Outer_Loop:
   for (k = 0; k < DCT_SIZE; ++k) {
      int sum = 0;
IDCT_Inner_Loop:
      for (n = 0; n < DCT_SIZE; ++n)
         sum += (int)src[n] * coeff[n][k];
      dst[k] = (dct_data_t)(sum >> (CONST_BITS + 3));
   }
}

void idct_2d(dct_data_t input[DCT_SIZE][DCT_SIZE], dct_data_t output[DCT_SIZE][DCT_SIZE])
{
   dct_data_t rows[DCT_SIZE][DCT_SIZE], col_in[DCT_SIZE], col_out[DCT_SIZE];
   int r, c;
   for (r = 0; r < DCT_SIZE; ++r) idct_1d(input[r], rows[r]);
   for (c = 0; c < DCT_SIZE; ++c) {
      for (r = 0; r < DCT_SIZE; ++r) col_in[r] = rows[r][c];
      idct_1d(col_in, col_out);
      for (r = 0; r < DCT_SIZE; ++r) output[r][c] = col_out[r];
   }
}

void idct(short input[N], short output[N])
{
   short src[DCT_SIZE][DCT_SIZE], dst[DCT_SIZE][DCT_SIZE];
   read_data(input, src);
   idct_2d(src, dst);
   write_data(dst, output);
}

