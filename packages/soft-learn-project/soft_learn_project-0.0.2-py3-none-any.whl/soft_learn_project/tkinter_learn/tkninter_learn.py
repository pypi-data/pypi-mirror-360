# Python GUI编程(Tkinter)
"""
查找一个莫烦教程
Python 提供了多个图形开发界面的库，几个常用 Python GUI 库如下：

Tkinter： Tkinter 模块(Tk 接口)是 Python 的标准 Tk GUI 工具包的接口 .Tk 和 Tkinter 可以在大多数的 Unix 平台下使用,同样可以应用在 Windows 和 Macintosh 系统里。Tk8.0 的后续版本可以实现本地窗口风格,并良好地运行在绝大多数平台中。

wxPython：wxPython 是一款开源软件，是 Python 语言的一套优秀的 GUI 图形库，允许 Python 程序员很方便的创建完整的、功能健全的 GUI 用户界面。

Jython：Jython 程序可以和 Java 无缝集成。除了一些标准模块，Jython 使用 Java 的模块。Jython 几乎拥有标准的Python 中不依赖于 C 语言的全部模块。比如，Jython 的用户界面将使用 Swing，AWT或者 SWT。Jython 可以被动态或静态地编译成 Java 字节码
"""

""" 流程
创建一个GUI程序
1、导入 Tkinter 模块
2、创建控件
3、指定这个控件的 master， 即这个控件属于哪一个
4、告诉 GM(geometry manager) 有一个控件产生了。
"""

# 创建按钮
"""
# 语法格式如下：
# w = Button ( master, option=value, ... )
# master: 按钮的父容器。
# options: 可选项，即该按钮的可设置的属性。
import tkinter
top = tkinter.Tk()
top.geometry("200x150")

def helloCallBack():
    print("hello runoob")


B = tkinter.Button(master=top,
                   text="点我",
                   command=helloCallBack,
                   padx=30, # 按钮在x轴方向上的内边距(padding)，是指按钮的内容与按钮边缘的距离
                   relief=tkinter.RIDGE
                   )
B.pack()

top.mainloop()
# """

# 画布（Canvas）组件
"""
# 和 html5 中的画布一样，都是用来绘图的。您可以将图形，文本，小部件或框架放置在画布上。
# 创建一个矩形，指定画布的颜色为白色
import tkinter
from turtle import color
window = tkinter.Tk()
# 创建一个Canvas，设置其背景色为白色
cv = tkinter.Canvas(window,bg = 'white')

# 创建一个矩形，坐标为(10,10,110,110)
cv.create_rectangle(10,10,110,110)
cv.pack()
# filename = PhotoImage(file = "sunshine.gif")
# image = cv.create_image(50, 50, anchor=tkinter.NE, image=filename)

window.mainloop()
# """


# 复选框（Checkbutton）
"""
import tkinter

def check1_ture():
        print("OK")

top = tkinter.Tk()
CheckVar1 = tkinter.IntVar()
C1 = tkinter.Checkbutton(top, text="RUNOOB",
                         variable=CheckVar1,
                         command=check1_ture,
                         onvalue=1, offvalue=0, height=5,
                         width=20)

C2 = tkinter.Checkbutton(top, text="GOOGLE",
                         variable=0,
                         onvalue=1, offvalue=0, height=5,
                         width=20)
C1.pack()
C2.pack()

top.mainloop()
# """


# 文本框用来让用户输入一行文本字符串
"""
# 你如果需要输入多行文本，可以使用 Text 组件。
# 你如果需要显示一行或多行文本且不允许用户修改，你可以使用 Label 组件。
import tkinter

top = tkinter.Tk()
L1 = tkinter.Label(top, text="网站名")
L1.pack(side=tkinter.LEFT)
E1 = tkinter.Entry(top, bd=5)
E1.pack(side=tkinter.RIGHT)
# input_str = E1.get() # 获取文件框的值，不知道怎么用

top.mainloop()
# """

# 框架（Frame）
"""
# 控件在屏幕上显示一个矩形区域，多用来作为容器。
import tkinter
window = tkinter.Tk()
window.title("tkinter frame")
window.geometry('500x500') # 窗口大小

frame1 = tkinter.Frame(window)  # 窗口上建立一个框
label = tkinter.Label(frame1, text="Label",)# justify=tkinter.LEFT)  # 框1加入建立标签
label.pack(side=tkinter.LEFT)
frame1.pack(padx=1, pady=1)

frame2 = tkinter.Frame(window)  # 窗口上建立第二个框
def say_hi():
    print("hello ~ !")
hi_there = tkinter.Button(frame2, text="say hi~", command=say_hi)  # 建立按键
hi_there.pack()
frame2.pack(padx=10, pady=10)

window.mainloop()
# """


# 创建一个列表组件
"""
import tkinter
# 1. # 建立窗口
window = tkinter.Tk()  
window.title("我的tkinter")

# 2. 创建控件， 列表组件
listb = tkinter.Listbox(window)  # 创建列表组件
li = ['C', 'python', 'php', 'html', 'SQL', 'java']
for item in li:                 # 小部件插入数据
    listb.insert(0, item)
listb.pack()                    # 将小部件放置到主窗口中

window.mainloop() 
# """


