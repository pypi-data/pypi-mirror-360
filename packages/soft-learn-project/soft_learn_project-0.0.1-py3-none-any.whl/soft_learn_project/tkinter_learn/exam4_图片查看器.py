
import tkinter as tk
from PIL import Image, ImageTk
import glob

windows = tk.Tk()
windows.geometry('800x600+100+100')
windows.title('图片查看器')

# 获取图片并调整图片大小
photo_list = glob.glob('photos/*jpeg')
image_list = []
for photo in photo_list:
  image = Image.open(photo)
  image.thumbnail(size=(800,500))  
  image_list.append(image)

image_tk_list = [ImageTk.PhotoImage(image=image) for image in image_list]

current_photo_num = 0
image_tk = image_tk_list[current_photo_num]
photo_label = tk.Label(master=windows,
                 image=image_tk,
                 width=800,
                 height=500,)
photo_label.pack()

# 信息栏
number_var = tk.StringVar()
number_var.set(f'{current_photo_num+1} of {len(photo_list)}')
tk.Label(master=windows, textvariable=number_var, bd=1, relief='flat', anchor='center').pack(fill='x')

# 两个按键 
button_frame = tk.Frame(master=windows)
button_frame.pack(anchor='center')

button1 = tk.Button(master=button_frame, text='上一页', )
button2 = tk.Button(master=button_frame, text='下一页', )
button1.pack(side='left', anchor='center')   # side 放在哪一边 ，anchor: 对齐方式
button2.pack(side='right',anchor='center' )
 
# 按键事件 
def change_photos(next_no):
  global current_photo_num
  current_photo_num += next_no
  current_photo_num = current_photo_num % len(photo_list)
  photo_label.config(image=image_tk_list[current_photo_num])
  number_var.set(f'{current_photo_num+1} of {len(photo_list)}')
  

button1.config(command=lambda: change_photos(-1))
button2.config(command=lambda: change_photos(1))

windows.mainloop()
