from PyQt5.QtCore import Qt
import os, json
from database import Database
import random
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

app = QApplication([])
main_win = QWidget()
main_win.setWindowTitle('Розыгрыш')
main_win.resize(800, 600)

main_layout = QVBoxLayout()



text = QLabel('                                                                                                                    Жми на кнопку!')
number = QListWidget()
button = QPushButton('Получить номер')


main_win.setLayout(main_layout)

main_layout.addWidget(text)
main_layout.addWidget(button)
main_layout.addWidget(number)

def play():
    score = f' ваш номер - {random.randint(0, 100)}'
    number.addItem(score)


button.clicked.connect(play)


main_win.show()
app.exec()




