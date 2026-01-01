"""
Copyright 2024 IsBenben

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

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk, UnidentifiedImageError
import random
import os
import time
import functools

path = os.path.split(__file__)[0]
font_path = os.path.join(path, 'font.ttf')
tk_image = None  # 用于设置预览图片，无实际用途

def find(num, sorted_nums):
    left = 0
    right = len(sorted_nums) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if abs(sorted_nums[mid][0] - num) < abs(sorted_nums[result][0] - num):
            result = mid
        if sorted_nums[mid][0] < num:
            left = mid + 1
        else:
            right = mid - 1

    return result

def resize_image(image, max_size):
    width, height = image.size
    if width > height:
        new_height = round(height * max_size / width)
        new_width = max_size
    else:
        new_width = round(width * max_size / height)
        new_height = max_size
    return image.resize((new_width, new_height))

def open_image(filename, open_message_box=True):
    try:
        image = Image.open(filename)
        return image
    except FileNotFoundError:
        if open_message_box:
            messagebox.showerror('错误：', '图片文件不存在。')
        return None
    except UnidentifiedImageError:
        if open_message_box:
            messagebox.showerror('错误：', '不支持该类型的图片。')
        return None

all_chars = [chr(i) for i in range(0x4e00, 0x9fa5 + 1)] \
            + list('　，。！？：；【】（）《》、ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ＄～｀＃＠％＾＆＊＿＋－＝１２３４５６７８９０．＜＞｛｝｜＼／＇＇＂＂')

def get_text_colors(font_size=8, texts=tuple(all_chars)):
    # 字体
    fnt = ImageFont.truetype(font_path, font_size)

    # 获取文字颜色
    text_colors = {}
    for text in texts:
        image = Image.new('L', (font_size, font_size), 255)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, font=fnt, fill=0)

        # 计算像素点平均颜色
        sum_num = 0
        for y in range(font_size):
            for x in range(font_size):
                sum_num += image.getpixel((x, y))

        avg_num = sum_num / (font_size * font_size * 1.375)
        text_colors.setdefault(avg_num, list()).append(text)

    # 排序颜色 高->低
    sorted_text_colors = sorted(text_colors.items(), key=lambda item: item[0])
    return list(sorted_text_colors)

def open_file(*args, **kwargs):
    try:
        return open(*args, **kwargs)
    except FileNotFoundError:
        return None

def safe_float(value, default=-1.0):
    try:
        return float(value)
    except ValueError:
        return default


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('字符画')
        self.resizable(False, False)

        self.input_frame = ttk.Labelframe(self, text='输入设置')
        self.input_file_preview = ttk.Label(self.input_frame, width=8)
        self.input_file_preview.grid(column=0, row=0, padx=5, pady=5, rowspan=2)
        self.input_select_button = ttk.Button(self.input_frame, text='选择文件', command=self.select_input_file_func)
        self.input_select_button.grid(column=1, row=0, padx=5, pady=5)
        self.input_filename_entry = ttk.Entry(self.input_frame)
        self.input_filename_entry.grid(column=2, row=0, padx=5, pady=5)
        self.input_filename_entry.bind('<Key>', lambda e: self.update_input_file_preview())
        self.input_scale_label = ttk.Label(self.input_frame, text='缩放')
        self.input_scale_label.grid(column=1, row=1, padx=5, pady=5)
        self.input_scale_entry = ttk.Entry(self.input_frame)
        self.input_scale_entry.grid(column=2, row=1, padx=5, pady=5)
        self.input_rotate_label = ttk.Label(self.input_frame, text='旋转')
        self.input_rotate_label.grid(column=1, row=2, padx=5, pady=5)
        self.input_rotate_select = ttk.Combobox(self.input_frame, state='readonly', values=('不进行旋转', '逆时针旋转90°', '180°旋转', '顺时针旋转90°'))
        self.input_rotate_select.current(0)
        self.input_rotate_select.grid(column=2, row=2, padx=5, pady=5)
        self.input_frame.pack(padx=10, pady=10)

        self.output_frame = ttk.Labelframe(self, text='输出设置')
        self.output_select_button = ttk.Button(self.output_frame, text='选择文件', command=self.select_output_file_func)
        self.output_select_button.grid(column=0, row=0, padx=5, pady=5)
        self.output_filename_entry = ttk.Entry(self.output_frame)
        self.output_filename_entry.grid(column=1, row=0, padx=5, pady=5)
        self.output_info = ttk.Label(self.output_frame, text='提示：当文件不存在时会自动创建')
        self.output_info.grid(column=0, row=1, padx=5, pady=5, columnspan=2)
        self.output_frame.pack(padx=10, pady=10)

        self.output_texts_frame = ttk.Labelframe(self.output_frame, text='字符集')
        self.output_texts_var = tk.StringVar(self, 'all')
        self.output_texts_all_radio = ttk.Radiobutton(self.output_texts_frame, text='全部', value='all', variable=self.output_texts_var)
        self.output_texts_all_radio.grid(column=0, row=0, padx=5, pady=5)
        self.output_texts_custom_radio = ttk.Radiobutton(self.output_texts_frame, text='自定义', value='custom', variable=self.output_texts_var)
        self.output_texts_custom_radio.grid(column=1, row=0, padx=5, pady=5)
        self.output_texts_custom_text = tk.Text(self.output_texts_frame, height=5, width=32)
        self.output_texts_custom_text.grid(column=0, row=1, padx=5, pady=5, columnspan=2)
        self.output_texts_info = ttk.Label(self.output_texts_frame, text='提示：建议输入等宽字符')
        self.output_texts_info.grid(column=0, row=2, padx=5, pady=5, columnspan=2)
        self.output_texts_frame.grid(column=0, row=2, padx=5, pady=5, columnspan=2)

        self.start_button = ttk.Button(self, text='开 始', command=self.start_func, width=20, padding=3)
        self.start_button.pack(padx=10, pady=10)
        self.process = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=330, mode='determinate')

    def select_input_file_func(self):
        filename = filedialog.askopenfilename(filetypes=[('图片文件', '*.bmp *.jpg *.jpeg *.png *.webp'), ('所有文件', '*.*')])

        if filename:
            self.input_filename_entry.delete(0, tk.END)
            self.update_input_file_preview(True, os.path.join(path, filename))

    def select_output_file_func(self):
        filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('所有文件', '*.*'), ('文本文件', '*.txt')])
        if filename:
            self.output_filename_entry.delete(0, tk.END)
            self.output_filename_entry.insert(0, filename)

    def update_input_file_preview(self, open_message_box=False, filename_=None):
        def _inner():
            global tk_image
            nonlocal filename_

            filename = filename_ or self.input_filename_entry.get()
            image = open_image(os.path.join(path, filename), open_message_box)
            if image:
                tk_image = ImageTk.PhotoImage(resize_image(image, 64))
                self.input_file_preview.config(image=tk_image)
                if filename_:
                    self.input_filename_entry.insert(0, filename_)
            else:
                self.input_file_preview.config(image='')
        self.after('idle', _inner)

    def toggle_state(self, state):
        self.input_select_button.config(state=state)
        self.input_filename_entry.config(state=state)
        self.input_scale_entry.config(state=state)
        self.output_select_button.config(state=state)
        self.output_filename_entry.config(state=state)
        self.output_texts_all_radio.config(state=state)
        self.output_texts_custom_radio.config(state=state)
        self.output_texts_custom_text.config(state=state)
        self.start_button.config(state=state)
        self.update()

    def start_func(self):
        start = time.time()
        self.start_button.config(text='请稍等……')
        self.input_rotate_select.config(state='disabled')
        self.process.config(value=0)  # 清空上次的进度
        self.process.pack(padx=10, pady=10)
        self.toggle_state(tk.DISABLED)

        in_file = self.input_filename_entry.get()
        out_file = self.output_filename_entry.get()

        image = open_image(os.path.join(path, in_file))
        if not image:
            self.end_func()
            return None

        f = open_file(os.path.join(path, out_file), 'w', encoding='utf-8')
        if not f:
            self.end_func()
            messagebox.showerror('错误', '未选择输出文件！')
            return None

        # 获取文字颜色
        if self.output_texts_var.get() == 'all':
            sorted_text_colors = get_text_colors()
        else:
            texts_custom_text_value = self.output_texts_custom_text.get(0.0, tk.END)
            texts = tuple(set(texts_custom_text_value.replace('\n', '').replace('\r', '')))
            if not texts:
                self.end_func()
                messagebox.showerror('错误', '请输入自定义的文字！')
                return None
            sorted_text_colors = get_text_colors(texts=texts)

        # 预处理图片
        scale = safe_float(self.input_scale_entry.get(), 1.0)
        rotate = self.input_rotate_select.current() * 90

        rgb_image = image.convert('RGB')
        rotated_image = rgb_image.rotate(rotate, expand=True)
        rotated_image_w, rotated_image_h = rotated_image.size
        resized_image = rotated_image.resize((
            max(round(rotated_image_w * scale), 1),
            max(round(rotated_image_h / 1.375 * scale), 1)
        ))
        resized_w, resized_h = resized_image.size

        @functools.lru_cache(maxsize=1024)
        def cached_find(num):
            return find(num, sorted_text_colors)

        # 开始转换
        sum_count = resized_w * resized_h
        self.process.configure(maximum=sum_count)
        processed_count = 0
        for y in range(resized_h):
            for x in range(resized_w):
                r_num, g_num, b_num = resized_image.getpixel((x, y))
                num =  (r_num * 299 + g_num * 587 + b_num * 114) / 1000
                f.write(random.choice(sorted_text_colors[cached_find(num)][1]))

                processed_count += 1
                self.start_button.config(text=f'转换中…… {processed_count / sum_count * 100:.2f}%')
                if processed_count == sum_count or processed_count % 2160 == 0:
                    self.process.configure(value=processed_count)
                    self.update()
            f.write('\n')

        messagebox.showinfo('信息', f'转换完成，耗时 {time.time() - start:.2f} 秒，请在文件中查看！')
        self.end_func()

    def end_func(self):
        self.start_button.config(text='开 始')
        self.input_rotate_select.config(state='readonly')
        self.process.pack_forget()
        self.toggle_state(tk.NORMAL)

if __name__ == '__main__':
    window = Window()
    window.mainloop()
