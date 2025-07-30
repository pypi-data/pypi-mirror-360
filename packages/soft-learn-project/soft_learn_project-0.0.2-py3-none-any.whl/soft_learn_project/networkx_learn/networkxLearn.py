import matplotlib.pyplot as plt
import networkx as nx


class NetworkxLearn():
  def __init__(self) -> None:
    """https://networkx.org/documentation/stable/tutorial.html
    """
    pass

  def install(self):
    """pip install networkx
    """
    pass

  def useage(self):
    # Creating a graph
    g = nx.Graph()
    dg = nx.DiGraph()  # 有向图
    # 添加一个节点
    g.add_node(1)
    # 添加多个节点
    g.add_nodes_from([2, 3])
    g.add_nodes_from([
        (4, {"color": "red"}),  # 包括属性
        (5, {"color": "green"}),
    ])

  def example_1(self):
    DG = nx.DiGraph()
    DG.add_edges_from([(1, 2), (2, 3)])
    pos = {
        1: (0, 1),
        2: (0, 0),
        3: (0, -1)
    }
    nx.draw(DG,  pos=pos, with_labels=True, font_family='Heiti TC')

    # 保存图形
    # plt.savefig("path.png")

  def example_2(self):
    # 创建有向图
    G = nx.DiGraph()
    # 添加节点和边
    G.add_edges_from([(1, 2), (2, 3)])

    node_labels = {
        1: '开始执行程序',
        2: '执行',
        3: '结束'
    }

    # 创建绘图对象
    pos = {
        1: (0, 1),
        2: (0, 0),
        3: (0, -1)
    }

    # 定义节点标签的边界框属性
    node_label_options = {
        'bbox': dict(facecolor='white',  boxstyle='round', pad=0.3),
        'font_weight': 'bold',
        'font_family': 'Heiti TC',
    }

    # 绘制节点标签
    nx.draw_networkx(G, **node_label_options, labels=node_labels)

  def example_3(self):
    # 创建有向图
    G = nx.DiGraph()

    # 添加节点
    G.add_node(1, label='开始执行程序', color='lightgreen', position=(0, 1))
    G.add_node(2, label='执行', color='lightblue', position=(0, 0))
    G.add_node(3, label='结束', color='lightcoral', position=(0, -1))

    # 添加边
    G.add_edges_from([(1, 2), (2, 3)])

    # 绘制节点
    pos = {node: data['position'] for node, data in G.nodes(data=True)}
    colors = [data['color'] for node, data in G.nodes(data=True)]
    labels = {node: data['label'] for node, data in G.nodes(data=True)}

    # 定义节点标签的边界框属性
    node_label_options = {
        # alpha=0.3
        'bbox': dict(facecolor='white',  boxstyle='round', pad=0.3, ),
        'font_weight': 'bold',
    }

    # 绘制图形
    # nx.draw_networkx(G, pos=pos, node_color=range(3), cmap=plt.cm.rainbow,
    #                  node_shape='s', labels=labels, font_family='Heiti TC',)
    # nx.draw_networkx(G, pos=pos, node_color=colors, node_shape='s')
    nx.draw_networkx(G, pos=pos, labels=labels,
                     font_family='Heiti TC', **node_label_options,)

  def example_4(self):
    G_yjnr = nx.Graph(title='研究内容')
    G_yjnr.add_node(1, label='内容1', position=(0, 0))
    G_yjnr.add_node(2, label='内容2', position=(1, 0))
    G_yjnr.add_node(3, label='内容3', position=(2, 0))
    G_yjnr.add_edges_from([(1, 2), (2, 3)])

    pos = {node: data['position'] for node, data in G_yjnr.nodes.items()}
    labels = {node: data['label'] for node, data in G_yjnr.nodes.items()}
    node_label_options = {
        'bbox': dict(facecolor='white',  boxstyle='round', pad=0.3,),
    }
    nx.draw_networkx(G_yjnr, pos=pos, labels=labels,
                     font_family='Heiti TC', **node_label_options)
