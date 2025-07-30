from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options  # 无头浏览器需要这个包
from selenium.webdriver.support.select import Select  # 对元素进行包装, 包装成下拉菜单
import time
from selenium.webdriver.common.by import By

# 准备好参数配置，无头浏览器的参数
opt = Options()
opt.add_argument("--headless")  # 无头 # 这是必需的
# opt.add_argument("--disable-gpu")  # 不用显卡就是不显示

web = Chrome(options=opt)  # 把参数配置设置到浏览器中, 就可以无头爬取数据了
web.get("https://www.endata.com.cn/BoxOffice/BO/Year/index.html")
time.sleep(2)

# 对网页中下拉列表的处理，需要包 from selenium.webdriver.support.select import Select
"""
sel_el = web.find_element_by_xpath('//*[@id="OptionDate"]')   # 定位到下拉列表
sel = Select(sel_el)   # 对元素进行包装, 包装成下拉菜单
# 让浏览器进行调整选项
for i in range(len(sel.options)):  # i就是每一个下拉框选项的索引位置
    sel.select_by_index(i)  # 按照索引进行切换
    time.sleep(2)
    table = web.find_element(By.XPATH, '//*[@id="TableList"]/table')
    print(table.text)  # 打印所有文本信息
    print("===================================")

print("运行完毕.  ")
web.close()
"""

# 如何拿到页面代码Elements(经过数据加载以及js执行之后的结果的html内容)
print(web.page_source)

"""
# selenium 处理反爬
from selenium.webdriver.chrome.options import Options
option = Options()
# option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_argument('--disable-blink-features=AutomationControlled')
"""
