"""
Copyright 2025 IsBenben

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations
import tkinter as tk
from fractions import Fraction
import textwrap

FONT = ('新宋体', 18)
SPAD = 5
BPAD = 10

def exactly_divide(a, b):
    remainder = []
    res = []
    t = a % b
    while str(t) not in remainder:
        remainder.append(str(t))
        t *= 10
        res.append(str(t // b))
        t %= b

    return (
        str(a // b),
        ''.join(res[:remainder.index(str(t))]),
        ''.join(res[remainder.index(str(t)) - len(remainder):]),
    )

class PolynomialMode:
    LATEX = 1
    DECIMAL = 2

class Polynomial:
    def __init__(self, coefficient):
        if not coefficient:
            coefficient = [0]
        coefficient = [Fraction(a) for a in coefficient]
        while len(coefficient) > 1 and coefficient[-1] == 0:
            coefficient.pop()
        self.coefficient = coefficient
    
    @property
    def n(self):  # 次数
        return len(self.coefficient) - 1

    def __call__(self, x):
        value = Fraction(0)
        for i, a in enumerate(self.coefficient):
            value += a * x ** i
        return value
    
    def to_string(self, mode: int = PolynomialMode.DECIMAL):
        result = 'f(x)='
        for i, a in reversed(list(enumerate(self.coefficient))):
            if a == 0:
                continue
            if a > 0 and i != self.n:
                result += '+'
            if a < 0:
                result += '-'
            if abs(a) != 1 or i == 0:
                absolute = abs(a)
                if mode == PolynomialMode.LATEX:
                    if absolute.denominator == 1:
                        string = f'{absolute.numerator}'
                    else:
                        string = f'\\frac{{{absolute.numerator}}}{{{absolute.denominator}}}'
                elif mode == PolynomialMode.DECIMAL:
                    a, b, c = exactly_divide(absolute.numerator, absolute.denominator)
                    if c == '0':
                        if b == '':
                            string = f'{a}'
                        else:
                            string = f'{a}.{b}'
                    else:
                        if len(c) <= 2:
                            string = f'{a}.{b}{c}{c}{c}…'
                        else:
                            string = f'{a}.{b}{c}{c}…'
                result += string
            if i >= 2:
                if mode == PolynomialMode.LATEX:
                    if i < 10:
                        string = f'x^{i}'
                    else:
                        string = f'x^{{{i}}}'
                elif mode == PolynomialMode.DECIMAL:
                    string = f'x^{i}'
                result += string
            if i == 1:
                result += 'x'
        return result
    
    def __add__(self, other: Polynomial):
        max_n = max(self.n, other.n)
        result = [Fraction(0) for _ in range(max_n + 1)]
        for i, a in enumerate(self.coefficient):
            result[i] += a
        for j, b in enumerate(other.coefficient):
            result[j] += b
        return Polynomial(result)
    
    def __mul__(self, other: Polynomial):
        result = [Fraction(0) for _ in range(self.n + other.n + 1)]
        for i, a in enumerate(self.coefficient):
            for j, b in enumerate(other.coefficient):
                result[i + j] += a * b
        return Polynomial(result)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('找规律')
        self.resizable(False, False)

        title_label = tk.Label(self, text='《找规律》', font=FONT)
        self.patterns_list = tk.Listbox(self, font=FONT, width=40, height=5)
        self.patterns: list[tuple[Fraction, Fraction]] = []
        self.patterns_str: list[tuple[str, str]] = []
        input_box = tk.Frame(self)
        self.index_var = tk.StringVar(self)
        index_label = tk.Label(input_box, text='数列的第', font=FONT)
        self.index_entry = tk.Entry(input_box, font=FONT, width=5, textvariable=self.index_var)
        self.value_var = tk.StringVar(self)
        value_label = tk.Label(input_box, text='项的值是', font=FONT)
        value_entry = tk.Entry(input_box, font=FONT, width=5, textvariable=self.value_var)
        add_button = tk.Button(input_box, text='添加/删除', font=FONT, command=self.edit_pattern)
        self.result = tk.Text(self, font=FONT, height=8, width=40, state=tk.DISABLED)
        mode_box = tk.Frame(self)
        self.mode_var = tk.IntVar(self, PolynomialMode.DECIMAL)
        latex_button = tk.Radiobutton(mode_box, text='LaTeX', font=FONT, value=PolynomialMode.LATEX, variable=self.mode_var)
        calculate_button = tk.Button(mode_box, text='确定', font=FONT, command=self.calculate, padx=BPAD)
        decimal_button = tk.Radiobutton(mode_box, text='Decimal', font=FONT, value=PolynomialMode.DECIMAL, variable=self.mode_var)

        self.patterns_list.bind('<Delete>', lambda e: self.edit_pattern())
        self.index_entry.bind('<Return>', lambda e: self.edit_pattern())
        value_entry.bind('<Return>', lambda e: self.edit_pattern())
        self.result.config(state=tk.NORMAL)
        self.result.insert(tk.END, textwrap.dedent('''\
            操作说明：
            输入项数、项值，点击“添加/删除”（Enter）按钮添加数列规律。
            在列表中选中某项，点击“添加/删除”（Delete）按钮删除数列规律。
            点击确定按钮，开始找规律。
            这里会显示结果。
        '''))
        self.result.config(state=tk.DISABLED)

        title_label.pack(pady=BPAD)
        self.patterns_list.pack(pady=BPAD)
        index_label.pack(side=tk.LEFT, padx=SPAD)
        self.index_entry.pack(side=tk.LEFT, padx=SPAD)
        value_label.pack(side=tk.LEFT, padx=SPAD)
        value_entry.pack(side=tk.LEFT, padx=SPAD)
        add_button.pack(side=tk.LEFT, padx=SPAD)
        input_box.pack(pady=BPAD)
        latex_button.pack(side=tk.LEFT, padx=SPAD)
        calculate_button.pack(side=tk.LEFT, padx=SPAD)
        decimal_button.pack(side=tk.LEFT, padx=SPAD)
        mode_box.pack(pady=BPAD)
        self.result.pack(pady=BPAD)
    
    def edit_pattern(self):
        if self.patterns_list.curselection():
            # 删除选中的项目
            index = self.patterns_list.curselection()[0]
            self.patterns_list.delete(index)
            self.patterns.pop(index)
            self.patterns_str.pop(index)
        else:
            # 添加项目
            try:
                index_str = self.index_var.get()
                index = Fraction(index_str)
                for i, (index2, value) in enumerate(self.patterns):
                    if index == index2:
                        self.patterns_list.delete(i)
                        self.patterns.pop(i)
                        self.patterns_str.pop(i)
                        break
            except ValueError:
                index_str = '0'
                index = Fraction(0)
            try:
                value_str = self.value_var.get()
                value = Fraction(value_str)
            except ValueError:
                value_str = '0'
                value = Fraction(0)
            self.index_var.set('')
            self.value_var.set('')
            pattern = f'数列的第{index_str}项的值是{value_str}'
            self.patterns_list.insert(tk.END, pattern)
            self.patterns.append((index, value))
            self.patterns_str.append((index_str, value_str))
            self.index_entry.focus()
    
    def calculate(self):
        self.result.config(state=tk.NORMAL)
        self.result.delete(1.0, tk.END)
        if not self.patterns:
            self.result.insert(tk.END, '请先添加数列规律。')
        else:
            mode = self.mode_var.get()
            result = Polynomial([])
            for index, value in self.patterns:
                sub_result = Polynomial([value])
                coefficient = Fraction(1)
                for index2, value2 in self.patterns:
                    if index2 != index:
                        # *(index2-x)
                        sub_result *= Polynomial([index2, -1])
                        coefficient *= index2 - index
                sub_result *= Polynomial([1 / coefficient])
                result += sub_result
            
            patterns_str = ''
            for index, value in self.patterns:
                assert result(index) == value
            for index_str, value_str in self.patterns_str:
                if mode == PolynomialMode.LATEX:
                    patterns_str += f'\n- $f({index_str})={value_str}$'
                else:
                    patterns_str += f'\n- f({index_str})={value_str}'
            patterns_str = textwrap.indent(patterns_str, '                    ')

            if mode == PolynomialMode.LATEX:
                self.result.insert(tk.END, textwrap.dedent(f'''\
                    容易注意到多项式函数：
                    $$
                    {result.to_string(mode)}
                    $$
                    满足{patterns_str}
                    '''))
            else:
                self.result.insert(tk.END, textwrap.dedent(f'''\
                    容易注意到多项式函数：
                    {result.to_string(mode)}
                    满足{patterns_str}
                    '''))
        self.result.config(state=tk.DISABLED)

if __name__ == '__main__':
    root = MainWindow()
    root.mainloop()
