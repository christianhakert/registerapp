#!/bin/bash

docker pull debian:buster
docker build . --platform linux/amd64 -t bap_cnt

docker run -v $(pwd)/..:/mnt --platform linux/amd64 bap_cnt /bin/bash -c "cd /mnt && python3 bap/analysis.py"