#!/bin/bash -eu
pip3 install . atheris
compile_python_fuzzer .clusterfuzzlite/fuzzer.py
