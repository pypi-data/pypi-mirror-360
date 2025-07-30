# import tkinter as tk
# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QAction


# class MyWindow(QMainWindow):
#   def __init__(self):
#     super().__init__()

#     self.setWindowTitle("记事本")
#     self.setGeometry(100, 100, 800, 500)

#     # 创建菜单栏
#     menubar = self.menuBar()

#     # 创建文件菜单
#     file_menu = menubar.addMenu("文件")

#     # 创建菜单项
#     new_action = QAction("新建", self)
#     open_action = QAction("打开", self)
#     save_action = QAction("保存", self)
#     save_as_action = QAction("另存为", self)

#     # 将菜单项添加到文件菜单中
#     file_menu.addAction(new_action)
#     file_menu.addAction(open_action)
#     file_menu.addAction(save_action)
#     file_menu.addAction(save_as_action)


# if __name__ == "__main__":
#   app = QApplication(sys.argv)
#   window = MyWindow()
#   window.show()
#   sys.exit(app.exec_())


# def file_new():
#   print("New File")


# def file_open():
#   print("Open File")


# def file_save():
#   print("Save File")


# def exit_program():
#   root.destroy()


# root = tk.Tk()

# # 创建菜单栏
# menubar = tk.Menu(root)

# # 创建"文件"菜单
# file_menu = tk.Menu(menubar, tearoff=0)
# file_menu.add_command(label="新建", command=file_new)
# file_menu.add_command(label="打开", command=file_open)
# file_menu.add_command(label="保存", command=file_save)
# file_menu.add_separator()
# file_menu.add_command(label="退出", command=exit_program)

# # 将"文件"菜单添加到菜单栏
# menubar.add_cascade(label="文件", menu=file_menu)

# # 将菜单栏添加到主窗口
# root.config(menu=menubar)

# root.mainloop()

import tkinter as tk

root = tk.Tk()

# 创建两个 Label
label1 = tk.Label(root, text="Label 1", bg="red", width=10, height=2)
label2 = tk.Label(root, text="Label 2", bg="blue", width=10, height=2)

# 使用 pack() 方法布局 Label，并设置 side 参数为 LEFT
label1.pack(side='top')
label2.pack()

root.mainloop()
