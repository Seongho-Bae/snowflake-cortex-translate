#!/bin/bash -eu
pip3 install --ignore-requires-python . atheris
compile_python_fuzzer .clusterfuzzlite/fuzzer.py
