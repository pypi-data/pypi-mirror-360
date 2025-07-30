import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import random

# 创建Tkinter窗口
window = tk.Tk()
window.geometry('800x600+100+100')
window.title('辞职信')

frame1 = tk.Frame(master=window)
frame1.pack()

tk.Label(frame1, text='尊敬的各位领导:', font=24,
         padx=30, pady=30).pack(side=tk.LEFT, anchor=tk.N)

# 或者通过 PIL 来导入图片
# # 打开图像
# image = Image.open('photos/gc.jpg')
# # 创建PhotoImage对象
# image_tk = ImageTk.PhotoImage(image)

image_tk = ImageTk.PhotoImage(file='photos/gc.png')
# 创建Label组件，并显示图像
tk.Label(frame1, image=image_tk, font=24, padx=30,
         pady=30, ).pack(side=tk.LEFT, anchor=tk.N)

tk.Label(frame1, text='辞职人: 王启航',  height=25, anchor=tk.S).pack(side=tk.RIGHT)
# tk.Label(frame1, text='辞职人: 正新').place(relx=0.8, rely=0.9)

yes_image = ImageTk.PhotoImage(file='photos/yes.png')
no_image = ImageTk.PhotoImage(file='photos/no.png')

yes_button = tk.Button(frame1, image=yes_image, bd=0)
no_button = tk.Button(frame1, image=no_image, bd=0,)
yes_button.place(relx=0.2, rely=0.8, anchor=tk.CENTER)
no_button.place(relx=0.6, rely=0.8, anchor=tk.CENTER)

# 对第二个frame 操作
frame2 = tk.Frame(master=window)
# frame2.pack()

tk.Label(frame2, text='老板大人, 臣告退了,\n这一退可能就是一辈子了!',
         font=('WeibeiSC-Bold', 20), justify=tk.LEFT,
         height=250,
         padx=50,
         fg='red').pack()
tk.Button(frame2, text='退出', command=window.quit).place(relx=0.8, rely=0.9)


# 设置点击关闭窗口时 无法关闭
def on_exit():
  messagebox.showwarning(title='提示', message='此路不通')


window.protocol('WM_DELETE_WINDOW', func=on_exit)


# 移动到不同意 使得不同意移动
def move(event):
  no_button.place(relx=random.random(), rely=random.random(), anchor=tk.CENTER)
  pass


no_button.bind('<Enter>', move)

# 点击同意移动到下一个页面


def sure():
  frame1.pack_forget()  # 隐藏第一个frame
  frame2.pack()


yes_button.config(command=sure)

# 运行Tkinter事件循环
window.mainloop()
