import os


class VmwareFusionLearn():
  def __init__(self) -> None:
    pass

  def install_win11(self):
    """https://blog.csdn.net/weixin_52799373/article/details/129658881?spm=1001.2101.3001.6650.3&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ECtr-3-129658881-blog-131996051.235%5Ev43%5Epc_blog_bottom_relevance_base8&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ECtr-3-129658881-blog-131996051.235%5Ev43%5Epc_blog_bottom_relevance_base8&utm_relevant_index=4
    很详细的指导 

    # fn + shift + F10 
    # 安装vmtools 后才可以联网
    """
    pass 

  def share_folder(self,):
    d_home = os.environ['HOME']
    dname_shared = 'wangjinlong'  # 共享的目录名
    # 启动虚拟机后, 虚拟机-> 共享 -> 启用共享文件夹 -> 取消再选中即可 # 注意是最上面那个而不是下面的文件夹
    s1 = f'/mnt/hgfs/{dname_shared}'
    s2 = f'ln -s {s1} {d_home}'
    # os.system(s2)  # 即可

  def vmware_硬盘扩容(self,):
    print('关闭要修改的系统, 然后首先在vmware 设置里面选择硬盘, 扩展到需要的容量')
    # 查看分区 nvme0n1p1 nvme0n1p2 nvme0n1p3 那么 nvme0n1 是那块硬盘
    os.system('sudo fdisk -l')
    os.system('sudo fdisk /dev/nvme0n1')
    print('查看帮助信息: d 删掉要扩容的分区, n 新建一个分区, 注意不要去掉已有的标签选择 N, 重启')
    print('如果要增加swap分区, t 新建分区后还要修改其标签, swap, 或者使用swap对应的 ID')
    os.system('df -h')  # 看到系统还没识别
    os.system('sudo resize2fs /dev/nvme0n1p2')  # 这是要扩容的分区 nvme0n1p2
    os.system('df -h')  # 看到系统识别后的分区大小
    return None 