

class PypandocLearn():
  def __init__(self) -> None:
    """可以用来转 tex 到 md, docx 
    """
    pass

  def install(self):
    """
    pip install pypandoc
    还需要确保系统装了 pandoc（这是它的依赖工具）：
    brew install pandoc   # macOS
    sudo apt install pandoc  # Ubuntu
    """
    pass

  def convert_file_md(self,
                      source_file='/Users/wangjinlong/job/science_research/foundation/ahkjt_安徽省科技厅/2025/tmp.tex',
                      fname_md='/Users/wangjinlong/job/science_research/foundation/ahkjt_安徽省科技厅/2025/x.md'):
    """
      转换.tex 到.md 
    """
    import pypandoc
    output = pypandoc.convert_file(source_file=source_file,
                                   to='md')

    with open(file=fname_md, mode='w',
              encoding='utf-8') as f:
      f.write(output)
    pass

  def convert_file_docx(self, source_file,
                        outputfile):
    import pypandoc
    pypandoc.convert_file(source_file=source_file,
                          to='docx',
                          outputfile=outputfile)
    pass
