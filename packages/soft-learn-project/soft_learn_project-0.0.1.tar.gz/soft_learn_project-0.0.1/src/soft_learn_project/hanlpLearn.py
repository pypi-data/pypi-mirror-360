# %% [markdown]
# ### 安装

# %%
from pyhanlp import *
import hanlp
%pip install hanlp

# %%

# %% [markdown]
# ### 使用hanlp进行中文分词:

# %%
# 加载CTB_CONVSEG预训练模型进行分词任务
tokenizer = hanlp.load('CTB6_CONVSEG')
tokenizer("工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作")[10:]


# %%
tokenizer(eng_str)

# %% [markdown]
# ### 进行英文分词, 英文分词只需要使用规则即可

# %%
eng_str = 'Mr. Hankcs bought hankcs.com for 1.5 thousand dollars.'

# %%
tokenizer = hanlp.load('CTB6_CONVSEG')
tokenizer(eng_str)[:10]

# %%
# 进行英文分词, 英文分词只需要使用规则即可
tokenizer = hanlp.utils.rules.tokenize_english
tokenizer('Mr. Hankcs bought hankcs.com for 1.5 thousand dollars.')
# ['Mr.', 'Hankcs', 'bought', 'hankcs.com', 'for', '1.5', 'thousand', 'dollars', '.']


# %% [markdown]
# ### 什么是命名实体识别  NER
# 命名实体: 通常我们将人名, 地名, 机构名等专有名词统称命名实体. 如: 周杰伦, 黑山县, 孔子学院, 24辊方钢矫直机.
# 顾名思义, 命名实体识别(Named Entity Recognition，简称NER)就是识别出一段文本中可能存在的命名实体

# %% [markdown]
# #### 使用hanlp进行中文命名实体识别:

# %%
# 加载中文命名实体识别的预训练模型MSRA_NER_BERT_BASE_ZH
recognizer = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH)
# 这里注意它的输入是对句子进行字符分割的列表, 因此在句子前加入了list()
str_list = list('上海华安工业（集团）公司董事长谭旭光和秘书张晚霞来到美 国纽约现代艺术博物馆参观。')
recognizer(str_list)
# 返回结果是一个装有n个元组的列表, 每个元组代表一个命名实体, 元组中的每一项分别代表具体的命名实体, 如: '上海华安工业（集团）公司'; 命名实体的类型, 如: 'NT'-机构名; 命名实体的开始索引和结束索引, 如: 0, 12.

# %%
str_list[:5]

# %% [markdown]
# #### 使用hanlp进行英文命名实体识别:

# %%
hanlp.pretrained.ner.CONLL03_NER_BERT_BASE_CASED_EN

# %%
# 加载英文命名实体识别的预训练模型CONLL03_NER_BERT_BASE_UNCASED_EN
# recognizer = hanlp.load(hanlp.pretrained.ner.CONLL03_NER_BERT_BASE_UNCASED_EN)
recognizer = hanlp.load(hanlp.pretrained.ner.CONLL03_NER_BERT_BASE_CASED_EN)
# 这里注意它的输入是对句子进行分词后的结果, 是列表形式.
recognizer(["President", "Obama", "is", "speaking",
           "at", "the", "White", "House"])
# [('Obama', 'PER', 1, 2), ('White House', 'LOC', 6, 8)]
# 返回结果是一个装有n个元组的列表, 每个元组代表一个命名实体, 元组中的每一项分别代表具体的命名实体, 如: 'Obama', 如: 'PER'-人名; 命名实体的开始索引和结束索引, 如: 1, 2.

# %% [markdown]
# ### 什么是词性标注 POS
# 词性: 语言中对词的一种分类方法，以语法特征为主要依据、兼顾词汇意义对词进行划分的结果, 常见的词性有14种, 如: 名词, 动词, 形容词等.
# 顾名思义, 词性标注(Part-Of-Speech tagging, 简称POS)就是标注出一段文本中每个词汇的词性

# %% [markdown]
# #### 使用hanlp进行中文词性标注:

# %%
# 加载中文命名实体识别的预训练模型CTB5_POS_RNN_FASTTEXT_ZH
# tagger = hanlp.load(hanlp.pretrained.pos.CTB5_POS_RNN_FASTTEXT_ZH)
tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL)
# 输入是分词结果列表
tagger(['我', '的', '希望', '是', '希望', '和平'])
# 结果返回对应的词性
# ['PN', 'DEG', 'NN', 'VC', 'VV', 'NN']

# %% [markdown]
# #### 使用hanlp进行英文词性标注:

# %%
# 加载英文命名实体识别的预训练模型PTB_POS_RNN_FASTTEXT_EN
# hanlp.pretrained.pos.PTB_POS_RNN_FASTTEXT_EN
# tagger = hanlp.load(hanlp.pretrained.pos.PTB_POS_RNN_FASTTEXT_EN)
tagger = hanlp.load(hanlp.pretrained.pos.PKU98_POS_ELECTRA_SMALL)
# 输入是分词结果列表
tagger(['I', 'banked', '2', 'dollars', 'in', 'a', 'bank', '.'])
# ['PRP', 'VBD', 'CD', 'NNS', 'IN', 'DT', 'NN', '.']

# %%


# %%
text = "中文分词只是第一步；HanLP从中文分词开始，覆盖词性标注、" \
       "命名实体识别、句法分析、文本分类等常用任务，提供了丰富的API。" \
       "不同于一些简陋的分词类库，HanLP精心优化了内部数据结构和IO接口，" \
       "做到了毫秒级的冷启动、千万字符每秒的处理速度，而内存最低仅" \
       "需120MB。无论是移动设备还是大型集群，都能获得良好的体验。" \
       "不同于市面上的商业工具，HanLP提供训练模块，可以在用户的语" \
       "料上训练模型并替换默认模型，以适应不同的领域。项目主页上提" \
       "供了详细的文档，以及在一些开源语料上训练的模型。HanLP希望兼" \
       "顾学术界的精准与工业界的效率，在两者之间取一个平衡，真正将自" \
       "然语言处理普及到生产环境中去。"
phraseList = HanLP.extractPhrase(text, 3)
for line in phraseList:
  print(line)


# %% [markdown]
# ### hanlp词性对照表:

# %% [markdown]
#
# 【Proper Noun——NR，专有名词】
#
# 【Temporal Noun——NT，时间名词】
#
# 【Localizer——LC，定位词】如“内”，“左右”
#
# 【Pronoun——PN，代词】
#
# 【Determiner——DT，限定词】如“这”，“全体”
#
# 【Cardinal Number——CD，量词】
#
# 【Ordinal Number——OD，次序词】如“第三十一”
#
# 【Measure word——M，单位词】如“杯”
#
# 【Verb：VA，VC，VE，VV，动词】
#
# 【Adverb：AD，副词】如“近”，“极大”
#
# 【Preposition：P，介词】如“随着”
#
# 【Subordinating conjunctions：CS，从属连词】
#
# 【Conjuctions：CC，连词】如“和”
#
# 【Particle：DEC,DEG,DEV,DER,AS,SP,ETC,MSP，小品词】如“的话”
#
# 【Interjections：IJ，感叹词】如“哈”
#
# 【onomatopoeia：ON，拟声词】如“哗啦啦”
#
# 【Other Noun-modifier：JJ】如“发稿/JJ 时间/NN”
#
# 【Punctuation：PU，标点符号】
#
# 【Foreign word：FW，外国词语】如“OK

# %%
