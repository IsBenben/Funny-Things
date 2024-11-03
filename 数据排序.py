# 114514 语言 + Python
# AI 协作：无

# 114514 语言编译器：
def compile():
    name = input('请输入txt文件路径作为源代码：')
    with open(name, 'r') as f:
        code = f.read()
    lines = code.splitlines()
    nums = list(map(int, lines))
    res = sorted(nums)
    out = map(lambda x: str(x), res)
    with open('out_sort.py', 'w') as f:
        f.write('import sys; sys.stdout = open("sort.txt", "w"); print("""' + '\n'.join(out) + '""")\n')
    print('编译输出文件为out_sort.py')

if __name__ == '__main__':
    compile()
