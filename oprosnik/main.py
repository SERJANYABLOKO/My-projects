import random
import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QRadioButton, \
     QMessageBox
from PyQt5.QtCore import QTimer

score = 0
start_time = time.time()


app = QApplication([])
main_win = QWidget()
main_win.setWindowTitle('Опросник')
main_win.resize(500, 500)

text = QLabel('Функция для вывода в питоне?')

button_1 = QRadioButton('print')
button_2 = QRadioButton('input()')
button_otvet = QPushButton('Ответить')

questions = [
     ['Функция для вывода в питоне?', 'print', 'input', 1],
     ['Как импортироовать библиотеку?', 'import библиотека', 'from библиотека', 'библиотека from import', 'библиотека', 1]
]
question = []
def load():
    global question
    if len(questions) == 0:
        end_time = time.time()
        show_message(f'Ты прошел тест за {round(end_time - start_time, 2)} секунд \nНабранно баллов: {score}')
        buttons = [button_1, button_2,  button_otvet]
        for button in buttons:
            button.hide()

        return
    question = random.choice(questions)
    questions.remove(question)
    text.setText(question[0])
    button_1.setText(question[1])
    button_2.setText(question[2])

Hline = QHBoxLayout()
Hline_1 = QHBoxLayout()
Hline_2 = QHBoxLayout()

Hline.addWidget(text, alignment= Qt.AlignCenter)

Hline_1.addWidget(button_1, alignment= Qt.AlignCenter)
Hline_2.addWidget(button_2, alignment= Qt.AlignCenter)




Vline = QVBoxLayout()

# Vline.addWidget(text, alignment = Qt.AlignCenter)

Vline.addLayout(Hline)
Vline.addLayout(Hline_1)
Vline.addLayout(Hline_2)
Vline.addWidget(button_otvet)

main_win.setLayout(Vline)

def show_message(text):
    victory_win = QMessageBox()
    victory_win.setText(text)
    victory_win.exec_()

def check_answer():
    global score
    for button in [button_1, button_2]:
        if button.isChecked():
            # print(button.text())
            # print(question[question[5]])
            if button.text() == question[question[5]]:
                print('ты победил')
                score += 1
            load()





button_otvet.clicked.connect(check_answer)
# button_1.clicked.connect(lambda: show_message('ты победил'))
# button_2.clicked.connect(lambda: show_message('ты не угадал'))
# button_3.clicked.connect(lambda: show_message('ты проиграл'))
# button_4.clicked.connect(lambda: show_message('увы.. но нет'))

load()

main_win.show()
app.exec_()

