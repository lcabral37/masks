#!/usr/bin/env python3

import argparse
import face_recognition
from PIL import Image, ImageTk
import numpy
import sys
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument('image')
parser.add_argument('mask')
parser.add_argument('output')
args = parser.parse_args()

print("Loading image '%s'" % args.image)
image = Image.open(args.image)
imageN = image.convert("RGB")
imageN = numpy.array(imageN)
face_location = face_recognition.face_locations(imageN)[0]

print("Found face at: %s" % str(face_location))
face_size = [
    face_location[1] - face_location[3],
    face_location[2] - face_location[0]]

print("Loading image '%s'" % args.image)
mask = Image.open(args.mask)
maskN = mask.copy().convert("RGB")

mask_data_file = args.mask + ".json"
if os.path.isfile(mask_data_file):
    data = json.load(open(mask_data_file))
    print("Loading mask location from file...")
    mask_location = (data['face'][0], data['face'][1], data['face'][2], data['face'][3])
else:
    maskN = numpy.array(maskN)
    mask_location = face_recognition.face_locations(maskN)[0]

print("Resizing mask...")
mask_size = [
    mask_location[1] - mask_location[3],
    mask_location[2] - mask_location[0]]
ratio = max(mask_size) / max(face_size)
print("ratio: %f" % ratio)
mask = mask.resize((int(mask.size[0]/ratio), int( mask.size[1]/ratio)))

mask_location = (int(mask_location[0] /ratio),
    int(mask_location[1] /ratio),
    int(mask_location[2] /ratio),
    int(mask_location[3] /ratio))

print("Mask location: %s" % str(mask_location))

paste_location = (face_location[3] - mask_location[3], face_location[0] - mask_location[0])
print("place mask: %s" % str(paste_location))
image.paste(mask, paste_location, mask)


print("writting output file: %s" % args.output)
image.save(args.output)
