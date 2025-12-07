from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer
import random

app = QApplication([])
main_win = QWidget()
main_win.setWindowTitle('Генератор случайных чисел')
main_win.resize(500, 500)

button = QPushButton('Сгенерировать')
text = QLabel('Узнать победителя')
Hline = QHBoxLayout()
labels = []
for i in range(10):
    winner_1 = QLabel('?')
    Hline.addWidget(winner_1, alignment = Qt.AlignCenter)
    labels.append(winner_1)


Vline = QVBoxLayout()
Vline.addWidget(text, alignment = Qt.AlignCenter)
Vline.addLayout(Hline)
Vline.addWidget(button, alignment = Qt.AlignCenter)
main_win.setLayout(Vline)
i = 0

def show_winner():
    global i
    i += 1
    numbers = []
    for lbl in labels:
        rnd = random.randint(0, 2)
        lbl.setText(str(rnd))
        numbers.append(rnd)
    if len(list(set(numbers))) == 1:
        text.setText(f'Вы победили за {i} попыток')
        timer.stop()
    else:
        text.setText(f'Вы проиграли за {i} попыток')
        i += 1

timer = QTimer()
timer.timeout.connect(show_winner)

def time():
    global i
    i = 0
    timer.start(1)

button.clicked.connect(time)


main_win.show()
app.exec_()

