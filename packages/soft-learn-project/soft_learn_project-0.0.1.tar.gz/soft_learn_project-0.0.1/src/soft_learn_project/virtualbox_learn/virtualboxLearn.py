
class VirtualBoxLearn():
  def __init__(self) -> None:
    pass

  def install(self):
    """
    sudo apt update
    sudo apt install build-essential make perl gcc
    sudo apt install ubuntu-desktop
    """
    url = 'https://blog.csdn.net/qq_62888264/article/details/134299465'
    string = f"""安装教程--> {url}
    如果安装非桌面版还需要--> sudo apt install build-essential make perl gcc ubuntu-desktop
    """
    print(string)
    return None 

  def share_folder(self):
    string = """* 共享文件夹
    更新系统源: sudo apt update
    需要时安装桌面: sudo apt install ubuntu-desktop # or sudo apt install lubuntu-desktop, sudo reboot
    安装必要的命令: sudo apt install make perl build-esential gcc
    安装增强扩展包: 从网上下载-> virtulbox界面->工具 -> 扩展-> 安装, 
    ubutnu->设备-> 安装增强功能 -> 重启, 设备->共享文件夹->共享文件夹->添加-> 选择路径, 挂载点为/mnt/xxx, 勾选自动挂载
    sudo usermod -a -G vboxsf wjl; reboot 
    建立快捷方式: ubuntu终端 -> ln -s /mnt/wangjinlong /home/wjl/wangjinlong  其中我的文件名字为 wangjinlong
    """
    print(string)
    return None

  def mount(self):
    """* 共享文件夹

    1. Device 中设置共享文件夹
    2. sudo mount -t vboxsf Desktop /mnt/Desktop/
    3. ln -s /mnt/Desktop share_desktop #-建立快捷方式
    4. 如果选择了自动挂载则需要：sudo usermod -aG vboxsf <your username>，最后一个参数是你的linux用户名，把你的linux用户加入到vboxsf组。然后重启。
    """
    pass
