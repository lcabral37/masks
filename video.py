#!/usr/bin/env python3

import imageio
from imageProcessor import ImageProcessor
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("video")
parser.add_argument("mask")
parser.add_argument("output")
parser.add_argument("--processing", default=1024,
    help="Size of the processing image (512,1024,20148) the smaller the faster")
parser.add_argument("--mask-boundary",
    help="The boundary for the mask \"top,right,bottom,left\"")
args = parser.parse_args()

reader = imageio.get_reader(args.video)
fps = reader.get_meta_data()["fps"]

print("Loading image '%s' %d" % (args.mask, args.processing))
mask = ImageProcessor(filename=args.mask, processing=args.processing)
print(args)
if args.mask_boundary:
    boundaries=args.mask_boundary.split(",")
    mask.faces = [(int(boundaries[0]), int(boundaries[1]), int(boundaries[2]), int(boundaries[3]))]
elif not len(mask.faces):
    print("Could not detect face boundary in mask area")
    mask.faces = [(0, mask.image.size[0], mask.image.size[1], 0)]

print ("Writting video to %s" % args.output)
writer = imageio.get_writer(args.output, fps=fps)
faces = None
counter = 1
failed = 0
missed = 0
for im in reader:
    if counter % 10 == 0:
        print(counter)
    try:
        image = ImageProcessor(nparray=im, processing=args.processing)
        if not len(image.faces) and not faces is None:
            image.faces = faces
            missed = missed + 1
            image.add_mask(mask)
            image.draw(image.faces)
        elif len(image.faces):
            faces = image.faces
            image.add_mask(mask)
        writer.append_data(image.nparray())
    except IndexError as error:
        failed = failed +1
        writer.append_data(im)
        print ("%d failed: %s" % (counter, str(error)))
    counter = counter + 1

writer.close()

print ("Missed/failed/Total: %d/%d/%d" %(missed, failed, counter))
