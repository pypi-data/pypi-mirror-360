class SevennLearn:
  def __init__(self) -> None:
    """https://github.com/MDIL-SNU/SevenNet/tree/main"""
    pass

  def install(self):
    """pip install git+https://github.com/MDIL-SNU/SevenNet.git # for the latest main branch
    conda install sevenn 
    """
    pass

  def get_calc(self):
    import sevenn.calculator
    # "mpa" refers to the MPtrj + sAlex modal, used for evaluating Matbench Discovery.
    # Use modal='omat24' for OMat24-trained modal weights.
    # calc = SevenNetCalculator('7net-mf-ompa', modal='mpa', device='cpu')
    # r2scan_calculator = SevenNetCalculator(
    #     model='7net-MF-0', device='cpu', modal='R2SCAN')
    # pbe_calculator = SevenNetCalculator(
    #     model='7net-MF-0', device='cpu', modal='PBE')

    calc = sevenn.calculator.SevenNetCalculator(
        model='/Users/wangjinlong/job/soft_learn/py_package_learn/sevenn_learn/package/SevenNet-main/sevenn/pretrained_potentials/SevenNet_MF_0/checkpoint_sevennet_mf_0.pth', modal='PBE')
    return calc
