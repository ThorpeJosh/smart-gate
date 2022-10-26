#!/bin/bash
VERSION="1.0.0"

echo "Building smart-gate docker version:$VERSION"
docker build \
    --build-arg VERSION=$VERSION \
    -t thorpejosh/smart-gate:$VERSION \
    -t thorpejosh/smart-gate:latest \
    --pull \
    --target prod \
    .
    #--platform linux/arm/v7 \
