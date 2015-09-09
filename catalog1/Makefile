
CC := gcc
CFLAGS := -std=c99

# Path of the so lib after installation:
LIB_PATH := /usr/local/lib/libcatalog1.so
 
# The full path to the directory containing the makefile:
mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
 
# Build everything:
all: libcatalog1 test_catalog1
 
 
# Install the lib libcatalog1.so
install:
	cp ./bin/libcatalog1.so $(LIB_PATH)
 
# Uninstall the lib libcatalog1.so from /usr/lib
uninstall:
	rm -f $(LIB_PATH)
 
clean:
	rm -rf ./bin
 
libcatalog1: bin/libcatalog1.so
 
bin/libcatalog1.so: catalog1.c | bin
	$(CC) -shared -Wl,-soname,libcatalog1.so \
                -o $@ -fPIC $< $(CFLAGS) -O3
 
test_catalog1: bin/test_catalog1
 
bin:
	mkdir -p ./bin
 
bin/test_catalog1: test_catalog1.c bin/libcatalog1.so | bin
	$(CC) $< -o $@ -Lbin -lcatalog1 $(CFLAGS)
 
.PHONY: test_catalog1 libcatalog1 clean uninstall install all
