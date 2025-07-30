# 可以用来解析命令行
import sys 
argv = sys.argv  # parse command line
# if len(argv) != 2:
#   print("Syntax: simple.py in.lammps")
#   sys.exit()

print(f"命令行的第1个参数为: {sys.argv[1]}")
print(f"命令行的第2个参数为: {sys.argv[2]}")
