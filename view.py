from PIL import Image, ImageTk
import tkinter

class ViewGUI:
    def __init__(self, view_size=400):
        self.view_size = view_size
        self._root = tkinter.Tk()
        self._root.geometry("+%d+%d" % (300, 300))
        self._root.geometry("%dx%d" % ((self.view_size + 20) * 3, self.view_size + 20 + self.view_size))

    def draw(self, image, position):
        global tkpi
        tkpi = [0,1,2,3,4,5]
        if not position:
            position = (0, 0)
        grid = (position[0] + 1) * position[1]
        image = image.copy()
        image.thumbnail((self.view_size, self.view_size))
        if image.size[0] > self.view_size or image.size[1] > self.view_size:
            image.thumbnail((self.view_size, self.view_size), Image.ANTIALIAS)

        tkpi[grid] = ImageTk.PhotoImage(image)
        label_image = tkinter.Label(self._root,
            image=tkpi[grid],
            compound=tkinter.TOP)
        label_image.place(
            x=(self.view_size + 20) * position[0] + 10,
            y=(self.view_size + 20) * position[1] + 10,
            width=self.view_size,
            height=self.view_size + 10)
        self._root.update()

    def destroy(self):
        self._root.destroy()
