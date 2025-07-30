from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

web = Chrome()

# web.get("http://lagou.com")
# web.find_element_by_xpath('//*[@id="cboxClose"]').click()
# time.sleep(1)
# web.find_element_by_xpath('//*[@id="search_input"]').send_keys("python", Keys.ENTER)
# time.sleep(1)
# web.find_element_by_xpath('//*[@id="s_position_list"]/ul/li[1]/div[1]/div[1]/div[1]/a/h3').click()


# 如何进入到进窗口中进行提取  # 注意, 在selenium的眼中. 新窗口默认是不切换过来的.
"""
web.switch_to.window(web.window_handles[-1])  #切换到最后一个窗口-1 #  窗口句柄web.window_handles
job_detail = web.find_element_by_xpath('//*[@id="job_detail"]/dd[2]/div').text # 在新窗口中提取内容
print(job_detail)
web.close() # 关掉子窗口
web.switch_to.window(web.window_handles[0]) # 变更selenium的窗口视角. 回到原来的窗口中
"""

# 如果页面中遇到了 iframe如何处理
# 处理iframe的话. 必须先拿到iframe. 然后切换视角到iframe . 再然后才可以拿数据
"""
web.get("https://www.91kanju.com/vod-play/541-2-1.html")
iframe = web.find_element(By.XPATH, '//*[@id="player_iframe"]')  # 找到iframe 元素
web.switch_to.frame(iframe)  # 切换到iframe
tx = web.find_element(By.XPATH, '//*[@id="main"]/h3[1]').text
print(tx)
# web.switch_to.default_content()  # 切换回原页面
"""

