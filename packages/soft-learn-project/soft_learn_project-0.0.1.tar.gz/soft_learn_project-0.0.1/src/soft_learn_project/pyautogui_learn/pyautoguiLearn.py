import pyautogui
import time
import numpy as np


class Features():
  def __init__(self) -> None:
    """pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ pyautogui
    conda install -c conda-forge pyautogui

    print(pyautogui.KEY_NAMES) # 查看键盘的名字
    print(pyautogui.KEYBOARD_KEYS)
    pyautogui.PAUSE = 0.1 每次输入的等待时间 
    """
    pass

  def learn(self):
    """
    # 每个动作间隔0.5秒钟
    pyautogui.PAUSE = 0.5
    # pyautogui.FAILSAFE = True
    # 记事本打出时间
    pyautogui.press('f5')
    # 打入三行内容
    pyautogui.typewrite('\nhelo')
    pyautogui.typewrite('\nhelo')
    pyautogui.typewrite('\nhelo')

    # 按下Ctrl键
    pyautogui.keyDown('ctrl')
    # 按下a键，拷贝
    pyautogui.press('a')
    # 按下c键，复制
    pyautogui.press('c')
    # 松开Ctrl键
    pyautogui.keyUp('ctrl')
    # 鼠标点击记事本下方
    pyautogui.click(600, 600)
    # 输入两个空行
    pyautogui.typewrite('\n\n')
    # 粘贴
    pyautogui.hotkey('ctrl', 'v')
    """
    pass

  def enter_grade_one_row(self, values_list=[], pause=0.1):
    """用于网页上输入单行成绩成绩

    Args:
        values_list (list, optional): _description_. Defaults to [].
    """

    # 登陆成绩
    pyautogui.PAUSE = pause
    for value in values_list:
      pyautogui.typewrite(message=str(value))
      pyautogui.press(keys="tab", presses=1)

  def enter_grade(self,
                  df_dealed,
                  pingshi_score_name='mean',
                  qimo_score_name='期末',
                  second_for_sleep=3,
                  pyautogui_pause=0.2):
    """用于网页上输入成绩
    """

    print('登录成绩，准备开始...')
    pingshi = df_dealed[pingshi_score_name]
    qimo_score = df_dealed[qimo_score_name]
    time.sleep(second_for_sleep)
    # print(pyautogui.KEY_NAMES) # 查看键盘的名字
    # print(pyautogui.KEYBOARD_KEYS)
    pyautogui.PAUSE = pyautogui_pause
    for i in range(len(pingshi)):
      pyautogui.typewrite(str(pingshi[i]))
      pyautogui.press(keys="tab", presses=1)
      pyautogui.typewrite(str(qimo_score[i]))
      pyautogui.press(keys="tab", presses=1)
