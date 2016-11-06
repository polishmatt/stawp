#!/usr/bin/python3

import sys
import build

dist = sys.argv[2]
if dist is None or dist == "":
    sys.exit(0)
base = sys.argv[1]

try:
    builder = build.Builder(dist=dist, base=base)
    builder.interpret()
    builder.render()
except KeyboardInterrupt:
    print('stopping...')

