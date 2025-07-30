class HtespLearn():
  def __init__(self):
    """github: https://github.com/Neraaz/HTESP?tab=readme-ov-file
    doc: https://neraaz.github.io/HTESP/
    * htesp，高通量电子结构包，专为量子浓缩（QE）和VASP模拟。hesp简化了材料项目、OQMD和AFLOW数据库的输入文件准备，并提供了广泛的功能，从基本的基态计算到先进的电子-声子研究和超导分析。通过与QE和VASP的无缝集成，hesp使研究人员能够探索复杂的材料景观，自动计算并有效地研究材料电子结构。
    """
    pass

  def install(self):
    """ https://github.com/Neraaz/HTESP/
    git clone https://github.com/Neraaz/HTESP.git
    #Go to HTESP directory cd HTESP
    Conda environment
    conda create --name htesp python==3.12
    source activate myenv
    # Install requirements
    pip install -r requirements.txt
    # Also install phonopy in the conda environment
    # Install HTESP package
    pip install .
    """
    pass

  def env_set(self):
    string = """
    Provide path to ~/src/bash folder in ~/.bashrc
    export PATH="path_to_HTESP/src/bash:$PATH"
    Provide path to src file
    export PYTHONPATH="path_to_HTESP/src:$PYTHONPATH"
    Note: To run the mainprogram command without encountering errors, ensure you copy the config.json file from the /utility/input_files/ directory to the working directory.
    """

    pass
