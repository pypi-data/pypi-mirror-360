
import os


class AbinitLearn():
  def __init__(self,
               num_cores=1) -> None:
    """github: https://github.com/abinit/abinit?tab=readme-ov-file
    官网: https://docs.abinit.org/tutorial/base1/

    """

    self.envs_set()
    pass

  def envs_set(self, name_env='py3918'):
    """old 设置
    os.environ['ASE_ABINIT_COMMAND'] = f"mpirun -np {num_cores} /Users/wangjinlong/opt/anaconda3/envs/abinit/bin/abinit < PREFIX.files > PREFIX.log"
    os.environ['ABINIT_PP_PATH'] = '/Users/wangjinlong/opt/anaconda3/envs/abinit/share/abinit/LDA_PW'
    """
    os.environ['ASE_ABINIT_COMMAND'] = f'mpirun -np 4 abinit  < PREFIX.files > PREFIX.log'
    # 设置 PP 变量
    pp_path = f'/Users/wangjinlong/opt/anaconda3/envs/{name_env}/share/abinit'
    # 定义所有需要添加的路径
    dirname_list = ['GGA_FHI', 'GGA_HGHK', 'GGA_PAW', 'LDA_FHI',
                    'LDA_HGH', 'LDA_PAW', 'LDA_TM']
    paths = [os.path.join(pp_path, dirname) for dirname in dirname_list]
    # 将路径列表拼接成一个字符串
    os.environ['ABINIT_PP_PATH'] = ":".join(paths)
    return

  def install(self):
    """安装:
    conda install -c conda-forge abinit

    # Environment variables
    export ASE_ABINIT_COMMAND="mpirun -np 4 abinit  < PREFIX.files > PREFIX.log"
    PP=${HOME}/abinit-pseudopotentials-2
    export ABINIT_PP_PATH=$PP/LDA_FHI
    export ABINIT_PP_PATH=$PP/GGA_FHI:$ABINIT_PP_PATH
    export ABINIT_PP_PATH=$PP/LDA_HGH:$ABINIT_PP_PATH
    export ABINIT_PP_PATH=$PP/LDA_PAW:$ABINIT_PP_PATH
    export ABINIT_PP_PATH=$PP/LDA_TM:$ABINIT_PP_PATH
    export ABINIT_PP_PATH=$PP/GGA_FHI:$ABINIT_PP_PATH
    export ABINIT_PP_PATH=$PP/GGA_HGHK:$ABINIT_PP_PATH
    export ABINIT_PP_PATH=$PP/GGA_PAW:$ABINIT_PP_PATH

    # Pseudopotentials
    Pseudopotentials in the ABINIT format are available on the pseudopotentials website. A database of user contributed pseudopotentials is also available there. url ='https://www.abinit.org/downloads/atomic-data-files'

    The best potentials are gathered into the so called JTH archive, in the PAW/XML format, specified by GPAW. You should then add the correct path to ABINIT_PP_PATH:

    ABINIT_PP_PATH=$PP/GGA_PBE:$ABINIT_PP_PATH
    ABINIT_PP_PATH=$PP/LDA_PW:$ABINIT_PP_PATH
    At execution, you can select the potential database to use with the pps argument, as one of ‘fhi’, ‘hgh’, ‘hgh.sc’, ‘hgh.k’, ‘tm’, ‘paw’, 'pawxml'.
    """
    pass

  def example(self,):
    # 有错误以后再说
    import ase
    import ase.build
    os.environ['ASE_ABINIT_COMMAND'] = f"abinit < PREFIX.files > PREFIX.log"
    os.environ['ABINIT_PP_PATH'] = '/Users/wangjinlong/opt/anaconda3/envs/abinit/share/abinit/pseudopotentials'

    atoms = ase.build.molecule('H2O',)
    atoms.center(5)
    atoms.pbc = True

    from ase.calculators.abinit import Abinit
    calc = Abinit(ecut=300, xc='LDA', kpts=(1, 1, 1))
    # calc = Abinit(ecut=300,kpts=(1,1,1),pps='psp8',xc='LDA')

    atoms.calc = calc
    e = atoms.get_potential_energy()
    print(e)
