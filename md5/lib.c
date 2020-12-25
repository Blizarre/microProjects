
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

void md5_round(Source *source, State *state, uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d, int k, int s, int i)
{
  *a = *b + ((*a + F(*b, *c, *d) + source->data[k] + T[i]) << s);
}

void State_iterate(State *state, Source *source)
{
  //State previous = *s;
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
