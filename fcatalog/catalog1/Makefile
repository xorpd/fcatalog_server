CC=gcc
# The full path to the directory containing the makefile:
mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Build everything:
all: catalog1lib test_catalog1


# Install the lib catalog1lib.so
install: 
	cp ./bin/catalog1lib.so /usr/lib/catalog1lib.so

# Uninstall the lib catalog1lib.so from /usr/lib
uninstall:
	rm -f /usr/lib/catalog1lib.so

clean:
	rm -rf ./bin


catalog1lib: catalog1.c
	mkdir -p ./bin
	$(CC) -shared -Wl,-soname,catalog1lib -o ./bin/catalog1lib.so -fPIC catalog1.c -std=c99 -O3

test_catalog1: catalog1lib
	mkdir -p ./bin
	$(CC) test_catalog1.c -o ./bin/test_catalog1 -l:./bin/catalog1lib.so -std=c99


