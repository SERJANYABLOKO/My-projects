from turtle import *
from random import *

screen = Screen()
screen.title("Название проекта")  # Установить название окна

speed(0)

setup(500,500)

colors = ["red", "green", "blue", "yellow", "orange", "pink","brown", "white", "gray", "cyan", "magenta", "violet", "gold", "silver", "maroon", "lime"] * 30

penup()
goto(-250, 200)
pendown()

count = 0

for n_color in colors:
    color('black', n_color)
    begin_fill()
    for i in range(4):
        forward(50)
        left(90)
    end_fill()
    forward(25)
    left(90)
    penup()
    forward(4)
    write(n_color[0].upper(), font=("Arial", 25, "normal"), align='center')
    right(180)
    forward(4)
    left(90)
    count += 1
    pendown()
    penup()
    forward(25)
    if count == 10:
        goto(-250,  ycor() -50)
        count = 0
    pendown()

mainloop()