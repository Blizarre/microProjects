HEADERS = *.h
CFLAGS += -pedantic -Wall -Werror -std=c99
# Quick release/test flag switch. NOTE: The testtool binary will not build with
# the RELEASE flags as this flag disable the asserts, which means that some variables
# are no longer used anywhere, which will make $CC fail. It's not good, but you
# didn't really wanted to use that code anywhere right?
CFLAGS_RELEASE = $(CFLAGS) -O3 -DNDEBUG -march=native
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
