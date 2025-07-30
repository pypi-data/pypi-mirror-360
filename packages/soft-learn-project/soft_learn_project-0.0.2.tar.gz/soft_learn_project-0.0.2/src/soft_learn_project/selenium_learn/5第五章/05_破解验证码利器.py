# 1. 图像识别
# 2. 选择互联网上成熟的验证码破解工具

import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from myown.chaojiying_Python.chaojiying import Chaojiying_Client
# 调入类Chaojiying_Client, 由于引入了chaojiying包，网页在打开后，会自己关闭，还不清楚原因

url = "http://www.chaojiying.com/user/login/"
web = Chrome()
web.get(url)
# web.close()

# 先处理验证码
img = web.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div[1]/form/div/img').screenshot_as_png  # 拿到图片字节
chaojiying = Chaojiying_Client('wangjl580', '1011320sr', '924488')  # 用户中心>>软件ID 生成一个替换 96001
dic = chaojiying.PostPic(img, 1902)
verify_code = dic['pic_str']

# 填入信息
web.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div[1]/form/p[1]/input').send_keys('wangjl580')
web.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div[1]/form/p[2]/input').send_keys('1011320sr')
web.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div[1]/form/p[3]/input').send_keys(verify_code)

time.sleep(5) #查看是否正确
# 点击登陆
web.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div[1]/form/p[4]/input').click()
time.sleep(10)

