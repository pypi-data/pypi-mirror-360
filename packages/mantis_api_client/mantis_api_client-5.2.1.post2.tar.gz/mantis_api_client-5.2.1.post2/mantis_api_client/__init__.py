#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import threading
from pathlib import Path

# Component version
__version__ = "4.8.0"

# Remove incompatible env variable
os.environ.pop("USE_PERMISSIONS", None)

# Get component full version from file generated at build time
current_file_dir = Path(__file__).resolve().parent
fullversion_file = Path(current_file_dir, "fullversion.txt")
if os.path.isfile(fullversion_file):
    __fullversion__ = open(fullversion_file, "r").read().strip()
else:
    __fullversion__ = __version__

shutil_make_archive_lock = threading.Lock()
