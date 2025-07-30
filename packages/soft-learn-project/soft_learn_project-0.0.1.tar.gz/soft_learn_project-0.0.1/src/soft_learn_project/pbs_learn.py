import os


class PBS_learn():
  def __init__(self) -> None:
    pass

  def restart(self,):
    # 2、 重新启动pbs 意要按照顺序重启服务
    s1 = 'service pbs_mom restart'
    s2 = 'service pbs_server restart'
    s3 = 'service pbs_sched restart'
    s4 = 'service trqauthd restart'
    # os.popen()

  def check(self):
    s = 'which pbs_mom'
