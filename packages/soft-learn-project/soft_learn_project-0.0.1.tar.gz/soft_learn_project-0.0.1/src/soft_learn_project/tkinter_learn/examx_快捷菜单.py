import tkinter as tk
import platform

window = tk.Tk()
window.geometry('800x500+100+100')
window.title("记事本")

# 添加菜单栏
menu = tk.Menu(master=window, tearoff=False)

# 添加文件菜单
file_menu = tk.Menu(master=menu, tearoff=False)
file_menu.add_command(label='新建')
file_menu.add_command(label='打开')
file_menu.add_command(label='另存')
file_menu.add_command(label='另存为')
menu.add_cascade(label='文件', menu=file_menu)

# 在macOS上，需要进行特殊处理来显示菜单栏
if platform.system() == 'Darwin':
  def show_menu(event):
    menu.post(event.x_root, event.y_root)
  window.bind("<Button-2>", show_menu)

window.config(menu=menu)
window.mainloop()
