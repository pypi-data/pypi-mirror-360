__copyright__ = "Copyright 2024-2025 Mark Kim"
__license__ = "Apache 2.0"
__version__ = "0.2.4"
__author__ = "Mark Kim"

import importlib.util

#
# Import the wasmer version if available (it's faster) otherwise import the
# wasmtime version (it's more widely available)
#
if importlib.util.find_spec("wasmer") is not None:
    from .je_wasmer import *
else:
    from .je_wasmtime import *


# vim:ft=python:
