import datetime
import time


class Features():
  def __init__(self) -> None:
    """datatime模块重新封装了time模块，提供更多接口，
    - 提供的类有: date,time,datetime,timedelta,tzinfo。
    - 日期和时间datetime.date.today()
    """
    pass

  def update_and_bk_file(self,
                         fname='/Users/wangjinlong/my_server/my/db_all.json',
                         fname_bk='/Users/wangjinlong/my_server/my/db_all.bk.json',
                         bk_days=3):
    """如果需要备份的文件超过三天没有备份, 则备份

    Args:
        fname (str, optional): _description_. Defaults to '/Users/wangjinlong/my_server/my/db_all.json'.
        fname_bk (str, optional): _description_. Defaults to '/Users/wangjinlong/my_server/my/db_all.bk.json'.
        bk_day (int, optional): _description_. Defaults to 3.

    Returns:
        _type_: _description_
    """
    import os
    import shutil
    import ase.parallel
    time_now = datetime.datetime.now()
    file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(fname_bk))
    days = (time_now - file_mod_time).days
    if days > bk_days:
      shutil.copy(fname, fname_bk)
      ase.parallel.parprint(f'{fname} 已备份-> {fname_bk}')
    return None

  def date(self):
    # date 类
    # d1 = datetime.date(2011, 06, 03)  # date对象
    # d1.year、date.month、date.day：年、月、日；
    # d1.replace(year, month, day)：生成一个新的日期对象，用参数指定的年，月，日代替原有对象中的属性。（原有对象仍保持不变）
    # d1.timetuple()：返回日期对应的time.struct_time对象；
    # d1.weekday()：返回weekday，如果是星期一，返回0；如果是星期2，返回1，以此类推；
    # d1.isoweekday()：返回weekday，如果是星期一，返回1；如果是星期2，返回2，以此类推；
    # d1.isocalendar()：返回格式如(year，month，day)的元组；
    # d1.isoformat()：返回格式如'YYYY-MM-DD’的字符串；
    # d1.strftime(fmt)：和time模块format相同。
    pass

  def time(self):
    """ time 类
    """
    t1 = datetime.time(
        10, 23, 15)  # time对象t1.hour、t1.minute、t1.second、t1.microsecond：时、分、秒、微秒；
    # t1.tzinfo：时区信息；
    # t1.replace([ hour[ , minute[ , second[ , microsecond[ , tzinfo] ] ] ] ] )：创建一个新的时间对象，用参数指定的时、分、秒、微秒代替原有对象中的属性（原有对象仍保持不变）；
    # t1.isoformat()：返回型如"HH:MM:SS"格式的字符串表示；
    # t1.strftime(fmt)：同time模块中的format；
    pass

  def datetime(self):
    """ datetime 类  datetime 相当于date和time结合起来。
    """
    #
    # dt=datetime.now()#datetime对象
    # dt.year、month、day、hour、minute、second、microsecond、tzinfo：
    # dt.date()：获取date对象；
    # dt.time()：获取time对象；
    # dt. replace ([ year[ , month[ , day[ , hour[ , minute[ , second[ , microsecond[ , tzinfo] ] ] ] ] ] ] ])：
    # dt. timetuple ()
    # dt. utctimetuple ()
    # dt. toordinal ()
    # dt. weekday ()
    # dt. isocalendar ()
    # dt. isoformat ([ sep] )
    # dt. ctime ()：返回一个日期时间的C格式字符串，等效于time.ctime(time.mktime(dt.timetuple()))；
    # dt. strftime (format)

    datetime.date.today()  # ：返回一个表示当前本地日期的date对象；
    # datetime.date.fromtimestamp(timestamp) # ：根据给定的时间戮，返回一个date对象；

    print(datetime.datetime.now().strftime("%d"))
    print(datetime.datetime.now())

    print(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))
    pass

  def find_weekday2(self, start_date, end_date, weekday_num=1):

    # 将字符串日期转换为datetime对象
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # 存储所有星期二的日期
    weekday_list = []

    # 从开始日期遍历到结束日期
    current_date = start_date
    while current_date <= end_date:
      # 如果是星期二（weekday() 返回 1 表示星期二）
      if current_date.weekday() == weekday_num:
        weekday_list.append(current_date.strftime('%Y-%m-%d'))
      # 日期加一天
      current_date += datetime.timedelta(days=1)

    return weekday_list

  def find_weekday(self, start_date='2024-9-2', num_weeks=12, weekday_num=1,):
    # 将字符串日期转换为datetime对象
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    # 存储每周星期二的日期
    tuesdays = []

    for week in range(num_weeks):
      tuesday_date = start_date + \
          datetime.timedelta(weeks=week, days=weekday_num)
      tuesdays.append(tuesday_date.strftime('%m-%d'))

    return tuesdays

  def find_weekday_wrapper(self, weekday_num_list=[0, 2]):
    weekday_list = []
    for weekday_num in weekday_num_list:
      weekday = self.find_weekday(weekday_num=weekday_num)
      weekday_list.extend(weekday)
    weekday_list.sort()
    return weekday_list

  def get_select_days(self):
    # 起始日期
    start_date = datetime.datetime(2025, 2, 17)

    select_day_list = []
    # 输出每周周一和周五的日期
    for week in range(12):
        # 计算当前周的周一和周五
      monday = start_date + \
          datetime.timedelta(weeks=week, days=(
              0 - start_date.weekday()))  # 当前周的周一
      friday = monday + datetime.timedelta(days=4)  # 当前周的周五
      select_day_list.extend([monday, friday])
    return select_day_list

  def timer(self, func):
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

  def timer_no_return(self, func):
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
