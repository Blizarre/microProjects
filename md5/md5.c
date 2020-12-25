#include "md5.h"

int main(int argc, char **argv)
{
  printf("Number of files: %d\n", argc - 1);
  Source s;
  State state;
  for (int i = 1; i < argc; i++)
  {
    Source_init(&s);
    FILE *fd = fopen(argv[i], "r");
    if (fd == NULL)
    {
      perror("[main] ");
      return 1;
    }

    State_init(&state);
    while (Source_continue(&s))
    {
      printf("Chunk: %d", s.status);
      Source_read(fd, &s);
      State_init(&state);
      State_iterate(&state, &s);
    }
  }
  return 0;
}
