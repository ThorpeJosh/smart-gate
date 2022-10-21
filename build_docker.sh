#!/bin/bash
VERSION="1.0.0"

echo "Building smart-gate docker version:$VERSION"
docker build \
    --build-arg VERSION=$VERSION \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t thorpejosh/smart-gate:$VERSION \
    -t thorpejosh/smart-gate:latest \
    --platform linux/arm/v7 \
    --cache-from thorpejosh/smart-gate:latest \
    --target prod \
    - < Dockerfile

VERSION="$VERSION-dev"
docker build \
    --build-arg VERSION=$VERSION \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t thorpejosh/smart-gate:$VERSION \
    -t thorpejosh/smart-gate:latest-dev \
    --platform linux/arm/v7 \
    --cache-from thorpejosh/smart-gate:latest \
    --target dev \
    - < Dockerfile
