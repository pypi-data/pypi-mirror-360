class WinSublinux():
  def __init__(self) -> None:

    pass

  def x(self):
    """
      #--如何录屏？首先保证电脑插着带语音的耳机然后打开录屏软件如下操作win+alt+R即可
      #--win10有自带的录屏软件
      win+alt+G启动 
      win+alt+R 运行和停止 录屏效果很好不会有其他干扰

      #--win linux subsystem 子系统重启命令
      以管理员身份运行cmd 然后里面输入：
      net stop lxssmanager
      net start lxssmanager
      #或者 Win+R  输入services.msc 找到lxssmanager服务然后鼠标右键选择重启

      #--开启xrdp Linux子系统的图形界面 然后使用远程桌面连接 进行连接
      #sudo sed -i 's/port=3389/port=3390/g' /etc/xrdp/xrdp.ini
      #sudo echo xfce4-session > ~/.xsession
      sudo service xrdp restart

      #2.1. 安装 xming
      #没什么特殊的，下载安装，打开就行。
      #地址：https://xming.en.softonic.com/?ex=REG-60.2
      #2.2. 确定 OpenSSH 已经安装
      #在终端执行：sudo apt-get install openssh-server
      #2.3. 配置 DISPLAY 方法运行变量
      #1、打开 ${HOME}/.bashrc 文档，在最后面加入：
      #if [ -d "${HOME}/bin" ] ; then
      #export? PATH="${PATH}:${HOME}/bin"
      #if [ -f "${HOME}/bin/ssh_login" ] ; then
      #. "${HOME}/bin/ssh_login"
      #fi
      #fi
      #2、在 ${HOME}/bin / 文件夹下新增 ssh_login 文件（bin 文件夹没有就新建一个），内容如下：
      #if [ -n "${SSH_CLIENT}" ] ; then
      #if [ -z "${DISPLAY}" ] ; then
      #export DISPLAY='localhost:10'
      #fi
      #fi
      #3、给 ssh_login 文件 777 权限，代码：
      #sudo chmod 777 ${HOME}/bin/ssh_login
      DISPLAY=:0 startxfce4 &
      eg: DISPLAY=:0 xdg-open

      #---根据我的理解只要运行export DISPLAY=:0，然后就可以运行startxfce4 了,前提是xming要打开着,如果打开export DISPLAY=:0,则远程桌面连接看不了图
      #---通过XMing 打开图形窗口
      1. 在自己的程序前添加DISPLAY=:0, e.g. DISPLAY=:0 gnuplot
      2. 或者在.bashrc或者.zshrc 添加
      #XMing display
      export DISPLAY=:0.0
      执行source ~/.zshrc
    """
    pass
