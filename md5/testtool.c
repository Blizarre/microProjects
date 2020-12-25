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


int testSimpleCaseSourceRead() {

  //. Simple case: data is much smaller than 512 bits.
  char* data1 = "Hello World";
  FILE* fd1 = create_test_file(data1, 11);

  Source s;
  Source_init(&s);
  assert(Source_continue(&s));
  Source_read(fd1, &s);
  assert(!Source_continue(&s));
  assert(s.size == 11);
  assert(((unsigned char*)s.data)[11] == BYTE_10000000);

  State state;
  State_init(&state);
  State_iterate(&state, &s);
  char md5[32];
  State_to_md5(&state, &md5[0]);
  assert(strcmp(md5, "b10a8db164e0754105b7a99be72e3fe5") == 0);

  printf("[testSimpleCaseSourceRead] OK\n");
  return 1;
}

int main() {
  testSimpleCaseSourceRead();

  printf("All tests ok");
}