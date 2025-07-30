import graphviz
import pygraphviz


class GraphvizLearn():
  def __init__(self) -> None:
    """https://www.graphviz.org/doc/info/attrs.html
    """
    pass

  def install(self):
    s = r"""conda install pygraphviz"""
    print(s)
    return None

  def write_fig(self, dot: graphviz.Digraph):
    # jupyter 中直接查看
    # dot
    # 只保存 source 文件
    # dot.save('dot.gv')
    # 保存pdf
    dot.render(filename='xyz', format='pdf', cleanup=True)

  def example_1(self):
    # 创建一个新的有向图
    dot = graphviz.Digraph(graph_attr={'rankdir': 'LR'})  # LR表示从左到右排列

    # 添加节点
    dot.node('A', '程序开始')
    dot.node('B', 'Node B')
    dot.node('C', 'Node C')
    dot.node('D', '结束')

    # 添加边
    dot.edges(['AB', 'AC', 'BD'])

    # 渲染并显示图形
    # display(dot)
    # 渲染图形并保存为文件
    # dot.render('test', format='pdf', cleanup=True)
    return dot

  def example_2(self):
    dot = graphviz.Digraph(graph_attr={'rankdir': 'LR'})  # LR表示从左到右排列
    # 创建注释框
    dot.node('start', shape='record', label='重大需求|<start>开始', color='red',)
    dot.node('end', shape='record', label='|<end> 结束')

    # 创建箭头连接注释框和节点
    dot.edge('start', 'A')
    dot.edge('A', 'end')

    # jupyter 中直接查看
    # dot
    # 只保存 source 文件
    # dot.save('dot.gv')
    # 保存pdf
    dot.render(filename='xyz', format='pdf', cleanup=True)
    return dot

  def example_3(self):
    dot = graphviz.Digraph()

    # 定义节点B为record形状，并添加并列项
    dot.node('A', '开始')
    dot.node('B', shape='record', label='步骤1 | {项目1 | 项目2}')
    dot.node('C', '步骤2')
    dot.node('D', '结束')

    # 添加边
    dot.edge('A', 'B')
    dot.edge('B', 'C')
    dot.edge('C', 'D')
    dot: graphviz.Digraph
    return dot


class PygraphvizLearn():
  def __init__(self) -> None:
    """https://www.graphviz.org/docs/clusters/
    """
    pass

  def install(self):
    """
      1. 安装
      brew install graphviz
      export C_INCLUDE_PATH=/opt/homebrew/include
      export LIBRARY_PATH=/opt/homebrew/lib
      pip install pygraphviz --no-cache-dir
      2. 验证
      python -c "import pygraphviz; print(pygraphviz.__version__)"
    """
    pass

  def get_attr(self):
    # 创建一个有向图
    G = pygraphviz.AGraph()

    # 添加节点并设置属性
    G.add_node('A', color='red', shape='circle')
    # 获取节点 'A' 的属性
    attr_dict = dict(G.get_node('A').attr)
    # 获取子图的属性
    # dict(subgraph.graph_attr)['name_subgraph']
    return attr_dict

  def basic_operation(self):
    """基本操作

    Returns:
        _type_: _description_
    """
    # 创建一个有向图
    G = pygraphviz.AGraph(strict=True, directed=True)

    # 添加节点
    G.add_node('A')
    G.add_node('B')
    G.add_node('C')
    G.add_node('D')
    G.add_node('E')

    # 添加边
    G.add_edge('A', 'B')
    G.add_edge('A', 'C')
    G.add_edge('B', 'D')
    G.add_edge('B', 'E')

    # 渲染并显示图形
    # from IPython.display import Image
    # Image(G.draw(format='png', prog='dot')) # 可以在jutpyer中显示
    # dot = graphviz.Source(G.draw(format='dot', prog='dot').decode())
    # return dot

    # 保存图形到文件
    # G.draw('test.pdf', format='pdf', prog='dot')

    # 或者
    G.layout('dot')
    return G

  def node_edge_sets(self):
    """ 节点属性设置
    https://www.graphviz.org/docs/edges/

    # shape 的可取参数 ellipse, circle
    box: 矩形框
    circle: 圆形
    ellipse: 椭圆形
    triangle: 三角形
    diamond: 菱形
    parallelogram: 平行四边形
    hexagon: 六边形
    octagon: 八边形
    oval: 椭圆形
    plaintext: 显示为纯文本
    此外，还有一些更复杂的形状选项，如 record 和 Mrecord，允许你在节点内部创建表格或记录来显示多行文本或子项。

    # shape = 'record' 时的说明 https://www.graphviz.org/doc/info/shapes.html
    """
    # pad='1.5', rankdir='LR', ranksep=1, rotate=90,
    G = pygraphviz.AGraph(shape='rect', rankdir='TB',)
    # height=1, image='wqh6_7yue.jpeg', imagescale='height', margin=0.5
    G.add_node(1, label='测试', shape='rect', width=1, height=2,
               style='filled', color='lightblue', )
    G.add_node(2, label='中文', fontname='Heiti TC', group='cluster3')
    G.add_node(3, label='英语')
    G.add_node(4, label='检验', fontcolor='red', fontname='Songti TC', fontsize=20,  # 字体颜色
               style='filled', fillcolor='lightgreen',  # 填充颜色
               color='blue',)  # 边界颜色
    # 注意 name 必须是 cluster开头 才被认为是 cluster
    subgraph = G.add_subgraph(nbunch=[2, 3],   name='cluster_1',  label='标签', pencolor='green',
                              style='filled', color='lightyellow', fontcolor='red',
                              # bgcolor='yellow', style='filled', fillcolor='lightblue', center=True, labelloc='t', margin=3, ordering='out',
                              fontname='Heiti TC', )

    # dir='both', 'forward', 'back', 'none'
    G.add_edge(1, 2,  dir='both', label='对比研究, 得出结论', )
    G.add_edge(3, 4)

    G.layout('dot')
    return G

  def subgraph_sets(aelf):
    """子图, 子图中的nbunch 必须是 主图中的节点

    Args:
        aelf (_type_): _description_
    """
    # 创建一个有向图
    G = pygraphviz.AGraph(strict=True, rankdir='TB', directed=False)

    # 添加节点，并设置填充颜色为绿色
    G.add_node('A', label='程序', color='red', shape='box',
               style='filled', fillcolor='green')
    G.add_node('E', label='结束', shape='box',
               style='filled', fillcolor='green')

    G.add_node('B', label='内容1', shape='box',
               style='filled', fillcolor='green')
    G.add_node('C', label='内容2', shape='box',
               style='filled', fillcolor='green')
    G.add_node('D', label='内容3', shape='box',
               style='filled', fillcolor='lightyellow')

    # 子图
    subgraph2 = G.add_subgraph(nbunch=['A', 'E'], name='cluster1', label='重大需求',
                               style='dashed',)  # rank='same', rankdir='LR',

    # 创建子图，将节点 B、C、D 放入其中
    subgraph = G.add_subgraph(nbunch=['B', 'C', 'D'], name='cluster_BCD', label='研究内容',
                              style='dashed', rank='same', rankdir='LR',)

    # 添加边将子图内节点连接起来
    subgraph.add_edge('B', 'C')
    subgraph.add_edge('C', 'D')

    # 添加边
    G.add_edge('A', 'B', dir='forward')
    G.add_edge('A', 'C')
    G.add_edge('A', 'D')
    G.add_edge('B', 'E')
    G.add_edge('C', 'E')
    G.add_edge('D', 'E')

    G.layout('dot')
    return G


