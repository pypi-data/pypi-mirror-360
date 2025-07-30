# 如果pdf 读取时出错, 可以使用 pdfjam 出错的.pdf -o ok.pdf  生成没有问题的pdf

import PyPDF2 
import numpy as np
import os


class Base():
  def __init__(self,) -> None:
    """
    合并页:
    # 写入文件的两种方法
    # with open('merged.pdf', 'wb') as output:  
    #     pdf_writer.write(output)  # 根据文件对象写入文件
    writer.write('tmp.pdf')  # 根据文件路径写入文件

    Args:
        read_fname (str, optional): _description_. Defaults to 'sm_扫描版.pdf'.
        write_fname (str, optional): _description_. Defaults to 'x.pdf'.
    """
    pass

  def get_numPages(self, fname_pdf,):
    """获取总页码

    Returns:
        _type_: _description_
    """
    reader = PyPDF2.PdfReader(stream=fname_pdf)
    numPages = len(reader.pages)
    return numPages

  def page_operation(self, fname_pdf, fname_out):

    with PyPDF2.PdfWriter() as writer:
      # 读取文件的两种方法
      # 从文件对象读取文件
      reader = PyPDF2.PdfReader(open(fname_pdf, 'rb'),)
      # 从文件路径读取文件
      reader = PyPDF2.PdfReader(stream=fname_pdf)
      # 获取页面对象
      page0 = reader.pages[0]
      page3 = reader.pages[3].rotate(90)
      writer = PyPDF2.PdfWriter()
      writer.add_page(page=page3)
      writer.add_page(page=page0)
      writer.write(fname_out)

      page0.merge_page(page3)  # 两页的内容合并到一页
      writer.add_page(page0)
      writer.write(fname_out)
    pass

  def write_operation(self, fname_pdf, fname_out='t.pdf'):
    with PyPDF2.PdfMerger() as merger:
      # 写入 1和3 页
      merger.append(fileobj=fname_pdf,
                    pages=[1, 3])
      # 写入 0-3 页
      merger.append(fileobj=fname_pdf,
                    pages=(0, 3))
      # 写入 1-end 页
      numPages = PyPDF2.PdfReader(stream=fname_pdf).pages.__len__()
      merger.append(fileobj=fname_pdf,
                    pages=(1, numPages))
      # 使用页码范围
      pagerange = PyPDF2.pagerange.PageRange('-2:')
      merger.append(fileobj=fname_pdf,
                    pages=pagerange)
      # 指定位置写入
      merger.merge(position=1,
                   fileobj=fname_pdf,
                   pages=[1, 2])

      # 写入
      merger.write(fname_out)
    pass

  def get_page_obj(self, fname_pdf, page=0):
    reader = PyPDF2.PdfReader(fname_pdf)
    page = reader.pages[page]
    return page

  def replace_one_page(self,
                       original_pdf,
                       replaced_1page_pdf,
                       replaced_pageNum=-2,  # 可以为负值
                       fname_out='t.pdf',):
    """取代一页pdf

    Args:
        original_pdf (_type_): _description_
        replaced_1page_pdf (_type_): _description_
        replaced_pageNum (int, optional): _description_. Defaults to -2.
        fname_out (str, optional): _description_. Defaults to 't.pdf'.
    """
    reader = PyPDF2.PdfReader(original_pdf)
    pageNum = reader.pages.__len__()
    replaced_page = PyPDF2.PdfReader(replaced_1page_pdf).pages[0]

    writer = PyPDF2.PdfWriter()
    if replaced_pageNum < 0:
      replaced_pageNum = pageNum + replaced_pageNum

    for idx in range(pageNum):
      if idx != replaced_pageNum:
        writer.add_page(page=reader.pages[idx])
      else:
        writer.add_page(page=replaced_page)

    writer.write(fname_out)

  def get_page_range_tuple(self, fname, pages='1:-2',):
    """以数组的方式选取页码范围

    Args:
        fname (_type_): _description_
        pages (str, optional): _description_. Defaults to '1:-2'.

    Returns:
        _type_: _description_
    """
    reader = PyPDF2.PdfReader(stream=fname)
    numPages = reader.pages.__len__()
    p1, p2 = pages.split(':')
    if p1 == '':
      p1 = 0
    elif int(p1) < 0:
      p1 = int(p1) + numPages
    if p2 == '':
      p2 = numPages
    elif int(p2) < 0:
      p2 = int(p2) + numPages
    pages = np.array([p1, p2]).astype(int)
    pages = tuple(pages)
    return pages


