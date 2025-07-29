#!/bin/bash
# build wheel file in a container
# pass it a python version

pyver=$1

uv build --wheel --python=$pyver --out-dir wheels
