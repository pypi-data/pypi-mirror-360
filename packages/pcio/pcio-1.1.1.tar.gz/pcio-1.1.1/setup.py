#!/usr/bin/env python3

from setuptools import setup, Extension

setup(
	name = "pcio",
	version = "1.1.1",
	ext_modules = [Extension("pcio", ["src/bind.c", "src/libinput.c", "src/libprint.c"], include_dirs=["src"], extra_compile_args=["-O2"])]
        
)
