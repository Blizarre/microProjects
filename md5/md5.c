#include "md5.h"

int main(int argc, char **argv)
{
  for (int i = 1; i < argc; i++)
  {
    FILE *fd = fopen(argv[i], "r");
    if (fd == NULL)
    {
      perror("[main] ");
      return 1;
    }

    char hash[33];
    md5(hash, fd);
    printf("%s  %s\n", hash, argv[i]);
  }
  return 0;
}
