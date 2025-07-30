import tkinter as tk

window = tk.Tk()
window.geometry('800x500+100+100')
window.title("记事本")

# 创建菜单栏
menu = tk.Menu(master=window, tearoff=False)

# 创建"文件"菜单
file_menu = tk.Menu(master=menu, tearoff=False)
file_menu.add_command(label='新建')
file_menu.add_command(label='打开')
file_menu.add_command(label='另存')
file_menu.add_command(label='另存为')

# 将"文件"菜单添加到菜单栏
menu.add_cascade(label='文件', menu=file_menu)


# 创建"编辑"菜单
edit_menu = tk.Menu(master=menu, tearoff=False)
edit_menu.add_command(label='撤销')
edit_menu.add_command(label='重做')
edit_menu.add_separator()  # 增加分割线
edit_menu.add_command(label='复制')
edit_menu.add_command(label='粘贴')
edit_menu.add_command(label='剪切')
menu.add_cascade(label='编辑', menu=edit_menu)

# 创建"关于"菜单
about_menu = tk.Menu(master=menu, tearoff=False)
about_menu.add_command(label='作者')
about_menu.add_command(label='版权')

# 将菜单栏添加到主窗口
window.config(menu=menu)

# 添加状态栏
status_str_var = tk.StringVar()
status_str_var.set('字符数: {}'.format(0))

status_lable = tk.Label(
    master=window, textvariable=status_str_var, bd=1, relief='sunken', anchor='w', height=1,)  # relief: 边框的样式, anchor: 文本的对齐方式
# status_lable.pack(side=tk.BOTTOM, fill=tk.X)
status_lable.pack(side='bottom', fill='x')

# 添加左侧栏
var_line = tk.StringVar()
left_label = tk.Label(master=window, textvariable=var_line, width=1, bg='#faebd7',
                      anchor='n', font=18)
left_label.pack(side='left', fill='y')

# 添加文本
text_pad = tk.Text(master=window, font=18)
text_pad.pack(fill='both', expand=True)

# 添加滚轴
scroll = tk.Scrollbar(text_pad, )
text_pad.config(yscrollcommand=scroll.set)
scroll.config(command=text_pad.yview)
scroll.pack(side='right', fill='y')

window.mainloop()
