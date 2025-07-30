import sys
import getopt

# 1. 导入模块

# 取得命令行参数列表  sys.argv
# 其中第1个为脚本的文件名
print(sys.argv)
# 下面的h 是开关选项，o后面需要带一个参数, 
opts, args = getopt.getopt(args=sys.argv[1:], shortopts="ho:", longopts=["help", "output="])
print('opts=', opts)
print('args=', args)

# 　第三步主要是对分析出的参数进行判断是否存在，然后再进一步处理。主要的处理模式为：
for o, a in opts:
    if o in ("-h", "--help"):
        print("用法为...")
        sys.exit()
    if o in ("-o", "--output"):
        output = a
print(f"output={output}")