class Features():
  def __init__(self) -> None:
    """弃用, 最好使用 pypdf
    - from py_package_learn.pypdf_learn import pypdfLearn
    """
    self.base = Base()

  def get_pdf_with_pagerange(self,
                             fname_input='/Users/wangjinlong/Desktop/wang2020molecular.pdf',
                             page_range='1:',
                             fname_output='x.pdf'):
    """把 pdf 中的首页去掉 首页是图片 故而pdf较大 去掉后可以减小pdf

    Args:
        fname_input (str, optional): _description_. Defaults to '/Users/wangjinlong/Desktop/wang2020molecular.pdf'.
        page_range (str, optional): _description_. Defaults to '1:'.
        fname_output (str, optional): _description_. Defaults to 'x.pdf'.
    """

    reader = pypdf.PdfReader(stream=fname_input)
    writer = PyPDF2.PdfWriter()
    import pypdf
    page_range_tuple = self.base.get_page_range_tuple(
        fname=fname_input, pages=page_range)
    for page in reader.pages[page_range_tuple[0]:page_range_tuple[1]]:
      writer.addPage(page=page)
    writer.write(stream=fname_output)
    pass

  def get_info(self, fname):
    size = os.path.getsize(filename=fname)
    size_mb = round(size/1024/1024, 2)
    abspath = os.path.abspath(fname)
    data = {'abspath': abspath, 'size': size_mb}
    return data

  def compress_pdf_old(self, input_pdf, output_pdf=None, level='ebook'):
    """level 可以是
    /screen：适合屏幕显示，低分辨率，文件最小化。
    /ebook：适合电子书或在线发布，中等分辨率和压缩。
    /printer：适合打印输出，高分辨率和质量。

    Args:
        input_pdf (_type_): _description_
        output_pdf (_type_): _description_
        level (str, optional): _description_. Defaults to 'ebook'.
    """
    if output_pdf is None:
      output_pdf = 'compressed_'+input_pdf

    import subprocess
    subprocess.run(['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', f'-dPDFSETTINGS=/{level}',
                   '-dNOPAUSE', '-dQUIET', '-dBATCH', '-sOutputFile=' + output_pdf, input_pdf])
    data1 = self.get_info(fname=input_pdf)
    data2 = self.get_info(fname=output_pdf)
    print(
        f"{data1['abspath']} ({data1['size']} MB) -> {data2['abspath']} ({data2['size']} MB)")

  def compress_pdf(self, fname='zm.pdf',
                   pdf_page=0,
                   pdf_page_image=0,
                   devide=2,
                   fname_out='zm_small.pdf'):

    # 1. 首先抽取图片
    from py_package_learn.pymupdf_learn import pymupdfLearn
    image = pymupdfLearn.PymuPDFLearn().extract_image_from_pdf(fname=fname,
                                                               pdf_page=pdf_page,
                                                               pdf_page_image=pdf_page_image)
    # 2. 压缩图片
    from py_package_learn.pillow_learn import pillowLearn
    pf = pillowLearn.Features()
    image_small = pf.resize_from_image(img=image, devide=devide)

    # 3. 保存pdf
    image_small.save(fname_out)

    # 4. 描述
    # data1 = self.get_info(fname=fname)
    # print(f"{data1['abspath']} ({data1['size']} MB)")

    data2 = self.get_info(fname=fname_out)
    print(f"{data2['abspath']} ({data2['size']} MB)")
    pass

  def merge_pdf(self, pdf_list, pages=None, fname_out='tmp.pdf'):
    merge = PyPDF2.PdfMerger()
    for file_obj in pdf_list:
      merge.append(fileobj=file_obj, pages=pages)
    merge.write(fname_out)
