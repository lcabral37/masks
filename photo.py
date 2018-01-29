#!/usr/bin/env python3.6

import os
from pathlib import Path

directory = "./source"
counter = 1

pathlist = Path(directory).glob("**/*.jpg")
for filename in pathlist:
    print("%05d: %s" % (counter, filename))
    counter += 1
    continue
