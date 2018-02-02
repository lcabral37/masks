#!/usr/bin/env python3

import argparse
import json
import os
from imageProcessor import ImageProcessor

processing = 1024

parser = argparse.ArgumentParser()
parser.add_argument('image')
parser.add_argument('mask')
parser.add_argument('output')
args = parser.parse_args()
print("Loading image '%s'" % args.image)
image = ImageProcessor(filename=args.image, convert="RGB", processing=processing)

print("Loading image '%s'" % args.mask)
mask = ImageProcessor(filename=args.mask, processing=processing)

if os.path.isfile(args.mask + ".json"):
    data = json.load(open(args.mask + ".json"))
    print("Loading mask location from file...")
    mask.faces = [(data['face'][0], data['face'][1], data['face'][2], data['face'][3])]

image.add_mask(mask)

print("writting output file: %s" % args.output)
image.image.save(args.output)
