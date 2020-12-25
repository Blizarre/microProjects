#include "md5.h"

int main(int argc, char **argv)
{
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
      Source_read(fd, &s);
      State_init(&state);
      State_iterate(&state, &s);
    }
    char md5[33];
    State_to_md5(&state, md5);
    printf("%s  %s\n", md5, argv[i]);

  }
  return 0;
}
