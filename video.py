#!/usr/bin/env python3

import imageio
from imageProcessor import ImageProcessor
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('video')
parser.add_argument('mask')
parser.add_argument('output')
args = parser.parse_args()

reader = imageio.get_reader(args.video)
fps = reader.get_meta_data()['fps']

print("Loading image '%s'" % args.mask)
mask = ImageProcessor(filename=args.mask, processing=1024)

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
        image = ImageProcessor(nparray=im, processing=1204)
        if not len(image.faces) and not faces is None:
            image.faces = faces
            missed = missed + 1
            image.add_mask(mask)
            image.draw(image.faces)
        elif len(image.faces):
            faces = image.faces
            image.add_mask(mask)
        #print("%5d: %s" % (counter, str(image.faces)))
        #image.draw(image.faces)
        writer.append_data(image.nparray())
    except IndexError:
        failed = failed +1
        writer.append_data(im)
        print ("%d failed" % counter)
    counter = counter + 1

writer.close()

print ("Missed/failed/Total: %d/%d/%d" %(missed, failed, counter))
