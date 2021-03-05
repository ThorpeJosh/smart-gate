#!/bin/bash

docker run -d \
    -v ~/.config/smart-gate:/root/.config/smart-gate \
    -v ~/gate-media:/root/gate-media \
    -v ~/pipe:/root/pipe \
    smart-gate:latest
