# 综上所述，ProcessPoolExecutor是在multiprocessing模块的基础上提供了更高级、更方便的并行计算接口，对于大部分情况下的并行计算任务，使用ProcessPoolExecutor可以更简洁、更易于管理和处理异常。但如果需要更细粒度的控制和定制化的并行计算，可以选择使用multiprocessing模块。

# 多进程模板
# """
import multiprocessing
import numpy as np
import time
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp


def my_name(name, value=10):
  # print(name)
  for i in range(value):
    print(name, i)
  return i


# 多线程必须使用 __name__ == "__main__"这一行， 另外必须通过python3 tt.py 来提交，在jupyter中会出现错误
if __name__ == "__main__":
  num_cores = mp.cpu_count()
  with mp.Pool(4) as pool:
    results = [pool.apply_async(my_name, args=(name, 1000))
               for name in ['王金龙', '王启航']]
    out = [result.get() for result in results]
    print(out)
# """

# 另一种模板
# """


def fn(name):
  for i in range(100):
    print(name, i)


if __name__ == '__main__':
  # 创建线程池
  from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
  # with ThreadPoolExecutor(5) as t:
  with ProcessPoolExecutor(5) as t:
    for i in range(20):
      t.submit(fn, name=f"线程{i}")
  # 等待线程池中的任务全部执行完毕. 才继续执行(守护)
  print("执行完毕")
# """


# my example
def task_function(par):
  start_time = time.time()
  time.sleep(np.random.randint(1, 6))
  end_time = time.time()
  return {par: f'{par**2} 用时{end_time - start_time}'}


def main():
  start_time = time.time()
  # method 1
#   with multiprocessing.Pool(processes=4) as pool:
#     result = pool.map(task_function, [1, 2, 4, 4])

  # method 2
  result = {}
  with ProcessPoolExecutor(max_workers=4) as excutor:
    tasks = [excutor.submit(task_function, par) for par in [1, 2, 3, 4]]
    for future in concurrent.futures.as_completed(tasks):
      result.update(future.result())
  end_time = time.time()
  print(f'总用时{end_time - start_time}')
  return result


if __name__ == '__main__':
  print(main())

# ============================
# my another example

# 定义要在子进程中执行的函数


def process_func(arg):
    # 进程任务逻辑
  result = ...
  return result


if __name__ == '__main__':
  # 创建进程池
  pool = multiprocessing.Pool(processes=num_processes)

  # 提交任务给进程池
  result = pool.apply_async(process_func, args=(arg1, arg2, ...))

  # 获取任务的结果
  result_value = result.get()

  # 关闭进程池
  pool.close()
  pool.join()

# ====================

# example
"""
import math
import time
import multiprocessing as mp
    
def final_fun(name, param):
    result = 0
    for num in param:
        result += math.cos(num) + math.sin(num)         
    return {name: result}
 
if __name__ == '__main__':
 
    start_time = time.time()
 
    num_cores = int(mp.cpu_count())
 
    print("你使用的计算机有: " + str(num_cores) + " 个核，当然了，Intel 7 以上的要除以2")
    print("如果你使用的 Python 是 32 位的，注意数据量不要超过两个G")
    print("请你再次检查你的程序是否已经改成了适合并行运算的样子")
    
    pool = mp.Pool(num_cores)
    param_dict = {'task1': list(range(10, 3000000)),
                  'task2': list(range(3000000, 6000000)),
                  'task3': list(range(6000000, 9000000)),
                  'task4': list(range(9000000, 12000000)),
                  'task5': list(range(12000000, 15000000)),
                  'task6': list(range(15000000, 18000000)),
                  'task7': list(range(18000000, 21000000)),
                  'task8': list(range(21000000, 24000000)),
                  'task9': list(range(24000000, 27000000)),
                  'task10': list(range(27000000, 30000000))}
    
    results = [pool.apply_async(final_fun, args=(name, param)) for name, param in param_dict.items()]
    
    results = [p.get() for p in results]
 
    end_time = time.time()
    use_time = end_time - start_time
 
    print("多进程计算 共消耗: " + "{:.2f}".format(use_time) + " 秒")


    result = 0
    for i in range(0,10):
        result += results[i].get("task"+str(i+1))
    print(result)
 
    start_time = time.time()
    result = 0
    for i in range(10,30000000):
        result += math.cos(i) + math.sin(i)
    end_time = time.time()
    print("单进程计算 共消耗: " + "{:.2f}".format(end_time - start_time) + " 秒")
    print(result)
"""
