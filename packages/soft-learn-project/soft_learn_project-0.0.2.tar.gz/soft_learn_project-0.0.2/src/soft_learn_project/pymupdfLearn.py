from PIL import Image
import io
import pymupdf


class PymupdfLearn():
  def __init__(self) -> None:
    """PyMuPDF (fitz)
    * 优点:
    - 功能强大: 支持 PDF 文件的精细操作，包括文本提取、图像处理、注释、表单处理、PDF 页面操作（如插入、删除、旋转、裁剪等）以及将 PDF 转换为图像。
    - 高效: 在处理大文件或需要快速操作时，PyMuPDF 通常表现出更好的性能。
    广泛的格式支持: 除了 PDF，PyMuPDF 还支持处理 XPS、OpenXPS、ePub、CBZ、FB2 等多种文件格式。

    *缺点:
    - 学习曲线稍陡: 由于功能较多，可能需要花一些时间熟悉其 API。
    文档相对少: 虽然 PyMuPDF 功能强大，但相关的文档和社区支持可能不如 PyPDF 广泛。

    """
    pass

  def install(self):
    """pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ PyMuPDF
    """
    pass

  def merge_pdf(self, pdf_list, pages_list,
                fname_out='merged.pdf'):
    """_summary_

    Args:
        pdf_list (_type_): 指定pdf的合并列表
        pages_list (_type_): 指定每个pdf的起止页码, 例如[[0,0],[2,3]]
        fname_out (str, optional): _description_. Defaults to 'merged.pdf'.
    """

    merged_pdf = pymupdf.open()
    for pdf, pages in zip(pdf_list, pages_list):
      pdf_doc = pymupdf.open(pdf)
      from_page, to_page = pages
      merged_pdf.insert_pdf(docsrc=pdf_doc,
                            from_page=from_page,
                            to_page=to_page,)
      pdf_doc.close()
    merged_pdf.save(filename=fname_out)
    merged_pdf.close()

    print(f'合并文件-> {fname_out}')

  def pdf_page_to_image(self, fname_pdf,
                        page_number=0,
                        is_save=False,
                        dpi=300,
                        fname_jpg='xx.png'):
    """读取pdf中的一页为图片

    Args:
        fname_pdf (_type_): _description_
        page_number (int, optional): _description_. Defaults to 0.
        is_save (bool, optional): _description_. Defaults to False.
        dpi (int, optional): _description_. Defaults to 300.
        fname_jpg (str, optional): _description_. Defaults to 'xx.jpg'.

    Returns:
        _type_: _description_
    """

    pdf_document = pymupdf.open(fname_pdf)
    pdf_page = pdf_document.load_page(page_number)
    # 获取像素图（Pixmap）
    image = pdf_page.get_pixmap(dpi=dpi)
    # 将Pixmap转换为字节流
    image_bytes = image.tobytes()

    # 使用Pillow将字节流转换为图像对象
    image_pil = Image.open(io.BytesIO(image_bytes))
    # 显示图像
    # image_pil.show()
    if is_save:
      image_pil.save(fname_jpg, dpi=(300, 300))
    pdf_document.close()
    image_pil: Image.Image
    return image_pil

  def extract_image_from_pdf(self, fname='zm.pdf',
                             pdf_page=0,
                             pdf_page_image=0,
                             ):
    """抽取pdf中的 png, jpg 等图片, 对于直接plt 产生的pdf 好像不行

    Args:
        fname (str, optional): _description_. Defaults to 'zm.pdf'.
        pdf_page (int, optional): _description_. Defaults to 0.
        pdf_page_image (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    doc = pymupdf.Document(filename=fname)
    page = doc.load_page(pdf_page)
    image_list = page.get_images()
    img = image_list[pdf_page_image]

    xref = img[0]
    base_image = doc.extract_image(xref=xref)
    image_bytes = base_image['image']

    # 保存图片
    # with open(fname_fig, 'wb') as f:
    # f.write(image_bytes)
    image = Image.open(io.BytesIO(image_bytes))
    return image

  def merge_pdfs_horizontally(self, pdf_paths, output_path):
    """把多个pdf图片 水平合并至一个pdf图片

    Args:
        pdf_paths (_type_): _description_
        output_path (_type_): _description_

    Raises:
        ValueError: _description_
    """
    # 打开每个 PDF 文件
    pdf_docs = [pymupdf.open(pdf_path) for pdf_path in pdf_paths]

    # 确保每个 PDF 文件都有至少一页
    for pdf in pdf_docs:
      if pdf.page_count < 1:
        raise ValueError(f"PDF {pdf.name} has no pages")

    # 获取第一个 PDF 文件的第一页大小
    page_rect = pdf_docs[0][0].rect
    page_width, page_height = page_rect.width, page_rect.height

    # 计算新页面的总宽度
    total_width = page_width * len(pdf_docs)

    # 创建一个新的 PDF 文档
    merged_pdf = pymupdf.open()

    # 创建一个空白页，用于放置并排合并的页面
    new_page = merged_pdf.new_page(width=total_width, height=page_height)

    # 将每个 PDF 页面粘贴到新页面上
    x_offset = 0
    for pdf in pdf_docs:
      page = pdf.load_page(0)  # 仅使用第一个页面
      new_page.show_pdf_page(
          pymupdf.Rect(x_offset, 0, x_offset + page_width, page_height), pdf, 0)
      x_offset += page_width

    # 保存合并后的 PDF 文件
    merged_pdf.save(output_path)
