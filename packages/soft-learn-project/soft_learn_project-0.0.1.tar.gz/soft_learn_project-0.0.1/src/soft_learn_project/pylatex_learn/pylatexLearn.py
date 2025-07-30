import os
import shutil
import pylatex
import numpy as np
import re
import time
import string
import pandas as pd
import pylatex.base_classes
import pylatex.config
import random
import matplotlib


class PylatexLearn():
  def __init__(self) -> None:
    """https://jeltef.github.io/PyLaTeX/current/
    pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ pylatex
    """
    pass

  def Basic_example(self):
    """This example shows basic document generation functionality.
    """

    def fill_document(doc: pylatex.document.Document):
      """Add a section, a subsection and some text to the document.

      :param doc: the document
      :type doc: :class:`pylatex.document.Document` instance
      """
      with doc.create(pylatex.Section('A section')):
        doc.append('Some regular text and some ')
        doc.append(pylatex.utils.italic('italic text. '))

        with doc.create(pylatex.Subsection('A subsection')):
          doc.append('Also some crazy characters: $&#{}')

    # Basic document
    doc = pylatex.Document('basic')
    fill_document(doc)

    doc.generate_pdf(clean_tex=False)
    doc.generate_tex()

    # Document with `\maketitle` command activated
    doc = pylatex.Document()

    doc.preamble.append(pylatex.Command('title', 'Awesome Title'))
    doc.preamble.append(pylatex.Command('author', 'Anonymous author'))
    doc.preamble.append(pylatex.Command('date', pylatex.NoEscape(r'\today')))
    # doc.append(pylatex.NoEscape(r'\maketitle'))
    doc.append(pylatex.Command('maketitle'))

    fill_document(doc)

    doc.generate_pdf('basic_maketitle', clean_tex=False)

    # # Add stuff to the document
    # with doc.create(Section('A second section')):
    #   doc.append('Some text.')

    # doc.generate_pdf('basic_maketitle2', clean_tex=False)
    # tex = doc.dumps()  # The document as string in LaTeX syntax

  def Basic_inheritance_example(self):
    """This example shows basic document generation functionality by inheritance.
    """

    class MyDocument(pylatex.Document):
      def __init__(self):
        super().__init__()

        self.preamble.append(pylatex.Command('title', 'Awesome Title'))
        self.preamble.append(pylatex.Command('author', 'Anonymous author'))
        self.preamble.append(pylatex.Command(
            'date', pylatex.NoEscape(r'\today')))
        self.append(pylatex.NoEscape(r'\maketitle'))

      def fill_document(self):
        """Add a section, a subsection and some text to the document."""
        with self.create(pylatex.Section('A section')):
          self.append('Some regular text and some ')
          self.append(pylatex.utils.italic('italic text. '))

          with self.create(pylatex.Subsection('A subsection')):
            self.append('Also some crazy characters: $&#{}')

    # Document
    doc = MyDocument()

    # Call function to add text
    doc.fill_document()

    # Add stuff to the document
    with doc.create(pylatex.Section('A second section')):
      doc.append('Some text.')

    doc.generate_pdf('basic_inheritance', clean_tex=False)
    # tex = doc.dumps()  # The document as string in LaTeX syntax
    return doc

  def Complex_report_example(self, fname_fig='/Users/wangjinlong/Desktop/wqh6_7yue.jpeg'):
    """This example shows the functionality of the PyLaTeX library.

    It creates a sample report with 2 tables, one containing images and the other containing data. It also creates a complex header with an image.
    """
    geometry_options = {
        "head": "40pt",
        "margin": "0.5in",
        "bottom": "0.6in",
        "includeheadfoot": True
    }
    doc = pylatex.Document(geometry_options=geometry_options)

    # Generating first page style
    first_page = pylatex.PageStyle("firstpage")

    # Header image
    with first_page.create(pylatex.Head("L")) as header_left:
      with header_left.create(pylatex.MiniPage(width=pylatex.NoEscape(r"0.49\textwidth"),
                                               pos='c')) as logo_wrapper:
        # logo_file = os.path.join(os.path.dirname(__file__),'sample-logo.png')
        logo_file = './logo.png'
        logo_wrapper.append(pylatex.StandAloneGraphic(image_options="width=120px",
                            filename=logo_file))

    # Add document title
    with first_page.create(pylatex.Head("R")) as right_header:
      with right_header.create(pylatex.MiniPage(width=pylatex.NoEscape(r"0.49\textwidth"),
                                                pos='c', align='r')) as title_wrapper:
        title_wrapper.append(
            pylatex.LargeText(pylatex.utils.bold("Bank Account Statement")))
        title_wrapper.append(pylatex.LineBreak())
        title_wrapper.append(pylatex.MediumText(pylatex.utils.bold("Date")))

    # Add footer
    with first_page.create(pylatex.Foot("C")) as footer:
      message = "Important message please read"
      with footer.create(pylatex.Tabularx(
              "X X X X",
              width_argument=pylatex.NoEscape(r"\textwidth"))) as footer_table:

        footer_table.add_row(
            [pylatex.MultiColumn(4, align='l', data=pylatex.TextColor("blue", message))])
        footer_table.add_hline(color="blue")
        footer_table.add_empty_row()

        branch_address = pylatex.MiniPage(
            width=pylatex.NoEscape(r"0.25\textwidth"),
            pos='t')
        branch_address.append("960 - 22nd street east")
        branch_address.append("\n")
        branch_address.append("Saskatoon, SK")

        document_details = pylatex.MiniPage(width=pylatex.NoEscape(r"0.25\textwidth"),
                                            pos='t', align='r')
        document_details.append("1000")
        document_details.append(pylatex.LineBreak())
        document_details.append(pylatex.simple_page_number())

        footer_table.add_row([branch_address, branch_address,
                              branch_address, document_details])

    doc.preamble.append(first_page)
    # End first page style

    # Add customer information
    with doc.create(pylatex.Tabu("X[l] X[r]")) as first_page_table:
      customer = pylatex.MiniPage(
          width=pylatex.NoEscape(r"0.49\textwidth"), pos='h')
      customer.append("Verna Volcano")
      customer.append("\n")
      customer.append("For some Person")
      customer.append("\n")
      customer.append("Address1")
      customer.append("\n")
      customer.append("Address2")
      customer.append("\n")
      customer.append("Address3")

      # Add branch information
      branch = pylatex.MiniPage(width=pylatex.NoEscape(r"0.49\textwidth"), pos='t!',
                                align='r')
      branch.append("Branch no.")
      branch.append(pylatex.LineBreak())
      branch.append(pylatex.utils.bold("1181..."))
      branch.append(pylatex.LineBreak())
      branch.append(pylatex.utils.bold("TIB Cheque"))

      first_page_table.add_row([customer, branch])
      first_page_table.add_empty_row()

    doc.change_document_style("firstpage")
    doc.add_color(name="lightgray", model="gray", description="0.80")

    # Add statement table
    with doc.create(pylatex.LongTabu("X[l] X[2l] X[r] X[r] X[r]",
                                     row_height=1.5)) as data_table:
      data_table.add_row(["date",
                          "description",
                          "debits($)",
                          "credits($)",
                          "balance($)"],
                         mapper=pylatex.utils.bold,
                         color="lightgray")
      data_table.add_empty_row()
      data_table.add_hline()
      row = ["2016-JUN-01", "Test", "$100", "$1000", "-$900"]
      for i in range(30):
        if (i % 2) == 0:
          data_table.add_row(row, color="lightgray")
        else:
          data_table.add_row(row)

    doc.append(pylatex.NewPage())

    # Add cheque images
    with doc.create(pylatex.LongTabu("X[c] X[c]")) as cheque_table:
      # cheque_file = os.path.join(os.path.dirname(__file__),'chequeexample.png')
      cheque_file = fname_fig
      cheque = pylatex.StandAloneGraphic(
          cheque_file, image_options="width=200px")
      for i in range(0, 20):
        cheque_table.add_row([cheque, cheque])

    doc.generate_pdf("complex_report", clean_tex=False)

  def config_example(self):
    """This example shows basic document generation functionality.
    """

    lorem = '''
    Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere
    cubilia Curae; Phasellus facilisis tortor vel imperdiet vestibulum. Vivamus et
    mollis risus. Proin ut enim eu leo volutpat tristique. Vivamus quam enim,
    efficitur quis turpis ac, condimentum tincidunt tellus. Praesent non tellus in
    quam tempor dignissim. Sed feugiat ante id mauris vehicula, quis elementum nunc
    molestie. Pellentesque a vulputate nisi, ut vulputate ex. Morbi erat eros,
    aliquam in justo sed, placerat tempor mauris. In vitae velit eu lorem dapibus
    consequat. Integer posuere ornare laoreet.

    Donec pellentesque libero id tempor aliquam. Maecenas a diam at metus varius
    rutrum vel in nisl. Maecenas a est lorem. Vivamus tristique nec eros ac
    hendrerit. Vivamus imperdiet justo id lobortis luctus. Sed facilisis ipsum ut
    tellus pellentesque tincidunt. Mauris libero lectus, maximus at mattis ut,
    venenatis eget diam. Fusce in leo at erat varius laoreet. Mauris non ipsum
    pretium, convallis purus vel, pulvinar leo. Aliquam lacinia lorem dapibus
    tortor imperdiet, quis consequat diam mollis.

    Praesent accumsan ultrices diam a eleifend. Vestibulum ante ipsum primis in
    faucibus orci luctus et ultrices posuere cubilia Curae; Suspendisse accumsan
    orci ut sodales ullamcorper. Integer bibendum elementum convallis. Praesent
    accumsan at leo eget ullamcorper. Maecenas eget tempor enim. Quisque et nisl
    eros.
    '''
    # 是否缩进
    pylatex.config.active = pylatex.config.Version1(indent=False)
    doc = pylatex.Document(data=pylatex.NoEscape(lorem))
    doc.generate_pdf('config2_without_indent', clean_tex=False)

    with pylatex.config.Version1().use():
      doc = pylatex.Document(data=pylatex.NoEscape(lorem))
      doc.generate_pdf('config3_with_indent_again', clean_tex=False)

    doc = pylatex.Document(data=pylatex.NoEscape(lorem),)
    doc.generate_pdf('config4_without_indent_again', clean_tex=False)
    pass

  def Environment_example(self):
    """Wrapping existing LaTeX environments with the Environment class.
    """

    class AllTT(pylatex.base_classes.Environment):
      """A class to wrap LaTeX's alltt environment."""

      packages = [pylatex.package.Package('alltt')]
      escape = False
      content_separator = "\n"

    # Create a new document
    doc = pylatex.Document()
    with doc.create(pylatex.Section('Wrapping Latex Environments')):
      doc.append(pylatex.NoEscape(
          r"""
            The following is a demonstration of a custom \LaTeX{}
            command with a couple of parameters.
            """))

      # Put some data inside the AllTT environment
      with doc.create(AllTT()):
        verbatim = ("This is verbatim, alltt, text.\n\n\n"
                    "Setting \\underline{escape} to \\underline{False} "
                    "ensures that text in the environment is not\n"
                    "subject to escaping...\n\n\n"
                    "Setting \\underline{content_separator} "
                    "ensures that line endings are broken in\n"
                    "the latex just as they are in the input text.\n"
                    "alltt supports math: \\(x^2=10\\)")
        doc.append(verbatim)

      doc.append("This is back to normal text...")

    # Generate pdf
    doc.generate_pdf('environment_ex', clean_tex=False)
    pass

  def Full_example(self,
                   directory,
                   fname_fig='/Users/wangjinlong/Pictures/zqb_元素周期表.jpeg',
                   clean_tex=False,
                   clean=True,
                   ):
    """This example demonstrates several features of PyLaTeX.

    It includes plain equations, tables, equations using numpy objects, tikz plots, and figures.
    """

    # image_filename = os.path.join(os.path.dirname(__file__), 'kitten.jpg')
    image_filename = fname_fig

    doc = pylatex.Document(
        document_options=['onehalfspacing',
                          '12pt'],  # 1.5 倍行距和12pt 字体
        geometry_options={
            # {'scale': 0.8}
            'top': '2.5cm', 'bottom': '2.5cm', 'left': '3cm', 'right': '3cm'},
        documentclass='ctexart')
    # 加入包
    package = pylatex.package.Package(name='float')
    doc.packages.append(package)
    # lineno 宏包 可以使用 \linenumbers 命令启用行号。每一行文本之后都会显示行号。
    doc.packages.append(pylatex.Package('lineno'))
    latex_obj = pylatex.NoEscape(r'\linenumbers')
    doc.append(latex_obj)
    doc.preamble.append(pylatex.Package('lipsum'))  # 虚拟英文
    doc.preamble.append(pylatex.Package('zhlipsum'))

    # doc.preamble.append(pylatex.Package('ctex'))
    # 用法
    # doc.append(pylatex.NoEscape(r'\lipsum[1]'))

    # 斜体
    with doc.create(pylatex.Section('The simple stuff')):
      doc.append('Some regular text and some')
      doc.append(pylatex.utils.italic('italic text. '))
      doc.append('\nAlso some crazy characters: $&#{}')
      with doc.create(pylatex.Subsection('Math that is incorrect')):
        doc.append(pylatex.Math(data=['2*3', '=', 9]))

      # 表格
      with doc.create(pylatex.Subsection('Table of something')):
        with doc.create(pylatex.Tabular('rc|cl')) as table:
          table: pylatex.Tabular
          table.add_hline()
          table.add_row((11, 12, 13, 154))
          table.add_hline(1, 2)
          table.add_empty_row()
          table.add_row((4, 5, 6, 7))
      # 或者用这种方式
      # tb = pylatex.Tabular('rc|cl')
      # tb.add_hline()
      # tb.add_row((11, 12, 13, 154))
      # tb.add_hline(1, 2)
      # tb.add_empty_row()
      # tb.add_row((4, 5, 6, 7))
      # doc.append(tb)

    a = np.array([[100, 10, 20]]).T
    M = np.matrix([[2, 3, 4],
                  [0, 0, 1],
                  [0, 0, 2]])

    with doc.create(pylatex.Section('The fancy stuff')):
      with doc.create(pylatex.Subsection('Correct matrix equations')):
        doc.append(pylatex.Math(data=[pylatex.Matrix(
            M), pylatex.Matrix(a), '=', pylatex.Matrix(M * a)]))

      with doc.create(pylatex.Subsection('Alignat math environment')):
        with doc.create(pylatex.Alignat(numbering=False, escape=False)) as agn:
          agn: pylatex.Alignat
          agn.append(r'\frac{a}{b} &= 0 \\')
          agn.extend([pylatex.Matrix(M), pylatex.Matrix(a),
                     '&=', pylatex.Matrix(M * a)])

      with doc.create(pylatex.Subsection('Beautiful graphs')):
        with doc.create(pylatex.TikZ()):
          plot_options = 'height=4cm, width=6cm, grid=major'
          with doc.create(pylatex.Axis(options=plot_options)) as plot:
            plot.append(pylatex.Plot(name='model', func='-x^5 - 242'))

            coordinates = [
                (-4.77778, 2027.60977),
                (-3.55556, 347.84069),
                (-2.33333, 22.58953),
                (-1.11111, -493.50066),
                (0.11111, 46.66082),
                (1.33333, -205.56286),
                (2.55556, -341.40638),
                (3.77778, -1169.24780),
                (5.00000, -3269.56775),
            ]

            plot.append(pylatex.Plot(name='estimate', coordinates=coordinates))

      with doc.create(pylatex.Subsection('Cute kitten pictures')):
        with doc.create(pylatex.Figure(position='H')) as kitten_pic:
          kitten_pic.add_image(image_filename,
                               width=pylatex.NoEscape(r'0.5\linewidth')
                               )
          kitten_pic.add_caption('Look it\'s on its back')

    # 颜色
    par1 = pylatex.NoEscape(
        r'\par 这是修改的部分: \color{blue} 已修改 \color{black}这是未修改的部分.')
    doc.append(par1)
    # 结束行号
    # doc.append(pylatex.NoEscape(r'\nolinenumbers'))

    fname_out = os.path.join(directory, 'full')
    doc.generate_pdf(fname_out,
                     clean_tex=clean_tex,
                     clean=clean,
                     compiler='xelatex',
                     )
    return doc

  def Header_example(self):
    """This example shows the functionality of the PageHeader object.

    It creates a sample page with the different types of headers and footers.
    """

    from pylatex import Document, PageStyle, Head, MiniPage, Foot, LargeText, \
        MediumText, LineBreak, simple_page_number

    # Add document header
    header = PageStyle("header")
    # Create left header
    with header.create(Head("L")):
      header.append("Page date: ")
      header.append(LineBreak())
      header.append("R3")
    # Create center header
    with header.create(Head("C")):
      header.append("Company")
    # Create right header
    with header.create(Head("R")):
      header.append(simple_page_number())
    # Create left footer
    with header.create(Foot("L")):
      header.append("Left Footer")
    # Create center footer
    with header.create(Foot("C")):
      header.append("Center Footer")
    # Create right footer
    with header.create(Foot("R")):
      header.append("Right Footer")

    geometry_options = {"margin": "0.7in"}
    doc = Document(geometry_options=geometry_options)
    doc.preamble.append(header)
    doc.change_document_style("header")

    # Add Heading
    with doc.create(MiniPage(align='c')):
      doc.append(LargeText(pylatex.utils.bold("Title")))
      doc.append(LineBreak())
      doc.append(MediumText(pylatex.utils.bold("As at:")))

    doc.generate_pdf("header", clean_tex=False)

    pass

  def Lists_example(self):
    """This example shows list functionality.
    """
    # Test for list structures in PyLaTeX.
    # More info @ http://en.wikibooks.org/wiki/LaTeX/List_Structures

    doc = pylatex.Document()

    # create a bulleted "itemize" list like the below:
    # \begin{itemize}
    #   \item The first item
    #   \item The second item
    #   \item The third etc \ldots
    # \end{itemize}

    with doc.create(pylatex.Section('"Itemize" list')):
      with doc.create(pylatex.Itemize()) as itemize:
        itemize: pylatex.Itemize
        itemize.add_item("the first item")
        itemize.add_item("the second item")
        itemize.add_item("the third etc")
        # you can append to existing items
        itemize.append(pylatex.Command("ldots"))

    # create a numbered "enumerate" list like the below:
    # \begin{enumerate}[label=\alph*),start=20]
    #   \item The first item
    #   \item The second item
    #   \item The third etc \ldots
    # \end{enumerate}

    with doc.create(pylatex.Section('"Enumerate" list')):
      with doc.create(pylatex.Enumerate(enumeration_symbol=r"\alph*)",
                                        options={'start': 20})) as enum:
        enum.add_item("the first item")
        enum.add_item("the second item")
        enum.add_item(pylatex.NoEscape("the third etc \\ldots"))

    # create a labelled "description" list like the below:
    # \begin{description}
    #   \item[First] The first item
    #   \item[Second] The second item
    #   \item[Third] The third etc \ldots
    # \end{description}

    with doc.create(pylatex.Section('"Description" list')):
      with doc.create(pylatex.Description()) as desc:
        desc.add_item("First", "The first item")
        desc.add_item("Second", "The second item")
        desc.add_item("Third", pylatex.NoEscape("The third etc \\ldots"))

    doc.generate_pdf('lists', clean_tex=False)
    pass

  def Longtable_example(self):
    """This example shows the functionality of the longtable element.

    It creates a sample multi-page spanning table
    """

    def genenerate_longtabu():
      geometry_options = {
          "margin": "2.54cm",
          "includeheadfoot": True
      }
      doc = pylatex.Document(
          page_numbers=True, geometry_options=geometry_options
      )

      # Generate data table
      with doc.create(pylatex.LongTable("l l l")) as data_table:
        data_table: pylatex.LongTable
        data_table.add_hline()
        data_table.add_row(["header 1", "header 2", "header 3"])
        data_table.add_hline()
        data_table.end_table_header()
        data_table.add_hline()
        data_table.add_row((pylatex.MultiColumn(3, align='r',
                            data='Continued on Next Page'),))
        data_table.add_hline()
        data_table.end_table_footer()
        data_table.add_hline()
        data_table.add_row((pylatex.MultiColumn(3, align='r',
                            data='Not Continued on Next Page'),))
        data_table.add_hline()
        data_table.end_table_last_footer()
        for i in range(80):
          data_table.add_row([f"Content{i}", "9", "Longer String"])

      doc.generate_pdf("longtable", clean_tex=False)

    genenerate_longtabu()
    pass

  def Longtabu_example(self):
    """This example shows the functionality of the MiniPage element.

    It creates a sample page filled with labels using the MiniPage element.
    """

    def genenerate_longtabu():
      geometry_options = {
          "landscape": True,
          "margin": "0.5in",
          "headheight": "20pt",
          "headsep": "10pt",
          "includeheadfoot": True
      }
      doc = pylatex.Document(
          page_numbers=True, geometry_options=geometry_options)

      # Generate data table
      with doc.create(pylatex.LongTabu("X[r] X[r] X[r] X[r] X[r] X[r]")) as data_table:
        data_table: pylatex.LongTabu
        header_row1 = ["Prov", "Num", "CurBal", "IntPay", "Total", "IntR"]
        data_table.add_row(header_row1, mapper=[pylatex.utils.bold])
        data_table.add_hline()
        data_table.add_empty_row()
        data_table.end_table_header()
        data_table.add_row(["Prov", "Num", "CurBal", "IntPay", "Total",
                            "IntR"])
        # data_table.end_table_footer()
        row = ["PA", "9", "$100", "%10", "$1000", "Test"]
        for i in range(50):
          data_table.add_row(row)

      doc.append(pylatex.utils.bold("Grand Total:"))
      doc.append(pylatex.HFill())
      doc.append(pylatex.utils.bold("Total"))

      doc.generate_pdf("longtabu", clean_tex=False)

    genenerate_longtabu()

  def Matplotlib_example(self):
    """This example shows matplotlib functionality.
    """

    matplotlib.use('Agg')  # Not to use X server. For TravisCI.
    import matplotlib.pyplot as plt  # noqa

    def main(fname, width, *args, **kwargs):
      geometry_options = {"right": "2cm", "left": "2cm"}
      doc = pylatex.Document(fname, geometry_options=geometry_options)

      doc.append('Introduction.')

      with doc.create(pylatex.Section('I am a section')):
        doc.append('Take a look at this beautiful plot:')

        with doc.create(pylatex.Figure(position='htbp')) as plot:
          plot.add_plot(width=pylatex.NoEscape(width), *args, **kwargs)
          plot.add_caption('I am a caption.')

        doc.append('Created using matplotlib.')

      doc.append('Conclusion.')

      doc.generate_pdf(clean_tex=False)

    # ---
    x = [0, 1, 2, 3, 4, 5, 6]
    y = [15, 2, 7, 1, 5, 6, 9]

    plt.plot(x, y)

    main('matplotlib_ex-dpi', r'1\textwidth', dpi=300)
    main('matplotlib_ex-facecolor', r'0.5\textwidth', facecolor='b')

  def Minipage_example(self):
    """This example shows the functionality of the MiniPage element.

    It creates a sample page filled with labels using the MiniPage element.
    """

    def generate_labels():
      geometry_options = {"margin": "0.5in"}
      doc = pylatex.Document(geometry_options=geometry_options)

      doc.change_document_style("empty")

      for i in range(10):
        with doc.create(pylatex.MiniPage(width=r"0.5\textwidth")):
          doc.append("Vladimir Gorovikov")
          doc.append("\n")
          doc.append("Company Name")
          doc.append("\n")
          doc.append("Somewhere, City")
          doc.append("\n")
          doc.append("Country")

        if (i % 2) == 1:
          doc.append(pylatex.VerticalSpace("20pt"))
          doc.append(pylatex.LineBreak())

      doc.generate_pdf("minipage", clean_tex=False)

    generate_labels()
    pass

  def Multirow_example(self):
    """This example shows how multirow and multicolumns can be used.
    """

    doc = pylatex.Document("multirow")
    section = pylatex.Section('Multirow Test')

    test1 = pylatex.Subsection('MultiColumn')
    test2 = pylatex.Subsection('MultiRow')
    test3 = pylatex.Subsection('MultiColumn and MultiRow')
    test4 = pylatex.Subsection('Vext01')

    table1 = pylatex.Tabular('|c|c|c|c|')
    table1.add_hline()
    table1.add_row((pylatex.MultiColumn(4, align='|c|', data='Multicolumn'),))
    table1.add_hline()
    table1.add_row((1, 2, 3, 4))
    table1.add_hline()
    table1.add_row((5, 6, 7, 8))
    table1.add_hline()
    row_cells = ('9', pylatex.MultiColumn(
        3, align='|c|', data='Multicolumn not on left'))
    table1.add_row(row_cells)
    table1.add_hline()

    table2 = pylatex.Tabular('|c|c|c|')
    table2.add_hline()
    table2.add_row((pylatex.MultiRow(3, data='Multirow'), 1, 2))
    table2.add_hline(2, 3)
    table2.add_row(('', 3, 4))
    table2.add_hline(2, 3)
    table2.add_row(('', 5, 6))
    table2.add_hline()
    table2.add_row((pylatex.MultiRow(3, data='Multirow2'), '', ''))
    table2.add_empty_row()
    table2.add_empty_row()
    table2.add_hline()

    table3 = pylatex.Tabular('|c|c|c|')
    table3.add_hline()
    table3.add_row((pylatex.MultiColumn(2, align='|c|',
                                        data=pylatex.MultiRow(2, data='multi-col-row')), 'X'))
    table3.add_row((pylatex.MultiColumn(2, align='|c|', data=''), 'X'))
    table3.add_hline()
    table3.add_row(('X', 'X', 'X'))
    table3.add_hline()

    table4 = pylatex.Tabular('|c|c|c|')
    table4.add_hline()
    col1_cell = pylatex.MultiRow(4, data='span-4')
    col2_cell = pylatex.MultiRow(2, data='span-2')
    table4.add_row((col1_cell, col2_cell, '3a'))
    table4.add_hline(start=3)
    table4.add_row(('', '', '3b'))
    table4.add_hline(start=2)
    table4.add_row(('', col2_cell, '3c'))
    table4.add_hline(start=3)
    table4.add_row(('', '', '3d'))
    table4.add_hline()

    test1.append(table1)
    test2.append(table2)
    test3.append(table3)
    test4.append(table4)

    section.append(test1)
    section.append(test2)
    section.append(test3)
    section.append(test4)

    doc.append(section)
    doc.generate_pdf(clean_tex=False)

  def Numpy_example(self):
    """This example shows numpy functionality.
    """

    doc = pylatex.Document()
    section = pylatex.Section('Numpy tests')
    subsection = pylatex.Subsection('Array')

    a = np.array([[100, 10, 20]]).T
    vec = pylatex.Matrix(a)
    vec_name = pylatex.VectorName('a')
    math = pylatex.Math(data=[vec_name, '=', vec])

    subsection.append(math)
    section.append(subsection)

    subsection = pylatex.Subsection('Matrix')
    M = np.matrix([[2, 3, 4],
                  [0, 0, 1],
                  [0, 0, 2]])
    matrix = pylatex.Matrix(M, mtype='b')
    math = pylatex.Math(data=['M=', matrix])

    subsection.append(math)
    section.append(subsection)

    subsection = pylatex.Subsection('Product')

    math = pylatex.Math(data=['M', vec_name, '=', pylatex.Matrix(M * a)])
    subsection.append(math)

    section.append(subsection)

    doc.append(section)
    doc.generate_pdf('numpy_ex', clean_tex=False)
    pass

  def Own_commands_example(self):
    """How to represent your own LaTeX commands and environments in PyLaTeX.
    """
    class ExampleEnvironment(pylatex.base_classes.Environment):
      """
      A class representing a custom LaTeX environment.

      This class represents a custom LaTeX environment named
      ``exampleEnvironment``.
      """

      _latex_name = 'exampleEnvironment'
      packages = [pylatex.Package('mdframed')]

    class ExampleCommand(pylatex.base_classes.CommandBase):
      """
      A class representing a custom LaTeX command.

      This class represents a custom LaTeX command named
      ``exampleCommand``.
      """

      _latex_name = 'exampleCommand'
      packages = [pylatex.Package('color')]

    # Create a new document
    doc = pylatex.Document()
    with doc.create(pylatex.Section('Custom commands')):
      doc.append(pylatex.NoEscape(
          r"""
            The following is a demonstration of a custom \LaTeX{}
            command with a couple of parameters.
            """))

      # Define the new command
      new_comm = pylatex.UnsafeCommand('newcommand',
                                       r'\exampleCommand',
                                       options=3,
                                       extra_arguments=r'\color{#1} #2 #3 \color{black}')
      doc.append(new_comm)

      # Use our newly created command with different arguments
      doc.append(ExampleCommand(
          arguments=pylatex.base_classes.Arguments('blue', 'Hello', 'World!')))
      doc.append(ExampleCommand(
          arguments=pylatex.base_classes.Arguments('green', 'Hello', 'World!')))
      doc.append(ExampleCommand(
          arguments=pylatex.base_classes.Arguments('red', 'Hello', 'World!')))

    with doc.create(pylatex.Section('Custom environments')):
      doc.append(pylatex.NoEscape(
          r"""
            The following is a demonstration of a custom \LaTeX{}
            environment using the mdframed package.
            """))

      # Define a style for our box
      mdf_style_definition = pylatex.UnsafeCommand('mdfdefinestyle',
                                                   arguments=['my_style',
                                                              ('linecolor=#1,'
                                                               'linewidth=#2,'
                                                               'leftmargin=1cm,'
                                                               'leftmargin=1cm')])

      # Define the new environment using the style definition above
      new_env = pylatex.UnsafeCommand('newenvironment', 'exampleEnvironment', options=2,
                                      extra_arguments=[
                                          mdf_style_definition.dumps() +
                                          r'\begin{mdframed}[style=my_style]',
                                          r'\end{mdframed}'])
      doc.append(new_env)

      # Usage of the newly created environment
      with doc.create(
              ExampleEnvironment(arguments=pylatex.base_classes.Arguments('red', 3))) as environment:
        environment.append('This is the actual content')

    # Generate pdf
    doc.generate_pdf('own_commands_ex', clean_tex=False)
    pass

  def custom_cmd_example(self):
    """How to represent your own LaTeX commands and environments in PyLaTeX.
    """
    class ExampleCommand(pylatex.base_classes.CommandBase):
      """
      A class representing a custom LaTeX command.

      This class represents a custom LaTeX command named
      ``exampleCommand``.
      """

      _latex_name = 'exampleCommand'
      packages = [pylatex.package.Package('color')]

    # Create a new document
    doc = pylatex.Document()

    with doc.create(pylatex.Section('Custom commands')):
      doc.append(pylatex.NoEscape(
          r"""
            The following is a demonstration of a custom \LaTeX{}
            command with a couple of parameters.
            """))

      # Define the new command
      new_comm = pylatex.UnsafeCommand('newcommand',
                                       r'\exampleCommand',
                                       options=3,
                                       extra_arguments=r'\color{#1} #2 #3 \color{black}')
      doc.append(new_comm)

      # Use our newly created command with different arguments
      doc.append(ExampleCommand(
          arguments=pylatex.base_classes.Arguments('blue', 'Hello', 'World!')))

    # Generate pdf
    doc.generate_pdf('custom_cmd', clean_tex=False)
    pass

  def custom_env_example(self):
    """How to represent your own LaTeX commands and environments in PyLaTeX.
    """

    class ExampleEnvironment(pylatex.base_classes.Environment):
      """
      A class representing a custom LaTeX environment.

      This class represents a custom LaTeX environment named
      ``exampleEnvironment``.
      """

      _latex_name = 'exampleEnvironment'
      packages = [pylatex.Package('mdframed')]

    # Create a new document
    doc = pylatex.Document()

    with doc.create(pylatex.Section('Custom environments')):
      doc.append(pylatex.NoEscape(
          r"""
              The following is a demonstration of a custom \LaTeX{}
              environment using the mdframed package.
              """))

      # Define a style for our box
      mdf_style_definition = pylatex.UnsafeCommand('mdfdefinestyle',
                                                   arguments=['my_style',
                                                              ('linecolor=#1,'
                                                               'linewidth=#2,'
                                                               'leftmargin=1cm,'
                                                               'leftmargin=1cm')])

      # Define the new environment using the style definition above
      new_env = pylatex.UnsafeCommand('newenvironment', 'exampleEnvironment', options=2,
                                      extra_arguments=[
                                          mdf_style_definition.dumps() +
                                          r'\begin{mdframed}[style=my_style]',
                                          r'\end{mdframed}'])
      doc.append(new_env)

      # Usage of the newly created environment
      with doc.create(
              ExampleEnvironment(arguments=pylatex.base_classes.Arguments('red', 3))) as environment:
        environment.append('This is the actual content')

    # Generate pdf
    doc.generate_pdf('custom_env', clean_tex=False)
    pass

  def Quantities_example(self):
    """This example shows quantities functionality.
    """

    """
    import quantities as pq
    from pylatex import Document, Section, Subsection, Math, Quantity
    # from scipy import constants
    # G = constants.gravitational_constant

    doc = Document()
    section = Section('Quantity tests')
    subsection = Subsection('Scalars with units')
    G = pq.constants.Newtonian_constant_of_gravitation
    moon_earth_distance = 384400 * pq.km
    moon_mass = 7.34767309e22 * pq.kg
    earth_mass = 5.972e24 * pq.kg
    moon_earth_force = G * moon_mass * earth_mass / moon_earth_distance**2
    q1 = Quantity(moon_earth_force.rescale(pq.newton),
                  options={'round-precision': 4, 'round-mode': 'figures'})
    math = Math(data=['F=', q1])
    subsection.append(math)
    section.append(subsection)

    subsection = Subsection('Scalars without units')
    world_population = 7400219037
    N = Quantity(world_population, options={'round-precision': 2,
                                            'round-mode': 'figures'},
                 format_cb="{0:23.17e}".format)
    subsection.append(Math(data=['N=', N]))
    section.append(subsection)

    subsection = Subsection('Scalars with uncertainties')
    width = pq.UncertainQuantity(7.0, pq.meter, .4)
    length = pq.UncertainQuantity(6.0, pq.meter, .3)
    area = Quantity(width * length, options='separate-uncertainty',
                    format_cb=lambda x: "{0:.1f}".format(float(x)))
    subsection.append(Math(data=['A=', area]))
    section.append(subsection)

    doc.append(section)
    doc.generate_pdf('quantities_ex', clean_tex=False)
    """
    pass

  def Subfigure_example(self, fname_fig='/Users/wangjinlong/Desktop/wqh6_7yue.jpeg'):
    """This example shows subfigure functionality.
    """

    doc = pylatex.Document(default_filepath='subfigures')
    # image_filename = os.path.join(os.path.dirname(__file__), fname_fig)
    image_filename = fname_fig

    with doc.create(pylatex.Section('Showing subfigures')):
      with doc.create(pylatex.Figure(position='h!')) as kittens:
        with doc.create(pylatex.SubFigure(
                position='b',
                width=pylatex.NoEscape(r'0.45\linewidth'))) as left_kitten:

          left_kitten.add_image(image_filename,
                                width=pylatex.NoEscape(r'\linewidth'))
          left_kitten.add_caption('Kitten on the left')
        with doc.create(pylatex.SubFigure(
                position='b',
                width=pylatex.NoEscape(r'0.45\linewidth'))) as right_kitten:

          right_kitten.add_image(image_filename,
                                 width=pylatex.NoEscape(r'\linewidth'))
          right_kitten.add_caption('Kitten on the right')
        kittens.add_caption("Two kittens")

    doc.generate_pdf(clean_tex=False)

  def Tabus_example(self):
    """This example shows the functionality of the MiniPage element.

    It creates a sample page filled with labels using the MiniPage element.
    """

    geometry_options = {
        "landscape": True,
        "margin": "1.5in",
        "headheight": "20pt",
        "headsep": "10pt",
        "includeheadfoot": True
    }
    doc = pylatex.Document(
        page_numbers=True, geometry_options=geometry_options)

    # Generate data table with 'tight' columns
    fmt = "X[r] X[r] X[r] X[r] X[r] X[r]"
    with doc.create(pylatex.LongTabu(fmt, spread="0pt")) as data_table:
      header_row1 = ["Prov", "Num", "CurBal", "IntPay", "Total", "IntR"]
      data_table.add_row(header_row1, mapper=[pylatex.utils.bold])
      data_table.add_hline()
      data_table.add_empty_row()
      data_table.end_table_header()
      data_table.add_row(["Prov", "Num", "CurBal", "IntPay", "Total",
                          "IntR"])
      row = ["PA", "9", "$100", "%10", "$1000", "Test"]
      for i in range(40):
        data_table.add_row(row)

    with doc.create(pylatex.Center()) as centered:
      # spread 应该是控制单元格的宽度
      with centered.create(pylatex.Tabu("X[c] X[r]", spread="1cm")) as data_table:
        header_row1 = ["X", "Y"]
        data_table.add_row(header_row1, mapper=[pylatex.utils.bold])
        data_table.add_hline()
        row = [random.randint(0, 1000), random.randint(0, 1000)]
        for i in range(4):
          data_table.add_row(row)

    with doc.create(pylatex.Center()) as centered:
      with centered.create(pylatex.Tabu("X[r] X[r]", to="4in")) as data_table:
        header_row1 = ["X", "Y"]
        data_table.add_row(header_row1, mapper=[pylatex.utils.bold])
        data_table.add_hline()
        row = [random.randint(0, 1000), random.randint(0, 1000)]
        for i in range(4):
          data_table.add_row(row)

    doc.generate_pdf("tabus", clean_tex=False)

  def Textblock_example(self):
    """This example shows the functionality of the TextBlock element.

    It creates a sample cheque to demonstrate the positioning of the elements on the page.
    """

    geometry_options = {"margin": "0.5in"}
    doc = pylatex.Document(indent=False, geometry_options=geometry_options)
    doc.change_length(r"\TPHorizModule", "1mm")
    doc.change_length(r"\TPVertModule", "1mm")

    with doc.create(pylatex.MiniPage(width=r"\textwidth")) as page:
      with page.create(pylatex.TextBlock(100, 0, 0)):
        page.append("**** Ten Thousand Dollars")

      with page.create(pylatex.TextBlock(100, 0, 30)):
        page.append("COMPANY NAME")
        page.append("\nSTREET, ADDRESS")
        page.append("\nCITY, POSTAL CODE")

      with page.create(pylatex.TextBlock(100, 150, 40)):
        page.append(pylatex.HugeText(pylatex.utils.bold("VOID")))

      with page.create(pylatex.TextBlock(80, 150, 0)):
        page.append("DATE")
        page.append(pylatex.MediumText(pylatex.utils.bold("2016 06 07\n")))
        page.append(pylatex.HorizontalSpace("10mm"))
        page.append(pylatex.SmallText("Y/A M/M D/J"))

      with page.create(pylatex.TextBlock(70, 150, 30)):
        page.append(pylatex.MediumText(pylatex.utils.bold("$***** 10,000.00")))

      page.append(pylatex.VerticalSpace("100mm"))

    doc.generate_pdf("textblock", clean_tex=False)

  def Tikzdraw_example(self):
    """This example shows TikZ drawing capabilities.
    """

    # create document
    doc = pylatex.Document()

    # add our sample drawings
    with doc.create(pylatex.TikZ()) as pic:
      # options for our node
      node_kwargs = {'align': 'center',
                     'minimum size': '100pt',
                     'fill': 'black!20'}

      # create our test node
      box = pylatex.TikZNode(text='My block',
                             handle='box',
                             at=pylatex.TikZCoordinate(0, 0),
                             options=pylatex.TikZOptions('draw',
                                                         'rounded corners',
                                                         **node_kwargs))

      # add to tikzpicture
      pic.append(box)

      # draw a few paths
      pic.append(pylatex.TikZDraw([pylatex.TikZCoordinate(0, -6),
                                   'rectangle',
                                   pylatex.TikZCoordinate(2, -8)],
                                  options=pylatex.TikZOptions(fill='red')))

      # show use of anchor, relative coordinate
      pic.append(pylatex.TikZDraw([box.west,
                                   '--',
                                   '++(-1,0)']))

      # demonstrate the use of the with syntax
      with pic.create(pylatex.TikZDraw()) as path:
        # start at an anchor of the node
        path.append(box.east)

        # necessary here because 'in' is a python keyword
        path_options = {'in': 90, 'out': 0}
        path.append(pylatex.TikZUserPath('edge',
                                         pylatex.TikZOptions('-latex', **path_options)))

        path.append(pylatex.TikZCoordinate(1, 0, relative=True))

    doc.generate_pdf('tikzdraw', clean_tex=False)

  def href_url_example(self, doc: pylatex.Document):
    doc.append(pylatex.Command('href', ['https://www.baidu.com', '百度']))
    doc.append(pylatex.NoEscape(r'请访问这个网: \href{www.baidu.com}{百度}'))

    doc.append(pylatex.NoEscape(r'请访问这个网: \url{www.baidu.com}'))

  def teach_notes(self):
    """教学 内容"""
    string = r"""
    # 关于 latex  pylatex
    https://jeltef.github.io/PyLaTeX/current/examples/full.html
    from py_package_learn.pylatex_learn import pylatexLearn
    import importlib
    import pylatex
    importlib.reload(pylatexLearn)
    pl = pylatexLearn.PylatexLearn()
    doc = pl.Full_example(directory='/Users/wangjinlong/Desktop/latex_test',
                          )
    doc.append(pylatex.NoEscape(r'\par 我新想添加的'))
    doc.append(pylatex.NoEscape(
        r'\par \color{blue} \lipsum[1] \color{black} \par \lipsum[1]'))
    doc.append(pylatex.NoEscape(r'\nolinenumbers'))

    doc.append(pylatex.NoEscape(
        r'\par \zhlipsum[2-3]'))
    doc.generate_tex('/Users/wangjinlong/Desktop/latex_test/full')
    """
    print(string)
    return None


