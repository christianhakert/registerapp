#!/bin/bash

docker pull debian:latest
docker build . -t reg_bld_ctr
docker run -it -v $(pwd):/mnt reg_bld_ctr bash -c "cd /mnt && make"