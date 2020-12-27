#include "md5.h"

#include <unistd.h>
#include <memory.h>
#include <string.h>

void State_init(State *s)
{
  s->A = 0x67452301; // little endian for 0x01234567;
  s->B = 0xefcdab89; // 0x89abcdef
  s->C = 0x98badcfe; // 0xfedcba98
  s->D = 0x10325476; // 0x76543210
}


// F(X,Y,Z) = XY v not(X) Z
// G(X,Y,Z) = XZ v Y not(Z)
// H(X,Y,Z) = X xor Y xor Z
// I(X,Y,Z) = Y xor (X v not(Z))

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

// Taken directly from the RFC reference implementation
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

//    /* Round 1. */
//   /* Let [abcd k s i] denote the operation
//        a = b + ((a + F(b,c,d) + X[k] + T[i]) <<< s). */
//   /* Do the following 16 operations. */
//   [ABCD  0  7  1]  [DABC  1 12  2]  [CDAB  2 17  3]  [BCDA  3 22  4]
//   [ABCD  4  7  5]  [DABC  5 12  6]  [CDAB  6 17  7]  [BCDA  7 22  8]
//   [ABCD  8  7  9]  [DABC  9 12 10]  [CDAB 10 17 11]  [BCDA 11 22 12]
//   [ABCD 12  7 13]  [DABC 13 12 14]  [CDAB 14 17 15]  [BCDA 15 22 16]
// Note that T is 1-indexed in the RFC but 0-indexed in C
int params_round1[4][4][3] = {
     {{ 0,  7,  0},  { 1, 12,  1},  {2, 17,  2}, {3, 22,  3}},
     {{ 4,  7,  4},  { 5, 12,  5},  {6, 17,  6}, {7, 22,  7}},
     {{ 8,  7,  8},  { 9, 12,  9},  {10, 17, 10}, {11, 22, 11}},
     {{12,  7, 12},  {13, 12, 13},  {14, 17, 14}, {15, 22, 15}}
};

// Same as above but for round 2
int params_round2[4][4][3] = {
     {{ 1, 5, 16},  {  6,  9, 17},  { 11, 14, 18},  {  0, 20, 19}},
     {{ 5, 5, 20},  { 10,  9, 21},  { 15, 14, 22},  {  4, 20, 23}},
     {{ 9, 5, 24},  { 14,  9, 25},  {  3, 14, 26},  {  8, 20, 27}},
     {{13, 5, 28},  {  2,  9, 29},  {  7, 14, 30},  { 12, 20, 31}}
};

// Same as above but for round 2
int params_round3[4][4][3] = {
     {{  5,  4, 32},  {  8, 11, 33},  { 11, 16, 34},  { 14, 23, 35}},
     {{  1,  4, 36},  {  4, 11, 37},  {  7, 16, 38},  { 10, 23, 39}},
     {{ 13,  4, 40},  {  0, 11, 41},  {  3, 16, 42},  {  6, 23, 43}},
     {{  9,  4, 44},  { 12, 11, 45},  { 15, 16, 46},  {  2, 23, 47}}
};

// Same as above but for round 2
int params_round4[4][4][3] = {
     {{  0,  6, 48},  {  7, 10, 49},  { 14, 15, 50},  {  5, 21, 51}},
     {{ 12,  6, 52},  {  3, 10, 53},  { 10, 15, 54},  {  1, 21, 55}},
     {{  8,  6, 56},  { 15, 10, 57},  {  6, 15, 58},  { 13, 21, 59}},
     {{  4,  6, 60},  { 11, 10, 61},  {  2, 15, 62},  {  9, 21, 63}}
};

// This macro is there to make the the code more readable. It assume that a row variable is available
// which is the row in the param_round variable, and the second argument (col) is the column. if you compile
// with -s you should see that the generated code match what is described in the RFC. I could have used function
// pointers but I feared that the performance coest would have been too high. Thats something to check.
#define ROUND(X, col, A, B, C, D) (md5_round##X(source, &state->A, &state->B, &state->C, &state->D, \
        params_round##X[row][col][0], params_round##X[row][col][1], params_round##X[row][col][2]))

void State_iterate(State *state, Source *source)
{
  State previous = *state;
  int row;

  // Round 1
  for (row = 0; row < 4; row++)
  {
    ROUND(1, 0, A, B, C, D);
    ROUND(1, 1, D, A, B, C);
    ROUND(1, 2, C, D, A, B);
    ROUND(1, 3, B, C, D, A);
  }

  // Round 2
  for (row = 0; row < 4; row++)
  {
    ROUND(2, 0, A, B, C, D);
    ROUND(2, 1, D, A, B, C);
    ROUND(2, 2, C, D, A, B);
    ROUND(2, 3, B, C, D, A);
  }

  // Round 3
  for (row = 0; row < 4; row++)
  {
    ROUND(3, 0, A, B, C, D);
    ROUND(3, 1, D, A, B, C);
    ROUND(3, 2, C, D, A, B);
    ROUND(3, 3, B, C, D, A);
  }

  // Round 4
  for (row = 0; row < 4; row++)
  {
    ROUND(4, 0, A, B, C, D);
    ROUND(4, 1, D, A, B, C);
    ROUND(4, 2, C, D, A, B);
    ROUND(4, 3, B, C, D, A);
  }

  state->A += previous.A;
  state->B += previous.B;
  state->C += previous.C;
  state->D += previous.D;
}

void append_size(Source *s)
{
  ((uint64_t *)s->data)[CHUNK_SIZE_U64 - 1] = s->size * 8; // We write the number of bits as a 64-bit value
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

  // Incomplete chunk, create padding (zeros except the first bit set to 1)
  memset((unsigned char *)s->data + sz_read, 0, CHUNK_SIZE - sz_read);
  ((unsigned char *)s->data)[sz_read] = BYTE_10000000;
  // We read just enough to have enough space to spare for the size
  if (sz_read < MAX_READ)
  {
    append_size(s);
    s->status = DONE;
    return s->status;
  }

  // We read too much: We need to write the size on the next chunk
  s->status = PADDING_CHUNK;
  return s->status;
}

// print the number in hex, littel-endian style
void sprintf_u32_le(uint32_t number, char* hash) {
  int i;
  for(i=0; i<sizeof(uint32_t); i++) {
    snprintf(hash + 2 * i, 3, "%02x", (number >> 8*i) & 0xff);
  }
}

// Write the A, B, C, D in that order, but in little-endian mode (reversed)
void State_to_hash(State* state, char* hash) {
  sprintf_u32_le(state->A, hash);
  sprintf_u32_le(state->B, hash + 2 * 1 * sizeof(uint32_t)); // 2 char for each byte x 1 x 4 bytes for a single uint32
  sprintf_u32_le(state->C, hash + 2 * 2 * sizeof(uint32_t)); // 2 char for each byte x 2 x 4 bytes
  sprintf_u32_le(state->D, hash + 2 * 3 * sizeof(uint32_t)); // 2 char for each byte x 3 x 4 bytes
}

// Check for either the ERROR or DONE value. TODO: Make the interface less tied to the internals
Source_Status md5(char* hash, FILE* fd) {
  Source source;
  State state;
  Source_Status status;

  Source_init(&source);

  State_init(&state);
  while (Source_continue(&source))
  {
    status = Source_read(fd, &source);
    if(status == ERROR) {
      return status;
    }
    State_iterate(&state, &source);
  }
  State_to_hash(&state, hash);
  return DONE;
}