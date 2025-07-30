import requests
import re
import csv
import json


class RequestsLearn():
  def __init__(self) -> None:
    pass

  def douban_example(self,
                     fname_out='data.csv'):
    """1. 拿到源代码  request,
    2. 通过re来提取需要的信息

    Args:
        fname_out (str, optional): _description_. Defaults to 'data.csv'.
    """
    url = "https://movie.douban.com/top250"

    # 注意：headers中有很多内容，主要常用的就是user-agent 和 host，
    # 他们是以键对的形式展现出来，如果user-agent 以字典键对形式作为headers的内容，就可以反爬成功，就不需要其他键对；
    # 否则，需要加入headers下的更多键对形式。
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        'Connection': 'keep-alive', 'Keep-Alive': 'timeout=3',
    }

    # ,verify=False) #如果出现SSLError可以尝试使用取消安全验证
    with requests.get(url, headers=headers) as resp:
      # print(resp.headers) #取得服务器返回来的请求头:
      # print(resp.request.headers)  #获得我们发送的请求头:
      # resp.encoding = 'gb2312'  # 指定字符集，要与页面的源代码中的charset=gb2312 一致
      page_content = resp.text  # 获得页面内容

    # 解析数据
    obj = re.compile(r'<li>.*?<span class="title">(?P<name>.*?)</span>'
                     r'.*?<p class="">.*?<br>(?P<year>.*?)&nbsp.*?'
                     r'<span class="rating_num" property="v:average">(?P<rating>.*?)</span>'
                     r'.*?<span>(?P<num>.*?)人评价</span>', re.S)
    # 开始匹配
    result = obj.finditer(page_content)

    # 用写入列表的形式
    with open(fname_out, mode='w') as f:
      csvwriter = csv.writer(f)
      head = ['name', 'year', 'rating', 'num']  # 不要用大括号，因为字典在写入的时候顺序随机
      csvwriter.writerow(head)
      for it in result:
        # print(it.group("name")) # 返回的是值
        # print(it.groups()) # 返回的是值元组
        dic = it.groupdict()  # 返回的是字典
        dic['year'] = dic['year'].strip()  # 对年份处理  前面有空格
        csvwriter.writerow(dic.values())  # 写入的是字典的值
    print('over')

  def dytt_example(self,):
    """# 1. 定位到2021必看片
      # 2. 从中提取到子页面的链接地址
      # 3. 请求子页面的链接地址，拿到下载地址和电影名
    """

    domain = "https://www.dytt89.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
    }

    # ,verify=False) #去掉安全验证，如果出现SSLError可以尝试使用取消验证
    resp = requests.get(domain, headers=headers)
    resp.close()
    resp.encoding = 'gb2312'  # 指定字符集，要与页面的源代码中的charset=gb2312 一致
    # print(resp.text)

    obj1 = re.compile(r'2021必看热片.*?<ul>(?P<ul>.*?)</ul>', re.S)

    # 拿到ul里面的li
    result1 = obj1.finditer(resp.text)
    for it in result1:
      ul = it.group('ul')

    obj2 = re.compile(r"<li><a href='(?P<href>.*?)' title=", re.S)
    result2 = obj2.finditer(ul)
    href = []
    for it in result2:
      href.append(it.group('href'))

    sub_url = []
    for i in range(len(href)):
      sub_url.append(domain + href[i])

    for i in sub_url:
      resp = requests.get(i, headers=headers)
      resp.encoding = 'gb2312'
      # print(resp.text)
      resp.close()
      obj3 = re.compile(r'<div class="co_area2">.*?<h1>(?P<h1>.*?)</h1>.*?'
                        r'<td style="WORD-WRAP: break-word" bgcolor="#fdfddf">.*?<a href="(?P<download>.*?)"', re.S)
      # r'<div class=player_list>.*?<a href="(?P<download>.*?)">', re.S)

      result = obj3.finditer(resp.text)
      with open('data1.csv', mode='a+') as f:
        csvwriter = csv.writer(f)
        for it in result:
          #     h1=it.group('h1')
          #     download=it.group('download')
          #     print(h1,download)
          dic = it.groupdict()
          csvwriter.writerow(dic.values())
          print(dic.values())

  def dynamics_cookies(self,):
    # 对于动态 cookie 暂时没什么好办法，只有不能用的时候就换cookie吧
    # 获得 cookie 内容
    with open('cookies.txt', mode='r') as f:
      lis = json.loads(f.read())
      cookie_lis = []
      for li in lis:
        name = li['name']
        value = li['value']
        cookie = name + '=' + value
        cookie_lis.append(cookie)
      cookies = "; ".join(cookie_lis)

    # cookies 放入 headers 获取页面内容
    url = "https://www.zhipin.com/job_detail/?query=python&city=100010000&industry=&position="
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Cookie": cookies,
    }
    with requests.get(url, headers=headers) as resp:
      content = resp.content.decode()

  def sevideo(self):
    import requests
    from lxml import etree
    import re
    from concurrent.futures import ThreadPoolExecutor
    import asyncio
    import aiohttp
    import aiofiles
    import os
    import random
    import time
    import glob
    import argparse

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    }

    def get_urls(base_url):
      """
      注释：获取子urls_list 播放页面的列表
      @param base_url:
      @return:  获取子urls_list 播放页面的列表2
      """
      headers = {
          "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
      }
      with requests.get(base_url, headers=headers) as resp:
        resp = resp.content.decode('utf-8')
        # print(resp)
        tree = etree.HTML(resp)
        # print(tree)

      url_lst = tree.xpath(_path="/html/body/div[11]/div[5]/ul/li/a/@href")
      # urls = "https://tom3227.com/guochanzipai/2021-11-16/513713.html"
      #     yesterday = get_yesterday()
      # print(yesterday)
      urls_list = []
      for url in url_lst:
        date = url.rsplit('/', 2)[1]
        #         if date == yesterday:
        url = url.rsplit('/guochanzipai/')[1]
        url = base_url + url
        urls_list.append(url)

      return urls_list

    def get_m3u8(url, headers, name_m3u8="./m3u8/m3u8.m3u8"):
      """
      url: # 播放视频的url
      下载m3u8,并返回url_m3u8网址，下载ts文件的时候需要用
      @param url_list:
      @param headers:
      @param name_m3u8:
      @return: url_m3u8网址，下载ts文件的时候需要用
      """
      with requests.get(url=url, headers=headers) as resp:
        content = resp.content.decode()
        re_list = re.findall(r"url=(?P<url>.*?\.m3u8).*?",
                             content)  # 这是m3u8的网页列表
        url_m3u8 = re_list[0]
        obj_name = re.findall("<title>(.*?)</title>", content)[0]
        #  4.30 我发现获得的url_m3u8 网址不对，故使用下面命令更改
        pattten = re.compile(r"saohu191")
        url_m3u8 = pattten.sub(repl="tom802", string=url_m3u8)
      # 下载m3u8文件
      with requests.get(url=url_m3u8, headers=headers) as resp:
        with open(file=f"{name_m3u8}", mode="w") as f:
          f.write(resp.text)
      print(f"下载m3u8文件完毕:{name_m3u8}")
      return url_m3u8, obj_name

    def get_m3u8_saohu(url):
      """
      骚虎视频的url
      返回url_m3u8, 和视频名字
      @param url:
      @return:
      """
      with requests.get(url=url, headers=headers) as resp:
        content = resp.content.decode("utf-8")

      obj_name = re.findall(r"<title>(.*?)</title>", content)[0]  # 播放视频的名字
      url_m3u8 = re.findall(r"url=(https://.*?\.m3u8)&play", content)[0]
      print(url_m3u8, obj_name)

      # 下载m3u8文件
      name_m3u8 = "./m3u8/m3u8.m3u8"
      with requests.get(url=url_m3u8, headers=headers) as resp:
        with open(file=f"{name_m3u8}", mode="w") as f:
          f.write(resp.text)
      print(f"下载m3u8文件完毕:{name_m3u8}")
      return url_m3u8, obj_name

    # 首先定义(协程形式的)单个下载任务

    async def download_ts(url_ts, name_ts, number_of_tasks):
      """
      定义(协程形式的)单个下载任务
      @param url_ts:
      @param name_ts:
      @return: None
      """
      try:
        async with aiohttp.ClientSession() as session:
          async with session.get(url=url_ts, ssl=False) as resp:
            async with aiofiles.open(name_ts, mode="wb") as f:
              # 之前是resp.content 异步需要这样写resp.content.read()
              await f.write(await resp.content.read())
            print(f"{name_ts}-->下载完毕! 还剩余{number_of_tasks}个")
      except FileNotFoundError:
        print(f"{name_ts} 不能下载!")
      except Exception:
        pass
      #
      # async with aiohttp.ClientSession() as session:
      #     async with session.get(url=url_ts, ssl=False) as resp:
      #         try:
      #             async with aiofiles.open(name_ts, mode="wb") as f:
      #                 await f.write(await resp.content.read())  # 之前是resp.content 异步需要这样写resp.content.readd()
      #             print(f"{name_ts}-->下载完毕!")
      #         except FileNotFoundError:
      #             print(f"{name_ts} 不能下载!")
      #         except Exception:
      #             pass

    # 创建协程任务列表

    async def aio_tasks(url_m3u8, path, number_of_tasks, name_m3u8="./m3u8/m3u8.m3u8"):
      tasks = []
      async with aiofiles.open(file=name_m3u8, mode="r") as f:
        async for line in f:
          if line.startswith("#") or line.endswith("header.ts"):
            continue
          else:
            line = line.strip()  # 去掉空白或者换行符  hls/index.m3u8
            # print(line)
            url_ts = url_m3u8.rsplit(
                sep="/", maxsplit=1)[0] + "/" + line  # 获得ts的url
            name_ts = path + line

            if not os.path.exists(name_ts):  # or not os.path.getsize(name_ts):
              number_of_tasks -= 1
              task = asyncio.create_task(
                  download_ts(url_ts=url_ts, name_ts=name_ts, number_of_tasks=number_of_tasks))
              tasks.append(task)

        await asyncio.wait(tasks)

    def number_tasks(name_m3u8="./m3u8/m3u8.m3u8"):
      """
      测算任务的总数
      @param name_m3u8:
      @return: 测算任务的总数(int)
      """
      with open(file=name_m3u8, mode='r') as f:
        i = 0
        for line in f:
          if line.startswith("#"):
            continue
          else:
            i += 1
        return i

    def merge_ts(name_m3u8, path, obj_name):
      """
      合并ts文件
      # mac: cat 1.ts 2.ts 3.ts > xxx.mp4
      # windows: copy /b 1.ts+2.ts+3.ts xxx.mp4
      @return:
      """
      print("开始合并...")
      lst = []
      file_list = glob.glob("./video/*ts")
      with open(file=name_m3u8, mode="r", encoding="utf-8") as f:
        for line in f:
          if line.startswith("#") or line.endswith("headers.ts"):
            continue
          line = path + line.strip()
          if line in file_list:
            lst.append(line)

      s = " ".join(lst)  # 1.ts 2.ts 3.ts
      os.system(f"cat {s} > '{obj_name}'")
      print("合并完成！")

    def ts_delete(path):
      print("删除ts文件...")
      ts_list = glob.glob(f"{path}*ts")
      for ts in ts_list:
        os.remove(ts)
      print("搞定!")

    def main(video_url=None, i=0):
      """

      @return:
      """
      # 1. 获取子urls_list 播放页面的列表
      urls_list = get_urls(base_url="https://2685saohu.com/guochanzipai/")
      print(urls_list[:4])

      # 2. 从播放页面的列表选择其中一个视频的url获取其m3u8网址并保存为m3u8文件
      if video_url:
        url = video_url
      else:
        url = urls_list[i]  # 播放视频的url

      if "2625saohu.com" in url.split("/"):  # 如果播放视频为骚虎视频则使用不同的函数
        url_m3u8, obj_name = get_m3u8_saohu(url)
      else:
        url_m3u8, obj_name = get_m3u8(url=url, headers=headers)

      # print(url_m3u8)
      # exit()
      # 3. 定义下载一个ts文件的异步协程函数
      # download_ts(url_ts=,name_ts=)

      # 4. 异步协程下载
      number_of_tasks = number_tasks()
      obj_name = "".join(obj_name.split())  # 去掉标题中的空格
      print(f"正在下载:{obj_name}\n, 总共有{number_of_tasks}个任务")
      path = "./video/"
      asyncio.run(aio_tasks(url_m3u8=url_m3u8, path=path,
                  number_of_tasks=number_of_tasks))

      # 5. 合并文件
      merge_ts(name_m3u8="./m3u8/m3u8.m3u8", path=path,
               obj_name=f"./video/{obj_name}.mp4")

      # 6. 删除*ts
      ts_delete(path=path)

    def args_add():
      ap = argparse.ArgumentParser(usage="下载视频", description="输入网址即可")
      ap.add_argument("-u", "--url", required=True, help="视频所在的网址")
      args = ap.parse_args()
      return args.url

    if __name__ == '__main__':
      time_start = time.time()
      print("开始运行...")
      video_url = 'https://2972saohu.com/video/info2/20574.html'

      video_url = args_add()
      main(video_url=video_url)
      time_end = time.time()
      print(f"耗时{round(time_end - time_start)}s")

    pass
