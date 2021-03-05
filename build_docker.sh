#!/bin/bash
VERSION="1.0.0"

echo "Building smart-gate docker version:$VERSION"
docker build \
    --build-arg VERSION=$VERSION \
    -t smart-gate:$VERSION \
    -t smart-gate:latest \
    --no-cache \
    - < Dockerfile
