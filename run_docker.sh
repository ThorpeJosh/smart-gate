#!/bin/bash

docker run -d \
    -v ~/.config/smart-gate:/root/.config/smart-gate \
    -v ~/gate-media:/root/gate-media \
    -v ~/pipe:/root/pipe \
    --priveliged -v /dev:/dev \
    smart-gate:latest