class CustomCls():
  def __init__(self) -> None:
    pass

  def math_inline(self, data):
    class MyMathInline(pylatex.Math):
      def __init__(self, data=data, *, inline=True, escape=False):
        super().__init__(inline=inline, data=data, escape=escape)
    return MyMathInline(data=data)

  def get_overpic_obj(self, options=None,
                      arguments=None,
                      start_arguments=None,
                      **kwargs):
    class OverPic(pylatex.base_classes.Environment):
      """A class to wrap LaTeX's alltt environment."""

      def __init__(self, *, options=None, arguments=None, start_arguments=None, **kwargs):
        super().__init__(options=options, arguments=arguments,
                         start_arguments=start_arguments, **kwargs)
        # packages = [pylatex.Package('overpic')]

    overpic_obj = OverPic(options=options,
                          arguments=arguments,
                          start_arguments=start_arguments,
                          **kwargs)
    return overpic_obj


class Beamer():
  def __init__(self) -> None:
    pass

  def use_packages(self):
    r"""
    %%导入一些用到的宏包
    \usepackage{bm,amsfonts,amssymb,enumerate,epsfig,bbm,calc,color,ifthen,capt-of,multimedia}
    \usepackage{multicol}

    \usepackage{amsmath}
    \usepackage{amsthm}
    \usepackage{extarrows}
    \usepackage{mathrsfs}
    \usepackage{relsize}

    %文本
    \usepackage{miller} %加入\hkl命令, e.g. 文本中\hkl<111>即为好看的晶向指数
    \usepackage{pdfpages}  % 可以插入 pdf 文件
    \setbeamercolor{background canvas}{bg=}  % beameer 中需要进行的设置否则插入的pdf将会被背景覆盖。
    % \includepdf[pages={1,2,3},pagecommand={\thispagestyle{plain}}]

    %表格
    \usepackage{tabu} %必须同时加载longtable才能用longtabu, % 最好用
    \usepackage{booktabs} %在表格环境中加入\toprule[1pt]命令 \bottomrule[1pt] \midrule设置三线表表格线的宽度
    \usepackage{diagbox} %%加入了\diagbox命令, e.g. \diagbox [dir=NW, width=5em, trim=l]

    %代码设置
    \usepackage{fancybox}
    \usepackage{xcolor}

    %插入代码
    \usepackage{listings}
    % 用来设置附录中代码的样式
    \lstset{
      basicstyle          =   \sffamily,          % 基本代码风格
      keywordstyle        =   \bfseries,          % 关键字风格
      commentstyle        =   \rmfamily\itshape,  % 注释的风格，斜体
      stringstyle         =   \ttfamily,  % 字符串风格
      flexiblecolumns,                % 别问为什么，加上这个
      numbers             =   left,   % 行号的位置在左边
      showspaces          =   false,  % 是否显示空格，显示了有点乱，所以不现实了
      numberstyle         =   \zihao{-5}\ttfamily,    % 行号的样式，小五号，tt等宽字体
      showstringspaces    =   false,
      captionpos          =   t,      % 这段代码的名字所呈现的位置，t指的是top上面
      frame               =   lrtb,   % 显示边框
    }

    \lstdefinestyle{Python}{
      language        =   Python, % 语言选Python
      basicstyle      =   \zihao{-5}\ttfamily,
      numberstyle     =   \zihao{-5}\ttfamily,
      keywordstyle    =   \color{blue},
      keywordstyle    =   [2] \color{teal},
      stringstyle     =   \color{magenta},
      commentstyle    =   \color{red}\ttfamily,
      breaklines      =   true,   % 自动换行，建议不要写太长的行
      columns         =   fixed,  % 如果不加这一句，字间距就不固定，很丑，必须加
      basewidth       =   0.5em,
    }

    \lstdefinestyle{Matlab}{
      language        =   Matlab, % 语言选Python
      basicstyle      =   \zihao{-5}\ttfamily,
      numberstyle     =   \zihao{-5}\ttfamily,
      keywordstyle    =   \color{blue},
      keywordstyle    =   [2] \color{teal},
      stringstyle     =   \color{magenta},
      commentstyle    =   \color{red}\ttfamily,
      breaklines      =   true,   % 自动换行，建议不要写太长的行
      columns         =   fixed,  % 如果不加这一句，字间距就不固定，很丑，必须加
      basewidth       =   0.5em,
    }

    %例子
    \iffalse
    \lstinputlisting[
    style       =   Python,
    caption     =   {\bf ff.py},
    label       =   {ff.py}
    ]{../src/duke/ff.py}
    % style选择之前定义过的Python，label是一个可引用的标签，以后可以使用ref{ff.py}关键字引用这段代码，caption是我要在这个代码上面显示的表头
    \fi

    %---
    \usepackage{float}  %用来控制图片的位置[H,h,t,b]
    \usepackage[abs]{overpic}  % 用于在图形上添加文字:\begin{overpic}[width=\linewidth,grid]{fig/near-spherical_determine/small1} \put(45,11){6.5{\AA}} \end{overpic}还可以在overpic中加箭头 \put(85,89){\vector(-0.8,-1.2){8}} 分别表示起始位置,矢量方向,长度, 画圆：\put(x, y){\circle{diameter}} (x, y) – 圆心坐标 {diameter} – 直径，circle命令画出圆的最大直径约为14mm \circle* – 画实心圆, 椭圆：\put(x, y){\oval(w, h)[position]}

    %--
    \usepackage{verbatim} %使用verbatim环境
    \usepackage{pifont}  %带圈的数字 usage:\ding{172}
    \usepackage{ulem}  %--
    %\uuline{双下划线} \\
    %\uwave{波浪线} \\
    %\sout{中间删除线} \\
    %\xout{斜删除线} \\
    %\dashuline{虚线}
    %\dotuline{加点} \\

    %---设置行距
    \usepackage{setspace}  %例如要使用1.5倍行间距，则可使用 \begin{spacing}{1.5} 内容...... \end{spacing}
    %\setstretch{1.1}
    \linespread{1} % 设置行间距如1.1倍等

    %---插入任意位置的文本框或图片: The hsizei and hhposi arguments are given in units of a module \TPHorizModule, and hvposi is given in units of a module \TPVertModule
    \usepackage[absolute,overlay]{textpos} %textblock环境的位置坐标参数相对于当前页面的当前“锚点”位置进行排版。在绝对坐标模式中，textblock环境的位置坐标参数相对于当前页面的“左上角”位置进行排版。 %,showboxes=ture (false)选项可以显示边框
    \setlength{\TPHorizModule}{\paperwidth} %或者\textwidth
    \setlength{\TPVertModule}{\paperheight}
    %用法：
    %\begin{textblock}{hhsizei}(hhposi,hvposi)
    %	text...
    %\end{textblock}
    %例子:
    %\TPoptions{absolute=true,showboxes = false } 此命令可以随时改texpos包的选项 或ture
    %\TPMargin{0.5em} %边界空余的大小
    %\textblockcolour{red} %块颜色
    %\textblockrulecolour{blue} %边框颜色
    %\begin{textblock}{0.5}(0.5,0.5)
    %	Testdddd gasdg  dkg  dlgglaskdg lls
    %\end{textblock}

    %---4、插入环绕图片的方法：使用宏包：
    %\usepackage[all]{xy} 这是用来绘制箭头图的
    \usepackage{wrapfig}
    \iffalse 命令如下：
    \begin{wrapfigure}{r}{0.5\textwidth} %0.5\textwidth用来固定图片和右边缘的距离
      \vspace{-50pt} %\vspace{-50pt}用来固定图片和下边缘的距离

      \begin{center}
        \includegraphics[width=0.35\textwidth]{CQU.jpg}
        %\caption{Handwrite}\label{fig:digit}
      \end{center}
    \end{wrapfigure}
    \fi


    %---插入动画 %需要使用图片和动画宏包
    \usepackage{graphicx}
    \usepackage{animate}
    \usepackage{multimedia}
    %用法：\animategraphics[<options>]{<frame rate>}{<file basename>}{<first>}{<last>} %这个动画是由一个系列的图形文件构成的，自己定义动画的帧速<frame rate>，图形文件的目录和名称<file basename>，以及开始和结束的文件名称<first>、<last>。对于系列的图形文件，很多软件都有直接输出文件的命令。例如：1. 将动画文件如gif或AVI转化成图片文件 convert animate.gif -coalesce animate_%d.eps %--ImageMagick中的命令convert,其中eps可以换成jpg,png 转化>的结果就是出现animate_0.eps, animate_1.eps, ... 2. 在beamer中的frame中使用如下命令\animategraphics[controls, buttonsize=3mm,width=0.5\linewidth]{10}{fig/animate_}{0}{20}。 3.用acroread(adobe reader)打开，就会显示动态图了。用wps看不到动态图

    %---播放声音
    \usepackage{media9} %有机会研究研究

    %---使用超链接
    %\usepackage[hyperref]{beamerarticle} or
    %\usepackage[colorlinks, linkcolor=red]{hyperref}
    \usepackage{cite}  %可以使文献连号 17,18,19 --> 17-19  \usepackage[superscript]{cite}  %用于上角标
    \usepackage{url} %引入\url命令插入超链接，比如命令：\url{www.baidu.com}
    \usepackage{hyperref} %tex与latex宏包之间的冲突，与hpperref宏包的冲突较多，例如其中之一是：hyperref应该在 fancyhdr后面加载。
    """

    latex_obj_list = []
    for name in ['ctex', 'ulem']:
      latex_obj = pylatex.Package(name=name)
      latex_obj_list.append(latex_obj)

    return latex_obj_list

  def use_theme(self,
                innertheme='rounded',
                outertheme='smoothbars',
                colortheme='whale,rose',
                fonttheme='professionalfonts',
                usetheme_number=0,
                ):
    r"""_summary_
    # % 自定义底部信息模板，将页码放在最右边，中间显示标题
    # \setbeamertemplate{footline}{%
    #   \leavevmode%
    #   \hbox{%
    #     \begin{beamercolorbox}[wd=.5\paperwidth,ht=2.25ex,dp=1ex,left]{title in head/foot}%
    #       \usebeamerfont{title in head/foot}\hspace*{1.5em}\inserttitle
    #     \end{beamercolorbox}%
    #     \begin{beamercolorbox}[wd=.5\paperwidth,ht=2.25ex,dp=1ex,right]{author in head/foot}%
    #       \usebeamerfont{author in head/foot}
    #       \insertframenumber{} / \inserttotalframenumber\hspace*{1.5em}
    #     \end{beamercolorbox}%
    #   }%
    #   \vskip0pt%
    # }
    Args:
        innertheme (str, optional): _description_. Defaults to 'rounded'.
        outertheme (str, optional): _description_. Defaults to 'smoothbars'.
        colortheme (str, optional): _description_. Defaults to 'whale,rose'.
        fonttheme (str, optional): _description_. Defaults to 'professionalfonts'.

    Returns:
        _type_: _description_
    """
    # \usetheme{Berlin} : 设置usetheme可以影响以下四个设置.
    usetheme_list = ['default', 'AnnArbor', 'Antibes', 'Bergen',
                     'Berkeley', 'Berlin', 'Boadilla',
                     'cambridgeUS', 'Copenhagen', 'Darmstadt',
                     'Dresden', 'Frankfurt',
                     'Goettingen', 'Hannover', 'Ilmenau',
                     'JuanLesPins', 'Luebeck', 'Madrid',
                     'Malmoe', 'Marburg', 'Montpellier',
                     'PaloAlto', 'Pittsburgh', 'Rochester',
                     'Singapore', 'Szeged', 'Warsaw',]
    # \useinnertheme{rounded} %用于选择内部主题，即幻灯片内部元素的样式。内部主题控制标题、列表、块、定理环境、脚注等幻灯片内的元素样式。
    innertheme_list = ['default', ' circles',
                       ' rectangles', ' rounded', ' inmargin']
    # \useoutertheme{smoothbars}  % 用于选择外部主题，即幻灯片的外部布局和装饰。外部主题控制幻灯片的背景、页眉、页脚、边框等外观特征。
    outertheme_list = ['default', 'infolines', 'miniframes',
                       'smoothbars', 'sidebar', 'split', 'shadow', 'tree', 'smoothtree']
    # \usecolortheme{whale,rose}
    colortheme_list = ['default', 'albatross', 'beaver', 'beetle', 'crane', 'dolphin',
                       'dove', 'fly', 'lily', 'orchid', 'rose', 'seagull', 'seahorse', 'whale', 'wolverine']
    # \usefonttheme{professionalfonts} %
    fonttheme_list = ['default', 'professionalfonts', 'serif',
                      'structurebold', 'structureitalicserif', 'structuresmallcapsserif']
    # \useoutertheme{smoothbars}
    theme_dict = {'useinnertheme': innertheme,
                  'useoutertheme': outertheme,
                  'usecolortheme': colortheme,
                  'usefonttheme': fonttheme, }
    latex_obj_list = []
    for command, arguments in theme_dict.items():
      latex_obj = pylatex.Command(command=command,
                                  arguments=arguments)
      latex_obj_list.append(latex_obj)

    latex_obj = pylatex.Command(
        command='usetheme', arguments=usetheme_list[usetheme_number])
    latex_obj_list.append(latex_obj)

    return latex_obj_list

  def set_beamer_font(self):
    r"""%Beamer中字体的使用: 可以设置的属性有字体，和颜色
    %\setbeamerfont{beamer-font name}{attributes} 用预设值字体，属性名有title, frametitle, framesubtitle, normal text, 属性值为：family, shape, size, 例如family=\myheiti, shape=\upshape, size=\large,\normalsize

    %使用如下命令可以很方便的设置Beamer的字体, 更多的设置请参考Beamer appearance cheat-sheet与Beamer User Guide, 第18.3.3节.
    \setbeamerfont*{title}{family=\rmfamily\kaishu, shape=\scshape, series=\bfseries, size=\LARGE} %标题字体 \sffamily
    \setbeamerfont{frametitle}{family=\rmfamily\kaishu, shape=\upshape, series=\mdseries} %frame标题 \sffamily
    \setbeamerfont{normal text}{family=\rmfamily\heiti, shape=\upshape, series=\mdseries} %正文字体 \rmfamily
    \AtBeginDocument{\usebeamerfont{normal text}}

    \setbeamercolor{frametitle}{fg=blue, bg=white}  %设置颜色，语法：\setbeamercolor{beamer-color name}{options} 可以设置的属性名有title, frametitle, framesubtitle, normal text, background canvas; block title属性值为：fg(前景色)，bg(背景色) ；参数为颜色，例如fg=red, bg=white
    \setbeamertemplate{frametitle}
    {\vspace{-0.5em}
      \begin{center}
        \insertframetitle
      \end{center} \vspace{-0.7em}
    }

    %---对列表marker的样式和颜色设置,更多的设置参见/Users/wangjinlong/my_linux/soft_learn/latex_learn/useful_pdf/Beamer-appearance-cheat-sheet.pdf
    \setbeamertemplate{enumerate items}[ball] %可选项为default, circle, square, ball.  还可以对enumerate item，enumerate subitem，enumerate subsubitem 分别设置
    \setbeamercolor{item projected}{fg=black, bg=yellow}
    \setbeamertemplate{itemize items}[triangle]  %可选项为default, circle, square, ball, triangle，
    \setbeamercolor{itemize item}{fg=blue}  %设置itemize item的颜色
    \setbeamerfont{item projected}{size=\scriptsize}

    %设置block的模板
    %\setbeamertemplate{blocks}[default]
    \setbeamertemplate{blocks}[rounded][shadow=true]  %shadow=true or false
    """

    extra_arguments = pylatex.NoEscape(
        r"""\vspace{-0.5em}\begin{center}\insertframetitle\end{center} \vspace{-0.7em}""")
    c1 = pylatex.Command(command='setbeamertemplate',
                         arguments='frametitle',
                         extra_arguments=extra_arguments)
    # \setbeamercolor{frametitle}{fg=blue, bg=white}
    c2 = pylatex.Command(command='setbeamercolor', arguments='frametitle',
                         extra_arguments='fg=blue, bg=white')
    # 可选项为default, circle, square, ball.  还可以对enumerate item，enumerate subitem，enumerate subsubitem 分别设置
    c3 = pylatex.Command(command='setbeamertemplate',
                         arguments='enumerate items',
                         options='ball')
    # 可选项为default, circle, square, ball, triangle，
    c4 = pylatex.Command(command='setbeamertemplate',
                         arguments='itemize items',
                         options='triangle',)
    c5 = pylatex.Command(command='setbeamercolor',
                         arguments='item projected',
                         extra_arguments='fg=black, bg=yellow',
                         )
    # %设置itemize item的颜色
    c6 = pylatex.Command(command='itemize item',
                         arguments='fg=blue'
                         )
    c7 = pylatex.Command(command='setbeamerfont',
                         arguments='item projected',
                         extra_arguments=r'size=\scriptsize',
                         )
    # %设置block的模板
    # \setbeamertemplate{blocks}[rounded][shadow=true]
    c8 = pylatex.Command(command='setbeamertemplate',
                         options='rounded,shadow=true')

    latex_obj_list = [c1, c2]
    return latex_obj_list

  def add_packages(self, doc: pylatex.Document):
    package_list = self.use_packages()
    for package in package_list:
      doc.packages.append(package)

  def add_premeable(self, doc: pylatex.Document,
                    usetheme_number=0,  # 0为默认
                    innertheme='rounded',
                    outertheme='smoothbars',
                    colortheme='whale,rose',
                    fonttheme='professionalfonts',):
    """设置主题和字体

    Args:
        doc (pylatex.Document): _description_
    """
    latex_obj_list = [*self.use_theme(usetheme_number=usetheme_number,
                                      innertheme=innertheme,
                                      outertheme=outertheme,
                                      colortheme=colortheme,
                                      fonttheme=fonttheme,),
                      *self.set_beamer_font(),
                      ]
    for latex_obj in latex_obj_list:
      doc.preamble.append(latex_obj)

  def get_frame(self,
                options=['t', 'allowframebreaks'],
                arguments='这是标题'):
    class Frame(pylatex.base_classes.Environment):
      pass
    frame = Frame(options=options, arguments=arguments)
    return frame

  def get_mdframe(self, latex_obj_list):
    """带框的文本

    Args:
        latex_obj_list (_type_): _description_
    """
    mdframe = pylatex.frames.MdFramed()
    for latex_obj in latex_obj_list:
      mdframe.append(latex_obj)

  def get_doc(self, aspectratio=169,
              usetheme_number=0,  # 0为默认
              innertheme='rounded',
              outertheme='smoothbars',
              colortheme='whale,rose',
              fonttheme='professionalfonts',
              geometry_options={
                  "paperwidth": "5.5cm",
                  "paperheight": "5cm",
                  "left": "0cm",
                  "right": "0cm",
                  "top": "0cm",
                  "bottom": "0cm"
              }):
    """aspectratio=169 或者43

    Args:
        aspectratio (int, optional): _description_. Defaults to 169.

    Returns: doc
        _type_: _description_
    """

    doc = pylatex.Document(documentclass='beamer',
                           document_options=[
                               f'aspectratio={aspectratio},mathserif,9pt'],
                           geometry_options=geometry_options)

    self.add_packages(doc=doc)
    self.add_premeable(doc=doc,
                       usetheme_number=usetheme_number,
                       innertheme=innertheme,
                       outertheme=outertheme,
                       colortheme=colortheme,
                       fonttheme=fonttheme,
                       )
    return doc

  def get_title_author(self,
                       doc: pylatex.Document,
                       title='大学物理简明教程',
                       subtitle='重要知识点',
                       author='王金龙',
                       institute='铜陵学院---电气工程学院',
                       date=r'\today',
                       ):
    r"""\title{大学物理简明教程}
      \subtitle{\raisebox{0.1mm}{------}重要知识点}
      \author{王金龙}
      \institute{铜陵学院---电气工程学院}
      \date{\today}
    """
    title_obj = pylatex.Command('title', title)
    subtitle_obj = pylatex.Command('subtitle', subtitle)
    author_obj = pylatex.Command('author', author)
    institute_obj = pylatex.Command('institute', institute)
    date_obj = pylatex.Command('date', pylatex.NoEscape(fr'{{{date}}}'))

    latex_obj_list = [title_obj, subtitle_obj, author_obj,
                      institute_obj, date_obj]
    # date
    for latex_obj in latex_obj_list:
      doc.preamble.append(latex_obj)

    frame = self.get_frame(arguments='')
    frame.append(pylatex.NoEscape(r'\addtocounter{framenumber}{-1}'))
    frame.append(pylatex.NoEscape(r'\thispagestyle{empty}'))
    frame.append(pylatex.NoEscape(r'\titlepage'))  # \maketitle
    doc.append(frame)

  def get_toc(self):
    frame = self.get_frame(arguments='目录')
    frame.append(pylatex.Command('tableofcontents'))
    # frame.append(pylatex.NoEscape(r'\tableofcontents'))
    return frame


