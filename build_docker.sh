#!/bin/bash
VERSION="$(git describe --tags)"

echo "Building smart-gate docker version:$VERSION"
docker build \
    --build-arg VERSION=$VERSION \
    -t thorpejosh/smart-gate:$VERSION \
    -t thorpejosh/smart-gate:latest \
    --pull \
    --target prod \
    .
    #--platform linux/arm/v7 \
