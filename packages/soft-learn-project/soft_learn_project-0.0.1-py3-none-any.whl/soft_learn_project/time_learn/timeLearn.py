
import time
# 去看 ipynb,更清晰


class Features():
  def __init__(self) -> None:
    """time库包括三类函数:
    -时间获取:time（）、ctime()、gmtime()、localtime()
    -时间格式化:strftime()、strptime()、asctime()
    -程序计时:sleep()、perf_counter()
    """
    pass

  def notes(self):
    """
    """
    # perf_counter
    # print(time.time())
    day = int(time.strftime("%d")) - 1  # 获取前一天的日期
    print(time.strftime("%Y-%m") + f'-{day}')

    print(time.strftime("%Y-%m-%d"))
    print(time.asctime(time.localtime()))  # 获取格式化的时间
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 格式化>日期
    #
    pass

  def get_calender(self, theyear=2016, themonth=1):
    import calendar
    month_calender = calendar.month(
        theyear=theyear, themonth=themonth)  # 获取某月日历
    return month_calender

  def timer(func):
    """
    用于计时的装饰器函数

    :param func: 被装饰函数
    :return: 闭包函数，封装了自定义行为与被装饰函数的调用
    """
    def wrapper(*args, **kwargs):
      """
      闭包函数
      :param args: 被装饰函数的位置参数
      :param kwargs: 被装饰函数的关键字参数
      :return: int,被装饰函数的计算结果
      """
      t1 = time.perf_counter()
      res = func(*args, **kwargs)
      t2 = time.perf_counter()
      cost = round(t2 - t1, 2)
      print('函数--> {:s} 用时: {:.2f} s'.format(func.__name__, cost))
      return res
    return wrapper

  def timer_no_return(func):
    """
    用于计时的装饰器函数

    :param func: 被装饰函数
    :return: 闭包函数，封装了自定义行为与被装饰函数的调用
    """
    import mpi4py

    def wrapper(*args, **kwargs):
      """
      闭包函数
      :param args: 被装饰函数的位置参数
      :param kwargs: 被装饰函数的关键字参数
      :return: int,被装饰函数的计算结果
      """
      t1 = time.perf_counter()
      func(*args, **kwargs)
      t2 = time.perf_counter()
      cost = round(t2 - t1, 2)

      comm = mpi4py.MPI.COMM_WORLD
      rank = comm.Get_rank()
      if rank == 0:
        print('函数--> {:s} 用时: {:.2f} s'.format(func.__name__, cost))
      return None
    return wrapper
