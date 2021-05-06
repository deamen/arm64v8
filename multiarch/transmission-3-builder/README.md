# transmission-3-builder
Build and copy the transmission-3 artifacts to host.

# Usage:
## arm64v8:
Download the qemu interpreter for arm64v8:
```bash
VER="v5.1.0-5" && wget -c https://github.com/multiarch/qemu-user-static/releases/download/${VER}/qemu-aarch64-static -P bin/ && chmod a+x bin/*
```
Register the qemu interpreters:
```bash
docker run --rm --privileged multiarch/qemu-user-static --reset

```
Start the build:
```bash
DOCKER_BUILDKIT=1 docker build -o out .

```
---
## amd64/x86_64:
Start the build:
```bash
DOCKER_BUILDKIT=1 docker build -o out .

```
The artifacts should appear in the ./out folder after a successfull build.