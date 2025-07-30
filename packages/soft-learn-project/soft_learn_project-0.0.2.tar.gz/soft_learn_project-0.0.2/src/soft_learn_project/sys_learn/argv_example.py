import sys

print("请输入你的姓名:")
name = sys.stdin.readline()
print(f"输入的名字为->{name}")

print(sys.argv)

# python3 argv_example.py -n wjl --name=wjll