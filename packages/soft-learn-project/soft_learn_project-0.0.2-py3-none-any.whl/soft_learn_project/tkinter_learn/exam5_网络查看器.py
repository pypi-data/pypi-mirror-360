import tkinter as tk
from tkinter import ttk
window = tk.Tk()
window.geometry('800x600+100+100')
window.title('网络查看器')

# 1. 左边的布局
left_frame = tk.Frame(master=window)
left_frame.pack(side='left', anchor='n', padx=5, pady=5
                )  # 位置为左边, 该frame的布局为从上到下

# 1.1 左边的布局 中的网络设置
net_frame = tk.LabelFrame(master=left_frame, text='网络设置',
                          padx=5, pady=5)
net_frame.pack()

tk.Label(net_frame, text='(1)协议类型').pack(anchor='w')
socket_type = ttk.Combobox(master=net_frame, values=['TCP 服务', 'TCP 客户端'])
socket_type.current(0)
socket_type.pack(anchor='w')

tk.Label(net_frame, text='(2)本地主机地址').pack(anchor='w')
socket_type = ttk.Combobox(master=net_frame, values=[
                           '127.0.0.1', '192.168.2.5'])
socket_type.current(0)
socket_type.pack(anchor='w')

tk.Label(net_frame, text='(3)本地端口').pack(anchor='w')
entry_port = tk.Entry(master=net_frame,)
entry_port.pack(anchor='w', fill='x')

# 按钮
button_frame = tk.Frame(master=net_frame)
button_frame.pack()

button_open = tk.Button(master=button_frame, text='打开', relief='sunken')
button_close = tk.Button(master=button_frame, text='关闭', relief='raised')
button_open.pack(side='left',)
button_close.pack(side='right')


# 1.2 左边的布局 中的接收设置
receive_frame = tk.LabelFrame(master=left_frame, text='接收设置')
receive_frame.pack(anchor='w', side='top', fill='x')

tk.Radiobutton(master=receive_frame, text='utf-8', value=1).pack(anchor='w')
tk.Radiobutton(master=receive_frame, text='gbk', value=0).pack(anchor='w')
value_json_data = tk.IntVar()
tk.Checkbutton(master=receive_frame, text='json数据',
               variable=value_json_data).pack(anchor='w')
value_change_line = tk.IntVar()
tk.Checkbutton(master=receive_frame, text='自动换行',
               variable=value_change_line).pack(anchor='w')

# 1.3 左边的布局 中的发送设置
forward_frame = tk.LabelFrame(master=left_frame, text='接收设置')
forward_frame.pack(anchor='w', fill='x')

tk.Radiobutton(master=forward_frame, text='utf-8', value=1).pack(anchor='w')
tk.Radiobutton(master=forward_frame, text='gbk', value=0).pack(anchor='w')
value_json_data = tk.IntVar()
tk.Checkbutton(master=forward_frame, text='数据加密',
               variable=value_json_data).pack(anchor='w')
value_change_line = tk.IntVar()
tk.Checkbutton(master=forward_frame, text='信息接收',
               variable=value_change_line).pack(anchor='w')

# 2. 右边布局
right_frame = tk.Frame(master=window)
right_frame.pack()

# 2.1 右边布局 上半部分
tk.Label(master=right_frame, text='数据日志').pack(anchor='w')
info_frame = tk.Frame(master=right_frame)
info_frame.pack(side='top')


# 2.1. 文本框和滚动条
text_pad = tk.Text(info_frame, )
text_pad.pack(side='left',)
scroll = tk.Scrollbar(info_frame, )
scroll.pack(side='right', fill='y')

text_pad.config(yscrollcommand=scroll.set)
scroll.config(command=text_pad.yview)


# 2.2 右边布局 下半部分
tk.Label(master=right_frame, text='信息发送').pack(anchor='w')
send_frame = tk.Frame(right_frame)
send_frame.pack()

send_area = tk.Text(send_frame, )
send_area.pack(side='left')
send_button = tk.Button(master=send_frame, text='发送', width=4)
send_button.pack(side='right', fill='y')

window.mainloop()