class Features():
  def __init__(self) -> None:
    pass

  def get_graph(self, label_list=['重大需求', '科学问题', '关键技术', '研究内容',
                                  '研究方法', '涉及领域', '总体目标'],
                start_number=0,
                rankdir='TB',
                **kwargs):
    num_node = len(label_list)
    nodes_list = list(range(start_number, start_number+num_node))
    color_list = matplotlibLearn.Features().get_color_list(num_color=num_node,
                                                           alpha=0.5)
    color_list.reverse()

    # 创建一个有向图
    G = pygraphviz.AGraph(strict=True, directed=True,
                          rankdir=rankdir, **kwargs)  # rankdir='TB'
    # 增加节点
    for n, label, fillcolor in zip(nodes_list, label_list, color_list):
      G.add_node(n=n, label=label, fontname='Heiti TC',
                 shape='ellipse', style='filled', fillcolor=fillcolor, color='white', **kwargs)
    # 增加边
    for i in range(len(nodes_list)-1):
      # color = G.get_node(nodes_list[i]).attr['fillcolor'][:-2]
      G.add_edge(nodes_list[i], nodes_list[i+1], penwidth=3, **kwargs)
    return G

  def get_subgraph(self, G: pygraphviz.AGraph,
                   name_subgraph='研究方法',
                   start_number=10,
                   label_list=['模拟计算', '理论分析', '数值仿真', '程序编程'],
                   arrow_dirction_reverse=False,
                   **kwargs):

    # 这 name 必须是 cluster 字符串开头 才能识别为 集团
    subgraph = G.add_subgraph(name=f'cluster_{start_number}', style='dashed', rank='same',
                              cluster=True, name_subgraph=name_subgraph, **kwargs)  # rankdir='TB',

    nodename_list = [str(i) for i in range(
        start_number, start_number+len(label_list))]

    # 获得与子图连接的节点的填充颜色
    for Gnode in G.nodes():
      if G.get_node(Gnode).attr['label'] == subgraph.graph_attr['name_subgraph']:
        fillcolor = G.get_node(Gnode).attr['fillcolor']
        break
    for nodename, label in zip(nodename_list, label_list):
      subgraph.add_node(nodename, label=label,
                        shape='rect', style='filled', fillcolor=fillcolor, **kwargs)  # width=1, height=1,
    # 添加边
    for Gnode in G.nodes():
      if G.get_node(Gnode).attr['label'] == subgraph.graph_attr['name_subgraph']:
        for Snode in subgraph.nodes():
          a_to_b = [Gnode, Snode]
          if arrow_dirction_reverse:
            a_to_b.reverse()
          G.add_edge(a_to_b[0], a_to_b[1],
                     color=fillcolor[:-2], penwidth=2)  # 忽略透明度

    return subgraph

  def get_fig(self, G: pygraphviz.AGraph,
              save=True, fname='test.pdf',
              prog='fdp'):
    import os
    dirname = os.path.dirname(fname)
    if not os.path.exists(dirname):
      os.makedirs(dirname)

    G.layout(prog=prog)
    # 保存图形到文件
    if save:
      G.draw(fname, format='pdf')
    return G


