#!/usr/bin/env python3

import argparse
import face_recognition
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
import numpy
import tkinter
import time
from imageProcessor import ImageProcessor

test= 50
VIEW_SIZE = 400

class View:
    def __init__(self):
        self._root = tkinter.Tk()
        self._root.geometry("+%d+%d" % (300, 300))
        self._root.geometry("%dx%d" % ((VIEW_SIZE + 20) * 3, VIEW_SIZE + 20 + VIEW_SIZE))

    def draw(self, image, position):
        global tkpi
        tkpi = [0,1,2,3,4,5]
        if not position:
            position = (0, 0)
        grid = (position[0] + 1) * position[1]
        image = image.copy()
        image.thumbnail((VIEW_SIZE, VIEW_SIZE))
        if image.size[0] > VIEW_SIZE or image.size[1] > VIEW_SIZE:
            image.thumbnail((VIEW_SIZE, VIEW_SIZE), Image.ANTIALIAS)

        tkpi[grid] = ImageTk.PhotoImage(image)
        label_image = tkinter.Label(self._root,
            image=tkpi[grid],
        #    text=self.filename,
            compound=tkinter.TOP)
        label_image.place(
            x=(VIEW_SIZE + 20) * position[0] + 10,
            y=(VIEW_SIZE + 20) * position[1] + 10,
            width=VIEW_SIZE,
            height=VIEW_SIZE + 10)
        self._root.update()

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
    root.destroy()

print("Parsing needle")

view = View()
known = ImageProcessor(filename=get_source())
view.draw(known.image, (1, 0))
locations = known.faces
known_faces  = [face_recognition.face_encodings(known.numpy)]
known.draw(locations)
view.draw(known.image, (0, 0))

#view.draw(known_photo.thumbnail, (0, 0))
#view.draw(known_photo.extract(location[0]), (0, 1))

view._root.after(1000, parse_folder)
view._root.mainloop()
