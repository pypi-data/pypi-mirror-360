#!/usr/bin/env python3

from sys import argv  # 外部传参
import argparse


class ArgparseLearn():
  def __init__(self) -> None:
    """# 有一点注意事项
    #  parser.add_argument("-i", "--is_down", help="是否下载：输入bools") help 中如果想加入%百分号, 需要使用%%，例如 4%%。
    """
    pass

  def example(self):
    """用法: python Cv.py -t '298.15' -O '30' -ol '[1,3,4]'
    """
    def calculate_C_v(Omega=1, omega_list=[1, 2, 3], T=298.15,):
      """使用振动频率计算材料的热容
      公式: k_B/Omega*np.sum((hbar*omega/(k_B*T))**2 *
                      np.exp(hbar*omega/(k_B*T)) *
                      (np.exp(hbar*omega/(k_B*T))-1)**(-2))
      Omega 是晶胞中的原子数,
      omega_list 是频率列表, 以Hz为单位？
      """
      from scipy import constants
      import numpy as np
      k_B = constants.Boltzmann
      hbar = constants.hbar
      omega = np.array(omega_list)
      C_v = k_B/Omega*np.sum((hbar*omega/(k_B*T))**2 *
                             np.exp(hbar*omega/(k_B*T)) *
                             (np.exp(hbar*omega/(k_B*T))-1)**(-2))
      return C_v

    if __name__ == '__main__':
      parser = argparse.ArgumentParser()
      parser.add_argument('-O', '--Omega', default=3, help='晶胞中的原子数')
      parser.add_argument('-ol', '--omega_list', default=[1e12,], help='频率列表')
      parser.add_argument('-t', '--temperature', default=298.15, help='温度')
      args = parser.parse_args()
      omega_list = args.omega_list
      temperature = args.temperature
      Omega = args.Omega

      C_v = calculate_C_v(Omega=float(Omega),
                          omega_list=eval(omega_list),
                          T=float(temperature),)
      print(f'热容为: {C_v}')

  def old_str(self):
    """
    #  外部传参的推荐方法
    if __name__ == '__main__':
      # 1. 实例化ArgumentParser这个类
      parser = argparse.ArgumentParser(usage='示例程序', description="参数说明")
      # python3 py文件.py --help or -h 输入后会显示description 和下面的参数help

      # 2. 调用ArgumentParser这个类里的add_argument方法
      parser.add_argument("-t", "--title_article", help="文章标题")
      parser.add_argument("-i", "--is_down", help="是否下载：输入bools")

      # 3. 调用ArgumentParser类里的parse_arg方法。会返回一个类，包含若干属性，这个属性就是我们传进去的参数的值。
      args = parser.parse_args()  # type: argparse.Namespace

      # 4. 提取这个类中的属性，并赋值给相应的变量
      title_article = args.title_article
      is_down = args.is_down

      print(title_article, is_down)

      #  也可以这样提取属性
      args_dict = vars(args)  # vars() 函数返回对象object的属性和属性值的字典对象。
      title_article = args_dict["title_article"]
      print(args_dict)
      print(title_article)
      print("*"*50)
      exit()
    # ----

    # 外部传参的方法， 这样也可以
    _, title_article, is_down = argv
    main(title_article, is_down)

    # 参数
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--shape-predictor", default="./shape_predictor_68_face_landmarks.dat",
                    help="path to facial landmark predictor")
    ap.add_argument("-i", "--image", default="images/liudehua.jpg",  # required=True, 如果增加这个参数, 则终端必须给定 -i
                    help="path to input image")
    args = vars(ap.parse_args())  # 输出是一个字典  # vars() 函数返回对象object的属性和属性值的字典对象。

    # 在终端运行可以改变参数
    # $ python3 argparse_learn.py -p "./shape_predictor_68_face_landmarks.dat" -i "images/liudehua.jpg"

    if __name__ == '__main__':
      print("这是第一个参数:", args["shape_predictor"])
      print("这是第二个参数:", args["image"])
      # print(type(args), args)
      print(type(ap.parse_args()), ap.parse_args())

    #
    """
