from turtle import *

color("red")
shape("turtle")

speed(10)  # 慢



def star(size):
    for i in range(5):
        forward(size)
        right(180 - 180 / 5)


for i in range(10):
    forward(100)
    left(110)

up()
goto(200, 200)
down()
star(50)

done()
