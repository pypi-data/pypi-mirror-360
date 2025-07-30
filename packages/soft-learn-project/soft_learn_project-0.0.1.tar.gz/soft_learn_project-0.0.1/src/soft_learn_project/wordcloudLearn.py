# %% [markdown]
# ### 安装

# %%
# pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple wordcloud


# %% [markdown]
# ### 使用

# %%
# 导入绘制词云的工具包
import jieba
from wordcloud import WordCloud


# %%
import matplotlib.pyplot as plt


# %%
# 定义获取词云的函数并绘图
def get_word_cloud(keywords_list):
  # 首先实例化词云类对象, 里面三个参数
  # font_path: 字体路径,为了能够更好的显示中文
  # max_words: 指定词云图像最多可以显示的词汇数量
  # backgroud_color: 代表图片的北京颜色
  wordcloud = WordCloud(max_words=100, background_color='white',
                        font_path="/System/Library/Fonts/STHeiti Light.ttc")

  # 将传入的列表参数转化为字符串形式, 因为词云对象的参数要求是字符串类型
  keywords_string = " ".join(keywords_list)

  # 生成词云
  wordcloud.generate(keywords_string)

  # 绘图
  plt.figure()
  plt.imshow(wordcloud, interpolation="bilinear")
  plt.axis("off")
  plt.show()
  print(type(wordcloud))


# %%
content_str = "交通很方便，房间小了一点，但是干净整洁，很有香港的特色，性价比较高，推荐一下哦"


# %%
get_word_cloud(content_str)


# %%
wordcloud = WordCloud(max_words=100, background_color='white',
                      font_path="/System/Library/Fonts/STHeiti Light.ttc")


# %%
wordcloud.generate(content_str)


# %%
plt.imshow(wordcloud, interpolation="bilinear")


# %%
keywords_string = " ".join(content_str)
keywords_string


# %%
wordcloud.generate(keywords_string)


# %%
plt.imshow(wordcloud, interpolation="bilinear")


# %% [markdown]
# ### 练习

# %%
content = "去的时候 ,酒店大厅和餐厅在装修,感觉大厅有点挤.由于餐厅装修本来该享受的早饭,\
也没有享受(他们是8点开始每个房间送,但是我时间来不及了)不过前台服务员态度好!"


# %%


# %%
word_list = jieba.lcut(content)


# %%
word_list[:5]


# %%
word_string = " ".join(word_list)


# %%
word_string


# %%


# %%
wordcloud = WordCloud(max_words=100, background_color='white',
                      font_path="/System/Library/Fonts/STHeiti Light.ttc")


# %%
wordcloud.generate(word_string)


# %%
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()


# %%
