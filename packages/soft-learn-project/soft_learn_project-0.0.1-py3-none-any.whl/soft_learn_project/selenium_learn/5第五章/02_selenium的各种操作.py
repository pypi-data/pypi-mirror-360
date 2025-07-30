from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # 输入键盘上的特殊按键需要导入这个模块，如ENTER，SPACE

import time

web = Chrome()

web.get("https://lagou.com")

# 找到某个元素. 点击它
"""
el = web.find_element_by_xpath('//*[@id="changeCityBox"]/ul/li[1]/a')
# el = web.find_element_by_xpath('//*[@id="changeCityBox"]/ul/li[1]/a').click()
el.click()  # 点击事件
"""
web.find_element(By.XPATH, '//*[@id="changeCityBox"]/ul/li[1]/a').click()

time.sleep(1)  # 让浏览器缓一会儿，最好用这个，以免程序运行太快，导致页面还没刷新，就进行下面的操作从而报错

# 找到输入框. 输入python  =>  输入回车/点击搜索按钮  
# 输入键盘上的按键需要 导入包from selenium.webdriver.common.keys import Keys
web.find_element(By.XPATH, '//*[@id="search_input"]').send_keys('python', Keys.ENTER)

time.sleep(1)

# 查找存放数据的位置. 进行数据提取
# 找到页面中存放数据的所有的li  web.find_elements_by_xpath
# li_list = web.find_elements_by_xpath('//*[@id="s_position_list"]/ul/li')  #elements 返回的是列表
li_list = web.find_elements(By.XPATH, '//*[@id="s_position_list"]/ul/li')
for li in li_list:
    job_name = li.find_element(By.TAG_NAME, 'h3').text
    job_price = li.find_element(By.XPATH, "./div/div/div[2]/div/span").text
    # job_price= li.find_element(By.CLASS_NAME,"money").text 这样也可以
    company_name = li.find_element(By.XPATH, './div/div[2]/div/a').text
    print(company_name, job_name, job_price)
