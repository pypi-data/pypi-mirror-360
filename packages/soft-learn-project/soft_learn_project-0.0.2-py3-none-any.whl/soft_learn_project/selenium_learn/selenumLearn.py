from selenium.webdriver import ChromeOptions
from selenium import webdriver
import json
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options


class SeleniumLearn():
  def __init__(self, is_headless=True) -> None:
    """_summary_
    """
    # 实例化对象
    option = ChromeOptions()
    option.add_experimental_option(
        'excludeSwitches', ['enable-automation'])  # 开启实验性功能
    # 去除特征值
    option.add_argument("--disable-blink-features=AutomationControlled")
    # 无头, 这是必需的
    if is_headless:
      option.add_argument("--headless")

    self.driver = webdriver.Chrome(options=option)

  def get_page_source(self, url):
    self.driver.get(url=url)
    page_source = self.driver.page_source
    return page_source

  def get_citation_info_str(self, page_source):
    import re
    pattern = re.compile(pattern=r'>(@.*?}\n)</pre', flags=re.S)
    citation_info_str = pattern.search(page_source).group(1)
    return citation_info_str


class muchongHongbao():
  def __init__(self) -> None:
    pass

  def muchong(self):
    # 小木虫网站领取每日红包

    # 解决反爬
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--headless')

    # 1. 获得cookie 并保存为文件
    """
    # 打开小木虫
    web = Chrome(options=options)
    web.get("http://muchong.com/bbs/index.php")
    time.sleep(30)  # 在30秒内登陆用户，并通过下面的命令保存cookies

    # 获取cookies
    with open('cookies.txt', 'w') as f:
        # 将cookies保存为json格式
        f.write(json.dumps(web.get_cookies()))

    web.close()
    quit()
    # """

    cookies = '[{"domain": ".muchong.com", "expiry": 1668517676, "httpOnly": false, "name": "_discuz_pw", "path": "/", "secure": false, "value": "23b4838526ffe85d"}, {"domain": ".muchong.com", "expiry": 1668517676, "httpOnly": false, "name": "_discuz_uid", "path": "/", "secure": false, "value": "674885"}, {"domain": ".muchong.com", "httpOnly": false, "name": "Hm_lpvt_2207ecfb7b2633a3bc5c4968feb58569", "path": "/", "secure": false, "value": "1636981679"}, {"domain": ".muchong.com", "expiry": 1636982261, "httpOnly": false, "name": "_gat", "path": "/", "secure": false, "value": "1"}, {"domain": ".muchong.com", "httpOnly": false, "name": "_emuch_index", "path": "/", "secure": false, "value": "1"}, {"domain": ".muchong.com", "expiry": 1700053679, "httpOnly": false, "name": "_ga", "path": "/", "secure": false, "value": "GA1.2.488334736.1636981661"}, {"domain": ".muchong.com", "expiry": 1668517679, "httpOnly": false, "name": "Hm_lvt_2207ecfb7b2633a3bc5c4968feb58569", "path": "/", "secure": false, "value": "1636981661"}, {"domain": "muchong.com", "expiry": 1636983460, "httpOnly": true, "name": "acw_tc", "path": "/", "secure": false, "value": "2760827016369816603616585ee7d8079d762f68c34ac6b55e1428a5b63885"}]'

    # 2. 带 cookie 的登陆
    web = Chrome(options=options)
    web.get("http://muchong.com/bbs/index.php")

    cookie_lst = json.loads(cookies)
    for cookie in cookie_lst:
      if 'expiry' in cookie:
        del cookie['expiry']
      web.add_cookie(cookie)

    web.refresh()  # 让浏览器自动刷新，即可显示登录后的页面了。

    # 3. 点击红包
    hb = web.find_element(
        By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/ul/div/li[6]/a")
    hb.click()
    time.sleep(1)

    # 4. 点击领取红包
    try:
      web.find_element(
          By.XPATH, "/html/body/div[4]/div[5]/div[3]/dl/table/tbody/tr/td[2]/form/input[6]").click()
    except:
      print("该程序已经执行！")
    finally:
      print("小木虫网站领取每日红包已经领取啦！")

    web.close()
