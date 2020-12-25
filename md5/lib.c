
#include <unistd.h>
#include <memory.h>
#include <string.h>

#include "md5.h"

void State_init(State *s)
{
  s->A = 0x01234567;
  s->B = 0x89abcdef;
  s->C = 0xfedcba98;
  s->D = 0x76543210;
}

uint32_t F(uint32_t X, uint32_t Y, uint32_t Z)
{
  return (X & Y) | (~X & Z);
}

uint32_t G(uint32_t X, uint32_t Y, uint32_t Z)
{
  return (X & Z) | (Y & ~Z);
}

uint32_t H(uint32_t X, uint32_t Y, uint32_t Z)
{
  return X ^ Y ^ Z;
}

uint32_t I(uint32_t X, uint32_t Y, uint32_t Z)
{
  return Y ^ (X | ~Z);
}

uint32_t T[64] = {
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x2441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391};

void Source_init(Source *s)
{
  memset(s, 0, sizeof(*s));
}

int Source_continue(Source *s)
{
  return s->status != DONE && s->status != ERROR;
}

// Proper way to rotate left, which compile to a single instruction
// https://blog.regehr.org/archives/1063
uint32_t rotl32a (uint32_t x, uint32_t n)
{
  assert(n<32);
  assert(n!=0);
  return (x<<n) | (x>>(32-n));
}

void md5_round1(Source *source, uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d, int k, int s, int i)
{
  *a = *b + (rotl32a(*a + F(*b, *c, *d) + source->data[k] + T[i], s));
}

void md5_round2(Source *source, uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d, int k, int s, int i)
{
  *a = *b + (rotl32a(*a + G(*b, *c, *d) + source->data[k] + T[i], s));
}

void md5_round3(Source *source, uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d, int k, int s, int i)
{
  *a = *b + (rotl32a(*a + H(*b, *c, *d) + source->data[k] + T[i], s));
}

void md5_round4(Source *source, uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d, int k, int s, int i)
{
  *a = *b + (rotl32a(*a + I(*b, *c, *d) + source->data[k] + T[i], s));
}

int params_round1[4][4][3] = {
     {{ 0,  7,  1},  { 1, 12,  2},  {2, 17,  3}, {3, 22,  4}},
     {{ 4,  7,  5},  { 5, 12,  6},  {6, 17,  7}, {7, 22,  8}},
     {{ 8,  7,  9},  { 9, 12, 10},  {10, 17, 11}, {11, 22, 12}},
     {{12,  7, 13},  {13, 12, 14},  {14, 17, 15}, {15, 22, 16}}
};

int params_round2[4][4][3] = {
     {{ 1, 5, 17},  {  6,  9, 18},  { 11, 14, 19},  {  0, 20, 20}},
     {{ 5, 5, 21},  { 10,  9, 22},  { 15, 14, 23},  {  4, 20, 24}},
     {{ 9, 5, 25},  { 14,  9, 26},  {  3, 14, 27},  {  8, 20, 28}},
     {{13, 5, 29},  {  2,  9, 30},  {  7, 14, 31},  { 12, 20, 32}}
};

int params_round3[4][4][3] = {
     {{  5,  4, 33},  {  8, 11, 34},  { 11, 16, 35},  { 14, 23, 36}},
     {{  1,  4, 37},  {  4, 11, 38},  {  7, 16, 39},  { 10, 23, 40}},
     {{ 13,  4, 41},  {  0, 11, 42},  {  3, 16, 43},  {  6, 23, 44}},
     {{  9,  4, 45},  { 12, 11, 46},  { 15, 16, 47},  {  2, 23, 48}}
};

int params_round4[4][4][3] = {
     {{  0,  6, 49},  {  7, 10, 50},  { 14, 15, 51},  {  5, 21, 52}},
     {{ 12,  6, 53},  {  3, 10, 54},  { 10, 15, 55},  {  1, 21, 56}},
     {{  8,  6, 57},  { 15, 10, 58},  {  6, 15, 59},  { 13, 21, 60}},
     {{  4,  6, 61},  { 11, 10, 62},  {  2, 15, 63},  {  9, 21, 64}}
};

