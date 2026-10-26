CC = gcc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -Wno-unused-label

.PHONY: all sim clean
all: sim

sim: yuv_filter.exe
	./yuv_filter.exe

yuv_filter.exe: yuv_filter.c yuv_filter_test.c image_aux.c
	$(CC) $(CFLAGS) yuv_filter.c yuv_filter_test.c image_aux.c -o $@

clean:
	$(RM) yuv_filter.exe *.o
