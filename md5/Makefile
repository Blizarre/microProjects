HEADERS = *.h
CFLAGS += -pedantic -Wall -Werror
CFLAGS += -ggdb -O0
#CFLAGS += -O3 -DNDEBUG

ALL: md5

.PHONY: clean test

%.o: %.c $(HEADERS)
	$(CC) -c -o $@ $< $(CFLAGS)

testtool: testtool.o lib.o
	$(CC) -o $@ $^ $(LDFLAGS)

test: testtool
	./testtool

md5: md5.o lib.o
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f *.o test md5