#define ROUND(X, A, B, C, D) (md5_round##X(source, &state->A, &state->B, &state->C, &state->D, \
        params_round##X[i][j][0], params_round##X[i][j][1], params_round##X[i][j][2]))

void State_iterate(State *state, Source *source)
{
  State previous = *state;
  int i, j;

  // Round 1
  for (i = 0; i < 4; i++)
  {
    for (j = 0; j < 4; j++) { ROUND(1, A, B, C, D); }

    for (j = 0; j < 4; j++) { ROUND(1, D, A, B, C); }

    for (j = 0; j < 4; j++) { ROUND(1, C, D, A, B); }

    for (j = 0; j < 4; j++) { ROUND(1, B, C, D, A); }
  }

  // Round 2
  for (i = 0; i < 4; i++)
  {
    for (j = 0; j < 4; j++) { ROUND(2, A, B, C, D); }

    for (j = 0; j < 4; j++) { ROUND(2, D, A, B, C); }

    for (j = 0; j < 4; j++) { ROUND(2, C, D, A, B); }

    for (j = 0; j < 4; j++) { ROUND(2, B, C, D, A); }
  }

  // Round 3
  for (i = 0; i < 4; i++)
  {
    for (j = 0; j < 4; j++) { ROUND(3, A, B, C, D); }

    for (j = 0; j < 4; j++) { ROUND(3, D, A, B, C); }

    for (j = 0; j < 4; j++) { ROUND(3, C, D, A, B); }

    for (j = 0; j < 4; j++) { ROUND(3, B, C, D, A); }
  }

  // Round 4
  for (i = 0; i < 4; i++)
  {
    for (j = 0; j < 4; j++) { ROUND(4, A, B, C, D); }

    for (j = 0; j < 4; j++) { ROUND(4, D, A, B, C); }

    for (j = 0; j < 4; j++) { ROUND(4, C, D, A, B); }

    for (j = 0; j < 4; j++) { ROUND(4, B, C, D, A); }
  }

  state->A += previous.A;
  state->B += previous.B;
  state->C += previous.C;
  state->D += previous.D;
}

int md5(FILE *fd, char output[32])
{
  memset(output, 0, 32);
  return 1;
}

void append_size(Source *s)
{
  ((uint64_t *)s->data)[CHUNK_SIZE_U64 - 1] = s->size;
}

Source_Status Source_read(FILE *fd, Source *s)
{
  assert(Source_continue(s));

  // if we have some overflow from the previous read
  if (s->status == PADDING_CHUNK)
  {
    memset(s->data, 0, sizeof(s->data));
    append_size(s);
    s->status = DONE;
    return 1;
  }

  size_t sz_read = fread(s->data, 1, CHUNK_SIZE, fd);
  if (ferror(fd))
  {
    perror("[source_read] ");
    s->status = ERROR;
    return ERROR;
  }
  s->size += sz_read;
  s->status = READING;

  // We read the buffer completely
  if (sz_read == CHUNK_SIZE)
  {
    return s->status;
  }

  // We read just enough to have enough space to spare for the size
  if (sz_read < MAX_READ)
  {
    // Incomplete chunk, fill padding with 0
    memset((unsigned char *)s->data + sz_read, 0, CHUNK_SIZE - sz_read);
    // set first bit after the data to 1
    ((unsigned char *)s->data)[sz_read] = BYTE_10000000;
    append_size(s);
    s->status = DONE;
    return s->status;
  }

  // We read too much: We will need to zero the remaining data,
  // set the padding bits, and write the size on the next chunk
  memset(s->data + sz_read, 0, CHUNK_SIZE - sz_read);
  ((unsigned char *)s->data)[sz_read] = BYTE_10000000;
  s->status = PADDING_CHUNK;
  return s->status;
}

void State_to_md5(State* state, char* md5) {
  snprintf(md5, 33, "%08x%08x%08x%08x", state->A, state->B, state->C, state->D);
}
