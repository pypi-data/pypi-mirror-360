
import tkinter as tk

window = tk.Tk()
window.title('简易计算器')
window.geometry('410x280+100+100')

# 设置窗口属性
window.attributes('-alpha', 0.9)  # 透明
# window['background'] = '#ffffff'  # 背景颜色

# 设置结果
result_num = tk.StringVar()
result_num.set(' ')

tk.Label(master=window, textvariable=result_num,
         font=('SimSong-Regular', 20), height=2,
         width=20,  justify='left', anchor='se').grid(row=1, column=1)


# 设置按键
button_clear = tk.Button(window, text='C', width=5,
                         font=18, relief='flat', background='#ebd4ad')
button_back = tk.Button(window, text='<-', width=5,
                        font=18, relief='flat', bg='#ebd4ad')
button_division = tk.Button(window, text='/', width=5,
                            font=18, relief='flat', bg='#ebd4ad')
button_multiplication = tk.Button(window, text='x', width=5,
                                  font=18, relief='flat', bg='#ebd4ad')
button_clear.grid(row=2, column=1, padx=4, pady=2)
button_back.grid(row=2, column=2, padx=4, pady=2)
button_division.grid(row=2, column=3, padx=4, pady=2)
button_multiplication.grid(row=2, column=4, padx=4, pady=2)


# 7,8,9,-
button_seven = tk.Button(window, text='7', width=5,
                         font=18, relief='flat', background='#edd5af')
button_eight = tk.Button(window, text='8', width=5,
                         font=18, relief='flat', bg='#edd5af')
button_nine = tk.Button(window, text='9', width=5,
                        font=18, relief='flat', bg='#edd5af')
button_subtraction = tk.Button(window, text='-', width=5,
                               font=18, relief='flat', bg='#ebd4ad')
button_seven.grid(row=3, column=1, padx=4, pady=2)
button_eight.grid(row=3, column=2, padx=4, pady=2)
button_nine.grid(row=3, column=3, padx=4, pady=2)
button_subtraction.grid(row=3, column=4, padx=4, pady=2)

# 4,5,6 +
button_four = tk.Button(window, text='4', width=5,
                        font=18, relief='flat', background='#edd5af')
button_five = tk.Button(window, text='5', width=5,
                        font=18, relief='flat', bg='#edd5af')
button_six = tk.Button(window, text='6', width=5,
                       font=18, relief='flat', bg='#edd5af')
button_addition = tk.Button(window, text='+', width=5,
                            font=18, relief='flat', bg='#ebd4ad')
button_four.grid(row=4, column=1, padx=4, pady=2)
button_five.grid(row=4, column=2, padx=4, pady=2)
button_six.grid(row=4, column=3, padx=4, pady=2)
button_addition.grid(row=4, column=4, padx=4, pady=2)

# 1,2,3, =
button_one = tk.Button(window, text='1', width=5,
                       font=18, relief='flat', background='#edd5af')
button_two = tk.Button(window, text='2', width=5,
                       font=18, relief='flat', bg='#edd5af')
button_three = tk.Button(window, text='3', width=5,
                         font=18, relief='flat', bg='#edd5af')
button_equal = tk.Button(window, text='=', width=5,
                         font=18, relief='flat', bg='#ebd4ad', height=3)
button_one.grid(row=5, column=1, padx=4, pady=2)
button_two.grid(row=5, column=2, padx=4, pady=2)
button_three.grid(row=5, column=3, padx=4, pady=2)
button_equal.grid(row=5, column=4, padx=4, pady=2, rowspan=2)

# 0,. =
button_zreo = tk.Button(window, text='0', width=16,
                        font=18, relief='flat', background='#edd5af')
button_dot = tk.Button(window, text='.', width=5, height=2,
                       font=18, relief='flat', bg='#edd5af')
button_zreo.grid(row=6, column=1, padx=4, pady=2, columnspan=2)
button_dot.grid(row=6, column=3, padx=4, pady=2)


# 点击事件
def click_button(x):
  # print('x:\t', x)
  result_num.set(result_num.get() + x)


button_one.config(command=lambda: click_button('1'))
button_two.config(command=lambda: click_button('2'))
button_three.config(command=lambda: click_button('3'))
button_four.config(command=lambda: click_button('4'))
button_five.config(command=lambda: click_button('5'))
button_six.config(command=lambda: click_button('6'))
button_seven.config(command=lambda: click_button('7'))
button_eight.config(command=lambda: click_button('8'))
button_nine.config(command=lambda: click_button('9'))
button_zreo.config(command=lambda: click_button('0'))
button_addition.config(command=lambda: click_button('+'))
button_subtraction.config(command=lambda: click_button('-'))
button_multiplication.config(command=lambda: click_button('*'))
button_division.config(command=lambda: click_button('/'))


# 计算 =
def calculation():
  opt_str = result_num.get()
  result = eval(opt_str)
  result_num.set(str(result))
  # print(result_num.get())


button_equal.config(command=calculation)
window.mainloop()
