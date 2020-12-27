HEADERS = *.h
CFLAGS += -pedantic -Wall -Werror -std=c99
# Quick release/test flag switch. The testtool binary will not build is used with
# the RELEASE flags as it also disable the asserts and some variables are no longer
# used anywhere. That's for your own good.
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
