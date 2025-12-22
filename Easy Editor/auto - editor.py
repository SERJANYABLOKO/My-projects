from PIL import Image, ImageFilter, ImageEnhance
import os, shutil

class Editor:
    def __init__(self, filename):
        self.filename = filename
        self.original = Image.open(self.filename)
        self.history = [self.original]
    def gray(self):
        image_gray = self.history[-1].convert('L')
        self.history.append(image_gray)
    def save(self):
        self.history[-1].save(f'my_image{len(self.history)-1}.png')
    def rotate(self):
        image_pick_up = self.history[-1].transpose(Image.ROTATE_90)
        self.history.append(image_pick_up)
    def mirror(self):
        image_mirror = self.history[-1].transpose(Image.FLIP_LEFT_RIGHT)
        self.history.append(image_mirror)
    def do_cropped(self):
        box = (100, 100, 400, 450)
        cropped = self.history[-1].crop(box)
        self.history.append(cropped)
    def save_all(self):
        if os.path.exists('images'):
            shutil.rmtree('images')
        os.mkdir('images')
        for i, image in enumerate(self.history):
            image.save(f'images/image_{i}.png')




editor = Editor('image.png')
editor.mirror()
editor.gray()
editor.save()
editor.save_all()