import fabric
import invoke


class FabricLearn():
  def __init__(self):
    """https://docs.fabfile.org/en/latest/getting-started.html
    * Fabric最基本的用途是通过SSH在远程系统上执行shell命令，然后（可选地）查询结果。默认情况下，远程程序的输出直接打印到您的终端，并被捕获。一个基本的例子：

    """
    from py_package_learn.paramiko_learn import paramikoLearn
    self.ParamikoLearn = paramikoLearn.ParamikoLearn()
    pass

  def install(self):
    string = """conda install fabric
    """
    print(string)
    return None

  def operations(self, result):
    result.stdout.strip() == 'Linux'
    result.connection
    result.connection.host

    pass

  def Multiple_actions(self):
    from fabric import SerialGroup as Group
    results = Group('web1', 'web2', 'mac1').run('uname -s')
    print(results)
    for connection, result in results.items():
      print("{0.host}: {1.stdout}".format(connection, result))
    pass

  def myrun(self):
    @fabric.task
    def myrun(c):
      c.run('pwd')

  def serialgroup(self):
    pool = fabric.SerialGroup(
        'wjl@192.168.1.6:22', 'wangjinlong@192.168.1.3:22')
    pool.run('pwd')
    pass

  # ---- 有用的方法
  def get_connetion(self,
                    host='hfeshell.nscc-hf.cn',
                    user='wangjl',
                    port=65062):
    connection = fabric.Connection(host=host,
                                   user=user,
                                   port=port)
    return connection

  def run_command(self, connection: fabric.Connection,
                  shell_command='uname -s'):
    result_obj = connection.run(shell_command)
    return result_obj

  def transfer_file(self,
                    connection: fabric.Connection,
                    fname='a.txt',
                    remote_dir='/public/home/wangjl/'):
    """发送文件到服务器

    Args:
        connection (fabric.Connection): _description_
        fname (str, optional): _description_. Defaults to 'a.txt'.

    Returns:
        _type_: _description_
    """

    result = connection.put(fname, remote=remote_dir)
    print(f"Uploaded {result.local} to {result.remote}")
    return None

  def get_connetion_with_sudo(self):
    config = fabric.Config(overrides={'sudo': {'password': '123456'}})
    c = fabric.Connection(host='192.168.1.6', user='wjl',
                          port=22, config=config)
    # result = c.sudo('whoami', hide='stderr')
    return c

  def test(self):
    c = self.get_connetion()
    result = c.run('ls')
