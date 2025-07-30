
from fireworks.core.firework import FiretaskBase, Firework, FWAction
import shutil
import fireworks.core.firework


# @fireworks.explicit_serialize
# class ArchiveDirTask(fireworks.core.firework.FiretaskBase):
#   """
#   Wrapper around shutil.make_archive to make tar archives.

#   Args:
#       base_name (str): Name of the file to create.
#       format (str): Optional. one of "zip", "tar", "bztar" or "gztar".
#   """

#   _fw_name = 'ArchiveDirTask'
#   required_params = ["base_name"]
#   optional_params = ["format"]

#   def run_task(self, fw_spec):
#     shutil.make_archive(self["base_name"], format=self.get(
#         "format", "gztar"), root_dir=".")

# 这种方式也可以
"""1. 这个模块需要在Python的搜索路径内, 2. 必须注册您的Firetask, 通过添加 @fireworks.explicit_serialize 装饰器就可以
"""


@fireworks.explicit_serialize
class ArchiveDirTask(fireworks.core.firework.FiretaskBase):
  """ 
  Wrapper around shutil.make_archive to make tar archives.

  Args:
      base_name (str): Name of the file to create.
      format (str): Optional. one of "zip", "tar", "bztar" or "gztar".
  """
  # _fw_name = 'xx_ArchiveDirTask_xx'

  def run_task(self, fw_spec):
    shutil.make_archive(fw_spec["base_name"],
                        format=fw_spec['format'],
                        root_dir=".")
