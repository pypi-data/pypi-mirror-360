import os
import sys
import shutil
import re


class SourceList():
  def __init__(self,
               is_deb_src=False,
               is_pre_released=False,
               release_version='jammy',
               source_name='aliyun',
               filepath_source_list='.'
               ) -> None:
    """ # 弃用
    ubuntu 国内源
    https://mirrors.aliyun.com/ubuntu-ports/ # 这是针对 ARM 架构的镜像站
    https://mirrors.aliyun.com/ubuntu/  # 这是标准镜像站
    Args:
        is_deb_src (bool, optional): _description_. Defaults to False.
        is_pre_released (bool, optional): _description_. Defaults to False.
        release_version (str, optional): _description_. Defaults to 'jammy'.
        source_name (str, optional): _description_. Defaults to 'aliyun'.
    """
    source_url_list = ['https://mirrors.ustc.edu.cn/ubuntu-ports/',
                       'http://mirrors.aliyun.com/ubuntu-ports/',
                       'https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/',
                       'http://mirrors.163.com/ubuntu-ports/',
                       ]
    print(f'source_url_list= {source_url_list}')
    for source_url in source_url_list:
      if source_name in source_url:
        self.source_url = source_url
        break
    self.is_deb_src = is_deb_src
    self.release_version = release_version
    self.is_pre_released = is_pre_released
    self.filepath_source_list = filepath_source_list
    self.filename = f'{self.filepath_source_list}/sources.list.{source_name}'

    pass

  def get_deb_str_list(self,):
    # deb
    release_version_list = list(
        map(lambda v: self.release_version + v, ['', '-security', '-updates', '-backports']))
    assembly = 'main restricted universe multiverse'

    deb_str_list = [
        f'deb {self.source_url} {item} {assembly}' for item in release_version_list]
    pre_released_deb_str = f'deb {self.source_url} {self.release_version}-proposed {assembly}'
    if self.is_pre_released:
      deb_str_list.append(pre_released_deb_str)

    # deb-src
    deb_src_str_list = [deb_str.replace(
        'deb', 'deb-src') for deb_str in deb_str_list]
    return deb_str_list, deb_src_str_list

  def save_file(self, deb_str_list, deb_src_str_list):
    with open(file=self.filename, mode='w') as f:
      for deb_str in deb_str_list:
        f.write(f'{deb_str}\n')
      if self.is_deb_src:
        for deb_src_str in deb_src_str_list:
          f.write(f'{deb_src_str}\n')
      print(f'保存完毕 -> {self.filename}')


class RsyncLearn():
  def __init__(self):
    pass

  def rsync_example(self, pardir='/Users/wangjinlong/job/teach/course_课程/clsjymo_材料设计与模拟/kj_课件/exercise_tmp'):
    """-u, --update 用于更新时间比较晚的文件
    --delete 用于同步时删除目标目录下没有的文档
    -L 会同步软链接的源文件
    --max-size=1m  只同步大小小于1m的文件

    rsync -avzut A-bendi/ B-server/  #不做任何删除，只同步最新的文件
    rsync -avzut --delete B-server/ A-bendi/ #---删除目标目录下没有的

    rsync -avzut --rsh='ssh -p 22' dir_local/ wjl@192.168.1.7:/home/wjl/exercise_tmp/dir_remote/
    """
    print('查看帮助')
    dir_local = os.path.join(pardir, 'dir_local') + '/'
    dir_remote = os.path.join(pardir, 'dir_remote') + '/'
    os.makedirs(name=dir_local,
                exist_ok=True)
    os.makedirs(name=dir_remote,
                exist_ok=True)
    # 上传
    os.system(command=f'rsync -avzut --delete {dir_local} {dir_remote}')
    # 下载
    os.system(command=f'rsync -avzut {dir_remote} {dir_local}')
    # os.system(command="rsync -avzut --rsh='ssh -p 22' dir_local/ wjl@192.168.1.7:/home/wjl/exercise_tmp/dir_remote/")
    # 还可以免密码登陆或者同步文件
    return None

  def rsync_file(self):
    string = """* 同步文件
    - 很好用的一个命令, 主要用来同步本地和服务器上的文件, 备份等等功能
    语法: rsync -avzut SRC DEST, 同步SRC的文件到 DEST, 选项 -avzut 自行百度
    例如下载服务器上的文件: rsync -avzut wjl@192.168.1.7:/home/wjl/my_test/ /Users/wangjinlong/my_test/
    如果你要练习这个例子, 哪些地方需要改呢？
    """
    print(string)
    return None

  def get_rsync_order(self,
                      exclude_key_list=['CHG*', 'AECCAR*', 'WAVECAR'],
                      rsync_pars='--max-size=1m',
                      ):
    """- rsync -avzut --exclude='CHG*' --exclude='WAVECAR' --exclude='vasp_pot' --exclude='AECCAR*' --progress --rsh='ssh -i ~/.ssh/hfeshell.nscc-hf.cn_0703111440_rsa.txt -p 65062' wangjl@hfeshell.nscc-hf.cn:/public/home/wangjl/tmp /Users/wangjinlong/tmp
    - --exclude='*/' 不考虑子目录
    * --max-size=1m  只同步大小小于1m的文件
    """

    exclude_list = []
    for exclude_key in exclude_key_list:
      exclude_list.append(f"--exclude='{exclude_key}'")
    exclude_str = ' '.join(exclude_list)
    end_part = "--exclude='vasp_pot' --progress -e 'ssh -p 65062'"
    rsync_order = f"rsync -avzut {exclude_str} {rsync_pars} {end_part}"

    return rsync_order


