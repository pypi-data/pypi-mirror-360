import os


class JmolLearn():
  def __init__(self) -> None:
    """learn: https://wiki.jmol.org/index.php/Jmol_Application

    """
    pass

  def view(self, fname='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/PN_codoping_sub/O2H_P_N0_graphene/single_point/CHG', save=False, fname_fig=None):
    cmd = f'java -jar /Users/wangjinlong/my_linux/software/jmol-16.2.1/Jmol.jar {fname} -s /Users/wangjinlong/my_linux/soft_learn/jmol_learn/jmol_sets.spt'
    if save:
      fname_fig = fname_fig if fname_fig else fname+'.png'
      cmd += f' -q100 -w PNG:{fname_fig}'
    os.popen(cmd=cmd)
    pass
