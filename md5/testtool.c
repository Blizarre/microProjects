#include "md5.h"
#include <sys/mman.h> // for memfd_create
#include <string.h>

FILE* create_test_file(char* data, size_t size) {
  int fd = memfd_create("md5.test", 0);
  if(fd <0) {
    perror("[test] memfd_create");
    exit(1);
  }
  FILE* test = fdopen(fd, "r+");
  if(test == NULL) {
    perror("[test] fopen");
    exit(1);
  }
  fwrite(data, 1, size, test);
  rewind(test);
  return test;
}

// debug data: same output format as https://cse.unl.edu/~ssamal/crypto/genhash.php
void display_data(Source* source) {
  int i;
  for(i=0; i<16;i++) {
    printf("[%d] %u\n", i, source->data[i]);
  }
}


int testZeroLengthData() {
  //. Simple case: no data.
  char* data = "";
  FILE* fd = create_test_file(data, 0);

  Source s;
  Source_init(&s);
  assert(Source_continue(&s));
  Source_read(fd, &s);
  assert(!Source_continue(&s));
  assert(s.size == 0);
  assert(((unsigned char*)s.data)[0] == BYTE_10000000);
  State state;
  State_init(&state);
  State_iterate(&state, &s);
  char hash[32];
  State_to_hash(&state, &hash[0]);
  assert(strcmp(hash, "d41d8cd98f00b204e9800998ecf8427e") == 0);

  fclose(fd);
  printf("[testZeroLengthData] OK\n");
  return 1;
}


int testSingleBlockCase() {
  //. Simple case: data is much smaller than 512 bits.
  char* data = "Hello World";
  FILE* fd = create_test_file(data, 11);

  Source s;
  Source_init(&s);
  assert(Source_continue(&s));
  Source_read(fd, &s);
  assert(!Source_continue(&s));
  assert(s.size == 11);
  assert(((unsigned char*)s.data)[11] == BYTE_10000000);

  State state;
  State_init(&state);
  State_iterate(&state, &s);
  char hash[32];
  State_to_hash(&state, &hash[0]);
  assert(strcmp(hash, "b10a8db164e0754105b7a99be72e3fe5") == 0);

  fclose(fd);
  printf("[testSingleBlockCase] OK\n");
  return 1;
}


int test56CharCase() {
  //. Two block case: data is one byte too large
  char* data = "33333333333333333333333333333333333333333333333333333333";
  FILE* fd = create_test_file(data, 56);

  Source s;
  State state;

  State_init(&state);
  Source_init(&s);
  assert(Source_continue(&s));

  Source_read(fd, &s);
  assert(s.size == 56);
  State_iterate(&state, &s);
  assert(Source_continue(&s));
  assert(((unsigned char*)s.data)[56] == BYTE_10000000);

  Source_read(fd, &s);
  assert(s.size == 56);
  State_iterate(&state, &s);
  assert(!Source_continue(&s));

  char hash[32];
  State_to_hash(&state, &hash[0]);
  assert(strcmp(hash, "c78c9691eb9c21200f66024da3232619") == 0);

  fclose(fd);
  printf("[test56CharCase] OK\n");
  return 1;
}

int testTwoBlockCase() {
  //. Two block case: data fit in 2 512 bits blocks.
  char* data = "01234567689012345676890123456768901234567689012345676890123456768901234567689";
  FILE* fd = create_test_file(data, 77);

  Source s;
  State state;

  State_init(&state);
  Source_init(&s);
  assert(Source_continue(&s));

  Source_read(fd, &s);
  assert(s.size == 64);
  State_iterate(&state, &s);
  assert(Source_continue(&s));

  Source_read(fd, &s);
  assert(s.size == 77);
  State_iterate(&state, &s);
  assert(!Source_continue(&s));

  assert(((unsigned char*)s.data)[13] == BYTE_10000000);

  char hash[32];
  State_to_hash(&state, &hash[0]);
  assert(strcmp(hash, "0119a2cc7e7502d7ee512d22a293d19e") == 0);

  fclose(fd);
  printf("[testTwoBlockCase] OK\n");
  return 1;
}

int testSingleBlockExtraPaddingCase() {
  //. Two block case: data fit in a single 512 bits block, but is too large to fit the length

  char* data = "01234567890123456789012345678901234567890123456789012345678";
  FILE* fd = create_test_file(data, 59);

  Source s;
  State state;

  State_init(&state);
  Source_init(&s);
  assert(Source_continue(&s));

  Source_read(fd, &s);
  assert(s.size == 59);
  assert(s.status == PADDING_CHUNK);
  State_iterate(&state, &s);
  assert(Source_continue(&s));
  assert(((unsigned char*)s.data)[59] == BYTE_10000000);

  Source_read(fd, &s);
  assert(s.size == 59);
  State_iterate(&state, &s);
  assert(!Source_continue(&s));
  assert(s.status == DONE);


  char hash[32];
  State_to_hash(&state, &hash[0]);
  assert(strcmp(hash, "ad76b175d22a98a4e3bc2ad72affc53e") == 0);

  fclose(fd);
  printf("[testSingleBlockExtraPaddingCase] OK\n");
  return 1;
}

int test2BlocksExtraPaddingCase() {
  //. Two block case: data fit in two 512 bits block, but is too large to fit the length in the 2 blocks

  char* data = "012345678900123456789001234567890012345678900123456789001234567890012345678900123456789001234567890012345678900123456789";
  FILE* fd = create_test_file(data, 120);

  Source s;
  State state;

  State_init(&state);
  Source_init(&s);
  assert(Source_continue(&s));

  Source_read(fd, &s);
  assert(s.size == 64);
  State_iterate(&state, &s);
  assert(Source_continue(&s));

  Source_read(fd, &s);
  assert(s.size == 120);
  State_iterate(&state, &s);
  assert(Source_continue(&s));
  assert(((unsigned char*)s.data)[56] == BYTE_10000000);
  assert(s.status == PADDING_CHUNK);

  Source_read(fd, &s);

  assert(s.size == 120);
  State_iterate(&state, &s);
  assert(!Source_continue(&s));
  assert(s.status == DONE);
  char hash[32];
  State_to_hash(&state, &hash[0]);
  assert(strcmp(hash, "c7ef963feba90638da5661d7c73cb1ad") == 0);

  fclose(fd);
  printf("[test2BlocksExtraPaddingCase] OK\n");
  return 1;
}

void testFullDataset() {
  FILE* fd = fopen("test.data", "r");
  char expected[32 + 1], generated[32 + 1], data[512]; // NULL char ending
  expected[32] = 0; // null-terminated string
  int size;

  while(1) {
    fread(expected, 32, 1, fd);
    assert(!ferror(fd));
    if(feof(fd)) {
      printf("\n[testFullDataset] OK\n");
      fclose(fd);
      return;
    }

    fread(&size, 4, 1, fd);
    fread(data, size, 1, fd);

    FILE* fd_MD5 = create_test_file(data, size);
    md5(generated, fd_MD5);
    fclose(fd_MD5);
    printf(".");
    fflush(stdout);
    assert(strcmp(generated, expected) == 0);
  }
}

int main() {
  testSingleBlockCase();
  testTwoBlockCase();
  testSingleBlockExtraPaddingCase();
  test2BlocksExtraPaddingCase();
  test56CharCase();
  testZeroLengthData();
  testFullDataset();
  printf("All tests ok");
}
