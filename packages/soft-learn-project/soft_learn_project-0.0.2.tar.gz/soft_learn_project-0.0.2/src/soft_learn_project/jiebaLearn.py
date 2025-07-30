# %%
# 安装
# pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple jieba

# %%
import jieba.posseg as pseg
import jieba

# %% [markdown]
# ### 基本使用

# %%
content = "工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作"

# %%
# 将返回一个生成器对象
jieba.cut(content, cut_all=False)  # cut_all默认为False: 精确模式, True: 全模式分词

# %%
# 若需直接返回列表内容, 使用jieba.lcut即可
jieba.lcut(content, cut_all=False)[0:10]

# %%
# 搜索引擎模式分词 : 在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词.
jieba.cut_for_search(content)

# %%
jieba.lcut_for_search(content)[:10]

# %%
# 繁体字一样
content1 = "煩惱即是菩提，我暫且不提"
jieba.lcut(content1)

# %% [markdown]
# ### 使用用户自定义词典:

# %%
# 使用用户自定义词典:
jieba.lcut("八一双鹿更名为八一南昌篮球队！")
# 没有使用用户自定义词典前的结果:

# %%
# 使用了用户自定义词典后的结果
jieba.load_userdict("./userdict.txt")

# %%
jieba.lcut("八一双鹿更名为八一南昌篮球队！")

# %% [markdown]
# ### 使用jieba进行中文词性标注:
#
#
#

# %%
pseg.lcut("我爱北京天安门")
# [pair('我', 'r'), pair('爱', 'v'), pair('北京', 'ns'), pair('天安门', 'ns')]

# 结果返回一个装有pair元组的列表, 每个pair元组中分别是词汇及其对应的词性, 具体词性含义请参照[附录: jieba词性对照表]()

# %%
# 导入jieba 中的词性标注工具包

# 定义获取形容词的列表函数


def get_a_list(text):
  # 使用jieba的词性标注方法来切分文本, 获得两个属性word,flag
  # 利用flag属性去判断一个词汇是否是形容词
  r = []
  for g in pseg.lcut(text):
    if g.flag == 'a':
      r.append(g.word)
  return r


# %%
content2 = "交通很方便，房间小了一点，但是干净整洁，很有香港的特色，性价比较高，推荐一下哦"

# %%
r = get_a_list(content2)
r

# %%
mm = pseg.lcut(content2)
print(mm)
for gg in mm:
  print(gg.word, gg.flag)

# %% [markdown]
# ### jieba词性对照表:

# %% [markdown]
# jieba词性对照表:
#
#
# - a 形容词
#     - ad 副形词
#     - ag 形容词性语素
#     - an 名形词
# - b 区别词
# - c 连词
# - d 副词
#     - df
#     - dg 副语素
# - e 叹词
# - f 方位词
# - g 语素
# - h 前接成分
# - i 成语
# - j 简称略称
# - k 后接成分
# - l 习用语
# - m 数词
#     - mg
#     - mq 数量词
# - n 名词
#     - ng 名词性语素
#     - nr 人名
#     - nrfg
#     - nrt
#     - ns 地名
#     - nt 机构团体名
#     - nz 其他专名
# - o 拟声词
# - p 介词
# - q 量词
# - r 代词
#     - rg 代词性语素
#     - rr 人称代词
#     - rz 指示代词
# - s 处所词
# - t 时间词
#     - tg 时语素
# - u 助词
#     - ud 结构助词 得
#     - ug 时态助词
#     - uj 结构助词 的
#     - ul 时态助词 了
#     - uv 结构助词 地
#     - uz 时态助词 着
# - v 动词
#     - vd 副动词
#     - vg 动词性语素
#     - vi 不及物动词
#     - vn 名动词
#     - vq
# - x 非语素词
# - y 语气词
# - z 状态词
#     - zg

# %%