class LinuxLearn():
  def __init__(self) -> None:
    """https://www.bilibili.com/video/BV1CZ4y1z741?p=1&vd_source=5ec84b7f759de5474190c5f84b86a564
    """
    self.RsyncLearn = RsyncLearn()
    pass

  def terminal_sets(self):
    string = """* 终端设置
    打开终端, 右键-> Preferences -> unamed -> color-> 选择浅黄底色
    其它设置自己摸索
    """
    print(string)
    return None

  def ssh_login(self):
    string = """* 登陆另一台电脑, 主要用于远程登录服务器
    需要知道另一台电脑的ip地址: ip add show | grep inet |grep -v inet6
    ssh user@ip, 其中user 是用户名,ip 是地址

    """
    print(string)
    return None

  def ssh_login_none_passwd(self,):
    """1. 本地为mac，远程为ubuntu
    2. ssh -p 22 wjl@192.168.13.133 # 第一次输入会有提示是否保存安全登陆，
    输入yes之后在~/.ssh (配置)目录下会有known_hosts文件生成，以后在ssh -p 登陆就不用输入yes了
    3. ssh-keygen 一路回车 会在配置目录下生成id_rsa(私钥) is_rsa.pub(公钥)文件
    4. 执行ssh-copy-id -p 22 user@remote 可以让远端服务器记住我们的公钥，
    其功能其实是，拷贝id_rsa.pub的内容并追加到到远端服务器~/.ssh/authorized_keys 文件中
    5. 以后直接使用ssh的时候就不用输入密码了
    """
    string = """* 免密码ssh 登录
    本地终端执行: ssh-keygen, 一路回车 -> cd ~/.ssh -> 复制本地 id_ed25519.pub 的内容到服务器 ~/.ssh/authorized_keys 中
    再次尝试: ssh wjl@192.168.1.7
    """
    print(string)
    return None

  def common_comands_learn(self):
    string = """* 常用命令学习
    建立目录 make directory: mkdir a1 a2 b1
    建立空文件: touch x1.txt x2.txt y1.txt y2.txt
    查看文件 list: ls -lsh
    进入目录 change directory: cd a1
    移动文件 move: mv ../x1.txt ../x2.txt .
    进入上层目录: cd ..
    再次移动: mv y1.txt y2.txt b1, mv b1 a1
    mkdir my_test; mv a1 a2 my_test; ls
    删除文件 remove: rm my_test/a1/b1/y2.txt, 如果要删除目录: rm -rf my_test/a2
    cd my_test; ls
    查看是否存在某个命令: which tree
    安装软件或者命令: sudo apt install tree, tree 是一个例子也可以是其它软件
    安装拼音输入法: sudo apt install fcitx fcitx-pinyin
    删除软件: sudo apt remove tree
    再次安装: sudo apt install tree
    使用命令: tree, 你看到了什么
    自己去尝试探索学习更有趣有用复杂的命令: if, for, grep, sed, vim, chmod, 随时百度和google, 可以自己记录一下常用的
    """
    print(string)
    return None

  def useful_script(self):
    string = """* 有用的脚本
    cd; vim my_test.sh; 输入i; 键入以下命令:
    mkdir a1 a2 b1
    touch x1.txt x2.txt y1.txt y2.txt
    cd a1
    mv ../x1.txt ../x2.txt .
    cd ..
    mv y1.txt y2.txt b1
    mv b1 a1
    mkdir my_test; mv a1 a2 my_test
    cd my_test; tree # 井号后面为注释, 可以把多行命令写在一行, 间隔符号为';'
    终端执行: rm -rf my_test -> sh my_test.sh, 这里通过把多个命令放在一个文件里面依次执行
    """
    print(string)
    return None

  def if_usage(self,):
    """
      linux if 判断
      UNIX Shell 里面比较字符写法：
      -eq   等于
      -ne    不等于
      -gt    大于-lt    小于-le    小于等于-ge   大于等于
      =    两个字符相等!=    两个字符不等
      -z    空串
      -n    非空串
      无论什么编程语言都离不开条件判断。SHELL也不例外。

      大体的格式如下：
      if list then
      do something here
      elif list then
      do another thing here
      else
      do something else here
      fi

      一个例子：
      #!/bin/sh
      SYSTEM=`uname -s` # 获取操作系统类型，我本地是linux

      if [ $SYSTEM = "Linux" ] ; then # 如果是linux话输出linux字符串
      echo "Linux"
      elif [ $SYSTEM = "FreeBSD" ] ; then
      echo "FreeBSD"
      elif [ $SYSTEM = "Solaris" ] ; then
      echo "Solaris"
      else
      echo "What?"
      fi # 判断结束，以fi结尾

      基本上和其他脚本语言一样。没有太大区别。不过值得注意的是。[]里面的条件判断。说明如下：

      1 字符串判断
      str1 = str2　　　　　当两个串有相同内容、长度时为真
      str1 != str2　　　　 当串str1和str2不等时为真
      -n str1　　　　　　 当串的长度大于0时为真(串非空)
      -z str1　　　　　　　当串的长度为0时为真(空串)
      str1　　　　　　　　当串str1为非空时为真

      2 数字的判断
      int1 -eq int2　　　两数相等为真
      int1 -ne int2　　　两数不等为真
      int1 -gt int2　　　 int1大于int2为真
      int1 -ge int2　　　int1大于等于int2为真
      int1 -lt int2　　　 int1小于int2为真
      int1 -le int2　　　 int1小于等于int2为真

      3 文件相关的if判断条件语句

      -r file　　　　　用户可读为真
      -w file　　　　 用户可写为真
      -x file　　　　　用户可执行为真
      -f file　　　　　文件为正规文件为真
      -d file　　　　　文件为目录为真
      -c file　　　　　文件为字符特殊文件为真
      -b file　　　　　文件为块特殊文件为真
      -s file　　　　　文件大小非0时为真
      -t file　　　　　当文件描述符(默认为1)指定的设备为终端时为真

      3 复杂逻辑判断
      -a 　 　　　　 与
      -o　　　　　　 或
      !　　　　　　　非

      语法虽然简单，但是在SHELL里使用的时候，它可以实现强大的功能或执行逻辑。

      #--- if 语句的注意事项
      1、[ ]表示条件测试。注意这里的空格很重要。要注意在'['后面和']'前面都必须要有空格
      2、在shell中，then和fi是分开的语句。如果要在同一行里面输入，则需要用分号将他们隔开。
      3、注意if判断中对于变量的处理，需要加引号，以免一些不必要的错误。没有加双引号会在一些含空格等的字符串变量判断的时候产生错误。比如[ -n "$var" ]如果var为空会出错
      4、判断是不支持浮点值的
      5、如果只单独使用>或者<号，系统会认为是输出或者输入重定向，虽然结果显示正确，但是其实是错误的，因此要对这些符号进行转意
      6、在默认中，运行if语句中的命令所产生的错误信息仍然出现在脚本的输出结果中
      7、使用-z或者-n来检查长度的时候，没有定义的变量也为0
      8、空变量和没有初始化的变量可能会对shell脚本测试产生灾难性的影响，因此在不确定变量的内容的时候，在测试号前使用-n或者-z测试一下
      9、? 变量包含了之前执行命令的退出状态（最近完成的前台进程）（可以用于检测退出状态）

      #---由于if条件无法判断小数，故需要下面determinant这个变量
      determinant=$(echo |awk '{if('${diff}' < 0.01) {print 1} else {pri    nt 0}}');
      if [ "${determinant}" -eq 1 ]; then loop=$((loop+1));fi
          """
          pass

        def reboot_set(self,):
          """#---Linux定时重启设置
      1，编辑系统的crontab文件
      sudo vim /etc/crontab
      2，在crontab文件里面的run-parts部分加入一行：
      30 13 * * * root init 6
      或者 30 13 * * * root reboot
      3，保存退出 :wq

      #-第二种方法
      1.确保系统安装cron
      sudo apt-get install cron
      2. 开通并开启cronie后台服务，这一步很重要，不开通根本无法运行服务
      sudo systemctl enable cron.service; sudo systemctl start cron.service
      3. sudo crontab -e
      00 00 * * * /sbin/reboot #-推荐
      或者编辑文件 crontab.txt 为 00 00 * * * /sbin/reboot 然后 sudo crontab crontab.txt
      4. 查看 sudo crontab -l

      #---查看服务的运行状态
      方法1. service cron status
      方法2. /etc/init.d/cron status

      # ---Linux终端命令忽略大小写
      1. 新建文件 ~/.inputrc, 添加如下内容
      set completion-ignore-case on
      2. 重新打开终端即可
    """

  def vimrc_set(self, fname='vimrc'):
    default_set_list = ['set nu "显示行号"',
                        ':set hlsearch "搜索结果高亮"',
                        ':set mouse=n "使用鼠标定位"',
                        """au BufReadPost * if line("'\"") > 0|if line("'\"") <= line("$")|exe("norm '\"")|else|exe "norm ',$"|'endif|endif '""",
                        ':set fileformat=unix',
                        ':set ff=unix',
                        '":set cursorline',
                        '"hi CursorLine   cterm=NONE ctermbg=red ctermfg=white guibg=gray guifg=white',
                        'hi comment ctermfg=6',
                        ':set ignorecase ":set invlist "用于显示不可见字符"',
                        'syntax on "进行语法检查，颜色显示"',
                        'set autoindent "自动缩排"',
                        'set backspace=2        "可随时用退格键删除" ',
                        'set showmode "显示左下角的状态栏，默认是显示的"',
                        'set ruler  "显示右下角的状态栏”',
                        '"set all 可以用于显示目前的环境参数设定值"',]

    line_list = ['set nu "显示行号"\n',
                 ':set hlsearch "搜索结果高亮"\n',
                 ':set mouse=n "使用鼠标定位"\n',
                 'au BufReadPost * if line("\'\\"") > 0|if line("\'\\"") <= line("$")|exe("norm \'\\"")|else|exe "norm $"|endif|endif \n',
                 ':set fileformat=unix\n',
                 ':set ff=unix\n',
                 '":set cursorline\n',
                 '"hi CursorLine   cterm=NONE ctermbg=red ctermfg=white guibg=gray guifg=white\n',
                 'hi comment ctermfg=6\n',
                 ':set ignorecase ":set invlist #用于显示不可见字符"\n',
                 'syntax on "进行语法检查，颜色显示"\n',
                 'set autoindent "自动缩排"\n',
                 'set backspace=2        "可随时用退格键删除" \n',
                 'set showmode "显示左下角的状态栏，默认是显示的"\n',
                 'set ruler  "显示右下角的状态栏”\n',
                 '"set all 可以用于显示目前的环境参数设定值"\n']
    with open(fname, mode='w') as f:
      f.writelines(line_list)

  def vim_operation(self,):
    string = r"""
    # ---vim 使用命令
    ':r !command'  # 将shell命令command的结果插入到当前行的下一行
    ':r !date'  # 例如, 读取系统时间并插入到当前行的下一行。

    ':g/^\s*$/d'  # 全部空行
    ':10,20g/^\s*$/d'  # 只删除10-20行之间的空行

    # vim中文乱码问题解决方式: 在.vimrc 中加入如下设置即可
    set_list = ['set fileencodings=utf-8,gb2312,gbk,gb18030',
                'set termencoding=utf-8',
                'set encoding=prc',]
    """
    print(string)
    return None

  def autjump(self,):
    os.system("sudo apt-get install autojump")
    if os.path.exists("/usr/share/autojump/autojump.sh"):
      os.system("source /usr/share/autojump/autojump.sh")
      print("安装成功")
    else:
      print("目录不存在")
      sys.exit()

  def oh_my_zsh(self, is_default_zsh=False):
    self.home_path = os.path.expandvars('$HOME')
    # 1. 安裝
    os.system('sudo apt install zsh -y')
    # 2. 克隆
    os.system('git clone https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh')
    # 增加.zshrc
    zshrc_template_path = f'{self.home_path}/.oh-my-zsh/templates/zshrc.zsh-template'
    zshrc_path = f'{self.home_path}/.zshrc'
    shutil.copyfile(zshrc_template_path, zshrc_path)
    # 修改zsh主题
    with open(file=zshrc_path, mode='r') as f:
      content = f.read()
    new_txt = re.sub(pattern=r'\nZSH_THEME=(.*?)\n',
                     repl='\nZSH_THEME=amuse',
                     string=content)
    with open(file=zshrc_path, mode='w') as f:
      f.write(new_txt)

    # 提示和语法高亮
    os.system(
        f'git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions')
    os.system(
        f'git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting')

    with open(zshrc_path, mode='a') as f:
      f.write('plugins=(zsh-autosuggestions zsh-syntax-highlighting)\n')
      f.write(
          f'source {self.home_path}/.oh-my-zsh/custom/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh\n')
      f.write(
          f'source {self.home_path}/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.plugin.zsh\n')

    # if is_default_zsh:
    #   os.system('chsh -s `which zsh`')
    print('如果要改为默认zsh 终端 请执行: chsh -s `which zsh`')

    os.system(f'source {zshrc_path}')

  def install_glibc(self,):
    """可能还需要安装glibc
      1. 下载地址: <https://www.gnu.org/software/libc/sources.html>
      2. <http://ftp.gnu.org/gnu/glibc/>
      3.
          1. tar  -xzf glibc2.14.tar.gz;
          cd glibc2.17; mkdir build; cd build; ../configure --prefix=/home/你的用户名/opt/glibc2.17; make -j4; make -j8 install;
      1. 将LD_LIBRARY_PATH临时添加到自己的用户变量里（慎重，先看后边2）
          export LD_LIBRARY_PATH=/home/你的用户名/usr/glibc2.14/lib:$LD_LIBRARY_PATH

      2. 下面这个命令可以用来执行python3
      '/home/users/lxiaochun/opt/glibc2.17/lib/ld-2.17.so --library-path /home/users/lxiaochun/opt/glibc2.17/lib:/home/users/lxiaochun/tmp/my_lib64  /home/users/lxiaochun/opt/python3.9.7/bin/python3'
    """

    """
    # cd /lib64
    # LD_PRELOAD=/lib64/libc-2.15.so ln -sf /lib64/libc-2.15.so libc.so.6
    libc-2.15.so
    这个文件名根据你系统中的文件而定，如果有多个版本so文件可以逐个尝试
    原理分析：
    linux调用so的库文件时，搜索路径为当前路径，再是系统lib目录。但是提供了一个LD_PRELOAD系统变量来改变这个顺序。
    设置LD_PRELOAD了后，库加载的顺序就变成这样了：
    LD_PRELOAD —> 当前路径 —> 系统lib目录
    """

    pass

  def roots_notes(self):
    """
      1、开机顺序

      先开存储阵列柜 存储柜开启后5分钟开启IO节点
      开管理节点master 3分钟后

      存储正常后，依次打开计算节点。

      2、关机顺序

      先关计算节点node1-28
      再关管理节点master
      最后关IO节点 阵列柜

      账号密码：
      root 密码 sjh20150211

      # 挂载硬盘
      可以查看sudo vim /etc/rc.local 文件
      或者直接sudo /etc/rc.local 即可

      管理节点：root wuzhou.123456
      IO节点: root wuzhou.123456
      计算节点: root wuzhou.123456

      3.创建用户

      useradd 用户名 passwd 用户名
      输出两次密码

      同步用户 输入：syncusers ##管理员直接输出即可

      su 用户名

      输入：nopasswd  ##开机普通用户免密码登陆功能


      环境变量设置：

      intel 编译器 intelMPI vasp 都安装在/public/apps/下

      普通用户可以参考以下环境：vim ~/.bashrc
      ##intel 2018
      source /public/apps/intel/impi/2018.1.163/bin64/mpivars.sh
      source /public/apps/intel/compilers_and_libraries_2018.1.163/linux/bin/compilervars.sh intel64
      source /public/apps/intel/compilers_and_libraries_2018.1.163/linux/mkl/bin/mklvars.sh intel64

      4 删除用户和目录
      例如：userdel -r zhyh

      检查服务器状态是否正常

      df -h   查看硬盘空间状态
      [root@master software]# df -h
      Filesystem      Size  Used Avail Use% Mounted on
      /dev/sda3       218G   22G  186G  11% /
      devtmpfs         16G     0   16G   0% /dev
      tmpfs            16G     0   16G   0% /dev/shm
      tmpfs            16G   19M   16G   1% /run
      tmpfs            16G     0   16G   0% /sys/fs/cgroup
      /dev/sda1       477M  110M  338M  25% /boot
      110.1.1.11:/wz   22T   29G   22T   1% /public
      tmpfs           3.1G     0  3.1G   0% /run/user/0
      /dev/sdb1       917G  8.5G  862G   1% /backup

      pbsstat 查看计算节点状态与使用情况

      [root@master software]# pbsstat 
      +----------------------------------------------------------------------------------------------+
      | node        | state | load  | pmem  | ncpu |  mem   |  resi  | usrs | tasks | jobids/users   |
      +-------------+-------+-------+-------+------+--------+--------+------+-------+----------------+
      |node01       | free  |  0.00 | 64148 |  36  |  66196 |  627   | 0/0  |   0   |                |
      +-------------+-------+-------+-------+------+--------+--------+------+-------+----------------+
      |node02       | free  |  0.00 | 64148 |  36  |  66196 |  592   | 0/0  |   0   |                |

      内存容量，节点数，任务数，使用账号及节点是否正常运行都可以查看

      故障排查

      pbsstat 命令输入后发现有节点down

      1、管理节点ssh 节点编号 查看节点是否还正常运行，如不能ssh ，需要机房重启服务器。重启后不能ssh ，需接显示器查看节点运作状态。
      2、如能ssh 到计算节点 可能是pbs_mom 服务卡死，手动重启一次计算节点的pbs_mom 服务即可 (root 用户在down节点内使用pbs_mom命令）
      3、定期查看存储1，存储2 硬盘状态。显示红色灯级掉盘，发出刺耳的蜂鸣声也是有问题。

      售后服务器

      拨打我司 400 号售后热线，并提供相应的服务器系列号即可。
      软件问题与集群系统使用出现排队或者任务提交不上的情况，可直接联系我这边。

      修改用户使用资源
      vim /usr/local/maui/maui.cfg 打开后修改参数USERCFG[DEFAULT]  MAXNODE=7 MAXPROC=252
      最后重启maui服务service maui restart


      查看节点列表
      cat /etc/hosts

      进入gpu #cat /etc/hosts 查看节点列表
      ssh gpu1 可以进去gpu

      对胖节点的管理（@compuphys)
      胖节点显示器连接在6显示下；
      ifconfig -a 查看网线接口
      root用户下 ethtool eth0 可以确定网线就是插在eth0接口上面
      ifconfig eth0 10.1.1.98 up 可以将eth0的ip设置为10.1.1.98
      vim /etc/rc.local 打开后写入 上一条命令可以将上命令在每次开机进行设置
      进入管理节点（@master）
      以后在管理节点下使用命令ssh wjl@10.1.1.98就可以进入胖节点的wjl用户
      root用户下vim /etc/hosts 写入10.1.1.98 pang
      之后在管理节点下使用命令ssh wjl@pang就可以进入胖节点的wjl用户

      屏幕锁：账号秘密都是八个0.
      查看所有人任务还可以用showq命令

      #---material studio
      ./etc/init.d/msgateway_control_18888 restart

      #---PBS(torque)
      1、修改/var/spool/torque/server_priv/目录下的nodes文件
      Node1 np=16 gpus=4
      Node2 np=16 gpus=4
      ...
      其中Node1为计算节点名字，np为逻辑核数，gpus为显卡数
      该文件给出了计算集群的最大可用资源

      2、 重新启动pbs
      \#service pbs_mom restart
      \#service pbs_server restart
      \#service pbs_sched restart
      #  service trqauthd restart
      注意要按照顺序重启服务
      [root@master ~]# which pbs_mom
      /opt/torque/sbin/pbs_mom

      qdel -p 15220 使用root账户可以杀死原先杀不死的任务.
      qmgr -c 'print server'  // 查看默认配置的服务和队列
      修改方式
      sudo qmgr -c 'set queue batch max_running = 2'  // 最多同时运行2个作业

      #--开启向日葵
      #root 用户下/root/sunloginclient 是安装软件
      #---记住一点，如果远程登录不了，很有可能是由于没连上外网
      #安装在/usr/local/sunlogin
      #/usr/local/sunlogin  ./start.sh 即可 或者先./stop.sh 再开启
      service xrdp restart 执行此命令后才可以用于mstsc win10下面的远程桌面控制
      #---重启网络可以输入 
      #service network restart 或者 /etc/rc.d/init.d/network restart 
    """
    pass
