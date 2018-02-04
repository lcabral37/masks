
from PIL import Image, ImageDraw
import numpy
import face_recognition

class ImageProcessor:
    "Contains sevelral methods to processes into finding faces within"
    def __init__(self, image=None, nparray=None, filename=None, processing=1024):
        """class constructor
        The constructor requires either the filename, image, or nparray to be given as argument.

        Keyword arguments:
        filename -- the path to an image file
        image -- an PIL.Image object
        nparray -- a nparray
        processing - size of image to be used for processing (default 1024)
        """
        if filename:
            self._original = Image.open(filename)
        elif image:
            self._original = image
        elif not nparray is None:
            self._original = Image.fromarray(nparray)

        if not hasattr(self, '_original'):
            raise Exception("Image or filename missing")

        self.image = self._original.copy()
        self._processing = processing

    @property
    def processing_nparray(self):
        """The nparray used for processing.
        This is a resized version of the image so processing can be made faster.
        """
        if not hasattr(self, '_numpy'):
            small_image = self.image.copy().convert("RGB")
            self._processing_ratio = self._processing / max(small_image.size)
            small_image = small_image.resize((
                int(small_image.size[0] * self._processing_ratio),
                int(small_image.size[1] * self._processing_ratio)))
            self._numpy = numpy.array(small_image)
        return self._numpy

    def nparray(self):
        """ The image nparray
        """
        self.image.convert("RGB")
        return numpy.array(self.image)

    @property
    def faces(self):
        """ Returns an array of bounding boxes of human faces in a image
        """
        if not hasattr(self, "_faces"):
            faces = face_recognition.face_locations(self.processing_nparray)
            self._faces = self.fix_ratio(faces)
        return self._faces

    @faces.setter
    def faces(self, faces):
        """ Sets an array of bounding boxes of human faces.
        This is used to override the automated method or to be used when the automated method
        fails to return
        """
        self._faces = faces

    def fix_ratio(self, areas, ratio=None):
        """Fixes the ratio of bounding areas.
        As processing of images is done on a resized version, this is coommonly used to
        resize the boundary boxes to the original image sise

        Keyword arguments:
        areas -- the boundary areas to rezise
        ratio -- the ratio to use to resie the boxes (default is the ratio of the
            image vs the processing image size)
        """
        fixed = []
        if not ratio:
            ratio =  self._processing_ratio
        for area in areas:
            fixed.append((
                int(area[0] / ratio),
                int(area[1] / ratio),
                int(area[2] / ratio),
                int(area[3] / ratio)
            ))
        return fixed

    def resize(self, ratio):
        """Resizes the image

        Keyword arguments:
        ratio -- the ratio to use
        """
        self.image = self._original.copy()
        self.image = self.image.resize((int(self.image.size[0]/ ratio),
                                        int(self.image.size[1]/ ratio)))

    def add_mask(self, mask, location=None, align=True):
        """Adds a overlay image in the given locations.

        Keyword arguments:
        mask -- the overlay image to be used as mask
        location -- a boundary location wher to place the mask image (default the first face found within the image)
        align -- aligns the face location found in the mask with the given location  (default True)
        """
        if not location:
            location = self.faces[0]

        if not len(mask.faces):
            mask.faces = [(0, mask.image.size[0], mask.image.size[1], 0)]
        mask_location = mask.faces[0]

        location_size = max([location[1] - location[3],
                             location[2] - location[0]])
        mask_size = max([mask_location[1] - mask_location[3],
                         mask_location[2] - mask_location[0]])
        ratio = mask_size / location_size
        mask.resize(ratio)

        if align:
            location = (location[3] - int(mask_location[3] /ratio),
                        location[0] - int(mask_location[0] /ratio))
        else:
            location =  (location[3], location[0])
        self.image.paste(mask.image, location, mask.image)

    def draw(self, areas, outline=128, fill=None, width=5):
        """Draws rectangle in thumbnail
        It allows setting a thickness so the ractangle are still visible when resizing occurs

        Keyword arguments:
        areas -- boudary locations where to draw rectangles
        outline -- the color of the border (default red)
        fill -- the rectangle fill (default None)
        width -- thickness of the border (default 5)
        """
        if len(areas):
            draw = ImageDraw.Draw(self.image)
            for area in areas:
                 for i in range(width):
                     draw.rectangle([area[3] - i ,area[0] - i, area[1] - i, area[2] - i],
                                    outline=outline, fill=fill)


    def find(self, needles):
        """Finds specific faces within the image

        Keyword arguments:
        needles -- a list of known face encodings
        """
        faces = face_recognition.face_locations(self.processing_nparray)
        if len(faces):
            encodings = face_recognition.face_encodings(self.processing_nparray, faces)
            for idx, encoding in enumerate(encodings):
                matches = face_recognition.compare_faces(needles, encoding)
                if len(matches) :
                    return faces[idx]

    def rotate(self, degrees = -90):
        """Rotates the images

        Keyword arguments:
        degrees -- derees to rotate (default -90)
        """
        self.image = self.image.rotate(degrees, expand=True)
        self._numpy = None

    def extract(self, area):
        """ Crops the given area from the image

        Keyword arguments:
        area -- boundary area to crop
        """
        image = self.image.copy()
        return image.crop(area)
