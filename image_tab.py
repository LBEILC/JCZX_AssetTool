# image_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from PIL import Image
import numpy as np
import os
import threading


def premultiply_alpha(img):
    matrix = np.array(img, dtype=int)
    for row in matrix:
        for pixel in row:
            if pixel[3] == 255:
                continue
            elif pixel[3] == 0:
                pixel[0] = pixel[1] = pixel[2] = 0
            else:
                for i in range(3):
                    pixel[i] = pixel[i] * pixel[3] // 255
    matrix = matrix.astype("uint8")
    return Image.fromarray(matrix)


def straight_alpha(img):
    matrix = np.array(img)
    for row in matrix:
        for pixel in row:
            rgb = pixel[:-1]
            alpha = pixel[-1]
            if alpha != 0 and alpha != 255:
                maxrgb = max(rgb)
                if maxrgb > alpha:
                    for i in range(3):
                        pixel[i] = rgb[i] * 255 // maxrgb
                else:
                    for i in range(3):
                        pixel[i] = rgb[i] * 255 // alpha
    return Image.fromarray(matrix)


class ImageTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.frame.grid(row=0, column=0, sticky="nsew")  # 使用 grid 布局管理器放置 frame

    def create_widgets(self):
        # 直通转预乘按钮
        self.btn_convert_to_premultiplied = ttk.Button(
            self.frame,
            text="直通转预乘",
            command=lambda: self.select_images(False)
        )
        self.btn_convert_to_premultiplied.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # 预乘转直通按钮
        self.btn_convert_to_straight = ttk.Button(
            self.frame,
            text="预乘转直通",
            command=lambda: self.select_images(True)
        )
        self.btn_convert_to_straight.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # 日志显示区域
        log_label = ttk.Label(self.frame, text="日志")
        log_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.log_text = scrolledtext.ScrolledText(self.frame, height=10, width=80)
        self.log_text.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

        # 配置 grid 布局的权重
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(3, weight=1)  # 为日志区域所在的行设置权重，使其在垂直方向上扩展

        # 确保整个 ImageTab 的 frame 填充其父容器的空间
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.parent.grid_rowconfigure(0, weight=1)  # 为 ImageTab 的 frame 所在行设置权重
        self.parent.grid_columnconfigure(0, weight=1)  # 为 ImageTab 的 frame 所在列设置权重

    def select_images(self, premultiplied_to_straight):
        filetypes = [('PNG files', '*.png')]
        filenames = filedialog.askopenfilenames(title="选择 PNG 图片", filetypes=filetypes)
        if filenames:
            self.log("选择的图片: " + ", ".join(filenames))
            for filename in filenames:
                if premultiplied_to_straight:
                    # 注意这里传递了 3 个参数给 process_image 方法
                    threading.Thread(target=self.process_image, args=(filename, straight_alpha, "预乘转直通")).start()
                else:
                    # 注意这里传递了 3 个参数给 process_image 方法
                    threading.Thread(target=self.process_image,
                                     args=(filename, premultiply_alpha, "直通转预乘")).start()

    def process_image(self, filename, conversion_function, conversion_type):
        self.log(f"{conversion_type}: 处理中 {filename}")
        try:
            img = Image.open(filename)
            final = conversion_function(img)
            result_path, file_name = os.path.split(filename)

            # 根据转换类型来决定备份文件的后缀标识符
            if conversion_type == "预乘转直通":
                suffix = "_premultiplied_to_straight_bak"
            else:  # 对应 "直通转预乘"
                suffix = "_straight_to_premultiplied_bak"

            # 生成备份文件名
            new_name = os.path.join(result_path, file_name.split(".png")[0] + suffix + ".png")

            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(filename, new_name)
            final.save(filename)

            self.log(f"{conversion_type}: 文件修改成功！结果文件保存至: {filename}")
            self.log(f"{conversion_type}: 原文件备份至: {new_name}")

            if conversion_type == "预乘转直通":
                self.log(f"{conversion_type}: 完成!转换后的png可以用PS修改,修改完用另一个脚本转回直通即可")
            else:  # 对应 "直通转预乘"
                self.log(f"{conversion_type}: 完成!转换后的png在软件和游戏内能正常显示")
        except Exception as e:
            self.log(f"{conversion_type}: 处理图片时发生错误: {e}")

    def log(self, message):
        def append_message():
            self.log_text.insert(tk.END, message + '\n')
            self.log_text.yview(tk.END)

        # 在主线程中调用 GUI 更新
        self.parent.after(0, append_message)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
