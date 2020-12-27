HEADERS = *.h
CFLAGS += -pedantic -Wall -Werror -std=c99
# Quick prod/test flag switch. Do not use the prod flag when testing
# as it disable asserts. That's bad. But hey, you did not intend to use
# this lib in production, did you?
CFLAGS_PROD = $(CFLAGS) -O3 -DNDEBUG -march=native
CFLAGS_TEST = $(CFLAGS) -ggdb -Og
LDFLAGS += -std=c11

ALL: md5

.PHONY: clean test

%.o: %.c $(HEADERS)
	$(CC) -c -o $@ $< $(CFLAGS_TEST)

testtool: testtool.o lib.o
	$(CC) -o $@ $^ $(LDFLAGS)

check: testtool
	./testtool

md5: md5.o lib.o
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f *.o testtool md5
