FROM debian:latest

RUN bash -c "apt -y update"
RUN bash -c "apt -y install gcc-aarch64-linux-gnu"
RUN bash -c "apt -y install gdb"
RUN bash -c "apt -y install python3"
RUN bash -c "apt -y install make"
RUN bash -c "apt -y install less"