FROM debian:buster

RUN bash -c "apt -y update"
RUN bash -c "apt -y install build-essential"
RUN bash -c "apt -y install wget"

RUN bash -c "apt -y install python3"
RUN bash -c "apt -y install python3-pip"

RUN bash -c "apt -y install libtinfo5"
RUN bash -c "apt -y install libffi6"
RUN bash -c "apt -y install libz3-dev"
RUN bash -c "apt -y install libz3-ocaml-dev"


RUN bash -c "wget https://github.com/BinaryAnalysisPlatform/bap/releases/download/v2.4.0/{bap,libbap,libbap-dev}_2.4.0.deb"
RUN bash -c "dpkg -i {bap,libbap,libbap-dev}_2.4.0.deb"

RUN bash -c "pip3 install bap"