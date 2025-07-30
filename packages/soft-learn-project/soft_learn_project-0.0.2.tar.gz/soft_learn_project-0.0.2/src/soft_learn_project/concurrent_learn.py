
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 学习网址: http://c.biancheng.net/view/2627.html

# 线程池的基类是 concurrent.futures 模块中的 Executor，Executor 提供了两个子类，即 ThreadPoolExecutor 和 ProcessPoolExecutor，其中 ThreadPoolExecutor 用于创建线程池，而 ProcessPoolExecutor 用于创建进程池。

# 如果使用线程池/进程池来管理并发编程，那么只要将相应的 task 函数提交给线程池/进程池，剩下的事情就由线程池/进程池来搞定。

# Exectuor 提供了如下常用方法：
# submit(fn, *args, **kwargs)：将 fn 函数提交给线程池。*args 代表传给 fn 函数的参数，*kwargs 代表以关键字参数的形式为 fn 函数传入参数。
# map(func, *iterables, timeout=None, chunksize=1)：该函数类似于全局函数 map(func, *iterables)，只是该函数将会启动多个线程，以异步方式立即对 iterables 执行 map 处理。
# shutdown(wait=True)：关闭线程池。

# 线程可以这么干，而进程只能在if __name__ == "__main__": 里面
"""
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import threading
import time
# 定义一个准备作为线程任务的函数
def action(max):
    my_sum = 0
    for i in range(max):
        print(threading.current_thread().name + '  ' + str(i))
        my_sum += i
    return my_sum
# 创建一个包含2条线程的线程池, 
pool = ThreadPoolExecutor(max_workers=2)  
# 向线程池提交一个task, 50会作为action()函数的参数
future1 = pool.submit(action, 50)
# 向线程池再提交一个task, 100会作为action()函数的参数
future2 = pool.submit(action, 100)
# 判断future1代表的任务是否结束
print(future1.done())
time.sleep(3)
# 判断future2代表的任务是否结束
print(future2.done())
# 查看future1代表的任务返回的结果
print(future1.result())
# 查看future2代表的任务返回的结果
print(future2.result())
# 关闭线程池
pool.shutdown()
# """

# 线程进程都可以
""" 
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import threading
import time
# 定义一个准备作为线程任务的函数
def action(max):
    my_sum = 0
    for i in range(max):
        print(threading.current_thread().name + '  ' + str(i))
        my_sum += i
    return my_sum
# 创建一个包含2条线程的线程池
if __name__ == "__main__":
    pool = ProcessPoolExecutor(max_workers=2)
    # 向线程池提交一个task, 50会作为action()函数的参数
    future1 = pool.submit(action, 50)
    # 向线程池再提交一个task, 100会作为action()函数的参数
    future2 = pool.submit(action, 100)
    # 判断future1代表的任务是否结束
    print(future1.done())
    # time.sleep(3)
    # 判断future2代表的任务是否结束
    print(future2.done())
    # 查看future1代表的任务返回的结果
    print(future1.result())
    # 查看future2代表的任务返回的结果
    print(future2.result())
    # 关闭线程池
    pool.shutdown()
# """

# 获取执行结果
# 前面程序调用了 Future 的 result() 方法来获取线程任务的运回值，但该方法会阻塞当前主线程，只有等到钱程任务完成后，result() 方法的阻塞才会被解除。

# 如果程序不希望直接调用 result() 方法阻塞线程，则可通过 Future 的 add_done_callback() 方法来添加回调函数，该回调函数形如 fn(future)。当线程任务完成后，程序会自动触发该回调函数，并将对应的 Future 对象作为参数传给该回调函数。

# 下面程序使用 add_done_callback() 方法来获取线程任务的返回值：

"""
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import threading
import time
# 定义一个准备作为线程任务的函数
def action(max):
    my_sum = 0
    for i in range(max):
        print(threading.current_thread().name + '  ' + str(i))
        my_sum += i
    return my_sum

def get_result(future):
        print(future.result())

if __name__ == "__main__":
    # 创建一个包含2条线程的线程池
    with ProcessPoolExecutor(max_workers=2) as pool:
        # 向线程池提交一个task, 50会作为action()函数的参数
        future1 = pool.submit(action, 50)
        # 向线程池再提交一个task, 100会作为action()函数的参数
        future2 = pool.submit(action, 100)
        
        # 为future1添加线程完成的回调函数
        future1.add_done_callback(get_result)
        # 为future2添加线程完成的回调函数
        future2.add_done_callback(get_result)
        print('--------------')
# """

# 此外，Exectuor 还提供了一个 map(func, *iterables, timeout=None, chunksize=1) 方法，该方法的功能类似于全局函数 map()，区别在于线程池的 map() 方法会为 iterables 的每个元素启动一个线程，以并发方式来执行 func 函数。这种方式相当于启动 len(iterables) 个线程，井收集每个线程的执行结果。

# 例如，如下程序使用 Executor 的 map() 方法来启动线程，并收集线程任务的返回值：
# """
# 定义一个准备作为线程任务的函数


def action(max):
    my_sum = 0
    for i in range(max):
        print(threading.current_thread().name + '  ' + str(i))
        my_sum += i
    return my_sum
# 创建一个包含4条线程的线程池


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        # 使用线程执行map计算
        # 后面元组有3个元素，因此程序启动3条线程来执行action函数
        results = pool.map(action, (50, 100, 150))
        print('--------------')
        for r in results:  # results 是iterator
            print(r)
# 上面程序使用 map() 方法来启动 3 个线程（该程序的线程池包含 4 个线程，如果继续使用只包含两个线程的线程池，此时将有一个任务处于等待状态，必须等其中一个任务完成，线程空闲出来才会获得执行的机会），map() 方法的返回值将会收集每个线程任务的返回结果。
# 运行上面程序，同样可以看到 3 个线程并发执行的结果，最后通过 results 可以看到 3 个线程任务的返回结果。
# 通过上面程序可以看出，使用 map() 方法来启动线程，并收集线程的执行结果，不仅具有代码简单的优点，而且虽然程序会以并发方式来执行 action() 函数，但最后收集的 action() 函数的执行结果，依然与传入参数的结果保持一致。也就是说，上面 results 的第一个元素是 action(50) 的结果，第二个元素是 action(100) 的结果，第三个元素是 action(150) 的结果。
# """




# ⾄于进程池. 就把ThreadPoolExecutor更换为ProcessPoolExecutor就可以了. 其他⼀模⼀样
"""
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from os import name


def fn(name):
    for i in range(100):
        print(name, i)


if __name__ == '__main__':
    # 创建线程池
    with ThreadPoolExecutor(5) as t:
        for i in range(20):
            t.submit(fn, name=f"线程{i}")
    # 等待线程池中的任务全部执行完毕. 才继续执行(守护)
    print("执行完毕")
# """