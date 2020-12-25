HEADERS: *.h
CFLAGS += -pedantic -ggdb -O0

.PHONY: clean test

ALL: md5

%.o: %.c $(HEADERS)
	$(CC) -c -o $@ $^ $(CFLAGS)

testtool: testtool.o lib.o
	$(CC) -o $@ $^ $(LDFLAGS)

test: testtool
	./testtool

md5: md5.o lib.o
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f *.o test md5