# 定义一个lable
""" 
import tkinter as tk
# 创建窗口
window = tk.Tk()
window.title('Mywindow')  # 窗口的标题
window.geometry('400x200')  # 窗口的大小

# 定义一个lable
l = tk.Label(window,
             text='Hi! this is TK!',    # 标签的文字
             background="green",  # 标签背景颜色
             font=('Arial', 12),     # 字体和字体大小
             width=15, height=2  # 标签长宽（以字符长度计算）
             )
l.pack()    # 固定窗口位置

window.mainloop()
# """


# 高级设置
""" 按钮
import tkinter as tk 
# 创建窗口
window = tk.Tk()
window.title('Mywindow')  # 窗口的标题
window.geometry('200x100')  # 窗口的大小

# 定义一个lable
var = tk.StringVar()  # 定义一个字符串变量
l = tk.Label(window,
             textvariable=var,    # 标签的文字
             bg='green',     # 标签背景颜色
             font=('Arial', 12),     # 字体和字体大小
             width=15, height=2  # 标签长宽
             )
l.pack()    # 固定窗口位置

# 定义一个全局变量，来表明字符显示与不显示
on_hit = False


def hit_me():
    # 按钮的函数
    global on_hit  # 声明全局变量
    if on_hit == False:
        on_hit = True
        var.set('You hit me!')  # 设置字符串变量
    else:
        on_hit = False
        var.set('')
        print("没有点我")


# 按钮
b = tk.Button(window, text='点我', width=15, height=2,
              command=hit_me)  # 点击按钮执行一个名为“hit_me”的函数
b.pack()

window.mainloop()
# """

# 输入框高级
"""  把输入框的内容写入到文本框
import tkinter as tk

window = tk.Tk()
window.title('my window')
# 窗口尺寸
window.geometry('200x200')
# 定义一个输入框entry
e = tk.Entry(window, show=None)  # 如果是输入密码，可以写show='*'
e.pack()
# 定义按钮功能


def insert_point():
    var = e.get()  # 获取输入框的内容
    t.insert('insert', var) # 插入到文本框


def insert_end():
    var = e.get()
    t.insert('end', var)  # 这里还可以定义字符串插入的具体位置，比如t.insert('1.1',var)，表示插入到第一行第一列


# 定义2个按钮 Button
b1 = tk.Button(window, text="insert point", width=15,
               height=2, command=insert_point)
b1.pack()

b2 = tk.Button(window, text="insert end", command=insert_end)
b2.pack()

# 定义一个文本框 Text
t = tk.Text(window, height=2)
t.pack()
# 显示出来
window.mainloop()
# """


# 创建一个Listbox和变量var2，并将var2的值赋给Listbox
"""
import tkinter as tk

window = tk.Tk()
window.title('my window')
# 窗口尺寸
window.geometry('200x200')
# 创建一个lable
var1 = tk.StringVar()  # 创建变量
l = tk.Label(window, bg='yellow', width=4, textvariable=var1)
l.pack()
# 按钮事件


def print_selection():
    value = lb.get(lb.curselection())  # 获取当前选中的文本
    var1.set(value)  # 为label设置值


# 创建一个按钮
b1 = tk.Button(window, text='print selection', width=15,
               height=2, command=print_selection)
b1.pack()

# 创建一个Listbox和变量var2，并将var2的值赋给Listbox
var2 = tk.StringVar()
var2.set((11, 22, 33, 44))  # 为变量设置值

# 创建Listbox
lb = tk.Listbox(window, listvariable=var2,)  # 将var2的值赋给Listbox

# 创建一个list并将值循环添加到Listbox控件中
list_items = [1, 2, 3, 4]  # 定义列表
for item in list_items:
    lb.insert('end', item)  # 从最后一个位置开始加入值
lb.insert(1, 'first')  # 在第一个位置加入'first'字符
lb.insert(2, 'second')  # 在第二个位置加入'second'字符
# lb.delete(2)  # 删除第二个位置的字符
lb.pack()


# 显示出来
window.mainloop()
# """


# radiobutton 部件 触发高级
'''
import tkinter as tk

window = tk.Tk()
window.title('my window')
##窗口尺寸
window.geometry('200x200')
#创建一个lable
var= tk.StringVar()    #创建变量
l =tk.Label(window,bg='yellow',width=20,height=2,text='empty')
l.pack()
#实现将选择的选项显示在lable
def print_selection():
    """
    当触发这个函数功能时，我们的 label 中就会显示 text 所赋值的字符串即 ‘you have selected’, 后面则是我们所选中的选项 var.get()就是获取到变量 var 的值，
    """
    l.config(text='you have selected'+var.get())

#创建几个Radiobutton
# 其中variable=var, value='A'的意思就是，当我们鼠标选中了其中一个选项，把value的值("A")放到变量var中，然后赋值给variable
r1 = tk.Radiobutton(window, text='Option A',
                    variable=var, value='A',
                    command=print_selection)
r1.pack()

r2 = tk.Radiobutton(window, text='Option B',
                    variable=var, value='B',
                    command=print_selection)
r2.pack()

r3 = tk.Radiobutton(window, text='Option C',
                    variable=var, value='C',
                    command=print_selection)
r3.pack()

##显示出来
window.mainloop()

# '''
