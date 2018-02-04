#!/usr/bin/env python3

import argparse
import face_recognition
from pathlib import Path
import time
from imageProcessor import ImageProcessor
from view import ViewGUI

test= 50

def get_source():
    parser = argparse.ArgumentParser()
    parser.add_argument('image')
    args = parser.parse_args()

    if args and args.image:
        return args.image
    else:
        return "source.jpg"

def parse_folder():
    directory = "./source"
    counter = 0
    print("Parsing haystach '%s'" % directory)
    pathlist = Path(directory).glob("**/*.jpg")

    for filename in pathlist:
        counter += 1
        if counter < test:
            print("%05d: %s" % (counter, filename))
            try:

                photo = ImageProcessor(filename = filename)
                view.draw(photo.image, (1, 0))
                found = photo.find(known_faces)
                if not found:
                    photo.rotate()
                    found = photo.find(known_faces)
                if found:
                    view.draw(photo.image, (2, 0))
                    face = photo.extract(found)
            except RuntimeError:
                print("Failed %s" % filename)
            except OSError:
                print("Failed %s" % filename)
        else:
            break
    print("Finished analysing %d images" % counter)
    time.sleep(5)
    view.destroy()

print("Parsing needle")

view = ViewGUI()
known = ImageProcessor(filename=get_source())
view.draw(known.image, (1, 0))
locations = known.faces
known_faces  = [face_recognition.face_encodings(known.processing_nparray)]
known.draw(locations)
view.draw(known.image, (0, 0))

#view.draw(known_photo.thumbnail, (0, 0))
#view.draw(known_photo.extract(location[0]), (0, 1))

view._root.after(1000, parse_folder)
view._root.mainloop()