class Base():
  def __init__(self,) -> None:
    self.pylatex = pylatex
    self.fname_bib = '/Users/wangjinlong/job/job_project/src/job_project/scientific_research/mybibref.bib'
    pass

  def get_author_data(self):
    import job_project
    srb = job_project.scientific_research.scientificResearchBase
    df = srb.ScientificResearchBase().get_df_researcher_information()
    author_email_dict = {}
    for k, v in zip(df['name'], df['email']):
      author_email_dict.update({k: v})

    author_affli_dict = {}
    for k, v in zip(df['name'], df['institution']):
      author_affli_dict.update({k: v})

    author_data = {'author_affli_dict': author_affli_dict,
                   'author_email_dict': author_email_dict}

    return author_data

  def get_authors_premeable_data(self,
                                 authors=['Jinlong Wang', 'Jinmin Guo', 'Xiao-Chun Li', 'Lu Sun', 'Bingling He']):
    """* 获得作者单位的集合, 保证出现的先后顺序
    * afflis 内容如: ["School of Electronic Engineering, Tongling University, Tongling, People's Republic of  China","Institute of plasma physics, HFIPS, Chinese Academy of Sciences, Hefei, People's Republic of China","School of Nuclear Science and Engineering, North China Electric Power University, Beijing 102200, China"]

    Args:
        authors (list, optional): _description_. Defaults to ['Jinlong Wang', 'Jinmin Guo', 'Xiao-Chun Li', 'Lu Sun'].

    Returns:
        _type_: _description_
    """

    author_data = self.get_author_data()

    afflis_set = set()
    afflis = []
    for author in authors:
      for affli in author_data['author_affli_dict'][author]:
        if affli not in afflis_set:
          afflis_set.add(affli)
          afflis.append(affli)

    # 获得单位和单位标签
    labels = string.ascii_lowercase  # 获取小写字母表
    affli_and_label = {}
    for affli, affli_label in zip(afflis, labels):
      affli_and_label.update({affli_label: affli})

    # 获得作者和单位标签
    def get_author_label_dict(author, affli_and_label, author_info_dict):
      """ author_and_label_dict 的形式: {'Jinlong Wang': ['a', 'b']}
      """
      author_label = []
      for k, v in affli_and_label.items():
        for affli in author_info_dict[author]:
          if affli == v:
            author_label.append(k)
      author_and_label_dict = {author: author_label}
      return author_and_label_dict

    author_and_label = {}
    for author in authors:
      author_label_dict = get_author_label_dict(
          author, affli_and_label, author_info_dict=author_data['author_affli_dict'])
      author_and_label.update(author_label_dict)

    data = {'affli_and_label': affli_and_label,
            'author_and_label': author_and_label}
    return data

  def premeable_examples(self, doc: pylatex.Document,):
    """用于参考

    Args:
        doc (pylatex.Document): _description_
    """
    # 添加其他序言
    # 包不可以在这里(premeable) 添加, 因为序言不会查重, 重复导包会报错
    # 添加标题
    doc.preamble.append(pylatex.Command('title', '铜陵学院翠湖领军人才聘任申请材料'))
    doc.preamble.append(pylatex.Command('author', 'Anonymous author'))
    doc.preamble.append(pylatex.Command('date', pylatex.NoEscape(r'\today')))
    doc.append(pylatex.Command('maketitle'))
    doc.append(pylatex.NewPage())

    # 设置行间距为1.5倍
    doc.preamble.append(pylatex.Command('setstretch', 1.5))
    # 建议通过pylatex.Document(documentclass='article', document_options=['12pt', 'onehalfspacing',]) 来设置行间距, 以为结果是不同的
    # 页面格式
    pagestyle = pylatex.PageStyle("empty")
    with pagestyle.create(pylatex.Foot('C')):
      pagestyle.append(pylatex.simple_page_number())
    doc.preamble.append(pagestyle)
    doc.change_document_style("empty")

    # 定义命令
    doc.preamble.append(pylatex.NoEscape(
        r'\definecolor{myqianlan}{RGB}{0,112,192} '))
    # 标题 section 格式
    doc.preamble.append(pylatex.NoEscape(r"""\ctexset{
      section={
        indent={2em},
        format = \zihao{4} \kaishu\bfseries\color{myqianlan},
        name = {（,）},
        number = \zhnum{section},
        beforeskip = 1 ex plus 0.2ex minus .2ex,
        afterskip = 1.0ex plus 0.2ex minus .2ex,
        aftername = \hspace{0pt}
      },
      subsection={
        indent={2em},
        format = \zihao{4} \kaishu\color{myqianlan},
        name = {,.},
        number = \arabic{subsection},
        beforeskip = 1.0ex plus 0.2ex minus .2ex,
        afterskip = 1.0ex plus 0.2ex minus .2ex,
        aftername = \hspace{0.5 em}
      },
      subsubsection={
        indent={2em},
        format = \zihao{-4}\bfseries,
        name = {,},
        number = \arabic{subsection}.\arabic{subsubsection},
        beforeskip = 1.0ex plus 0.2ex minus .2ex,
        afterskip = 1.0ex plus 0.2ex minus .2ex,
        aftername = \hspace{0.5 em}
      }
    }"""))

    # %或者使用如下设置
    # %titlespec包提供了如下命令. \titleformat{command}[shape]{format}{label}{sep}{before-code}[after-code]
    # %\titleformat{\section}{\zihao{4}\bfseries\mykaiti\color{myqianlan}}{\hspace{2em}（\zhnum{section}）}{0 em}{}
    # %\titleformat{\subsection}{\zihao{4}\mykaiti\color{myqianlan}}{\hspace{2em}\thesection. }{0 em}{}

  def premeable_title_author_example(self, doc: pylatex.Document,
                                     title='An Possible Approach for Simulating the Formation of Tungsten Fuzz under Helium Irradiation',
                                     is_date=False):
    # 添加标题
    doc.preamble.append(pylatex.Command('title', title))

    # 添加作者
    doc.preamble.append(pylatex.Command(
        'author', arguments=pylatex.NoEscape(r'Jinlong Wang \thanks{Corresponding author: 396292346@qq.com}'), options='a,b'))
    doc.preamble.append(pylatex.NoEscape(
        r'\author[b]{Xiao-Chun Li\thanks{Corresponding author: xcli@ipp.ac.cn}}'))
    doc.preamble.append(pylatex.NoEscape(r'\author[b]{Jinmin Guo}'))
    doc.preamble.append(pylatex.Command('author', arguments='Jinmin Guo',
                                        options='a'))

    # 添加单位
    doc.preamble.append(pylatex.Command(
        command='affil', arguments="School of Electronic Engineering, Tongling University, Tongling, People's Republic of  China", options='a'))
    doc.preamble.append(pylatex.NoEscape(
        r"\affil[b]{Institute of plasma physics, HFIPS, Chinese Academy of Sciences, Hefei, People's Republic of China}"))
    # 修改机构名称的字体与大小
    doc.preamble.append(pylatex.NoEscape(
        r'\renewcommand*{\Affilfont}{\small\it}'))
    # 去掉 and 前的逗号
    doc.preamble.append(pylatex.NoEscape(r'\renewcommand{\Authands}{ and }'))

    # date
    date = pylatex.NoEscape(
        r'\date{\today}') if is_date else pylatex.NoEscape(r'\date{}')
    doc.preamble.append(date)

    doc.append(pylatex.NoEscape(r'\maketitle'))
    pass

  def get_package_name(self, pkg: pylatex.Package):
    package_name = pkg.dumps()  # 输出: '\usepackage{ctex}'
    # 提取包名（去掉 "\usepackage{" 和 "}"）
    extracted_name = package_name.split("{")[1].split("}")[0]
    return extracted_name

  def get_packages(self,
                   exclude_pkgs=['fontspec', 'lipsum'],
                   packages=['authblk', 'ctex', 'cite',
                             'xurl', 'hyperref',
                             'miller', 'color', 'lineno', 'float',
                             'setspace', 'ulem', 'amsmath', 'overpic',
                             'tcolorbox', 'diagbox', 'booktabs', 'multirow',
                             'fancyhdr', 'zhnumber', 'mdframed',
                             ]):
    r"""
    ---
    fontspec 包会导致 提交文件不成功去掉即可
    ---
    - authblk 宏包用于排版作者和机构信息. 如果不加作者而引用这个包会在标题下面出现 immediate 字样的文字
    - 中文包 ctex
    - cite
    - \usepackage{xurl}  % 允许在任意字符处换行, 用法: \url{https://www.example.com/very-long-url-that-needs-to-break-properly} xurl 包比 url 更智能，可以在任何安全的地方自动换行，非常适合处理长链接。
    - hyperref
    - miller
    # 用法: 自定义颜色 # \definecolor{myqianlan}{RGB}{0,112,192} \textcolor{myqianlan}{\textbf{请勿删除或改动下述提纲标题及括号中的文字. }
    - color
    - lineno 宏包 可以使用 \linenumbers 命令启用行号。每一行文本之后都会显示行号。
    # \rmfamily  % 默认的衬线字体, 中文汉语为宋体; \sffamily % 默认的无衬线字体, 中文汉语为黑体; \ttfamily % 默认的打印机字体, 中文汉语为仿宋, 使用其它的字体需要\usepackage{fontspec} 支持
    - fontspec
    - float
    # 用法: doc.preamble.append(pylatex.Command('setstretch', 1.5)) # 建议通过pylatex.Document(documentclass='article', document_options=['12pt', 'onehalfspacing',]) 来设置行间距, 因为结果是不同的
    - setspace 用来设置行间距
    # \usepackage{ulem} 会改变 \emph{} 的默认行为（由斜体变成了下划线）。如果你只想用删除线，不想影响其他格式，可以使用下面这个安全版本： \usepackage[normalem]{ulem}  其他用法: # \sout{}	删除线（strikethrough） \xout{}	交叉删除线（X 形）\uline{}	单下划线 \uuline{}	双下划线 \uwave{}	波浪线
    - ulem
    - amsmath # 公式中\text{} 命令需要 amsmath 宏包支持。若未加载该宏包，LaTeX 会报错。
    - lipsum  # 用法 doc.append(pylatex.NoEscape(r'\lipsum[1]'))
    - overpic 环境
    # 给文本框增加带底色的框 \begin{tcolorbox}[colback=white, width=10em]  (a) Top View \end{tcolorbox}}
    - tcolorbox
    - diagbox  表格分隔框 用法示例 \diagbox{fluence}{time consuming}{method} & conventional method & acceleration method & PRD acceleration method\\ \hline
    - booktabs  表格为了使用 \bottomrule \toprule \midrule 命令
    - multirow  表格多行
    - fancyhdr
    - zhnumber 中文编号 # 用法
    '''\ctexset{
        section={format+ = \songti \zihao{4}, name = {,},
        number = (\zhnum{section}) \,,
        beforeskip = 1.0ex plus 0.2ex minus .2ex,
        afterskip = 1.0ex plus 0.2ex minus .2ex,
        aftername = \hspace{0pt}
      }
    }
    '''
    - mdframed 用法: \begin{mdframed}[backgroundcolor=blue!10, roundcorner=10pt]  \end{mdframed}  # 可以设置背景颜色和圆角
    -
    """

    pkgs = []
    for exclude_pkg in exclude_pkgs:
      try:
        packages.remove(exclude_pkg)
      except ValueError:
        pass
    for package in packages:
      if package in ['ulem']:
        pkg = pylatex.Package(name=package, options=['normalem'])
      else:
        pkg = pylatex.Package(package)
      pkgs.append(pkg)
    return pkgs

  def use_packages(self, doc: pylatex.Document,
                   is_ctex=True,
                   is_authblk_pkg=True,):
    # 获取所有包并过滤
    pkgs = self.get_packages()
    pkgs_filtered = [
        pkg for pkg in pkgs
        if not (
            (self.get_package_name(pkg) == 'ctex' and not is_ctex) or
            (self.get_package_name(pkg) == 'authblk' and not is_authblk_pkg))]

    # 添加包到文档
    for pkg in pkgs_filtered:
      doc.packages.append(pkg)

    return None

  def get_newpage_obj(self):
    newpage_obj = pylatex.NewPage()
    return newpage_obj

  def get_toc_tableofcontents_obj(self,):
    """doc.append(doc)
    """
    com = pylatex.Command('tableofcontents')
    return com

  def get_par_obj(self,):
    par_obj = pylatex.Command('par')
    return par_obj

  def document_example(self, geometry_options={"right": "2cm", "left": "2cm"}, title='附件目录'):
    """_summary_

    Returns: doc
        _type_: _description_
    """
    # 创建一个新的文档
    doc = pylatex.Document(documentclass='ctexart',
                           geometry_options=geometry_options)
    # doc.preamble.append(pylatex.Command('usepackage', 'ctex'))

    # 添加标题
    doc.preamble.append(pylatex.Command('title', title))
    # doc.preamble.append(pylatex.Command('author', 'John Doe'))
    doc.preamble.append(pylatex.Command('date', ''))
    doc.append(pylatex.Command('maketitle'))

    doc.append(pylatex.Section('Section 1'))
    doc.append('Some regular text')

    # 添加一个小节
    with doc.create(pylatex.Subsection('Subsection 1')):
      doc.append('Text in subsection')

    # 输出到文件
    # self.write_file(doc=doc, fname='tmp')
    doc: pylatex.Document
    return doc

  def verb(self, string='a_m_x-y_x'):
    """
    x = 'a_c_d_e'
    verb_str = pylatex.NoEscape(fr'\verb|{x}|')
    还有个是verb环境
    \begin{verbatim}
    a_b_c
    \bend{verabatim}

    Returns: verb_str
        _type_: _description_
    """

    verb_str = pylatex.Command(command='verb||', arguments=string)
    return verb_str

  def find_duplicates(self, lst):
    """找到列表中的重复项作为新的列表

    Args:
        lst (_type_): _description_

    Returns: duplicate_item_list
        _type_: _description_
    """
    seen = set()
    duplicates = set()
    for item in lst:
      if item in seen:
        duplicates.add(item)
      else:
        seen.add(item)
    duplicate_item_list = list(duplicates)
    return duplicate_item_list

  def rename_fname(self, dname):
    """根据文件的path, 重命名文件名
    e.g.: 'adsorbate_slab/BN_codoping_sub/O2_B_N1_graphene/cdd/chg_diff.jpg'
    -> 'adsorbate_slab/BN_codoping_sub/O2_B_N1_graphene/cdd/cdd_chg_diff.jpg'

    """
    dir_name_list = dname.split('/')[:-1]
    dir_name_list.reverse()
    fname = dname.split('/')[-1]
    for dir_name in dir_name_list:
      if dir_name in fname:
        continue
      else:
        fname = dir_name + '_'+fname
        break
    dname = os.path.join(os.path.split(dname)[0], fname)
    return dname

  def resolve_duplicate_fname_list(self, dname_list):
    """如果path列表中文件名重复则重命名, 获得新的path列表
    可以用于latex source 的处理

    Args:
        dname_list (_type_): _description_

    Returns:
        _type_: _description_
    """
    fname_list = [os.path.basename(dname) for dname in dname_list]
    duplicates_fname_list = self.find_duplicates(fname_list)

    if duplicates_fname_list.__len__() == 0:
      return dname_list
    else:
      new_dname_list = []
      for dname, fname in zip(dname_list, fname_list):
        if fname in duplicates_fname_list:
          dname = self.rename_fname(dname=dname)
        new_dname_list.append(dname)

      return self.resolve_duplicate_fname_list(new_dname_list)

  def get_center_env(self,):
    """
    center.append('abc')

    Returns:
        _type_: _description_
    """
    class Center(pylatex.base_classes.Environment):
      pass
    center = Center()

    return center

  def ref2label(self, ref=r'\ref{abc_def}',):
    label = re.sub(pattern=r'\\ref{', repl=r'\\label{', string=ref)
    return label

  def label2ref(self, label=r'\label{abc_def}',):
    ref = re.sub(pattern=r'\\label{', repl=r'\\ref{', string=label)
    return ref

  def blue_text_obj(self, string='x'):
    latex_obj = pylatex.NoEscape(fr'\color{{blue}} {string} \color{{black}}')
    return latex_obj

  def rename_fname2fname_date(self, fname):
    """例如每次产生的reply.pdf 变成reply_2024_6_24.pdf

    Args:
        fname (_type_): _description_

    Returns:
        _type_: _description_
    """
    date = time.strftime('%Y_%m_%d', time.localtime())
    fname = fname + '_' + date
    return fname

  def linenumbers(self, control_str='begin|end',):
    """是否启用或结束行号
    """
    if control_str == 'begin':
      latex_obj = pylatex.NoEscape(r'\linenumbers')
    elif control_str == 'end':
      latex_obj = pylatex.NoEscape(r'\nolinenumbers')
    else:
      print(f'control_str 参数错误')
      return None
    return latex_obj

  def get_mdframed_env(self,
                       options=['backgroundcolor=white',
                                'linecolor=black',
                                'linewidth=0.5pt',
                                'everyline=true',  # 换页保持边框的完整
                                # 分页切割时顶部补偿 (必须 > innertopmargin)
                                'splittopskip=15pt',
                                'splitbottomskip=5pt',   # 分页底部补偿
                                ]
                       ):
    """ 边框段落, 给段落加边框
    ---
    backgroundcolor=blue!10!white
    yellow!10!black → 10% yellow + 90% black → 暗黄
    --- 需要使用的包
    md = pylatex.Package(name='mdframed')
    doc.packages.append(md)
    ---
    center.append('abc')
    """
    class Mdframed(pylatex.base_classes.Environment):
      pass
    env = Mdframed(options=options,)

    return env

  def get_abstract_env(self):
    class Abstract(pylatex.base_classes.Environment):
      pass
    abstract = Abstract()
    return abstract


