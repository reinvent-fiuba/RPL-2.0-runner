# Flags del compilador y de Valgrind.
CC := gcc
CFLAGS := -g -O2 -std=c99 -Wall -Wformat=2
CFLAGS += -Wshadow -Wpointer-arith -Wunreachable-code
CFLAGS += -Wconversion -Wno-sign-conversion -Wbad-function-cast
CFLAGS += -DCORRECTOR
VALGRIND = valgrind --leak-check=full --track-origins=yes --show-reachable=yes --error-exitcode=2

ARCHIVOS = $(wildcard *.c)

main: $(ARCHIVOS:.c=.o)
	$(CC) -o $@ $^

clean:
	rm -f main *.o *.d

.PHONY: main clean