from turtle import *

shape('turtle')
shapesize(2)
speed(5)

color('red')

# forward(300)  # 往前
# backward(300)  # 往后
# circle(100)  # 
# circle(110)

# left(90)
# forward(100)
# right(90)
#
# forward(100)
# right(90)
# forward(100)
# right(90)
# forward(150)
# right(90)
# forward(150)
# right(90)
# forward(180)
#
for i in [1,2,3,4]:
    right(90)   # 右转90度
    forward(150) # 向前走150米
# right(900)
# forward(200)
# right(560)
# forward(200)
# right(5000)
# forward(200)
# right(90)
# forward(100)

"""
for i in range(2):
    for j in range(10):
        right(130)   # 右转90度
        forward(60) # 向前走150米

    right(90)
    forward(150)

forward(300)
done()
quit()

# """


def xingxing():
    for j in range(10):
        right(130)  # 右转90度
        forward(30)  # 向前走150米


str1 = 200
up()
goto(str1, -str1)
down()
xingxing()

up()
goto(str1, str1)
down()
xingxing()

up()
goto(-str1, str1)
down()
xingxing()

up()
goto(-str1, -str1)
down()
xingxing()

done()
