#!/bin/bash -eu
pip3 install --ignore-requires-python . atheris==3.0.0
compile_python_fuzzer .clusterfuzzlite/fuzzer.py