class MyGraph():
  def __init__(self) -> None:
    pass

  def my_学术思路_old(self, prog='fdp',
                  fname='xssl_学术思路.pdf',
                  save=True,
                  add_extra_edge=True,
                  **kwargs,):
    # 主图
    G = Features().get_graph(label_list=['重大需求', '科学问题', '关键技术', '研究内容',
                                         '研究方法', '涉及领域', '总体目标'],
                             **kwargs, fontsize=16)
    # sub_graph
    from sci_scripts import bunch
    d1 = bunch.Bunch(name_subgraph='重大需求',
                     start_number=10,
                     label_list=['W-嬗变元素-H/He三元体系的研究'],
                     )
    d2 = bunch.Bunch(name_subgraph='科学问题',
                     start_number=20,
                     label_list=[
                         '由于缺少相关体系的势函数而无法\n使用分子动力学进行大尺度的模拟研究'],
                     )
    d3 = bunch.Bunch(name_subgraph='关键技术',
                     start_number=30,
                     label_list=['使用第一原理方法\n获得相关体系的物\n理性质',
                                 'W-嬗变元素-H/He\n三元体系嵌入势和\n对势的数学形式',
                                 '通过微分演化算法, 盆跳算法\n和基因(遗传)算法\n搜索目标函数的全局最小\n确定势函数的参数',
                                 '基于构造的势函数\n使用分子动力学方法\n研究相关体系的\n热学和力学性质'],
                     )
    d4 = bunch.Bunch(name_subgraph='研究内容',
                     start_number=40,
                     label_list=[
                         '第一原理计算和调研\nW-Re-H/He系统的相关性质, \n拟合势参数构建W-Re-H/He力场',
                         '基于构建的W-Re-He势函数, \n使用分子动力学方法\n研究Re在钨中的偏析行为\n以及Re/He在钨中的协同效应',
                         '构建W-Re-H势函数\n以及W-Os-H/He势函数, \n研究W中Os-H/He的\n相互作用和行为'],
                     )
    d5 = bunch.Bunch(name_subgraph='研究方法',
                     start_number=50,
                     label_list=[
                         '模拟计算', '理论分析',  '程序编程', '数值仿真'],
                     )
    d6 = bunch.Bunch(name_subgraph='涉及领域',
                     start_number=60,
                     label_list=['第一性原理计算',
                                 '分子动力学模拟',
                                 '信息科学', '辐照损伤'],
                     )
    d7 = bunch.Bunch(name_subgraph='总体目标',
                     start_number=70,
                     label_list=[
                         '构造W-嬗变元素-H/He三元体系势函数\n并用之于分子动力学进行大尺度的模拟. \n为相关体系的广泛和深入研究打下基础, \n为提出抗辐照损伤的策略提供科学依据.'],
                     )
    data_list = [d1, d2, d3, d4, d5, d6, d7]

    for data in data_list:
      subgraph = Features().get_subgraph(
          G, **data, **kwargs, arrow_dirction_reverse=True, penwidth=2)

    # 子图节点之间增加连线
    if add_extra_edge:
      subgrapgh_name_list = [subgrapgh.name for subgrapgh in G.subgraphs()]
      subgrapgh_name_list.sort()

      for i in range(len(subgrapgh_name_list)-1):
        nodes_A = G.get_subgraph(name=subgrapgh_name_list[i]).nodes()
        nodes_B = G.get_subgraph(name=subgrapgh_name_list[i+1]).nodes()
        result = [[x, y] for x in nodes_A for y in nodes_B]
        for node_AB in result:
          G.add_edge(node_AB[0], node_AB[1], dir='forward', penwidth=1)

    # 保存图片
    G = Features().get_fig(G, prog=prog, save=save, fname=fname)
    return G

  def my_学术思路(self, prog='dot',
              fname='xssl_学术思路.pdf',
              save=True, ratio=None,
              rankdir='TB',
              size=None, **kwargs):

    nodes = 'ABCDEFG'
    color_list = matplotlibLearn.Features().get_color_list(num_color=len(nodes),
                                                           alpha=0.5)
    color_list.reverse()
    data = {'nodes_left': {'nodes': [i for i in nodes],
                           'labels': ['重大需求', '科学问题', '关键技术', '研究内容', '研究方法', '涉及领域', '总体目标'],
                           'fillcolors': color_list},
            'nodes_right': {'nodes': [str(i) for i in range(len(nodes))],
                            'labels': ['W-嬗变元素-H/He三元体系的研究',
                                       r'由于缺少相关体系的势函数而无法使用\n分子动力学进行大尺度的模拟研究',
                                       r'{使用第一原理方法获得相关体系的物理性质, | 确定W-嬗变元素-H/He三元体系嵌入势和对势的数学形式 | 通过微分演化算法, 盆跳算法和基因(遗传)算法\n搜索目标函数的全局最小确定势函数的参数 | 基于构造的势函数研究相关体系的热学和力学性质}',
                                       r'第一原理计算和调研\nW-Re-H/He系统的相关性质,\n拟合并构建W-Re-H/He力场 | 基于构建的势函数\n研究Re在钨中的偏析行为\n以及Re-H/He在钨中的协同效应 | 构建W-Os-H/He势函数, \n研究W中Os-H/He的相互作用和行为',
                                       '模拟计算 | 理论分析 | 程序编程 | 数值仿真',
                                       r'第一性原理 | 分子动力学 | 信息科学 | 数据科学 | 计算机编程|辐照损伤',
                                       r'构造W-嬗变元素-H/He三元体系势函数\n并用之于分子动力学进行大尺度的模拟. \n为相关体系的广泛和深入研究打下基础, \n为提出抗辐照损伤的策略提供科学依据.'],
                            'fillcolors': color_list},

            }
    # 创建图
    G = pygraphviz.AGraph(directed=True, rankdir=rankdir,
                          ratio=ratio, size=size, **kwargs)
    # 添加节点
    for node, label, color in zip(data['nodes_left']['nodes'], data['nodes_left']['labels'], color_list):
      G.add_node(n=node, label=label, shape='ellipse',
                 style='filled', fillcolor=color, **kwargs)
    for node_detail, label_detail, color in zip(data['nodes_right']['nodes'], data['nodes_right']['labels'], color_list):
      G.add_node(n=node_detail, label=label_detail,
                 shape='record', style='filled', fillcolor=color, **kwargs)
    # 添加边，控制连接方向
    for i in range(len(nodes)-1):
      G.add_edge(data['nodes_left']['nodes'][i],
                 data['nodes_left']['nodes'][i+1])
      G.add_edge(data['nodes_right']['nodes'][i],
                 data['nodes_right']['nodes'][i+1])
    # 设置节点排列顺序和rank属)
    subgraph1 = G.add_subgraph(nbunch=data['nodes_left']['nodes'], name='cluster1',
                               style='dashed', rank='same',)
    subgraph2 = G.add_subgraph(nbunch=data['nodes_right']['nodes'], name='cluster2',
                               style='dashed', rank='same', )

    # 主次节点相连
    # for node, node_detail in zip(node_list, node_detail_list):
    #   G.add_edge(node,node_detail,tailport='e', headport='w')
    # G.add_edge('A','0')
    # G.add_edge('G', '6')
    # 保存图形
    G = Features().get_fig(G, save=save, fname=fname, prog=prog)
    return G

  def my_技术路线(self, ratio=1.2, prog='dot', overlap=False, rankdir='TB',
              fname='jslx_技术路线.pdf', save=True, **kwargs,):
    gf = Features()
    G = gf.get_graph(label_list=['构建W-嬗变元素-H/He势函数',
                                 '分子动力学方法研究Re在钨中的\n偏析行为以及Re/He\n在钨中的协同效应',
                                 '分子动力学方法研究W中Os-H/He的\n相互作用和行为'],
                     **kwargs,)  # rankdir='TB',

    edge_args = dict(G.get_edge(0, 1).attr)
    G.add_edge(1, 2, **edge_args, dir='both',
               label='对比研究, 得出结论', )
    G.add_edge(0, 2, **edge_args)

    # 增加子图
    gf.get_subgraph(G, name_subgraph='构建W-嬗变元素-H/He势函数',
                    start_number=10,
                    label_list=['确定嵌入势函数和\n对势函数的数学形式',
                                '搜索全局最小化\n->优化目标函数获得\n势函数拟合参数',],
                    arrow_dirction_reverse=True, **kwargs,
                    )

    gf.get_subgraph(G, name_subgraph='搜索全局最小化\n->优化目标函数获得\n势函数拟合参数',
                    label_list=['使用第一原理方法\n计算W-嬗变元素-H/He系统\n的相关性质,\n如各种缺陷(空位, 间隙原子, 位错环)\n的形成能, 结合能, \n迁移能, 体块模量等',], start_number=110,
                    arrow_dirction_reverse=True, **kwargs,
                    )

    gf.get_subgraph(
        G, name_subgraph='使用第一原理方法\n计算W-嬗变元素-H/He系统\n的相关性质,\n如各种缺陷(空位, 间隙原子, 位错环)\n的形成能, 结合能, \n迁移能, 体块模量等',
        start_number=101, label_list=['文献调研', '建模', '调参', '数据处理', '数据分析'],
        arrow_dirction_reverse=True, **kwargs)
    gf.get_subgraph(G, name_subgraph='确定嵌入势函数和\n对势函数的数学形式',
                    start_number=200, label_list=['文献调研'],
                    arrow_dirction_reverse=True, **kwargs
                    )
    gf.get_subgraph(G, name_subgraph='搜索全局最小化\n->优化目标函数获得\n势函数拟合参数',
                    start_number=300, label_list=['数值仿真', '程序编程', '调试参数', ],
                    arrow_dirction_reverse=True, **kwargs)
    gf.get_subgraph(G, name_subgraph='数值仿真',
                    start_number=3000, label_list=['最小二乘法', '微分演化算法', '对偶退火法', '盆跳算法', '基因遗传算法'],
                    arrow_dirction_reverse=True, **kwargs,)

    gf.get_subgraph(G, name_subgraph='分子动力学方法研究Re在钨中的\n偏析行为以及Re/He\n在钨中的协同效应',
                    start_number=20, label_list=['文献调研', '建模计算1', '调参', '原子构型可视化'],
                    arrow_dirction_reverse=True, **kwargs,
                    )
    gf.get_subgraph(G, name_subgraph='建模计算1',
                    start_number=220, label_list=['\n研究W中Re的偏析行为, \nRe杂质对氦泡的影响, \n对比W-Re合金/纯钨中氘(D)的行为等.'],
                    arrow_dirction_reverse=True, **kwargs,
                    )

    gf.get_subgraph(G, name_subgraph='分子动力学方法研究W中Os-H/He的\n相互作用和行为',
                    start_number=30, label_list=['文献调研', '建模计算2', '调参', '原子构型可视化'],
                    arrow_dirction_reverse=True, **kwargs,
                    )
    gf.get_subgraph(G, name_subgraph='建模计算2',
                    start_number=320, label_list=['研究W中Os的偏析行为, \nOs与H/He的相互作用和行为, \n对比W-Os合金/纯钨中氘(D)的行为, \n钨中嬗变元素对D滞留量的影响, \nW中Re/Os行为的异同等.'],
                    arrow_dirction_reverse=True, **kwargs,
                    )

    # 保存图片
    G = Features().get_fig(G, prog=prog, save=save, fname=fname)
    return G
