#!/usr/bin/env python3

import os
import sys
from setuptools import setup

SCRIPTDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(SCRIPTDIR, "src")))

with open(os.path.join(SCRIPTDIR, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
                             name = "jsonexpr",
                      description = "An expression language.",
                          version = "0.2.4",
                          license = "Apache 2.0",
                           author = "Mark Kim",
                     author_email = "markuskimius+py@gmail.com",
                              url = "https://github.com/markuskimius/jsonexpr",
                         keywords = [ "expression", "language", "json" ],
                 long_description = long_description,
    long_description_content_type = "text/markdown",
                         packages = [ "jsonexpr" ],
                      package_dir = { "" : "src" },
                 install_requires = [ "getopts", "wasmtime" ],
                   extras_require = {
                                      "faster"  : ["wasmer", "wasmer_compiler_cranelift"],
                                      "fastest" : ["wasmer", "wasmer_compiler_llvm"],
                                    },
             include_package_data = True,
                          scripts = [ "bin/je" ],
)
