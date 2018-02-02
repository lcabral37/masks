#!/usr/bin/env python3

import argparse
import face_recognition
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
import numpy
import tkinter
import time

test= 50
VIEW_SIZE = 400
TOLERANCE = 0.3

class Photo:
    "A object that loads and manipulates a given image"

    parse_size= 1024

    def __init__(self, filename):
        self.filename = filename
        self.load()

    def load(self):
        self._image = Image.open(self.filename)

        self._thumbnail = self._image.copy()
        self._thumbnail.thumbnail((VIEW_SIZE, VIEW_SIZE), Image.ANTIALIAS)

        self.generateNumpy()

    def generateNumpy(self):
        self._numpy = self._image.copy()
        self._numpy.thumbnail((self.parse_size, self.parse_size), Image.ANTIALIAS)
        self._numpy.convert("RGB")
        self._numpy = numpy.array(self._numpy)

    def image(self):
        return self._image

    @property
    def numpy(self):
        return self._numpy

    @property
    def faces(self):
        if not hasattr(self, '_faces'):
            self._faces = face_recognition.face_locations(self._numpy)
        return self._faces

    def display(self, window, grid, *face):
        global tkpi
        if face:
            face = self.fix_ratio([face])
            self._thumbnail = self.draw_rectangles(self._thumbnail, face)
        tkpi[grid] = ImageTk.PhotoImage(self._thumbnail)
        label_image = tkinter.Label(window, image=tkpi[grid], text=self.filename, compound=tkinter.TOP)
        label_image.place(
            x=(VIEW_SIZE + 20) * grid + 10,
            y=10,
            width=VIEW_SIZE,
            height=VIEW_SIZE + 10)
        root.update()

    def draw_rectangles(self, image, faces):
        if len(faces):
            for f in faces:
                draw = ImageDraw.Draw(image)
                draw.rectangle([f[3],f[0], f[1], f[2]], outline=128)
        return image

    def fix_ratio(self, areas, *ratio):
        "Flatens and fixes the rectangles ratios list"
        result = []
        if len(areas):
            if not ratio:
                ratio = VIEW_SIZE / self.parse_size
            for subareas in areas:
                for area in subareas:
                    result.append(
                        (int(ratio * area[0]), int(ratio * area[1]),
                        int(ratio * area[2]), int(ratio * area[3])))
        return result

    def find(self, needles):
        faces = face_recognition.face_locations(self.numpy)
        if len(faces):
            encodings = face_recognition.face_encodings(self.numpy, faces)
            for idx, encoding in enumerate(encodings):
                matches = face_recognition.compare_faces(needles, encoding, TOLERANCE)
                if len(matches) :
                    print("Found at %d" % idx)
                    return faces[idx]

    def rotate(self):
        self._image = self._image.rotate(-90, expand=True)
        self._thumbnail = self._thumbnail.rotate(-90, expand=True)
        self.generateNumpy()
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
                photo = Photo(filename)
                photo.display(root, 1)
                found = photo.find(known_faces)
                if not found:
                    photo.rotate()
                    found = photo.find(known_faces)
                if found:
                    photo.display(root, 2, found)
            except RuntimeError:
                print("Failed %s" % filename)
            except OSError:
                print("Failed %s" % filename)
        else:
            break
    print("Finished analysing %d images" % counter)
    time.sleep(5)
    root.destroy()

tkpi = [0,1,2]
root = tkinter.Tk()
root.geometry("+%d+%d" % (300, 300))
root.geometry("%dx%d" % ((VIEW_SIZE + 20) * 3, VIEW_SIZE + 20 + VIEW_SIZE))

print("Parsing needle")

known_photo = Photo(get_source())
known_photo.display(root, 1)
known_faces  = [face_recognition.face_encodings(known_photo.numpy)]
location = face_recognition.face_locations(known_photo.numpy)
print("known location: %s" % str(location))
known_photo.display(root, 0, location[0])
root.after(500, parse_folder)
root.mainloop()
