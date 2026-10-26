CC = gcc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -Wno-unused-label

.PHONY: all sim clean
all: sim

sim: dct.exe
	./dct.exe

dct.exe: dct.c dct_test.c
	$(CC) $(CFLAGS) dct.c dct_test.c -o $@

clean:
	$(RM) dct.exe *.o
