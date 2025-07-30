
# 如何一条命令将Python脚本打包成可执行程序

> Python是一个脚本语言，被解释器解释执行。它的发布方式：
.py 文件：对于开源项目或者源码没那么重要的，直接提供源码，需要使用者自行安装Python并且安装依赖的各种库。(Python官方的各种安装包就是这样做的)
.pyc 文件：有些公司或个人因为机密或者各种原因，不愿意源码被运行者看到，可以使用 pyc 文件发布，pyc 文件是 Python 解释器可以识别的二进制码，故发布后也是跨平台的，需要使用者安装相应版本的Python 和依赖库。
可执行文件：对于非码农用户或者一些小白用户，你让他装个 Python 同时还要折腾一堆依赖库，那简直是个灾难。对于此类用户，最简单的方式就是提供一个可执行文件，只需要把用法告诉 Ta 即可。比较麻烦的是需要针对不同平台需要打包不同的可执行文件(Windows,Linux,Mac,...)。
本文主要就是介绍最后一种方式，.py 和 .pyc 都比较简单，Python 本身就可以搞定。将 Python脚 本打包成可执行文件有多种方式，本文重点介绍 PyInstaller，其它仅作比较和参考。
————————————————
版权声明：本文为CSDN博主「AI悦创」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：<https://blog.csdn.net/qq_33254766/article/details/117923639>

## 一、简介

Python 中引入了许多 module，发送给其他人或在其他电脑运行时，提示找不到 module。这种情况应该如何解决呢，一种方法就是安装缺失的 module；另一种方法就是将 Python 文件打包成可执行文件。 作者：源码被猫吃了 <https://www.bilibili.com/read/cv17120413> 出处：bilibili

> 1 可执行文件是什么
可执行文件是什么呢？和具体的操作系统有关。
Linux 下可执行文件是 ELF 格式，可以通过 file命令打印可执行文件的信息。
比如  file /user/bin/ls 提示如下信息。
/usr/bin/ls: ELF 64-bit LSB shared object, x86-64
上面结果就是说 /usr/bin/ls 文件时一个 ELF 64 位文件，可以在体系结构 x86-64 的电脑上运行。
Windows 下的可执行文件格式是 PE 格式，一般这类文件拓展名以 .exe 结尾。

将python打包成可执行程序有好多办法，如pyinstaller、py2exe、cx_Freeze等等，这里主要介绍Pyinstaller的使用，pyinstaller可以在Windows、Linux、Mac OS X 等操作系统下将 Python 源文件打包成可执行程序，打包好的程序可以在没有安装python的环境中运行。

## 二、基本使用

### 安装

pip install pyinstaller 或 pip3 install pyinstaller

* 安装成功后，就可以使用下面的命令了：
  * pyinstaller : 打包可执行文件的主要命令，详细用法下面会介绍。
  * pyi-archive_viewer : 查看可执行包里面的文件列表。
  * pyi-bindepend : 查看可执行文件依赖的动态库(.so或.dll文件)
  * pyi-... : 等等。

### 用法

1. 语法：pyinstaller 应用程序
eg：pyinstaller Hello.py
2. 语法：pyinstaller -F 应用程序
eg：pyinstaller -F Hello.py
3. pyinstaller注意事项

> 虽然扩平台，但是pyinstaller也只能在当前操作系统中运行，比如你用mac只能打包出mac上的可执行脚本，要是你想打包出windwos电脑上的可执行程序，你就要用windows执行打包命令。
如果你的脚本文件中包含其他脚本，比如hello.py包含自定义脚本(world.py)或是系统脚本(sys.py)：则需要在打包的时候加上其他脚本的路径。
通过-p指定第三方包的路径，一条路径对应一个-p
eg：pyinstaller -F -p C:\SystemLib\site-packages -p C:\MyLib Hello.py
执行一次打包命令通常会生成两个目录一个附件，分别是build、dist、和xx.spec。build是编译过程中的中间产物，dist是最终可执行程序目录，spec文件是类似缓存，如果你第二次打包，则需要先把spec删掉，否则第二次打包会受影响。

### 参数介绍

常用的主要是-F、-p、-i、-w这几个参数。

```shell

-a：不包含编码.在支持Unicode的python版本上默认包含所有的编码
-c：使用控制台子系统执行(默认)(只对Windows有效)
-d：产生debug版本的可执行文件
-i：指定打包程序使用的图标（icon）文件
-F：打包成可执行程序: dist 下面只有一个可执行文件, 否则dist 下面有一堆文件，各种都动态库文件和 myscrip 可执行文件
-h：查看帮助
-p：添加使用的第三方库路径
-v：查看 PyInstaller 版本
-w：取消控制台显示（默认是显示控制台的）
```

举一个我在使用过程中的例子：

```shell
pyinstaller -F -p C:\SystemLib\site-packages -p C:\MyLib main.py -i C:\image\excel.ico
```

解释：
打包 main.py 脚本
main.py包含第三方脚本，一个是系统脚本，一个是自定义脚本
设置可执行程序的图标为excel.ico

## 在example 中的终端执行命令

```shell
pyinstaller -F -p /Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages muchong_hongbao.py -i jp.ico
pyinstaller -F /Users/wangjinlong/my_script/sci_research/lmp_use/tobedelete/read_restart.py

```

## 4. PyInstaller 的原理简介

PyInstaller 其实就是把python解析器和你自己的脚本打包成一个可执行的文件，和编译成真正的机器码完全是两回事，所以千万不要指望成打包成一个可执行文件会提高运行效率，相反可能会降低运行效率，好处就是在运行者的机器上不用安装python和你的脚本依赖的库。在Linux操作系统下，它主要用的binutil工具包里面的ldd和objdump命令。

PyInstaller输入你指定的的脚本，首先分析脚本所依赖的其他脚本，然后去查找，复制，把所有相关的脚本收集起来，包括Python解析器，然后把这些文件放在一个目录下，或者打包进一个可执行文件里面。

可以直接发布输出的整个文件夹里面的文件，或者生成的可执行文件。你只需要告诉用户，你的应用App是自我包含的，不需要安装其他包，或某个版本的Python，就可以直接运行了。

需要注意的是，PyInstaller打包的执行文件，只能在和打包机器系统同样的环境下。也就是说，不具备可移植性，若需要在不同系统上运行，就必须针对该平台进行打包。
————————————————
版权声明：本文为CSDN博主「AI悦创」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：<https://blog.csdn.net/qq_33254766/article/details/117923639>

## 打包的步骤

![Alt text](image.png)
