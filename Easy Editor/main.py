from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QRadioButton, QMessageBox, QTextEdit, QListWidget, QLineEdit
import os, shutil
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import  Qt
from PIL import Image, ImageFilter, ImageEnhance

app = QApplication([])
main_win = QWidget()
main_win.setWindowTitle('Редактор фото')
main_win.resize(800, 600)


btn_files = QPushButton('Папка')
files_list = QListWidget()
picture_text = QLabel('Картинки')
btn_left = QPushButton('Лево')
btn_right = QPushButton('Право')
btn_mirror = QPushButton('Зеркало')
btn_contrast = QPushButton('Контраст')
btn_black = QPushButton('Ч/Б')

Vline_files = QVBoxLayout()
Vline_picture = QVBoxLayout()
Hline_picture = QHBoxLayout()
Hline_btns = QHBoxLayout()

Vline_files.addWidget(btn_files)
Vline_files.addWidget(files_list)
Vline_picture.addWidget(picture_text)
for btn in [btn_left, btn_right, btn_mirror, btn_black, btn_contrast]:
    Hline_btns.addWidget(btn)

Vline_picture.addLayout(Hline_btns)

Hline_picture.addLayout(Vline_files)
Hline_picture.addLayout(Vline_picture, 80)

work_dir = ''


def get_files():
    global work_dir
    work_dir = QFileDialog.getExistingDirectory()
    print(work_dir)
    if work_dir == '':
        return
    files = os.listdir(work_dir)
    files_list.clear()
    for file in files:
        end = file.split('.')[-1]
        if end in ['png', 'jpg', 'eps', 'svg', 'bpm', 'webp']:
            files_list.addItem(file)
def file_path():
    filename = files_list.selectedItems()[0].text()
    # print(f'{work_dir}/{filename}')
    global editor
    editor = Editor(filename = f'{work_dir}/{filename}')
    editor.show_image(editor.filename)

    btn_left.clicked.disconnect()
    btn_left.clicked.connect(editor.rotate)

    btn_right.clicked.disconnect()
    btn_right.clicked.connect(editor.rotate)

    btn_mirror.clicked.disconnect()
    btn_mirror.clicked.connect(editor.mirror)

    btn_contrast.clicked.disconnect()
    btn_contrast.clicked.connect(editor.contrast)

    btn_black.clicked.disconnect()
    btn_black.clicked.connect(editor.gray)

files_list.itemClicked.connect(file_path)

btn_left.clicked.connect(get_files)
btn_right.clicked.connect(get_files)
btn_mirror.clicked.connect(get_files)
btn_contrast.clicked.connect(get_files)
btn_black.clicked.connect(get_files)
btn_files.clicked.connect(get_files)

class Editor:
    def __init__(self, filename):
        self.filename = filename
        self.original = Image.open(self.filename)
        self.history = [self.original]
    def show_image(self, path):
        picture_text.hide()
        image = QPixmap(path)
        w, h = picture_text.width(), picture_text.height()
        image = image.scaled(w, h, Qt.KeepAspectRatio)
        picture_text.setPixmap(image)
        picture_text.show()
    def gray(self):
        image_gray = self.history[-1].convert('L')
        self.history.append(image_gray)
        self.save()
        self.show_image(f'my_image{len(self.history) - 1}.png')
    def save(self):
        self.history[-1].save(f'my_image{len(self.history)-1}.png')
    def blured(self):
        image_blured = self.history[-1].filter(ImageFilter.BLUR)
        self.history.append(image_blured)
    def rotate(self):
        image_pick_up = self.history[-1].transpose(Image.ROTATE_90)
        self.history.append(image_pick_up)
        self.save()
        self.show_image(f'my_image{len(self.history)-1}.png')
    def mirror(self):
        image_mirror = self.history[-1].transpose(Image.FLIP_LEFT_RIGHT)
        self.history.append(image_mirror)
        self.save()
        self.show_image(f'my_image{len(self.history) - 1}.png')
    def contrast(self):
        image_contrast = ImageEnhance.Contrast(self.history[-1])
        image_contrast = image_contrast.enhance(1.5)
        self.history.append(image_contrast)
        self.save()
        self.show_image(f'my_image{len(self.history) - 1}.png')
    def save_all(self):
        if os.path.exists('images'):
            shutil.rmtree('images')
        os.mkdir('images')
        for i, image in enumerate(self.history):
            image.save(f'images/image_{i}.png')
editor = ''


main_win.setLayout(Hline_picture)
main_win.show()
app.exec()
