
from PIL import Image, ImageDraw
import numpy
import face_recognition

class ImageProcessor:
    def __init__(self, image=None, filename=None, processing=1024, convert=None):

        if image:
            self._original = image
        if filename:
            self._original = Image.open(filename)
        if not hasattr(self, '_original'):
            raise Exception("Image or filename missing")

        self.image = self._original.copy()
        self._processing = processing

    @property
    def numpy(self):
        if not hasattr(self, '_numpy'):
            small_image = self.image.copy().convert("RGB")
            self._processing_ratio = self._processing / max(small_image.size)
            small_image = small_image.resize((
                int(small_image.size[0] * self._processing_ratio),
                int(small_image.size[1] * self._processing_ratio)))
            self._numpy = numpy.array(small_image)
        return self._numpy

    @property
    def faces(self):
        if not hasattr(self, "_faces"):
            faces = face_recognition.face_locations(self.numpy)
            self._faces = self.fix_ratio(faces)
        return self._faces

    @faces.setter
    def faces(self, faces):
        self._faces = faces

    def fix_ratio(self, areas, ratio=None):
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
        self.image = self._original.copy()
        self.image = self.image.resize((int(self.image.size[0]/ ratio),
                                        int(self.image.size[1]/ ratio)))

    def add_mask(self, mask, location=None, align=True):
        if not location:
            location = self.faces[0]

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
        "Draws rectangle in thumbnail"
        if len(areas):
            draw = ImageDraw.Draw(self.image)
            for area in areas:
                 for i in range(width):
                     draw.rectangle([area[3] - i ,area[0] - i, area[1] - i, area[2] - i],
                                    outline=outline, fill=fill)


    def find(self, needles, rotate=False):
        faces = face_recognition.face_locations(self.numpy)
        if len(faces):
            encodings = face_recognition.face_encodings(self.numpy, faces)
            for idx, encoding in enumerate(encodings):
                matches = face_recognition.compare_faces(needles, encoding)
                if len(matches) :
                    return faces[idx]

    def rotate(self):
        self.image = self.image.rotate(-90, expand=True)
        self._numpy = None

    def extract(self, face):
        image = self.image.copy()
        print(" crop %s / %s" % (str((face[3], face[0], face[1], face[2])), str(image.size)))
        return image.crop(face)
