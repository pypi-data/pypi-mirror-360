# 多线程和多进程没办法通过jupyter 运行
from multiprocessing import Process
from threading import Thread


""" 多线程的第一种写法


def func(name, age):
    for i in range(1000):
        print(name, i, age)


if __name__ == '__main__':
    t1 = Thread(target=func, args=("周杰伦",18))
    t2 = Thread(target=func, args=("王⼒宏",28))
    t1.start()
    t2.start()

# """


# 这是需要掌握的多线程并且传参数的方法，多进程只需要把Thread 变成 Process即可
""" 多线程的第二种写法
class MyThread(Thread):
    def __init__(self, name, age):
        # Thread.__init__(self)  # 继承父类的__init__
        super().__init__()
        self.name = name
        self.age = age

    def run(self):  # 必须要定义run 函数
        for i in range(10000000):
            print(self.name, i, self.age)


if __name__ == "__main__":
    t1 = MyThread(name='周杰伦', age=18)
    t1.start()  # 必须通过start方法开启

    t2 = MyThread(name='王力宏', age=28)
    t2.start()
# """

##########
""" 多进程
class MyProcess(Process):
    def __init__(self, name, age):
        super().__init__()
        self.name = name
        self.age = age

    def run(self):
        for i in range(100000000):
            print(self.name, i, self.age)


if __name__ == "__main__":
    p1 = MyProcess(name='周杰伦', age=18)
    p1.start()

    p2 = MyProcess(name='王力宏', age=28)
    p2.start()
# """
