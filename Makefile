default: main

main: main.c
	aarch64-linux-gnu-gcc -o main -static main.c

.PHONY: clean docker run console
clean:
	rm -f main
	rm -rf m5out

docker:
	./compile_in_docker.sh

run:
	~/repos/registergem5/build/ARM/gem5.opt ~/repos/registergem5/configs/regcpu.py $(realpath main)

console:
	docker run -it -v $$(pwd):/mnt reg_bld_ctr bash