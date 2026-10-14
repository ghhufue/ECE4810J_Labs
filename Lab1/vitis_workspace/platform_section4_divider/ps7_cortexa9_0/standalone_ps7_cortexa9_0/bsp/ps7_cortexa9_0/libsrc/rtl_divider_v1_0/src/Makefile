COMPILER=
ARCHIVER=
CP=cp
COMPILER_FLAGS=
EXTRA_COMPILER_FLAGS=
LIB=libxil.a

RELEASEDIR=../../../lib
INCLUDEDIR=../../../include
INCLUDES=-I./. -I${INCLUDEDIR}

INCLUDEFILES=$(wildcard *.h)
LIBSOURCES=$(wildcard *.c)
OUTS=$(patsubst %.c,%.o,$(LIBSOURCES))

libs:
	@echo "Compiling rtl_divider..."
ifneq ($(strip $(LIBSOURCES)),)
	$(COMPILER) $(COMPILER_FLAGS) $(EXTRA_COMPILER_FLAGS) $(INCLUDES) $(LIBSOURCES)
	$(ARCHIVER) -r ${RELEASEDIR}/${LIB} ${OUTS}
endif
	$(MAKE) clean

include:
ifneq ($(strip $(INCLUDEFILES)),)
	$(CP) $(INCLUDEFILES) $(INCLUDEDIR)
endif

clean:
	rm -rf $(OUTS)
