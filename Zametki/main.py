from PyQt5.QtCore import Qt
import os, json
from database import Database
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QRadioButton,
    QMessageBox,
    QTextEdit,
    QListWidget,
    QLineEdit
)

# Инициализация приложения
app = QApplication([])
main_win = QWidget()
main_win.setWindowTitle('Заметки')
main_win.resize(800, 600)
create_note_win = QWidget()
create_note_win.resize(600, 400)
create_note_win.setWindowTitle('Создайте заметку')

create_note_text = QLineEdit(placeholderText='Введите текст')
create_note_tags = QLineEdit(placeholderText='Введите теги')
notes_ok = QPushButton('Сохранить')
notes_no = QPushButton('Отменить')

create_win_layout = QVBoxLayout()
create_note_win_buttons = QHBoxLayout()
create_note_win.setLayout(create_win_layout)

create_win_layout.addWidget(create_note_text)
create_note_win_buttons.addWidget(notes_ok)
create_note_win_buttons.addWidget(notes_no)
create_win_layout.addWidget(create_note_tags)

create_win_layout.addLayout(create_note_win_buttons)

# Создание основных виджетов
note_text = QTextEdit()

# Создание лейаутов
main_layout = QHBoxLayout()
left_layout = QVBoxLayout()
right_layout = QVBoxLayout()

# Левая часть - поле для заметок
left_layout.addWidget(note_text)

# Правая часть - управление заметками и тегами
# Секция списка заметок
notes_section = QVBoxLayout()
label_notes = QLabel('Список заметок')
notes_list = QListWidget()

# Кнопки управления заметками
notes_buttons = QHBoxLayout()
add_note_btn = QPushButton('Создать заметку')
del_note_btn = QPushButton('Удалить заметку')
notes_buttons.addWidget(add_note_btn)
notes_buttons.addWidget(del_note_btn)


# Кнопка сохранения
save_note_btn = QPushButton('Сохранить заметку')

# Секция управления тегами
tags_section = QVBoxLayout()
label_tags = QLabel('Список тегов')
tags_list = QListWidget()
tag_input = QLineEdit(placeholderText='Введите тег')

# Кнопки управления тегами
tags_buttons = QHBoxLayout()
add_tag_btn = QPushButton('Добавить к заметке')
remove_tag_btn = QPushButton('Открепить от заметки')
tags_buttons.addWidget(add_tag_btn)
tags_buttons.addWidget(remove_tag_btn)

find_tag_btn = QPushButton('Искать по тегу')

# Сборка правой части
right_layout.addWidget(label_notes)
right_layout.addWidget(notes_list)
right_layout.addLayout(notes_buttons)
right_layout.addWidget(save_note_btn)

right_layout.addWidget(label_tags)
right_layout.addWidget(tags_list)
right_layout.addWidget(tag_input)
right_layout.addLayout(tags_buttons)
right_layout.addWidget(find_tag_btn)

# Сборка основного окна
main_layout.addLayout(left_layout)
main_layout.addLayout(right_layout)
main_win.setLayout(main_layout)

def show_message(text):
    victory_win = QMessageBox()
    victory_win.setText(text)
    victory_win.exec_()

def load():
    notes_list.clear()
    tags_list.clear()
    for key in db_data:
        notes_list.addItem(key)
        tags_list.addItems(db_data[key]['теги'])
    find_tag_btn.clicked.disconnect()
    find_tag_btn.clicked.connect(find_tag)
    find_tag_btn.setText('Искать по тегу')
def note_open():
    key = notes_list.selectedItems()[0].text()
    note_text.setText((db_data[key]['текст']))
    tags_list.clear()
    tags_list.addItems(db_data[key]['теги'])
notes_list.itemClicked.connect(note_open)
def show_note_win():
    create_note_win.show()
def save_note_win():
    text = create_note_text.text()
    tags = create_note_tags.text().split(' ')
    db_data[text] = {'текст': '', 'теги': tags}
    db.save_data(db_data)
    load()
    otm_note_win()
notes_ok.clicked.connect(save_note_win)

def set_note_text():
    try:
        key = notes_list.selectedItems()[0].text()
    except:
        show_message('Выберите заметку для сохранения')
        return
    text = note_text.toPlainText()
    db_data[key]['текст'] = text
    db.save_data(db_data)
    tags_list.addItem()

save_note_btn.clicked.connect(set_note_text)

def add_tag():
    text = tag_input.text()
    if len(text) == 0:
        show_message('Нельзя вводить пустой тег!')
        return
    try:
        key = notes_list.selectedItems()[0].text()
    except:
        show_message('Выбери заметку для добавления тега')
        return
    db_data[key]['теги'].append(text)
    db.save_data(db_data)
    create_note_tags.setText('')
    tags_list.addItem(text)
add_tag_btn.clicked.connect(add_tag)

def del_tag():
    try:
        key =  notes_list.selectedItems()[0].text()
    except:
        show_message('Выбери заметку для удаления тега')
        return
    try:
        tag =  tags_list.selectedItems()[0].text()
    except:
        show_message('Выбери тег для удаления тега')
        return
    db_data[key]['теги'].remove(tag)
    db.save_data(db_data)
    create_note_tags.setText('')
    tags_list.clear()
    tags_list.addItems(db_data[key]['теги'])

add_tag_btn.clicked.connect(add_tag)
remove_tag_btn.clicked.connect(del_tag)

add_note_btn.clicked.connect(show_note_win)
def otm_note_win():
    create_note_win.hide()
notes_no.clicked.connect(otm_note_win)
def del_note():
    try:
        key = notes_list.selectedItems()[0].text()
    except:
        show_message('Выберите заметку для удаления')
        return
    del db_data [key]
    db.save_data(db_data)
    load()
del_note_btn.clicked.connect(del_note)
def find_tag():
    try:
        tag = tags_list.selectedItems()[0].text()
    except:
        show_message('Выбери тег для поиска заметок')
        return
    notes_list.clear()
    for key in db_data:
        if tag in db_data[key]['теги']:
            notes_list.addItem(key)
    find_tag_btn.clicked.disconnect()
    find_tag_btn.clicked.connect(load)
    find_tag_btn.setText('Вывести все заметки')
find_tag_btn.clicked.connect(find_tag)

db = Database('filename.json')
db_data = db.get_data()

load()

# Отображение окна
main_win.show()
app.exec()