import os


class MacLearn():
  def __init__(self) -> None:
    pass

  def brew_instlal(self):
    """https://blog.csdn.net/wxb880114/article/details/141102293
    """
    pass

  def usb_insert(self):
    """#/bin/bash!
    #---对于NTFS格式的U盘，mac系统不识别所以只能读，可以通过下面的办法操作，或者直接将U盘格式化为ext_FAT格式，这样win和mac都可以读写
    #---命令解释参考/Users/wangjinlong/my_linux/soft_learn/mac_learn/usb_read_only-办法.txt
    if [ -n "$1" ] 
    then
    echo "OK"
    else 
    echo "用法: $0	 加一个参数(文件名)" 
    exit 0
    fi
    filename=$1
    echo $filename

    disk_name=$(df -h |grep "$filename" |awk '{print $1}') #磁盘名
    echo $disk_name    # diskname=/dev/disk41
    sudo umount $filename #卸载之前挂载的目录
    if [ -d "/Volumes/my_u"  ]; then echo "OK";else sudo mkdir /Volumes/my_u; fi #建立my_u目录
    sudo mount_ntfs -o rw,nobrowse $disk_name /Volumes/my_u #将磁盘以可读写的方式挂载在my_u目录下

    #hdiutil eject /Volumes/EFI #拔出U盘之前的操作
    """

  def brew(self):
    # 以下是重新安装 libxc 时从源码编译的方法：
    'brew reinstall --build-from-source libxc'

    # 使用国内镜像
    # 更改 Homebrew 的源：
    # 将 Homebrew 的默认源更改为国内镜像，例如中科大或清华大学的镜像，以加快下载速度。你可以通过以下命令来更改源：
    # 更换 Homebrew 源为中科大镜像
    'git - C "$(brew --repo)" remote set-url origin https: // mirrors.ustc.edu.cn/brew.git'

    # 更换 Homebrew Core 为中科大镜像
    'git - C "$(brew --repo homebrew/core)" remote set-url origin https: // mirrors.ustc.edu.cn/homebrew-core.git'

    # 更换 Homebrew Bottles 为中科大镜像
    """echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles' >> ~/.zshrc"""
    'source ~/.zshrc'
    # 清理 Homebrew 缓存：
    'brew cleanup'
    # 更新 Homebrew：
    'brew update'
    # 重装软件包：
    'brew reinstall --build-from-source libxc'
    pass

  def brew_source(self, zkd, tuna):
    s1 = """
git -C "$(brew --repo)" remote set-url origin https://mirrors.ustc.edu.cn/brew.git
git -C "$(brew --repo homebrew/core)" remote set-url origin https://mirrors.ustc.edu.cn/homebrew-core.git
git -C "$(brew --repo homebrew/cask)" remote set-url origin https://mirrors.ustc.edu.cn/homebrew-cask.git
echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles' >> ~/.zshrc
source ~/.zshrc
    """

    s2 = """
git -C "$(brew --repo)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git
git -C "$(brew --repo homebrew/core)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git
git -C "$(brew --repo homebrew/cask)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask.git
echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles' >> ~/.zshrc
source ~/.zshrc
    """
    if tuna:
      os.system(s1)
    if zkd:
      os.system(s2)

  def test_source(self):
    s = """
time brew update
time brew install wget
        """

  def unuse_passwd(self,):
    self.LinuxLearn.ssh_none_passwd()
    return None
