#!/bin/bash

source pypi_build/py_versions.sh

sdist="--sdist"

for pyver in $PYVERS
do
  docker run --rm -v $(pwd):/io -v /home/erik.vonreis/projects/rust:/rust -w /io dtt-build:deb uv build $sdist --wheel --python=$pyver --out-dir wheels
  sdist=""
done

