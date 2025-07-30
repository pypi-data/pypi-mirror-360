from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# Selenium中对滑块的操作基本是采用元素拖拽的方式，而这种方式需要用到Selenium的Actionchains功能模块的drag_and_drop_by_offset方法
from selenium.webdriver.common.action_chains import ActionChains
import time

# selenium 被网页识别了怎么办， 对于12306网站来说，滑动滑块后一直出错，进不了下一步，
# 反爬升级：2.chrome的版本大于等于88时可以进行如下操作
option = Options()
# option.add_experimental_option('excludeSwitches', ['enable-automation'])  #这句可以不加，主要是下面那一句
option.add_argument('--disable-blink-features=AutomationControlled')

# web = Chrome()  # 不带参数打开
web = Chrome(options=option)  # 带参数打开， 虽然页面上还是会显示chrome正受自动化软件控制，但拖动滑块后可以进入

# url='https://www.12306.cn/index/'
url = 'https://kyfw.12306.cn/otn/resources/login.html'
web.get(url)

time.sleep(2)
# 点击账号登陆
web.find_element(By.XPATH, '//*[@id="toolbar_Div"]/div[2]/div[2]/ul/li[1]/a').click()

# 输入用户名和密码
web.find_element(By.XPATH, '//*[@id="J-userName"]').send_keys('18790518707')
web.find_element(By.XPATH, '//*[@id="J-password"]').send_keys('1011320sr')

# 点击立即登陆
web.find_element(By.XPATH, '//*[@id="J-login"]').click()
time.sleep(3)  # 加载页面验证码

# Selenium自动化时滑块验证处理
web.maximize_window()  # 页面最大化
slider = web.find_element(By.XPATH, '//*[@id="nc_1_n1z"]')
# print(slider.size['width']) # 打印出滑块的宽度和高度 40
# print(slider.size['height']) # 34
slider_area = web.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
# print(slider_area.size['width'])  # 打印出滑动条的宽度和高度  340
# print(slider_area.size['height']) # 34
# 拖动滑动条的，并执行，别忘了perform()  前面是定义了事件链(计划)，perform()是开始执行
ActionChains(web).drag_and_drop_by_offset(slider, slider_area.size['width'], slider_area.size['height']).perform()
# ActionChains(web).drag_and_drop_by_offset(slider, 300, 0).perform() # 直接写数值也可以
time.sleep(2)
# 相关的或类似的操作还有
# 要让鼠标移动到某一个位置. 然后进行点击
# 醒了 -> 掀开被子 -> 坐起来 -> 穿鞋子  -> 穿衣服  -> 开始执行动作
# ActionChains(web).move_to_element_with_offset(verify_img_element, x, y).click().perform()

# 进入页面后，需要点击确定
# web.find_element(By.XPATH, '//*[@id="pop_163610888512379082"]/div[2]/div[3]/a').click() # 由于该Xpath会变故不能用
web.find_element(By.TAG_NAME, 'div').find_element(By.CLASS_NAME, 'modal-ft').find_element(By.TAG_NAME,
                                                                                          'a').click()  # 可以多次使用
print('ok')

'''
另外窗口的切换 和iframe的切换键03_..py
验证码的破解，暂时先用超级鹰
'''

