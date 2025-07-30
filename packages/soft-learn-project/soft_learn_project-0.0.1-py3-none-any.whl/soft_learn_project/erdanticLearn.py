import erdantic as erd
from erdantic.examples.pydantic import Party


class erdantic_learn():
  def __init__(self):
    """https://erdantic.drivendata.org/stable/examples/pydantic/
    erdantic是一个为Python数据模型类绘制实体关系图（erd）的简单工具。图表是使用古老的Graphviz库呈现的。支持的数据建模框架有：
    """
    pass

  def install(self):
    string = """conda install erdantic 

    """
    print(string)
    return None

  def ex(self):

    # Easy one-liner
    erd.draw(Party, out="diagram.png")

    # Or create a diagram object that you can inspect and do stuff with
    diagram = erd.create(Party)
    list(diagram.models.keys())
    # > [ 'erdantic.examples.pydantic.Adventurer',
    # >   'erdantic.examples.pydantic.Party',
    # >   'erdantic.examples.pydantic.Quest',
    # >   'erdantic.examples.pydantic.QuestGiver']
    diagram.draw('x.pdf')
    pass
