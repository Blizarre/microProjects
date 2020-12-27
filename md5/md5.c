#include "md5.h"

int main(int argc, char **argv)
{
  for (int i = 1; i < argc; i++)
  {
    FILE *fd = fopen(argv[i], "r");
    Source_Status result;
    if (fd == NULL)
    {
      perror("[main] ");
      return 1;
    }

    char hash[33];
    result = md5(hash, fd);
    if(result == ERROR) {
        fprintf(stderr, "Error during processing");
        return 1;
    }
    printf("%s  %s\n", hash, argv[i]);
  }
  return 0;
}
