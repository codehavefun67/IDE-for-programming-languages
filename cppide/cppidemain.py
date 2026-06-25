# Đây là 1 IDE mini tự làm về trình soạn thảo C++ đơn giản với Python.
# Trình soạn thảo IDE này dành cho người Việt Nam, nếu người nước ngoài muốn dùng thì 
# có thể xóa các dòng ghi chú này.
# Bản này là bản 1.0, nếu ai có góp ý xin gửi về email sau: duolingo1284user@gmail.com.
# Muốn sử dụng IDE này, bạn phải cài đặt MinGW và đảm bảo có g++
# Tôi sẽ phát hành thêm 1 bản IDE dành cho C, nếu ai cần học lập trình
# C++ cơ bản thì có thể sử dụng trực tiếp IDE này.
import sys as s
import tkinter as tk
import os as o
import subprocess as sp
import keyboard as k
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import ttk as t
from compiler import compiler
from tkinter import scrolledtext as st
# Thiết lập đường dẫn tới các Lib và Bin
gcom = r"D:\msys64\ucrt64\bin\g++.exe"
libs = r"D:\msys64\ucrt64\include\c++\16.1.0"
class check_if_file_exists:
    def __init__(self, file_path):
        self.file_path = file_path
        self.check()
    def check(self):
        if o.path.isfile(self.file_path):
            return True
        else:
            return False
class ide(st.ScrolledText):
    def __init__(self, root, width, height, state="normal"):
        super().__init__(root, wrap=tk.WORD, width=width, height=height)
        self.config(state=state)
        self.pack(expand=True, fill=tk.X)
        self.config(state=tk.NORMAL)
    # Phần tiếp theo sẽ khá dài về bắt lỗi cú pháp C++, ai ko muốn đọc thì bỏ qua lớp này.
    def catch_error_syntax(self):
        content = self.get("1.0", "end-1c")
        
class console_log(st.ScrolledText):
    def __init__(self, root, width, height, state="disabled"):
        super().__init__(root, wrap=tk.WORD, width=width, height=height)
        self.config(state=state)
        self.pack(expand=True, fill=tk.X)
        self.config(state=tk.DISABLED)
    def write(self, text):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text + "\n")
        self.config(state=tk.DISABLED)
        self.see(tk.END)
    def handle(self, event):
        if event == "compile":
            self.write("Compiling...")

































































if __name__ == "__main__":
    root = tk.Tk()