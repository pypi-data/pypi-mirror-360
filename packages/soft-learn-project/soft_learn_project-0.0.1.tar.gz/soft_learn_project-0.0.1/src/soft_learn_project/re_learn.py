import re
from sci_scripts import bunch
import sys


class ReLearn():
  def __init__(self) -> None:
    """
    # 记录文本规则的代码，就是对元字符的学习
    # 主要命令有
    re.match()  # 尝试从字符串的起始位置匹配一个模式，如果不是起始位置匹配成功的话，match()就返回none。
    re.search()  # 扫描整个字符串并返回第一个成功的匹配。#注意： match 和 search 是匹配一次 findall 匹配所有。
    # 用于替换字符串中的匹配项。 re.sub(pattern, repl, string, count=0, flags=0) 替换的字符串，也可为一个函数。
    re.sub
    re.findall()  # 在字符串中找到正则表达式所匹配的所有子串，并返回一个列表，如果没有找到匹配的，则返回空列表。
    re.finditer()  # 和 findall 类似，在字符串中找到正则表达式所匹配的所有子串，并把它们作为一个迭代器返回。
    re.split  # 按照匹配的子串将字符串分割后返回列表，
    # 函数用于编译正则表达式，生成一个正则表达式（ Pattern ）对象。re.compile(pattern[, flags])
    re.compile()
    # 除了以上的方法外，还有pattern.match(pattern) pattern.search(pattern) 等

    # 匹配模式中如果有(),为了避免与组混淆，需要转义
    # pattern=re.compile(r'<h3 class="gs_rt" ontouchstart="gs_evt_dsp\(event\).*?href="(?P<href>.*?)"',re.S)

    # 正则表达式修饰符 - 可选标志
    """
    pass

  def xsf_修饰符(self,):
    # 正则表达式可以包含一些可选标志修饰符来控制匹配的模式。修饰符被指定为一个可选的标志。多个标志可以通过按位 OR(|) 它们来指定。如 re.I | re.M 被设置成 I 和 M 标志：
    # 修饰符	描述
    # re.I	使匹配对大小写不敏感
    # re.L	做本地化识别（locale-aware）匹配
    # re.M	多行匹配，影响 ^ 和 $
    # ^ 元字符匹配字符串的开头，但在多行模式下，它也会匹配每一行的开头。
    # $ 元字符匹配字符串的结尾，但在多行模式下，它也会匹配每一行的结尾（换行符之前）。

    # re.S	使 . 匹配包括换行在内的所有字符  推荐用 re.DOTALL
    # re.U	根据Unicode字符集解析字符。这个标志影响 \w, \W, \b, \B.
    # re.X	该标志通过给予你更灵活的格式以便你将正则表达式写得更易于理解。
    pass

  def pattern(self,):
    # ---正则表达式总结
    """
    url = 'https://www.bilibili.com/video/BV1FV41177a6?p=128'
    正则表达式
    Regular Expression, 正则表达式, ⼀种使⽤表达式的⽅式对字符串进⾏匹配的语法规则.
    我们抓取到的⽹⻚源代码本质上就是⼀个超⻓的字符串, 想从⾥⾯提取内容.⽤正则再合适不过了.
    正则的优点: 速度快, 效率⾼, 准确性⾼ 正则的缺点: 新⼿上⼿难度有点⼉⾼.
    不过只要掌握了正则编写的逻辑关系, 写出⼀个提取⻚⾯内容的正则其实并不复杂
    正则的语法: 使⽤元字符进⾏排列组合⽤来匹配字符串 在线测试正则表达式https://tool.oschina.net/regex/

    元字符: 具有固定含义的特殊符号  只匹配一个字符
    常⽤元字符: 
    . 匹配除换⾏符以外的任意字符
    \w 匹配字⺟或数字或下划线
    \s 匹配任意的空⽩符
    \d 匹配数字
    \n 匹配⼀个换⾏符
    \t 匹配⼀个制表符
    ^ 匹配字符串的开始
    $ 匹配字符串的结尾
    \W 匹配⾮字⺟或数字或下划线
    \D 匹配⾮数字
    \S 匹配⾮空⽩符
    a|b 匹配字符a或字符b
    () 匹配括号内的表达式，也表示⼀个组
    [...] 匹配字符组中的字符
    [^...] 匹配除了字符组中字符的所有字符

    # 量词: 控制前⾯的元字符出现的次数
    * 重复零次或更多次
    + 重复⼀次或更多次
    ? 重复零次或⼀次
    {n} 重复n次
    {n,} 重复n次或更多次
    {n,m} 重复n到m次

    # 贪婪匹配和惰性匹配
    .* 贪婪匹配
    .*? 惰性匹配
    # 这两个要着重的说⼀下. 因为我们写爬⾍⽤的最多的就是这个惰性匹配.
    """

    # 常用的模式
    import re
    'industr(?:y|ies)'  # 可以匹配industry 和 industries
    '\d{n,}'  # 至少n位的数字
    '(\-|\+)?\d+(\.\d+)?'  # 正数、负数、和小数
    '[\u4e00-\u9fa5]{0,}'  # 汉字
    '\n\s*\r'  # 可以用来删除空白行

    # 元字符和模式的理解
    # \ #将下一个字符标记为一个特殊字符、或一个原义字符、或一个 向后引用、或一个八进制转义符。
    # 例如，'n' 匹配字符 "n"。'\n' 匹配一个换行符。序列 '\\' 匹配 "\" 而 "\(" 则匹配 "("。
    # ^ #匹配输入字符串的开始位置。
    # *	# 匹配前面的子表达式零次或多次。例如，zo* 能匹配 "z" 以及 "zoo"。* 等价于{0,}。
    # +	# 匹配前面的子表达式一次或多次。例如，'zo+' 能匹配 "zo" 以及 "zoo"，但不能匹配 "z"。+ 等价于 {1,}。
    # ?	# 匹配前面的子表达式零次或一次。例如，"do(es)?" 可以匹配 "do" 或 "does" 。? 等价于 {0,1}。

    # ?	# 当该字符紧跟在任何一个其他限制符 (*, +, ?, {n}, {n,}, {n,m}) 后面时，匹配模式是非贪婪的。
    # 非贪婪模式尽可能少的匹配所搜索的字符串，而默认的贪婪模式则尽可能多的匹配所搜索的字符串。
    # 例如，对于字符串 "oooo"，'o+?' 将匹配单个 "o"，而 'o+' 将匹配所有 'o'。

    # . #匹配除换行符（\n、\r）之外的任何单个字符。要匹配包括 '\n' 在内的任何字符，请使用像"(.|\n)"的模式。
    # x|y	匹配 x 或 y。例如，'z|food' 能匹配 "z" 或 "food"。'(z|f)ood' 则匹配 "zood" 或 "food"。

    # (pattern)	#匹配 pattern 并获取这一匹配。所获取的匹配可以从产生的 Matches 集合得到
    # (?:pattern)	#匹配 pattern 但不获取匹配结果，也就是说这是一个非获取匹配，不进行存储供以后使用。这在使用 "或" 字符 (|) 来组合一个模式的各个部分是很有用。例如， 'industr(?:y|ies)' 可以匹配industry 和 industries
    # (?=pattern)	#正向肯定预查（look ahead positive assert），在任何匹配pattern的字符串开始处匹配查找字符串。这是一个非获取匹配，也就是说，该匹配不需要获取供以后使用。例如，"Windows(?=95|98|NT|2000)"能匹配"Windows2000"中的"Windows"，但不能匹配"Windows3.1"中的"Windows"。预查不消耗字符，也就是说，在一个匹配发生后，在最后一次匹配之后立即开始下一次匹配的搜索，而不是从包含预查的字符之后开始。
    # (?!pattern)	#正向否定预查(negative assert)，在任何不匹配pattern的字符串开始处匹配查找字符串。这是一个非获取匹配，也就是说，该匹配不需要获取供以后使用。例如"Windows(?!95|98|NT|2000)"能匹配"Windows3.1"中的"Windows"，但不能匹配"Windows2000"中的"Windows"。预查不消耗字符，也就是说，在一个匹配发生后，在最后一次匹配之后立即开始下一次匹配的搜索，而不是从包含预查的字符之后开始。
    # (?<=pattern)	#反向(look behind)肯定预查，与正向肯定预查类似，只是方向相反。例如，"(?<=95|98|NT|2000)Windows"能匹配"2000Windows"中的"Windows"，但不能匹配"3.1Windows"中的"Windows"。
    # (?<!pattern)	#反向否定预查，与正向否定预查类似，只是方向相反。例如"(?<!95|98|NT|2000)Windows"能匹配"3.1Windows"中的"Windows"，但不能匹配"2000Windows"中的"Windows"。

    # [xyz] #字符集合。匹配所包含的任意一个字符。
    # [^xyz]	#负值字符集合。匹配未包含的任意字符。
    # \b	#匹配一个单词边界，也就是指单词和空格间的位置。例如， 'er\b' 可以匹配"never" 中的 'er'，但不能匹配 "verb" 中的 'er'。
    # \B	# 匹配非单词边界。'er\B' 能匹配 "verb" 中的 'er'，但不能匹配 "never" 中的 'er'。
    # \cx	# 匹配由 x 指明的控制字符。例如， \cM 匹配一个 Control-M 或回车符。x 的值必须为 A-Z 或 a-z 之一。否则，将 c 视为一个原义的 'c' 字符。
    # \d	# 匹配一个数字字符。等价于 [0-9]。
    # \D	# 匹配一个非数字字符。等价于 [^0-9]。
    # \f	# 匹配一个换页符。等价于 \x0c 和 \cL。
    # \n	# 匹配一个换行符。等价于 \x0a 和 \cJ。
    # \r	# 匹配一个回车符。等价于 \x0d 和 \cM。
    # \s	# 匹配任何空白字符，包括空格、制表符、换页符等等。等价于 [ \f\n\r\t\v]。
    # \S	# 匹配任何非空白字符。等价于 [^ \f\n\r\t\v]。
    # \t	# 匹配一个制表符。等价于 \x09 和 \cI。
    # \v	# 匹配一个垂直制表符。等价于 \x0b 和 \cK。
    # \w	# 匹配字母、数字、下划线。等价于'[A-Za-z0-9_]'。
    # \W	# 匹配非字母、数字、下划线。等价于 '[^A-Za-z0-9_]'。
    # \xn	# 匹配 n，其中 n 为十六进制转义值。十六进制转义值必须为确定的两个数字长。例如，'\x41' 匹配 "A"。'\x041' 则等价于 '\x04' & "1"。正则表达式中可以使用 ASCII 编码。
    # \num	# 匹配 num，其中 num 是一个正整数。对所获取的匹配的引用。例如，'(.)\1' 匹配两个连续的相同字符。
    # \1...\9	匹配第n个分组的内容。

    # 'section xdgdg xxend'  使用 python re 模块 取代'section'和end'之间的所有字符为’wjl'
    string = "section xdgdg xxend"
    # 替换字符串中的 \1 和 \3 分别表示第一个捕获组和第三个捕获组的内容，即 'section' 和 'end'。
    new_string = re.sub(r"(section)(.*)(end)", r"\1wjl\3", string)
    print(new_string)

    # 正则表达式 - 运算符优先级,以下按照优先的先后顺序
    # \	转义符
    # (), (?:), (?=), []	圆括号和方括号
    # *, +, ?, {n}, {n,}, {n,m}	限定符
    # ^, $, \任何元字符、任何字符	定位点和序列（即：位置和顺序）
    # |	替换，"或"操作
    # 字符具有高于替换运算符的优先级，使得"m|food"匹配"m"或"food"。若要匹配"mood"或"food"，请使用括号创建子表达式，从而产生"(m|f)ood"。
    pass

  def re_match(self,):
    # re.MatchObject  匹配对象，group() 返回被 RE 匹配的字符串。
    m = re.match('www', 'www.runoob.com')  # 在起始位置匹配
    print(m.group())
    line = 'Cats dogs are smarter than dogs'
    matchObj = re.match(r'(.*) are (.*) (.*)', line,
                        re.M | re.I)  # () 里面是为.group()准备的
    print(matchObj.group(1))
    matchObj = re.search(r'(.*) dogs .*', line,
                         flags=(re.M | re.I))  # 或者不要flags=
    print(matchObj.group())
    pass

  def re_search(self,
                line="Cats are smarter than dogs.",):
    # 匹配括号内的表达式，也表示一个组group()
    searchObj = re.search(r'(.*) are smarter than (.*?)\.',
                          line, re.M | re.I)
    print(searchObj)
    print(searchObj.group(), searchObj.group(0),
          searchObj.group(1), searchObj.group(2))
    return searchObj

  def re_sub(self,):

    phone = "2004-959-559 # 这是一个电话号码"
    num = re.sub(r'#.*$', "", phone)
    print(num)
    pattern = re.compile(r"\s+#.*$", re.S)
    print(pattern.sub("xx", phone))

    '''
    def double(matched):   #repl 参数是一个函数
        value = int(matched.group('value'))
        return str(value * 2)  # 将匹配的数字乘于 2

    s = 'A23G4HFD567'
    print(re.sub('(?P<value>\d+)', double, s))
    '''
    pass

  def re_findall(self,):
    # 返回的是列表故不需要.group("name")
    content = 'runoob 123 google 456'
    # 注意不加() findall 匹配所有， 加() findall 只给出()里面的内容
    pattern_test = re.compile(r'runoob \d+ google \d+')
    result1 = pattern_test.findall(content)
    print(result1)
    #  注意不加() findall 匹配所有， 加() findall 只给出()里面的内容， 而对于除了findall的其他命令，给出的都是匹配对象，
    #  通过.group()匹配所有，.group("ok")匹配(ok)的内容
    # 查找数字 (?P<num>.*?)
    pattern = re.compile(r'runoob (?P<ok>\d+) google (?P<ko>\d+)')
    result1 = pattern.findall(content)
    print(result1)
    result2 = pattern.search(content)
    print(result2.group(), "\t\t", result2.group("ok"))
    pass

  def re_finditer(self,):
    it = re.finditer(r"\d+", "12a32bc43jf3")
    for match in it:
      print(match.group())
    pass

  def re_compile(self,):
    # --re.compile()  建立匹配模式, 然后用于其他命令
    pattern = re.compile(r'\d{1,}')  # 用于匹配至少一个数字
    m = pattern.findall('one12twothree34fo3351ur')
    print(m)
    obj2 = re.compile(r"<li><a href='(?P<href>.*?)' title=", re.S)
    pass

  def re_split(self,):
    # --re.split
    m = re.split('\W+', 'runoob, runoob, runoob.')
    print(m)
    pass

  def example(self, page_content):
    obj = re.compile(r'<li>.*?<span class="title">(?P<name>.*?)</span>'
                     r'.*?<p class="">.*?<br>(?P<year>.*?)&nbsp.*?'
                     r'<span class="rating_num" property="v:average">(?P<rating>.*?)</span>'
                     r'.*?<span>(?P<num>.*?)人评价</span>', re.S)
    # 开始匹配
    result = obj.finditer(page_content)
    for it in result:
      # print(it.group("name"))
      # print(it.group("year").strip())  #对年份处理  前面有空格
      # print(it.group("rating"))
      # print(it.group("num"))
      dic = it.groupdict()
      dic['year'] = dic['year'].strip()
    #   csvwriter.writerow(dic.values())  # 写入的是字典的值
    pass

  def modify_str(self,
                 content,
                 pattern=r'CPP.*?=.*?gcc.*?\n',
                 old_str_pattern='gcc',
                 new_str='gcc-13',
                 ):
    """从content中找到匹配的字符串, 然后用 new_str 取代匹配的字符串中的 old_str

    Args:
        content (_type_): _description_
        pattern (regexp, optional): _description_. Defaults to r'CPP.*?=.*?gcc.*?\n'.
        old_str (str, optional): _description_. Defaults to 'gcc'.
        new_str (str, optional): _description_. Defaults to 'gcc-13'.

    Returns: data
        _type_: _description_
    """
    # 找到匹配模式的字符串
    try:
      match_str: str = re.search(pattern, content, re.S).group()
    except:
      print('没有匹配的内容, 请修改pattern')
      sys.exit()
    # 在匹配模式的字符串中取代关键词, 获得修改后的 -> 匹配模式字符串
    match_modified_str = re.sub(old_str_pattern, new_str, match_str)
    # match_modified_str = match_str.replace(old_str, new_str)
    content_modified = content.replace(match_str,
                                       match_modified_str)
    # 或者这样
    # content_modified = re.sub(pattern, repl=match_modified_str, string=content)
    data = bunch.Bunch(match_str=match_str,
                       match_modified_str=match_modified_str,
                       content_modified=content_modified
                       )
    return data
