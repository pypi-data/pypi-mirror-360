# https://www.bilibili.com/video/av38512783/?p=12&spm_id_from=pageDriver 数据挖掘中的学习
import numpy as np
from matplotlib import pyplot as plt
import random

# 添加中文支持 'Source Han Sans SC', 'Songti SC', 'Heiti TC','Source Han Sans SC'
plt.rcParams["font.family"] = ["HeiTi TC"]

# Matplotlib三层结构
"""  可以参见:
#  path = "/Users/wangjinlong/my_linux/soft_learn/python3_learn/mylearn/Python_data_mining数据挖掘基础教程资料/day1资料/03-资料/Matplotlib总结.pdf"
1）容器层
    画板层Canvas
    画布层Figure: 画布层plt.figure(figsize=, dpi=)
    绘图区/坐标系: 绘图区/坐标系figure, axes = plt.subplots(nrows=, ncols=, figsize=, dpi=)
        x、y轴张成的区域
2）辅助显示层：修改x, y轴刻度plt.x/yticks(); 添加描述信息plt.x/ylabel(); plt.title(); 显示图例plt.legend(); 添加⽹格plt.grid()
3）图像层: 图像层(可以设置图像颜⾊、⻛格、标签等)-> 包含五种图形，折线图，hist,bar,...
# """
#
# 常见图形种类及意义
"""
1. 折线图plot
2. 散点图scatter
    关系/规律
3. 柱状图bar
    统计/对比
4. 直方图histogram
    分布状况
5. 饼图pie π
    占比
# """


# 面向过程的绘图方法
"""
# 需求：画出某城市11点到12点1小时内每分钟的温度变化折线图，温度范围在15度~18度
# 1、准备数据 x y
x = range(60)
y_shanghai = [random.uniform(15, 18) for i in x]
y_beijing = [random.uniform(1,5) for i in x]

# 2、创建画布
plt.figure(figsize=(12, 8), dpi=80)

# 3、绘制图像
plt.plot(x, y_shanghai, color="r", linestyle="--", label="上海")
plt.plot(x, y_beijing, color="b", label="北京")  # 修改颜色color,

# 显示图例
plt.legend(loc="best")  # 默认的位置为best,

# 修改x、y刻度
# 准备x的刻度说明
x_label = ["11点{}分".format(i) for i in x]
plt.xticks(x[::5], x_label[::5])
plt.yticks(range(0, 40, 5))

# 添加网格显示
plt.grid(linestyle="--", alpha=0.5)

# 添加描述信息
plt.xlabel("时间变化")
plt.ylabel("温度变化")
plt.title("某城市11点到12点每分钟的温度变化状况")

# 保存图片
plt.savefig("./cs_城市温度2.pdf", dpi=80, bbox_inches='tight')
print("保存完毕")
quit()
# 4、显示图
plt.show()
# """

# 面向对象的绘图方法: 多个坐标系这个时候就需要用到面向对象的绘图方法
# """
# 需求：再添加一个城市的温度变化
# 收集到北京当天温度变化情况，温度在1度到3度。

# 1、准备数据 x y
x = range(60)
y_shanghai = [random.uniform(15, 18) for i in x]
y_beijing = [random.uniform(1, 3) for i in x]

# 2、创建画布
# plt.figure(figsize=(20, 8), dpi=80)
figure, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 8),
                            dpi=80)  # subplot()方法会返回两个对象，一个图对象，一个绘图区
figure:plt.Figure
axes: plt.Axes

# 3、绘制图像
axes[0].plot(x, y_shanghai, color="r", linestyle="-.", label="上海")
axes[1].plot(x, y_beijing, color="b", label="北京")

# 显示图例
axes[0].legend()
axes[1].legend()

# 修改x、y刻度
# 准备x的刻度说明
x_label = ["11点{}分".format(i) for i in x]
axes[0].set_xticks(x[::5])
axes[0].set_xticklabels(x_label[::5])   # axes[0].set_xticks(x[::5], x_label[::5])  或者直接这样写
axes[0].set_yticks(range(0, 40, 5))

axes[1].set_xticks(x[::5])
axes[1].set_xticklabels(x_label[::5])
axes[1].set_yticks(range(0, 40, 5))

# 添加网格显示
axes[0].grid(linestyle="--", alpha=0.5)
axes[1].grid(linestyle="--", alpha=0.5)

# 添加描述信息
axes[0].set_xlabel("时间变化")
axes[0].set_ylabel("温度变化")
axes[0].set_title("上海11点到12点每分钟的温度变化状况")
axes[1].set_xlabel("时间变化")
axes[1].set_ylabel("温度变化")
axes[1].set_title("北京11点到12点每分钟的温度变化状况")

# 4、显示图
plt.show()
# """
# 以上是绘制折线图，折线图的应用场景: 某事物、某指标随时间的变化状况

