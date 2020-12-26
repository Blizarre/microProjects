HEADERS = *.h
CFLAGS += -pedantic -Wall -Werror -std=c99
#CFLAGS += -ggdb -O0
CFLAGS += -O3 -DNDEBUG -march=native -mtune=native
LDFLAGS += -std=c11

ALL: md5

.PHONY: clean test lint

%.o: %.c $(HEADERS)
	$(CC) -c -o $@ $< $(CFLAGS)

testtool: testtool.o lib.o
	$(CC) -o $@ $^ $(LDFLAGS)

check: testtool
	./testtool

lint: *.c
	clang-tidy $^ $(CFLAGS)

md5: md5.o lib.o
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f *.o test md5
