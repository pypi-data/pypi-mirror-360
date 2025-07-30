import paramiko


class ParamikoLearn():
  def __init__(self):
    """paramiko 是 Fabric 的基础 
    """
    pass

  def install(self):
    string = """conda install paramiko
    """
    print(string)
    return None

  def connect(self):
    # 创建 SSHClient 对象
    client = paramiko.SSHClient()

    # 自动添加主机密钥
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 尝试连接，禁用 banner
    client.connect(hostname='hfeshell.nscc-hf.cn',
                   username='wangjl',
                   port=65062,)
    return client
