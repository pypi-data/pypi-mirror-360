# -*- coding:utf-8 -*-
# 作者：猫先生的早茶
# 时间：2019年5月26日

import pyautogui

"""获取鼠标当前的坐标位置"""
'''
x,y = pyautogui.position()

print ("当前鼠标的X轴的位置为：{}，Y轴的位置为：{}".format(x,y))
'''

"""获取屏幕分辨率"""
'''
x,y = pyautogui.size()
print ("当前屏幕的分辨率是{}*{}".format(x,y))
'''

"""移动鼠标到指定位置"""
'''
pyautogui.moveTo(x=300,y=300,duration=0.25)
'''

"""点击鼠标"""
'''
pyautogui.click(x=100,y=150,button='right')
'''

"""双击鼠标"""
'''
pyautogui.doubleClick(x=100,y=150,button="left")

'''

"""发送组合键"""
'''
pyautogui.hotkey('win', 'r')
'''

"""输入内容"""
'''
pyautogui.typewrite(message="hello world",interval=0.25)
'''

"""获取指定坐标的颜色"""
'''
img = pyautogui.screenshot()
color = img.getpixel((100,100))
print ("该坐标的像素点的颜色是：{}".format(color))
'''

"""获取图标的位置"""
'''
x,y,width,height =  pyautogui.locateOnScreen('a.png')
print ("该图标在屏幕中的位置是：X={},Y={}，宽{}像素,高{}像素".format(x,y,width,height))
'''

"""获取中心点"""
'''
x,y = pyautogui.center((9,741,81,95))
print ("该图标的中心点是:X={},Y={}".format(x,y))
'''
