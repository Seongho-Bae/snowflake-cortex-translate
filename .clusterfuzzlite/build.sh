#!/bin/bash -eu
pip3 install --require-hashes -r .clusterfuzzlite/requirements-fuzz.txt
pip3 install --ignore-requires-python .
compile_python_fuzzer .clusterfuzzlite/fuzzer.py
