#define _GNU_SOURCE

#include <stdint.h>

#include <stdio.h>
#include <assert.h>
#include <stdlib.h>

#define MAX_READ (448 / 8)
#define MAX_READ_U32 (MAX_READ / sizeof(uint32_t))
#define CHUNK_SIZE (512 / 8)
#define CHUNK_SIZE_U32 (CHUNK_SIZE / sizeof(uint32_t))
#define CHUNK_SIZE_U64 (CHUNK_SIZE / sizeof(uint64_t))

#define BYTE_10000000 ((unsigned char)(1 << 7))

typedef enum {
  NOT_STARTED,
  READING,
  PADDING_CHUNK,
  DONE,
  ERROR,
} Source_Status;

typedef struct {
  uint32_t data[CHUNK_SIZE_U32];
  uint64_t size;
  Source_Status status;
} Source;


typedef struct {
uint32_t A;
uint32_t B;
uint32_t C;
uint32_t D;
} State;

// High-level API
Source_Status md5(char* hash, FILE* fd);

void State_init(State *s);
void Source_init(Source* s);
int Source_continue(Source* s);
Source_Status Source_read(FILE* fd, Source* s);
void State_iterate(State * state, Source * source);
void State_to_hash(State*, char*);
