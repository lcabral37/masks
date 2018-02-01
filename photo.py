#!/usr/bin/env python3

import argparse
import face_recognition
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
import numpy
import tkinter
import time

VIEW_SIZE = 400

class Photo:
    "A object that loads and manipulates a given image"

    parse_size= 1024

    def __init__(self, filename):
        self.filename = filename
        self.load()

    def load(self):
        print_log("Loading photo '%s'" % self.filename)
        self._image = Image.open(self.filename)

        self._thumbnail = self._image.copy()
        self._thumbnail.thumbnail((VIEW_SIZE, VIEW_SIZE), Image.ANTIALIAS)

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

    def display(self, window, grid, *show_faces):
        global tkpi
        thumbnail = self._thumbnail.copy()
        if show_faces:
            faces = self.fix_ratio(self.faces)
            thumbnail = self.draw_rectangles(thumbnail, faces)
        tkpi[grid] = ImageTk.PhotoImage(thumbnail)
        label_image = tkinter.Label(window, image=tkpi[grid], text=self.filename, compound=tkinter.BOTTOM)
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
        result = []
        if len(areas):
            if not ratio:
                ratio = VIEW_SIZE / self.parse_size
                print("ratio: %f" % ratio)
                print(areas[0])
            for area in areas:
                result.append(
                    (int(ratio * area[0]), int(ratio * area[1]),
                    int(ratio * area[2]), int(ratio * area[3]))
                )
        print(result)
        return result

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
    print_log("Parsing haystach '%s'" % directory)
    pathlist = Path(directory).glob("**/*.jpg")

    for filename in pathlist:
        counter += 1
        if counter < 20:
            print_log("%05d: %s" % (counter, filename))
            try:
                photo = Photo(filename)
                photo.display(root, 1)
                encodings = face_recognition.face_encodings(photo.numpy)
                if encodings and face_recognition.compare_faces([known_face], encodings[0]):
                    photo.display(root, 2, True)
            except RuntimeError:
                print_log("Failed %s" % filename)
            except OSError:
                print_log("Failed %s" % filename)
        else:
            break
    print_log("Finished analysing %d images" % counter)
    time.sleep(5)
    root.destroy()

def print_log(text):
    if textBox and text:
        textBox.insert(tkinter.END, text)
        textBox.insert(tkinter.END, "\n")
        root.update()
    print(text)

tkpi = [0,1,2]
root = tkinter.Tk()
root.geometry("+%d+%d" % (300, 300))
root.geometry("%dx%d" % ((VIEW_SIZE + 20) * 3, VIEW_SIZE + 20 + 100))

textBox = tkinter.Text(root)
textBox.place(x=10, y=VIEW_SIZE + 20, height=50, width=VIEW_SIZE * 3)

print_log("Parsing needle")

known_photo = Photo(get_source())
known_photo.display(root, 0)

known_face = face_recognition.face_encodings(known_photo.numpy)
known_photo.display(root, 0, True)
root.after(500, parse_folder)
root.mainloop()