class Doc(Base):
  def __init__(self):
    super().__init__()
    self.font_size = ["tiny", "scriptsize", "footnotesize",
                      "small", "normalsize", "large", "Large",
                      "LARGE", "huge", "Huge"]

  def get_document(self,
                   documentclass='ctexart',
                   document_options=['onehalfspacing',
                                     '12pt'],  # 1.5 倍行距和12pt 字体
                   geometry_options={
                       # {'scale': 0.8}
                       'top': '2.5cm', 'bottom': '2.5cm', 'left': '3cm', 'right': '3cm'},
                   is_ctex=False,
                   is_authblk_pkg=True,
                   mainfont='rmfamily',
                   linespacing=None,
                   **kwargs,
                   ):
    """
    - font_size: 如 "tiny", "scriptsize", "footnotesize", "small", "normalsize", "large", "Large", "LARGE", "huge", "Huge" 等。预定义的字体大小名称并不对应特定的点数大小（例如12pt）。它们是相对大小，根据 LaTeX 的标准设置，它们会在不同的文档类和字体尺寸下自动调整。
    - document_options: 这个参数用于传递文档类的选项。文档类的选项决定了整个文档的格式，例如字体大小、纸张大小、行间距等。其中 12pt 和 onehalfspacing 就是文档类的选项之一，它们分别用于指定文档的字体大小为12pt和行间距为1.5倍。
    - linespacing=1.5, 如果内容不是1.5倍行间距, 则修改这里
    """
    # doc.documentclass = pylatex.Command('documentclass', type)
    doc = pylatex.Document(documentclass=documentclass,
                           document_options=document_options,
                           geometry_options=geometry_options,
                           **kwargs,
                           )
    # 使用 setspace 宏包设置双倍行距
    # doc.preamble.append(r'\setstretch{2}')
    if linespacing is not None:
      doc.preamble.append(pylatex.Command(command='setstretch',
                                          arguments=linespacing))
    Base().use_packages(doc=doc, is_ctex=is_ctex,
                        is_authblk_pkg=is_authblk_pkg,)
    # 字体命令
    doc.append(pylatex.Command(mainfont))
    return doc

  def set_pagestyle(self, doc, pagestyle='empty|plain'):
    doc.append(pylatex.NoEscape(fr'\pagestyle{{{pagestyle}}}'))

  def title_author(self, doc: pylatex.Document,
                   title='An Possible Approach for Simulating the Formation of Tungsten Fuzz under Helium Irradiation',
                   authors=['Jinlong Wang',
                            'Jinmin Guo',],
                   corresponding_authors=['Wei Song'],
                   is_date=False,
                   is_cn=False):
    r"""
    - \thispagestyle{empty} % 取消标题页的页码
    - \pagestyle{empty} % 取消正文的页码
    """

    doc.preamble.append(pylatex.Command('title', title))
    author_data = Base().get_author_data()
    if authors:
      # 或者作者和单位信息并写入 premeable
      data = Base().get_authors_premeable_data(authors=authors)
      for k, v in data['author_and_label'].items():
        for name in corresponding_authors:
          if k == name:
            if not is_cn:
              k += fr"\thanks{{Corresponding author.\newline E-mail addresses: {author_data['author_email_dict'][name]} ({k})}}"
            else:
              k += r"\thanks{郭晋闽, 1986, 女, 汉族, 籍贯新乡, 铜陵学院, 助理馆员, 学士。}"
              pass
        doc.preamble.append(pylatex.Command(
            'author', arguments=pylatex.NoEscape(k), options=','.join(v)))
      for k, v in data['affli_and_label'].items():
        doc.preamble.append(pylatex.Command(
            command='affil', arguments=v, options=k))
      # 修改机构名称的字体与大小
      doc.preamble.append(pylatex.NoEscape(
          r'\renewcommand*{\Affilfont}{\small\it}'))
      # 去掉 and 前的逗号
      doc.preamble.append(pylatex.NoEscape(r'\renewcommand{\Authands}{, }'))
    else:
      pass

    # date
    date = pylatex.NoEscape(
        r'\date{\today}') if is_date else pylatex.NoEscape(r'\date{}')
    doc.preamble.append(date)
    doc.append(pylatex.NoEscape(r'\maketitle'))
    return None

  def abstract(self, content='In this paper, we used the ...',
               keywords=['tungsten', 'helium', 'fuzz'],
               is_cn=False,
               flh_中图分类号='G252.17',
               bsm_文献标识码='A',
               ):
    """_summary_
      Returns: latex_obj_list
          _type_: _description_
    """
    # lo1 = pylatex.PageStyle('empty')
    # lo1 = pylatex.NoEscape(r'\thispagestyle{empty}')
    env = self.get_abstract_env()
    env.append(content)
    if keywords:
      string = r'\par \indent \textbf{Keywords:} '.replace(
          'Keywords', '关键词') if is_cn else r'\par \indent \textbf{Keywords:} '
      env.append(pylatex.NoEscape(string))
      env.append(pylatex.NoEscape('; '.join(keywords)))
      if is_cn:
        lo = pylatex.NoEscape(
            fr'\par \indent \textbf{{中图分类号:}} {flh_中图分类号}, \textbf{{文献标识码:}} {bsm_文献标识码}')
        env.append(lo)
        pass

    lo2 = pylatex.NewPage()
    # lo3 = pylatex.NoEscape(r'\pagenumbering{arabic}')

    return [env, lo2,]

  def abstract_old(self, abstract='In this paper, we used the ...',
                   keywords='tungsten; helium; fuzz; molecular dynamics'):
    """_summary_

    Args:
        abstract (str, optional): _description_. Defaults to 'In this paper, we used the ...'.
        keywords (str, optional): _description_. Defaults to 'tungsten; helium; fuzz; molecular dynamics'.

    Returns: latex_obj_list
        _type_: _description_
    """
    latex_obj_list = []
    latex_obj_list.append(pylatex.NoEscape(
        fr'\begin{{abstract}} {abstract} \par \textbf{{Keywords:}} {keywords} \end{{abstract}}'))
    latex_obj_list.append(pylatex.NoEscape(r'\thispagestyle{empty}'))
    latex_obj_list.append(pylatex.NewPage())
    latex_obj_list.append(pylatex.NoEscape(r'\pagenumbering{arabic}'))

    return latex_obj_list

  def header_and_footer_example(self, doc=pylatex.Document):
    # Add document headerpylatex.
    header = pylatex.PageStyle("header")
    # Create left header
    with header.create(pylatex.Head("L")):
      header.append("Page date: ")
      header.append(pylatex.LineBreak())
      header.append("R3")
    # Create center header
    with header.create(pylatex.Head("C")):
      header.append("Company")
    # Create right header
    with header.create(pylatex.Head("R")):
      header.append(pylatex.simple_page_number())
    # Create left footer
    with header.create(pylatex.Foot("L")):
      header.append("Left Footer")
    # Create center footer
    with header.create(pylatex.Foot("C")):
      header.append("Center Footer")
    # Create right footer
    with header.create(pylatex.Foot("R")):
      header.append("Right Footer")

    doc.preamble.append(header)
    doc.change_document_style("header")

  def set_pagestyle_header_and_footer(self,
                                      doc: pylatex.Document,
                                      location_header='R',
                                      content_header='这是页眉',
                                      location_footer='R',
                                      content_footer='',
                                      header_thickness=0.4,
                                      footer_thickness=0):
    """添加页眉和页脚
    - location: 'L' 左侧, 'C' 中间, 'R' 右侧
    - doc: pylatex.Document, 文档对象
    """
    pagestyle_name = 'mypagestyle'
    pagestyle = pylatex.PageStyle(name=pagestyle_name,
                                  header_thickness=header_thickness,
                                  footer_thickness=footer_thickness,)
    # 添加页眉和页脚
    head = pylatex.Head(position=location_header, data=content_header)
    pagestyle.append(head)
    foot = pylatex.Foot(position=location_footer, data=content_footer)
    pagestyle.append(foot)
    # ---
    doc.preamble.append(pagestyle)
    doc.change_document_style(pagestyle_name)
    return None

  def toc(self,):
    """目录
    """
    toc = self.get_toc_tableofcontents_obj()
    newpage = self.get_newpage_obj()
    lol = [toc, newpage]
    return lol

  def get_lol_bibref(self,):
    r"""
      _summary_
      # % 手动创建参考文献列表
      \begin{thebibliography}{9}
          \bibitem{item1} Author1. \textit{Title of the first item}. Publisher, Year.
          \bibitem{item2} Author2. \textit{Title of the second item}. Journal, Year.
          % 在此处添加其他引用
      \end{thebibliography}
    """

    # plain、abbrv、alpha , unsrt
    par1 = pylatex.Command('bibliographystyle', 'unsrt')
    par2 = pylatex.Command('bibliography', pylatex.NoEscape(self.fname_bib))
    latex_obj_list = [par1, par2]
    return latex_obj_list

  def my_compile(self,
                 doc: pylatex.Document,
                 fname_tex='xxx/manuscript',
                 compiler_args=[],
                 clean=True,
                 clean_tex=False):
    doc.generate_pdf(fname_tex, compiler='xelatex',
                     clean_tex=False, clean=False,
                     compiler_args=compiler_args,
                     )
    os.popen(f'bibtex {fname_tex}')

    doc.generate_pdf(fname_tex, compiler='xelatex',
                     clean_tex=False, clean=False,
                     compiler_args=compiler_args
                     )
    doc.generate_pdf(fname_tex, compiler='xelatex',
                     clean=clean,
                     clean_tex=clean_tex,
                     compiler_args=compiler_args
                     )
    pass

  def my_compile_CLI(self, doc: pylatex.Document,
                     compiler='xelatex',
                     compiler_args=['--synctex=1',
                                    "--interaction=nonstopmode",
                                    "--file-line-error",],
                     fname_tex='xxx/manuscript',
                     ):
    # 步骤 1: 生成 .tex 文件
    doc.generate_tex(fname_tex)
    # 步骤 2: 运行 pdflatex 编译
    from soft_learn_project import subprocessLearn
    sl = subprocessLearn.SubprocessLearn()
    cmd_xelatex = [compiler] + compiler_args + [fname_tex+'.tex']
    cmd_bibtex = ['bibtex', fname_tex]

    result = sl.CLI_cmd(directory=os.path.dirname(fname_tex),
                        args=cmd_xelatex)
    # 步骤 3: 运行 bibtex
    result = sl.CLI_cmd(directory=os.path.dirname(fname_tex),
                        args=cmd_bibtex)
    # 步骤 4: 运行 pdflatex 两次（以确保参考文献正确）
    for _ in range(2):
      result = sl.CLI_cmd(directory=os.path.dirname(fname_tex),
                          args=cmd_xelatex)
    return None

  def write_file(self, doc: pylatex.Document,
                 fname='xxx/tmp',
                 clean=True,
                 clean_tex=False,
                 with_bibref=False,
                 compiler_args=['--synctex=1',
                                "--interaction=nonstopmode",
                                "--file-line-error",],):
    """
      用不同的编译方法编译文件
      - 查看编译的方法
      - from latex_learn import latexLearn
      - latexLearn.LatexLearn().compile_tex()
      - 只产生 *.tex 文件: doc.generate_tex('output',)
      * 编译参数
      - compiler_args: xelatex --synctex=1 xx.tex, 该参数用于产生 xx.synctex.gz, 该文件可以同步 .tex 和 .pdf 的内容, 即 双击 pdf中的某个部分可以跳转到 .tex 对应的位置
    """

    danme = os.path.dirname(os.path.abspath(fname))
    if not os.path.exists(danme):
      os.makedirs(name=danme)
    # 输出到pdf
    if with_bibref:  # 编译带参考文献
      # doc.extend(self.bib())  # 参考文献
      self.my_compile(doc=doc,
                      fname_tex=fname,
                      compiler_args=compiler_args,
                      clean=clean, clean_tex=clean_tex,
                      )
    else:  # 不带参考文献的
      doc.generate_pdf(fname, compiler='xelatex',
                       clean_tex=clean_tex, clean=clean,
                       compiler_args=compiler_args)
      # 由于图表的标签也需要多次编译
      # self.my_compile(doc=doc,
      #                 fname_tex=fname,
      #                 compiler_args=compiler_args,
      #                 clean=clean, clean_tex=clean_tex,
      #                 )

    print(f'编译生成文件-> \n{fname}.pdf')
    return None

  def create_sections(self, doc: pylatex.Document):
    # 创建章节的两种方式
    # 使用with 这种方式可以用缩进的方式确保要添加的内容在文档里
    with doc.create(pylatex.Section('A second section')):
      doc.append('Some text.')
    # 直接添加
    doc.append(pylatex.Section("B"))
    doc.append("some in B")

  def sectsty(self, doc: pylatex.Document,
              align='raggedright|centering|raggedleft'):
    """设置section 标题的对齐格式
    """

    # doc.packages.append(pylatex.Package("sectsty"))
    doc.preamble.append(pylatex.Command(
        command='allsectionsfont',
        arguments=pylatex.Command(command=align),
        packages=[pylatex.Package('sectsty')]  # 最好用这个方式
    ))
    return doc

  def command(self, doc: pylatex.Document):
    # 使用命令的两种方式
    # 1. command 只有第一个命令名是必选参数, 其余是可选参数, 其中, argument/extra_arguments/options支持数字,字符串,list,甚至是map, 非常方便,packages必须为可迭代对象, 且每一个元素必须是Package实例
    doc.append(pylatex.Command("commandName", arguments={
               'a': 1.2}, options="options", extra_arguments="extra", packages=[pylatex.Package("graph")]))
    # 2.NoEscape 在doc.append()中直接添加字符串, 其中的\{}[]等会被转义, 因此我们如果想直接添加命令是不可行的, 但也不是不可以, 方法就是NoEscape对象
    # Python 中, 字符串前加r表示raw string, 不用对其中的斜杠等进行转义
    doc.append(pylatex.NoEscape(r'\commandname[]...{}'))

  def enum_example(self, doc: pylatex.Document):
    # 添加enumerate列表环境
    with doc.create(pylatex.Enumerate(enumeration_symbol=pylatex.NoEscape(r'\Alph*)'))) as enum:
      enum: pylatex.Enumerate
      enum.add_item('firet')
      enum.add_item('sectod')

    with doc.create(pylatex.Enumerate(enumeration_symbol=r'\arabic*)')) as enum:
      enum: pylatex.Enumerate
      enum.add_item(pylatex.NoEscape(r"First item\newline"))
      s = '这是一段话'*50
      enum.append(pylatex.NoEscape(s))  # \indent 不管用
      enum.add_item("Second item")
      enum.add_item("Third item")

    # 或者用下面的方式
    """
    enum = pylatex.Enumerate()
    enum.add_item('身份证, 博士毕业证、博士学位证、副教授任职资格证')
    enum.add_item('国家自然科学基金项目和省级项目材料')
    enum.add_item('发表的第一作者文章和检索报告')
    enum.add_item('教学工作量证明材料')
    doc.append(enum)
    """

  def enumerate(self,
                item_list=['a', 'b', 'c'],
                enumeration_symbol=r'\arabic*.\,',
                options=['left=0em', 'noitemsep'],
                ):
    r"""* enumeration_symbol 参数：
    r'\\arabic*'：用阿拉伯数字编号. 
    r'\\roman*'：用罗马数字编号. 
    r'\\alph*'：用小写字母编号. 
    r'\\Alph*'：用大写字母编号. 
    'fnsymbol'：用符号编号. ??
    --- 
    * options 的 其它可用选项, 更多的可以问 chatgpt 
    left 或 leftmargin：设置列表的左边距。
    rightmargin：设置列表的右边距。
    itemindent：设置每个列表项的缩进。
    labelindent：设置标签的缩进。
    labelwidth：设置标签的宽度。
    labelsep：设置标签与文本之间的间距。
    listparindent：设置段落内的缩进。
    topsep：设置列表与上方内容的间距。
    partopsep：设置列表与段落之间的额外间距。
    parsep：设置列表项之间的段落间距。
    itemsep：设置列表项之间的间距。
    """
    enum = pylatex.Enumerate(enumeration_symbol=enumeration_symbol,
                             options=options)
    for item in item_list:
      enum.add_item(pylatex.NoEscape(item))
    return enum

  def table_example(self, doc: pylatex.Document):
    """在 PyLaTeX 中, tabularx、tabular、table 和 tabu 是用于创建表格的不同环境或类. 它们各自有不同的特点和用途：
    tabularx:
    用于创建带有自动调整列宽功能的表格, 可以根据指定的宽度自动调整列宽, 适用于需要填充给定宽度的表格. 
    提供了 X 列格式, 允许某些列自动伸展以填充剩余空间. 

    tabular:
    是 LaTeX 最基本的表格环境, 用于创建简单的表格, 需要手动指定每列的宽度或对齐方式. 
    table:
    不是创建表格的环境, 而是用于容纳和控制表格的浮动体环境. table 环境允许表格浮动到页面的其他位置, 可以添加标题、标签等. 

    tabu:
    是一个功能强大的表格宏包, 相对于标准的 tabular, 提供了更多的功能和选项, 包括自动伸展列宽、跨页表格等. 

    tabu 在某些情况下比 tabularx 更灵活, 并且支持更多的表格样式和设置. 
    Args:
        doc (pylatex.Document): _description_
    """
    # 或者用这种方法
    # with doc.create(Section('Tables')):
    #   with doc.create(Tabular('ccc')) as table:
    #     table.add_hline()
    #     table.add_row(('Header 1', 'Header 2', 'Header 3'))
    #     table.add_hline()
    #     table.add_row((1, 2, 3))
    #     table.add_row((4, 5, 6))
    #     table.add_hline()

    # 创建一个表格
    # table = pylatex.Tabular('ll')
    # table.add_row(('申请人:', '王金龙',))
    # table.add_row(('申报档次:', '翠湖领军人才二挡'))
    # # 创建一个居中环境并添加表格
    # center = pylatex.Center()
    # center.append(table)
    # doc.append(center)

    with doc.create(pylatex.Tabular('rc|cl')) as table:
      table: pylatex.Tabular
      table.add_hline()
      table.add_row((1, 2, 3, 4))
      # table.add_hline(1, 2)
      table.add_hline()
      table.add_empty_row()
      table.add_row((4, 5, 6, 7))

  def table_example2(self):
    data_arr = np.array([['0.02', '650.33', '341.64', '148.83'],
                         ['0.05', '1273.97', '426.97', '323.99'],
                         ['0.11', '3111.34', '419.63', '702.00'],
                         ['0.16', '4619.82', '418.38', '1759.73'],
                         ['0.23', '8487.85', '504.45', '3803.63']])

    table = pylatex.Table(position='H')
    table.add_caption(pylatex.NoEscape(
        r'Using four ... \label{tab:acceleration_efficiency}'))
    table.append(pylatex.NoEscape(r'\vspace{1em}'))
    with table.create(pylatex.Tabular(table_spec='cccc', booktabs=True)) as tabular:
      tabular: pylatex.Tabular
      tabular.append(pylatex.NoEscape(
          r"""\diagbox{fluence}{time consuming}{method} & conventional method & acceleration method & PRD acceleration method\\ \hline """))
      for line in data_arr:
        tabular.add_row(line)

    return table

  def table_tabu(self, df,
                 table_ref=r'\ref{table}',
                 escape=False,
                 table_num=None,
                 table_spec=None,
                 font_size='normalsize',
                 caption=r'B与衬底之间的结合能',
                 ):
    """ 查看 self.font_size

    Args:
        df (_type_): _description_
        table_spec (_type_, optional): 'X[c]'*num_columns.'X[2l]'+'X[1c]'*4.  Defaults to None.
        caption (regexp, optional): _description_. Defaults to r'B与衬底之间的结合能'.
        table_ref (str, optional): _description_. Defaults to 'Eb_B_Nngraphene'.

    Returns:
        _type_: _description_
    """
    table = pylatex.Table(position='H',)
    num_columns = df.columns.__len__() + 1
    if table_num:  # 自定义表格编号
      table.append(pylatex.NoEscape(fr'\setcounter{{table}}{table_num-1}'))
    table.add_caption(pylatex.NoEscape(caption+self.ref2label(table_ref)))
    table.append(pylatex.NoEscape(r'\vspace{5pt}'))  # 调整间距表格标题和表格的间距
    table.append(pylatex.NoEscape(fr'\{font_size}'))
    if not table_spec:
      table_spec = 'X[l]'*num_columns
    with table.create(pylatex.Tabu(table_spec=table_spec, booktabs=True)) as tabu:
      tabu: pylatex.Tabu
      if df.columns.__len__() == num_columns:
        tabu.add_row([*df.columns], escape=escape)
      else:
        name1 = '' if df.index.name is None else df.index.name
        tabu.add_row([name1, *df.columns], escape=escape)
      tabu.add_hline()
      for index, line in zip(df.index, df.values):
        tabu.add_row([index, *line], escape=escape)

    return table

  def table_custom(self, df, table_ref=r'\ref{xxx}', caption=r'xxx',
                   table_num=None,
                   ):
    """根据 df.to_latex() 可以给出自定义df 的表格 比如多行多列

    Args:
        df (_type_): _description_
        table_ref (_type_): 为 r'\ref{xxx}' 的形式
        caption (_type_): _description_

    Returns:
        _type_: _description_
    """
    table_label_str = re.findall(pattern=r'\\ref{(.*?)}',
                                 string=table_ref)[0]
    table = pylatex.Table(position='H')
    if table_num:  # 自定义表格编号
      table.append(pylatex.NoEscape(fr'\setcounter{{table}}{table_num-1}'))
    table.add_caption(caption=pylatex.NoEscape(
        rf'{{{caption}}}'+rf'\label{{{table_label_str}}}'))
    table.append(pylatex.Command('centering'))
    table.append(pylatex.NoEscape(df.to_latex()))
    return table

  def change_name_df_index(self, df: pd.DataFrame):
    """处理 O2 H2, H2O O2H 为latex 格式

    Args:
        df (pd.DataFrame): _description_

    Returns:
        _type_: _description_
    """
    index_list = []
    for index in df.index:
      index: str
      if index == 'H2':
        index = index.replace('H2', r'H$_2$',)
      if index == 'O2':
        index = index.replace('O2', r'O$_2$',)
      if index == 'H2O':
        index = index.replace('H2O', r'H$_2$O',)
      index = index.replace('O2H', 'OOH')
      index = index.replace('O2', r'O$_2$')
      index_list.append(index)
    df.index = index_list
    return df

  def longtable(self, df: pd.DataFrame,
                table_spec=r'p{0.4\textwidth}'+r'p{0.2\textwidth}'*3,
                escape=None,
                row_height=None,
                col_space=None,
                width=None,
                is_inner_lines=False,
                ):
    r"""建议使用这个
    * table_spec 的设置技巧: 1-0.024*(columns) 剩余的即为table_spec宽度的总和, 例如, 7列的表格, 1-0.024*7=0.825, table_spec=r'p{0.825/7\textwidth}*7'. 6列的表格, 1-0.024*6=0.85, table_spec的总宽度应为0.85\textwidth. 
    ---
    * 表格后面还可以增加行, 例如
    table.add_hline()
    table.add_row([r'2028.11 $\sim$2028.12', pylatex.MultiColumn(
        2, align='c', data='撰写结题报告.'),], escape=False)

    - p{0.3\textwidth} : 默认左对齐
    - >{\centering\arraybackslash}p{0.2\textwidth}: 居中
    - >{\raggedright\arraybackslash}p{0.3\textwidth}: 左对齐
    - >{\raggedleft\arraybackslash}p{0.2\textwidth}: 右对齐

    * 表格的标准包 
    \usepackage{longtable}  % 处理跨页表格
    \usepackage{array}      % 控制列对齐方式
    \usepackage{booktabs}   % 提供更好看的表格线

    Args:
        df (pd.DataFrame): _description_
        table_spec (_type_, optional): table_spec 的设置技巧: 1-0.025*(columns) 剩余的即为table_spec宽度的总和, 例如, 7列的表格, 1-0.025*7=0.825, table_spec=r'p{0.825/7\textwidth}*7'.
        row_height (_type_, optional): _description_. Defaults to None.
        col_space (_type_, optional): _description_. Defaults to None.
        width (_type_, optional): 总列数, 一般不需要额外设置.
        is_inner_lines (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    num_col = df.columns.__len__() + 1
    table = pylatex.LongTable(table_spec=table_spec,
                              row_height=row_height,
                              col_space=col_space,
                              booktabs=True,
                              width=width,
                              )
    table.add_hline()
    df.columns = [pylatex.NoEscape(column) for column in df.columns]
    table.add_row(['', *df.columns],
                  mapper=[pylatex.utils.bold, ],
                  escape=escape)
    table.add_hline()
    table.end_table_header()
    table.add_hline()
    table.add_row((pylatex.MultiColumn(
        num_col, align="c", data="Continued on Next Page"),))
    table.add_hline()
    table.end_table_footer()
    # table.add_hline()
    # table.add_row(
    #     (pylatex.MultiColumn(num_col, align="c", data="Not Continued on Next Page"),))
    # table.add_hline()

    table.end_table_last_footer()

    for index in df.index:
      if is_inner_lines:
        table.add_hline()
      table.add_row([pylatex.NoEscape(index), *df.loc[index]], escape=escape)

    return table

  def longtable_wrapper(self,
                        df: pd.DataFrame,
                        table_spec=r'p{0.4\textwidth}'+r'p{0.2\textwidth}'*3,
                        escape=None,
                        row_height=None,
                        col_space=None,
                        width=None,
                        is_inner_lines=False,
                        font_size='normalsize',
                        caption=r"\textbf{Table:} The calculated data list includes the system's energy (E), the energy of the system considering the solvation effect (E$_{sol}$), the system's Gibbs free energy (G), the Gibbs free energy of the system considering the solvation effect (G$_{sol}$), the zero-point energy (ZPE), and entropy (S).",):
    """* 包括了表的标题
    * table_spec 的设置技巧: 1-0.024*(columns) 剩余的即为table_spec宽度的总和, 例如, 7列的表格, 1-0.024*7=0.825, table_spec=r'p{0.825/7\textwidth}*7'. 6列的表格, 1-0.024*6=0.85, table_spec的总宽度应为0.85\textwidth. 
    """
    # 标题
    # center.append(pylatex.NoEscape(caption))
    center = pylatex.NoEscape(r'\noindent '+caption)
    # 表格
    start = pylatex.NoEscape(fr'\{font_size}')
    table = self.longtable(df=df,
                           table_spec=table_spec,
                           escape=escape,
                           row_height=row_height,
                           col_space=col_space,
                           width=width,
                           is_inner_lines=is_inner_lines,)
    end = pylatex.NoEscape(fr'\normalsize')
    latex_obj_list = [center, start, table, end]
    return latex_obj_list

  def longtabularx(self, df: pd.DataFrame,
                   table_spec=r'p{0.4\textwidth}'+r'p{0.19\textwidth}'*3,
                   row_height=None,
                   col_space=None,
                   width=None,
                   is_inner_lines=False,
                   escape=None):
    num_col = df.columns.__len__() + 1
    table = pylatex.LongTabularx(table_spec=table_spec,
                                 row_height=row_height,
                                 col_space=col_space,
                                 booktabs=True,
                                 width=width,
                                 )
    table.add_hline()
    table.add_row(['', *df.columns], mapper=pylatex.utils.bold, escape=escape)
    table.add_hline()
    table.end_table_header()
    table.add_hline()
    table.add_row((pylatex.MultiColumn(
        num_col, align="c", data="Continued on Next Page"),))
    table.add_hline()
    table.end_table_footer()
    # 去掉最后的说明
    # table.add_hline()
    # table.add_row(
    #     (pylatex.MultiColumn(num_col, align="c", data="Not Continued on Next Page"),))
    # table.add_hline()
    table.end_table_last_footer()

    for index in df.index:
      if is_inner_lines:
        table.add_hline()
      table.add_row([index, *df.loc[index]], escape=escape)

    return table

  def longtabu(self, df: pd.DataFrame,
               table_spec=r'p{0.4\textwidth}'+r'p{0.19\textwidth}'*3,
               row_height=None,
               col_space=None,
               spread=None,
               to=None,
               width=None,
               is_inner_lines=False,
               escape=None):
    """弃用

    Args:
        df (pd.DataFrame): _description_
        table_spec (_type_, optional): _description_. Defaults to r'p{0.4\textwidth}'+r'p{0.19\textwidth}'*3.
        row_height (_type_, optional): _description_. Defaults to None.
        col_space (_type_, optional): _description_. Defaults to None.
        spread (_type_, optional): _description_. Defaults to None.
        to (_type_, optional): _description_. Defaults to None.
        width (_type_, optional): _description_. Defaults to None.
        is_inner_lines (bool, optional): _description_. Defaults to False.
        escape (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    num_col = df.columns.__len__() + 1
    table = pylatex.LongTabu(table_spec=table_spec,
                             row_height=row_height,
                             col_space=col_space,
                             booktabs=True,
                             width=width,
                             spread=spread,
                             to=to,
                             )
    table.add_hline()
    table.add_row(['', *df.columns], mapper=pylatex.utils.bold, escape=escape)
    table.add_hline()
    table.end_table_header()
    table.add_hline()
    table.add_row((pylatex.MultiColumn(
        num_col, align="c", data="Continued on Next Page"),))
    table.add_hline()
    table.end_table_footer()
    table.add_hline()
    table.add_row(
        (pylatex.MultiColumn(num_col, align="c", data="Not Continued on Next Page"),))
    table.add_hline()
    table.end_table_last_footer()

    for index in df.index:
      if is_inner_lines:
        table.add_hline()
      table.add_row([index, *df.loc[index]], escape=escape)

    return table

  def figure_example(self):
    # 添加图表
    # 创建一个新的文档
    doc = pylatex.Document()

    with doc.create(pylatex.Section('Figures')):
      with doc.create(pylatex.Figure(position='h!')) as fig:
        fig.add_image('example.jpg', width='120px')
        fig.add_caption('Caption of the figure')
        fig.append(pylatex.Label('Abstract Graph'))  # 增加图形标签
    # 输出到文件
    doc.generate_tex('figures.tex')

  def figure(self, fname,
             caption_str=r'xxx',
             fig_ref=r'\ref{xxx}',
             fig_num=None,):
    fig = pylatex.Figure(position='H')
    if fig_num:  # 自定义表格编号 如果为4 则标号为5
      fig.append(pylatex.NoEscape(fr'\setcounter{{figure}}{fig_num-1}'))
    fig.add_image(filename=fname,
                  width=pylatex.NoEscape(r'0.9\linewidth'))
    label = self.ref2label(ref=fig_ref)
    fig.add_caption(caption=caption_str)
    fig.append(pylatex.NoEscape(label))
    return fig

  def figure_2subfigs_example(self, doc: pylatex.Document,
                              image_filename='../fig/IMG20231213153558.jpg'):

    with doc.create(pylatex.Figure(position='h!')) as kittens:
      with doc.create(pylatex.SubFigure(position='b',
                                        width=pylatex.NoEscape(r'0.45\linewidth'))) as left_kitten:
        left_kitten.add_image(image_filename,
                              width=pylatex.NoEscape(r'\linewidth'))
        left_kitten.add_caption('Kitten on the left')

      with doc.create(pylatex.SubFigure(position='b',
                                        width=pylatex.NoEscape(r'0.45\linewidth'))) as right_kitten:
        right_kitten.add_image(image_filename,
                               width=pylatex.NoEscape(r'\linewidth'))
        right_kitten.add_caption('Kitten on the right')
      kittens.add_caption("Two kittens")

  def figure_2subfigs(self, fname_subfig1,
                      caption_subfig1,
                      fname_subfig2,
                      caption_subfig2,
                      caption,
                      label_str,
                      ):
    fig = pylatex.Figure(position='H')
    with fig.create(pylatex.SubFigure(width=pylatex.NoEscape(r"0.45\linewidth"),
                                      position='b')) as left_fig:
      left_fig: pylatex.SubFigure
      left_fig.add_image(fname_subfig1,
                         width=pylatex.NoEscape(r'\linewidth'))
      left_fig.add_caption(caption_subfig1)
    with fig.create(pylatex.SubFigure(width=pylatex.NoEscape(r"0.45\linewidth"),
                                      position='b')) as right_fig:
      right_fig: pylatex.SubFigure
      right_fig.add_image(fname_subfig2,
                          width=pylatex.NoEscape(r'\linewidth'))
      right_fig.add_caption(caption_subfig2)
    fig.add_caption(pylatex.NoEscape(caption+fr'\label{{{label_str}}}'))
    return fig

  def figure_list(self,
                  fname_list=[''],
                  sub_caption_list=[''],
                  fig_ref=r'\ref{fig}',
                  fig_num=None,
                  num_figs=2,
                  extra_opt='',
                  width_subfigure=0.45,
                  caption=r'x',):
    r"""插入多图, 例如四张图, 每隔两张换行 
    - width_subfigure: 可以是列表
    - extra_opt: 'trim=20in 7in 20in 15in, clip' 可以设置图片的剪裁left bottom right top 可以是一个列表, \includegraphics[trim=left bottom right top, clip]{image.png} 分别是你想要保留的图片左边、底部、右边和顶部的边距. 你可以将这些值设置为负数来扩大要裁剪的区域, 或者设置为正数来缩小裁剪的区域. 添加 clip 选项会使裁剪后的区域成为实际可见的图像大小, 即只显示裁剪后的部分. 

    Args:
        fname_list (_type_): _description_
        sub_caption_list (_type_): _description_
        caption (_type_): _description_
        extra_opt: 'trim=20in 7in 20in 15in, clip' 可以设置图片的剪裁left bottom right top 可以是一个列表

    Returns:
        _type_: _description_
    """

    fig = pylatex.Figure(position='H')
    if fig_num:  # 自定义表格编号
      fig.append(pylatex.NoEscape(fr'\setcounter{{figure}}{fig_num-1}'))
    fig.append(pylatex.NoEscape(r'\centering'))
    n = 0
    for fname, sub_caption in zip(fname_list,
                                  sub_caption_list,
                                  ):
      n += 1
      if isinstance(extra_opt, str):
        extra_opt_value = extra_opt
      elif isinstance(extra_opt, list):
        extra_opt_value = extra_opt[n-1]

      if isinstance(width_subfigure, list):
        width_subfigure_v = width_subfigure[n-1]
      else:
        width_subfigure_v = width_subfigure

      with fig.create(pylatex.SubFigure(width=pylatex.NoEscape(fr"{width_subfigure_v}\linewidth"))) as subfig:
        subfig: pylatex.SubFigure
        subfig.add_image(
            filename=fname, width=pylatex.NoEscape(r"0.95\linewidth," + extra_opt_value),)
        if sub_caption:
          subfig.add_caption(caption=pylatex.NoEscape(sub_caption))
      if n % num_figs == 0:
        fig.append(pylatex.NoEscape(r'\par'))  # 使用 \newline 不会居中
    fig.add_caption(caption=pylatex.NoEscape(fr'{caption}'))
    # r'\\label{abc_xxx}'
    fig.append(pylatex.NoEscape(self.ref2label(ref=fig_ref)))
    return fig

  def figure_list_with_top_front_view(self,
                                      fnames_list,
                                      sub_caption_list,
                                      caption,
                                      fig_ref=r'\ref{fig}',
                                      num_figs_per_row=2,
                                      extra_opt='',
                                      width_subfigure=0.45,
                                      fig_num=None,):
    r"""插入的子图带有上下两个图,2个子图，每个子图放置上下两幅图
    fnames_list=[['1_top.png','1_side.png'],['2_top.png','2_side.pnd']]
    sub_caption_list=['initial','final']

    Args:
        fname_list (_type_): _description_
        sub_caption_list (_type_): _description_
        caption (_type_): _description_
        extra_opt: 'trim=20in 7in 20in 15in, clip' 可以设置图片的剪裁
        \includegraphics[trim=left bottom right top, clip]{image.png} 分别是你想要保留的图片左边、底部、右边和顶部的边距. 你可以将这些值设置为负数来扩大要裁剪的区域, 或者设置为正数来缩小裁剪的区域. 添加 clip 选项会使裁剪后的区域成为实际可见的图像大小, 即只显示裁剪后的部分. 
    Returns:
        _type_: _description_
    """
    fig = pylatex.Figure(position='H')
    if fig_num:  # 自定义表格编号
      fig.append(pylatex.NoEscape(fr'\setcounter{{figure}}{fig_num-1}'))
    fig.append(pylatex.NoEscape(r'\centering'))
    n = 0
    for fnames, sub_caption in zip(fnames_list, sub_caption_list):
      n += 1
      with fig.create(pylatex.SubFigure(width=pylatex.NoEscape(fr"{width_subfigure}\linewidth"))) as subfig:
        subfig: pylatex.SubFigure
        for fname in fnames:
          subfig.add_image(
              filename=fname, width=pylatex.NoEscape(r"0.95\linewidth," + extra_opt),)
          subfig.append(pylatex.NewLine())
        if sub_caption:
          subfig.add_caption(caption=pylatex.NoEscape(sub_caption))
      if n % num_figs_per_row == 0:
        fig.append(pylatex.NewLine())  # pylatex.NoEscape(r'\newline')
    fig.add_caption(caption=pylatex.NoEscape(caption),)
    fig.append(pylatex.NoEscape(self.ref2label(ref=fig_ref)))

    return fig

  def figure_list_with_top_front_view_for_neb(self,
                                              directory='xxx/path2_initial2final_OSi_SiOC',
                                              images_index_list=[0, 2, 6],
                                              sub_caption_list=['Initial State',
                                                                'Transition State',
                                                                'Final State'],
                                              width_subfigure=0.33,
                                              num_figs_per_row=3,
                                              caption='x',
                                              fig_ref=r'\ref{fig}',
                                              fig_num=None,):

    fnames_list = []
    for index in images_index_list:
      fname_list = [os.path.basename(directory) + f'_{index}_top.png',
                    os.path.basename(directory) + f'_{index}_side.png',]
      fname_list = [os.path.join(directory, fname) for fname in fname_list]
      fnames_list.append(fname_list)
    fig = self.figure_list_with_top_front_view(
        fnames_list=fnames_list,
        sub_caption_list=sub_caption_list,
        width_subfigure=width_subfigure,
        num_figs_per_row=num_figs_per_row,
        caption=caption,
        fig_ref=fig_ref,
        fig_num=fig_num,
    )
    return fig

  def figure_save(self, fname_list,
                  substrate_name_list=None,
                  num_figs=2,
                  width_subfigure=0.5,
                  extra_opt='trim=23in 4in 24in 4in, clip',
                  fig_ref=r''):
    """弃用 考虑使用
    from py_package_learn.pymupdf_learn import pymupdfLearn
    image = pymupdfLearn.Features().pdf_page_to_image(
        fname_pdf=fname + '.pdf', page_number=page_number)

    保存一个图片, 用于之后 复杂图片的组合 例如: 左边四个小图2x2 右边一个图
    """
    doc = self.get_document(geometry_options={
        'top': '0cm', 'bottom': '0cm', 'left': '0cm', 'right': '0cm'}, )
    if not substrate_name_list:
      substrate_name_list = ['']*len(fname_list)
    fig = self.figure_list(fname_list=fname_list,
                           caption='',
                           sub_caption_list=substrate_name_list,
                           fig_ref=fig_ref,
                           num_figs=num_figs,
                           width_subfigure=width_subfigure,
                           extra_opt=extra_opt,)
    doc.append(fig)

  def get_overpic_obj(self,
                      options=r'width=0.5\linewidth,grid,trim=0in 0in 0in 0in, clip',
                      fname_fig=r'/Users/wangjinlong/my_server/my/myORR_B/slab/PN_codope/P1_N2_CoN4_like/ab_md/ab_md_initial.png',
                      start_arguments=None,
                      coords_string_list=[
                          [(30, 40), r'\colorbox{white}{\framebox{Initial configurations}}']],
                      **kwargs):
    class OverPic(pylatex.base_classes.Environment):
      """A class to wrap LaTeX's alltt environment."""

      def __init__(self, *, options=None, arguments=None, start_arguments=None, **kwargs):
        super().__init__(options=options, arguments=arguments,
                         start_arguments=start_arguments, **kwargs)
        # packages = [pylatex.Package('overpic')]

    overpic_obj = OverPic(options=pylatex.NoEscape(options),
                          arguments=pylatex.NoEscape(fname_fig),
                          start_arguments=start_arguments,
                          **kwargs)
    # 增加注释
    for coords_string in coords_string_list:
      coords, string = coords_string
      overpic_obj.append(pylatex.NoEscape(fr'\put{coords}{{{string}}}'))
    return overpic_obj

  def equation(self,
               string=r'E_f = E_{doped-C_{3}N} + E_{C/N} - E_{C_{3}N} - E_B'):
    """_summary_

    Args:
        string (regexp, optional): _description_. Defaults to r'E_f = E_{doped-C_{3}N} + E_{C/N} - E_{C_{3}N} - E_B'.

    Returns:
        _type_: _description_
    """
    text = pylatex.NoEscape(r'\begin{equation}')
    text += pylatex.NoEscape(string)
    text += pylatex.NoEscape(r'\end{equation}')
    return text

  def alignat_math_environment(self,
                               line_list=[r"\frac{a}{b} + \Gamma &= 0 \\",
                                          r'\alpha^{\beta} &= \gamma'],
                               aligns=2,
                               numbering=False,
                               escape=False
                               ):
    agn = pylatex.Alignat(aligns=aligns,
                          numbering=numbering,
                          escape=escape,)
    for line in line_list:
      agn.append(item=line)
    return agn

  def alignat_math_environment_example(self,):
    a = np.array([[100, 10, 20]]).T
    M = np.matrix([[2, 3, 4], [0, 0, 1], [0, 0, 2]])
    agn = pylatex.Alignat(numbering=False,
                          escape=False)
    agn.append(r"\frac{a}{b} &= 0 \\")
    agn.extend([pylatex.Matrix(M), pylatex.Matrix(a),
               "&=", pylatex.Matrix(M * a)])
    return agn

  def get_math_obj(self, data_list, inline=True, escape=False,
                   equ_num=None):
    """添加数学公式
    Math(data=['2*3', '=', 9]

    Args:
        section (pylatex.Section): _description_
    """
    math = pylatex.Math(data=data_list, inline=inline, escape=escape)
    if equ_num:  # 自定义表格编号, 是不是要放在第一行前面？
      math.append(pylatex.NoEscape(fr'\setcounter{{equation}}{equ_num-1}'))
    return math

  def get_no_page_num_obj(self,):
    no_page_num_obj = pylatex.NoEscape(r'\pagestyle{empty}')
    return no_page_num_obj

  def get_doc_manuscript(self, documentclass='ctexart',
                         title='abc efg',
                         authors=['Jinlong Wang', 'Jinmin Guo', 'Wei Song'],
                         corresponding_authors=['Wei Song'],
                         latex_obj_list=[],
                         linespacing=None,
                         is_cn=False,
                         ):
    """生成手稿"""
    doc = self.get_document(documentclass=documentclass,
                            is_authblk_pkg=True,
                            linespacing=linespacing,
                            )
    # 标题和作者
    self.title_author(doc=doc,
                      title=title,
                      authors=authors,
                      corresponding_authors=corresponding_authors,
                      is_cn=is_cn)
    doc.extend(latex_obj_list)

    return doc

  def write_manuscript(self, documentclass='ctexart',
                       title='abc efg',
                       authors=['Jinlong Wang', 'Jinmin Guo', 'Wei Song'],
                       corresponding_authors=['Wei Song'],
                       latex_obj_list=[],
                       fname='xxx/manuscript',
                       with_bibref=False,
                       clean=True,
                       clean_tex=False,
                       linespacing=None,
                       is_cn=False,
                       ):
    """生成手稿"""
    doc = self.get_doc_manuscript(
        documentclass=documentclass,
        title=title,
        authors=authors,
        corresponding_authors=corresponding_authors,
        latex_obj_list=latex_obj_list,
        linespacing=linespacing,
        is_cn=is_cn,
    )

    # 产生pdf
    self.write_file(doc=doc, fname=fname,
                    clean=clean, clean_tex=clean_tex,
                    with_bibref=with_bibref,
                    )

    return doc

  def write_source(self,
                   fname_input='manuscript_orr.tex',
                   dname_output='source',
                   is_clean=True):
    r"""获取提交文章的source, 包括tex 和图片 以及bib文件
    is_clean: 把修改的蓝色都去掉 也就是 \color{blue} \color{black}

    Args:
        fname_input (str, optional): _description_. Defaults to 'manuscript_orr.tex'.
        dname_output (str, optional): _description_. Defaults to 'source'.
    """
    if os.path.exists(dname_output):
      shutil.rmtree(dname_output)
      os.makedirs(dname_output)
    else:
      os.makedirs(dname_output)
    # 获得最初的 tex文本内容
    with open(fname_input, encoding='utf-8') as f:
      content_tex = f.read()

    import copy
    content_tex_original = copy.deepcopy(content_tex)

    # 处理文本内容和文件
    # bib文本 和 bib文件
    try:
      fname_bib = re.search(
          pattern=r'\\bibliography{(.*?)}',
          string=content_tex).group(1)
      fname_bib_replaced = os.path.basename(fname_bib)
      shutil.copy(fname_bib, os.path.join(dname_output,
                                          fname_bib_replaced))
      content_tex = re.sub(pattern=fname_bib,
                           repl=fname_bib_replaced,
                           string=content_tex)
    except:
      print('没有引用参考文献')

    # 图片 和 图片文件
    pname_origin_list = re.findall(
        pattern=r'\\includegraphics.*?{(.*?)}', string=content_tex)
    pname_list = [os.path.abspath(pname) for pname in pname_origin_list]
    pname_dealed_list = Base().resolve_duplicate_fname_list(
        dname_list=pname_list)
    pname_dealed_list = [os.path.basename(
        pname_dealed) for pname_dealed in pname_dealed_list]
    for pname, pname_dealed in zip(pname_origin_list, pname_dealed_list):
      shutil.copy(pname, os.path.join(dname_output, pname_dealed))
      content_tex = re.sub(
          pattern=pname, repl=pname_dealed, string=content_tex)
      pass

    if is_clean:  # 获得干净的 manuscript
      try:
        content_tex = re.sub(pattern=r'\\color{.*?}',
                             repl='', string=content_tex)
      except:
        pass

    fname_output = os.path.join(dname_output, 'manuscript_clean.tex')
    with open(fname_output, mode='w', encoding='utf-8') as f:
      f.write(content_tex)

    # print
    print(f'获得手稿的source 目录 ->\n{os.path.abspath(dname_output)}')

  def write_manuscript_and_source(self, documentclass='ctexart',
                                  title='abc efg',
                                  authors=['Jinlong Wang',
                                           'Jinmin Guo', 'Wei Song'],
                                  corresponding_authors=['Wei Song'],
                                  linespacing=None,
                                  latex_obj_list=[],
                                  fname='/Users/wangjinlong/my_server/my/myORR_B/submit_materials/NnGraPaper/manuscript',
                                  with_bibref=False,
                                  clean=True,
                                  clean_tex=False,
                                  prepare_source=True,
                                  clean_manuscript=True,
                                  is_cn=False):
    """产生手稿 和 source
    """
    doc = self.write_manuscript(documentclass=documentclass,
                                title=title,
                                authors=authors,
                                corresponding_authors=corresponding_authors,
                                latex_obj_list=latex_obj_list,
                                fname=fname,
                                with_bibref=with_bibref,
                                clean=clean,
                                clean_tex=clean_tex,
                                linespacing=linespacing,
                                is_cn=is_cn,
                                )

    # 产生 source 在同级目录下
    if prepare_source:
      dname_source = os.path.join(os.path.dirname(fname), 'source')
      self.write_source(fname_input=fname+'.tex',
                        dname_output=dname_source,
                        is_clean=clean_manuscript,
                        )

    return doc

  def temporary_test(self, latex_obj_list,
                     directory='',
                     documentclass='ctexart',
                     fname='tmp',
                     sectsty_align='raggedright',
                     with_bibref=False,
                     clean=True,
                     clean_tex=False,
                     linespacing=None,
                     ):
    """用于临时测试

    Args:
        latex_obj_list (_type_): _description_
        fname (str, optional): _description_. Defaults to 'tmp'.
        with_bibref (bool, optional): _description_. Defaults to False.
    """
    doc = self.get_document(is_authblk_pkg=False,
                            is_ctex=True,
                            documentclass=documentclass,
                            linespacing=linespacing,
                            )
    doc = self.sectsty(doc=doc, align=sectsty_align)
    # 不要页码
    doc.append(self.get_no_page_num_obj())
    doc.extend(latex_obj_list)
    fname = os.path.join(directory, fname)
    self.write_file(doc=doc, fname=fname,
                    clean=clean, clean_tex=clean_tex,
                    with_bibref=with_bibref,
                    )
    return doc

  def pdf_page_to_image(self,
                        fname='xx/tmp',
                        page_number=0,
                        save=False,
                        ):
    """保存为同路径下的 png 文件, 方便用于后期制作 GraphicalAbstracts

    Args:
        fname (str, optional): _description_. Defaults to 'xx/tmp'.
        page_number (int, optional): _description_. Defaults to 0.
        save (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    from soft_learn_project import pymupdfLearn
    image = pymupdfLearn.Features().pdf_page_to_image(
        fname_pdf=fname + '.pdf', page_number=page_number)
    os.path.basename(fname)
    if save:
      image.save(fname+'.png')
    print(f'保存为-> {fname}.png')
    return image


class Features(Doc):
  def __init__(self) -> None:
    """制作文档, beamer 的类
    """
    super().__init__()
    self.pylatex = pylatex
    self.Learn = PylatexLearn()
    self.CustomCls = CustomCls()
    self.Beamer = Beamer()
    self.Doc = Doc()

  def x(self):
    pass
