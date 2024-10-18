default: main

NUM_REGS := 34

REG_EXCLUDE_LIST := $(shell for i in $$(seq $(NUM_REGS) 63); do echo -n "-ffixed-$$i "; done)
REG_EXCLUDE_LIST := 

main: main.c
	@echo $(REG_EXCLUDE_LIST)
	aarch64-linux-gnu-gcc -O0 $(REG_EXCLUDE_LIST) -o main -static main.c

.PHONY: clean cleanup docker run console run_remote
clean:
	rm -f main
	rm -rf m5out

cleanup: clean
	rm -f main.txt regtrace.csv rtstats.csv shiftresults.csv cfg.pdf cfg.dot

docker:
	./compile_in_docker.sh

run:
	~/repos/registergem5/build/ARM/gem5.opt ~/repos/registergem5/configs/regcpu.py $(realpath main)

run_remote: main
	scp main ls12-nvm-oma1:/media/local/nvm_oma_back/hakert/registerracetrack/.
	ssh ls12-nvm-oma1 tmux new-session -d -s registergem5
	ssh ls12-nvm-oma1 tmux send-keys -t registergem5 "cd\ /media/local/nvm_oma_back/hakert/registerracetrack" C-m
	ssh ls12-nvm-oma1 tmux send-keys -t registergem5 "registergem5/build/ARM/gem5.opt\ registergem5/configs/regcpu.py\ main" C-m

console:
	docker pull debian:latest
	docker build dockerbuild -t reg_bld_ctr
	docker run -it -v $$(pwd):/mnt reg_bld_ctr bash