import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import reportlab.pdfgen
import reportlab.pdfgen.canvas

class ReportlabLearn():
  def __init__(self) -> None:
    """ReportLab 是一个 Python 库，用于创建、生成和处理 PDF 文件。它是一个功能强大的工具，广泛用于生成报告、发票、票据、表格、图表等类型的 PDF 文档。通过 ReportLab，你可以完全控制 PDF 的布局和内容，包括文本、图像、表格、图形、条形码等。

    主要特点：
    创建和生成 PDF：通过简单的 Python 脚本，可以快速生成高质量的 PDF 文件。
    精确的布局控制：支持固定的坐标系，允许精确地放置文本、图像和形状。
    图形和图表：可以使用强大的绘图功能，绘制复杂的图形、线条、曲线等。
    灵活的排版：可以使用不同的字体、颜色、样式，支持多种文本对齐和格式。
    表格：提供了生成带有动态内容的表格的功能，支持自动调整列宽、高度、分页等。
    图像支持：支持将各种格式的图像（如 PNG、JPEG、GIF 等）嵌入到 PDF 中。
    条形码生成：支持生成多种类型的条形码。
    """
    pass

  def install(self):
    string = """pip install reportlab
    conda install reportlab
    """
    print(string)
    return None

  def drawString(self,fname='hello_world.pdf'):
    c = reportlab.pdfgen.canvas.Canvas(filename=fname, pagesize=letter)
    c.drawString(100, 750, "Hello, ReportLab!")
    c.save()
    pass

  def fig2pdf(self,
              fname_image='xxx/xx.png',
              fname_pdf=None):
    """这样生成的pdf 和 png 图片大小一样
    fname_pdf=None: 默认为使用 image 同目录同名 .pdf 文件

    Args:
        fname_image (str, optional): _description_. Defaults to 'xxx/xx.png'.
        fname_pdf (str, optional): _description_. Defaults to 'xxx/xx.pdf'.

    Returns:
        _type_: _description_
    """
    from py_package_learn.pillow_learn import pillowLearn
    image = pillowLearn.PillowLearn().get_image(fname=fname_image)
    # 获取 PNG 图片的尺寸
    width, height = image.size

    # 创建 PDF 文件
    # 默认使用 image 同目录同名 .pdf 文件
    import os 
    fname_pdf = os.path.splitext(fname_image)[0] + '.pdf' if fname_pdf is None else fname_pdf

    c = canvas.Canvas(fname_pdf, pagesize=(width, height))
    # 在 PDF 中插入 PNG 图片，保持原尺寸
    c.drawImage(fname_image, 0, 0, width, height)
    # 保存 PDF 文件
    c.save()
    print(f'{fname_pdf} -> 保存完毕!')
    return None

  def x(self):
    pass 