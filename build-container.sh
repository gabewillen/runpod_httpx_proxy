#!/bin/bash

# Build for x86_64 architecture
docker build --platform linux/amd64 -t gwillen/runpod-httpx-proxy:${1} .

if [ "$2" == "--push" ]; then
    docker push gwillen/runpod-httpx-proxy:${1}
fi
