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
    out = map(lambda x: f'printf("%d\\n", {x});', res)
    with open('out_sort.cpp', 'w') as f:
        f.write('#include <bits/stdc++.h>\nusing namespace std;\nint main () {\n\nfreopen("out_sort.txt", "w", stdout);\n')
        f.write('\n'.join(out) + '\nreturn 0;\n\n}\n')
        # f.write('import sys; sys.stdout = open("sort.txt", "w");\n' + '\n'.join(out) + '\n')
    print('编译输出文件为out_sort.cpp')

if __name__ == '__main__':
    compile()