# 绘制数学函数图像，拓展：画各种数学函数图像
"""
x = np.linspace(-10,10,200)  # 左闭右闭，np.range() 左闭右开
y = np.sin(x)

# 2、创建画布
# plt.figure(figsize=(20, 8), dpi=80)
figure, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 8),
                            dpi=80)  # subplot()方法会返回两个对象，一个图对象，一个绘图区
figure:plt.Figure
axes: plt.Axes

# 3、绘制图像
axes.plot(x,y, linestyle=":", label="Sin")

# 显示图例
axes.legend()

# 修改x、y刻度
# x_label = [str(i/np.pi) for i in x]  # 准备x的刻度说明
axes.set_xticks([-np.pi, 0, np.pi])
axes.set_xticklabels([r'$-\pi$', r'$0$', r'$+\pi$'])   # axes[0].set_xticks(x[::5], x_label[::5])  或者直接这样写
# axes.set_yticks(range(0, 1, 5))

# 添加网格显示
axes.grid(linestyle="--", alpha=0.5)

# 添加描述信息
axes.set_xlabel("时间变化")
axes.set_ylabel("温度变化")
axes.set_title("变化")

# 4、显示图
plt.show()
# """

# 柱状图
"""
# 1、准备数据
movie_names = ['雷神3：诸神黄昏','正义联盟','东方快车谋杀案','寻梦环游记','全球风暴', '降魔传','追捕','七十七天','密战','狂兽','其它']
tickets = [73853,57767,22354,15969,14839,8725,8716,8318,7916,6764,52222]

# 2、创建画布
plt.figure(figsize=(16, 8), dpi=80)

# 3、绘制柱状图
x_ticks = range(len(movie_names))
plt.bar(x_ticks, tickets, color=['b','r','g','y','c','m','y','k','c','g','b'])

# 修改x刻度
plt.xticks(x_ticks, movie_names)

# 添加标题
plt.title("电影票房收入对比")

# 添加网格显示
plt.grid(linestyle="--", alpha=0.5)

# 4、显示图像
plt.show()
# """

# 紧挨着的柱状图
"""
# 1、准备数据
movie_name = ['雷神3：诸神黄昏','正义联盟','寻梦环游记']

first_day = [10587.6,10062.5,1275.7]
first_weekend=[36224.9,34479.6,11830]

# 2、创建画布
plt.figure(figsize=(10, 8), dpi=80)

# 3、绘制柱状图
plt.bar(range(3), first_day, width=0.2, label="首日票房")
plt.bar([0.2, 1.2, 2.2], first_weekend, width=0.2, label="首周票房")

# 显示图例
plt.legend()

# 修改刻度
plt.xticks([0.1, 1.1, 2.1], movie_name)

# 4、显示图像
plt.show()
# """

# 需求：电影时长分布状况 直方图
"""
# 1、准备数据
time = [131,  98, 125, 131, 124, 139, 131, 117, 128, 108, 135, 138, 131, 102, 107, 114, 119, 128, 121, 142, 127, 130, 124, 101, 110, 116, 117, 110, 128, 128, 115,  99, 136, 126, 134,  95, 138, 117, 111,78, 132, 124, 113, 150, 110, 117,  86,  95, 144, 105, 126, 130,126, 130, 126, 116, 123, 106, 112, 138, 123,  86, 101,  99, 136,123, 117, 119, 105, 137, 123, 128, 125, 104, 109, 134, 125, 127,105, 120, 107, 129, 116, 108, 132, 103, 136, 118, 102, 120, 114,105, 115, 132, 145, 119, 121, 112, 139, 125, 138, 109, 132, 134,156, 106, 117, 127, 144, 139, 139, 119, 140,  83, 110, 102,123,107, 143, 115, 136, 118, 139, 123, 112, 118, 125, 109, 119, 133,112, 114, 122, 109, 106, 123, 116, 131, 127, 115, 118, 112, 135,115, 146, 137, 116, 103, 144,  83, 123, 111, 110, 111, 100, 154,136, 100, 118, 119, 133, 134, 106, 129, 126, 110, 111, 109, 141,120, 117, 106, 149, 122, 122, 110, 118, 127, 121, 114, 125, 126,114, 140, 103, 130, 141, 117, 106, 114, 121, 114, 133, 137,  92,121, 112, 146,  97, 137, 105,  98, 117, 112,  81,  97, 139, 113,134, 106, 144, 110, 137, 137, 111, 104, 117, 100, 111, 101, 110,105, 129, 137, 112, 120, 113, 133, 112,  83,  94, 146, 133, 101,131, 116, 111,  84, 137, 115, 122, 106, 144, 109, 123, 116, 111,111, 133, 150]

# 2、创建画布
plt.figure(figsize=(20, 8), dpi=80)

# 3、绘制直方图
distance = 2
group_num = int((max(time) - min(time)) / distance)

plt.hist(time, bins=group_num, density=True)   # density 是否将频数变为频率

# 修改x轴刻度
plt.xticks(range(min(time), max(time) + 2, distance))

# 添加网格
plt.grid(linestyle="--", alpha=0.5)

# 4、显示图像
plt.show()
# """


# 绘制饼图
"""
# 1、准备数据
movie_name = ['雷神3：诸神黄昏','正义联盟','东方快车谋杀案','寻梦环游记','全球风暴','降魔传','追捕','七十七天','密战','狂兽','其它']

place_count = [60605,54546,45819,28243,13270,9945,7679,6799,6101,4621,20105]

# 2、创建画布
plt.figure(figsize=(20, 8), dpi=80)

# 3、绘制饼图
plt.pie(place_count, labels=movie_name, colors=['b','r','g','y','c','m','y','k','c','g','y'], autopct="%1.2f%%")

# 显示图例， 已经在绘图中给出labels了
plt.legend()

# 让饼图保持圆形
plt.axis('equal')

# 4、显示图像
plt.show()
# """
