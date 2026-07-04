"""
Built-in functions for making a C++ IDE.

This module is for Vietnamese people, if non-Vietnamese people wants to use,
delete the comments above.

This is 1.0 version, if anyone have bugs or excepts, send via Discord: helofj_96789.

If you want to use this module, you MUST install MinGW and sure it has g++.exe.

I will deploy another module for C IDE, if who need to learn programming C++ basic
then you can use this module for building your own IDE.
"""

import queue
import sys as s
import tkinter as tk
import os
import subprocess as sp
import re
import threading
from tkinter import filedialog as fdl
from tkinter import messagebox as msgb
from tkinter import ttk as t
from tkinter import scrolledtext as st
_version_ = 1.0 
class ide(st.ScrolledText):
    def __init__(self, root, width, height, state="normal", **kwargs):
        super().__init__(root, wrap=tk.WORD, width=width, height=height, bg="#1E1E1E", fg="#FFFFFF", undo=True)
        self.config(font=("Consolas", 10))
        self.config(state=state)
        self.root = root
        self.new_file_name = "noname.cpp"
        
        # Configure tags for syntax highlighting and error pointing
        self.tag_config("keyword", foreground="#0048A7", font=("Consolas", 10, "bold"))
        self.tag_config("type", foreground="#0048a7", font=("Consolas", 10, "bold"))
        self.tag_config("string", foreground="#CE9178")
        self.tag_config("comment", foreground="#608B4E")
        self.tag_config("error", background="#FFCCCC", foreground="#FF0000", underline=True)
        self.tag_config("include", foreground="#C586C0")
        # Simple real-time trigger
        self.bind("<KeyRelease>", lambda event: self.catch_error_syntax())

    def catch_error_syntax(self, event=None):
        
        # 1. Clear previous tags/errors across the text window
        for tag in ["keyword", "type", "string", "comment", "error", "include"]:
            self.tag_remove(tag, "1.0", tk.END)
            
        content = self.get("1.0", "end-1c")
        lines = content.split('\n')
        
        keywords = r'\b(alignas|alignof|and|and_eq|asm|atomic_cancel|atomic_commit|atomic_noexcept|bitand|bitor|break|case|catch|class|co_await|co_return|co_yield|compl|concept|const_cast|continue|default|delete|do|dynamic_cast|else|enum|explicit|export|extern|final|for|friend|goto|if|import|inline|module|namespace|new|noexcept|not_eq|operator|or|or_eq|override|private|protected|public|reflexpr|register|reinterpret_cast|requires|return|sizeof|static|static_assert|static_cast|struct|switch|synchronized|template|this|thread_local|throw|transaction_safe|transaction_safe_dynamic|try|typedef|typeid|typename|union|using|virtual|while|xor|xor_eq)\b'
        types = r'\b(bool|char|char8_t|char16_t|char32_t|double|float|int|long|short|signed|unsigned|void|wchar_t|auto|decltype|constexpr|consteval|constinit|const|volatile|mutable|nullptr|true|false)\b'
        
        try:
            current_cursor_line = int(self.index("insert").split('.')[0])
        except Exception:
            current_cursor_line = -1

        for row, line in enumerate(lines, start=1):
            clean_line = line.strip()
            if not clean_line:
                continue

            # ==========================================
            # STEP 1: PREPROCESSOR DIRECTIVES & ACTIONS
            # ==========================================
            if clean_line.startswith("#include"):
                # A. Run syntax highlighting for the include line
                include_match = re.search(r'#include\s*(<[^>]*>|"[^"]*")?', line)
                if include_match:
                    self.tag_add("include", f"{row}.{include_match.start()}", f"{row}.{include_match.end()}")
                
                # B. Rule A Linting: Check for outdated headers (like <iostream.h>)
                invalid_header = re.search(r'<[a-zA-Z0-9_]+\.h>', clean_line)
                if invalid_header:
                    start_col = line.find(invalid_header.group())
                    end_col = start_col + len(invalid_header.group())
                    self.tag_add("error", f"{row}.{start_col}", f"{row}.{end_col}")
                
                continue  # Skip checking keywords/strings inside include lines

            # ==========================================
            # STEP 2: COMMENTS (FULL LINE OR END-OF-LINE)
            # ==========================================
            comment_match = re.search(r'//.*', line)
            if comment_match:
                self.tag_add("comment", f"{row}.{comment_match.start()}", f"{row}.{comment_match.end()}")
                # If the line starts with a comment, skip parsing entirely
                if clean_line.startswith("//"):
                    continue

            # ==========================================
            # STEP 3: STRINGS, KEYWORDS, AND TYPES
            # ==========================================
            # Highlight literal strings
            for match in re.finditer(r'".*?"|\'.*?\'', line):
                self.tag_add("string", f"{row}.{match.start()}", f"{row}.{match.end()}")

            # Highlight C++ control flow keywords
            for match in re.finditer(keywords, line):
                self.tag_add("keyword", f"{row}.{match.start()}", f"{row}.{match.end()}")

            # Highlight native C++ data types
            for match in re.finditer(types, line):
                self.tag_add("type", f"{row}.{match.start()}", f"{row}.{match.end()}")

            # ==========================================
            # STEP 4: LINTING - MISSING SEMICOLONS
            # ==========================================
            if row == current_cursor_line:
                continue  # Don't throw errors on the line the user is actively typing on

            if not clean_line.startswith(('#', '//', '/*', '*')):
                if not clean_line.endswith((';', '{', '}', ',')) and not clean_line.startswith(('if', 'for', 'while', 'switch')):
                    stripped_line = line.rstrip()
                    if len(stripped_line) > 0:
                        end_idx = len(stripped_line)
                        self.tag_add("error", f"{row}.{end_idx - 1}", f"{row}.{end_idx}")
    
class file:
    def __init__(self, root, **kwargs):
        self.root = root
        self.editors = {} # Lưu trữ dictionary để quản lý text riêng cho từng tab
        
        self.notebook = t.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(pady=5)
        self.new_tab = tk.Button(self.btn_frame, text="New File", command=self.add_editor)
        self.new_tab.pack(side=tk.LEFT, padx=5, pady=5)
         
        self.save_btn = tk.Button(self.btn_frame, text="Save As (.cpp)", command=self.save)
        self.save_btn.pack(side=tk.LEFT, padx=0, pady=5)
        self.add_editor()

    def add_editor(self):
        frame = t.Frame(self.notebook)
        editor = ide(frame, width=600, height=400)
        editor.pack(expand=True, fill=tk.BOTH)
        
        tab_count = len(self.notebook.tabs()) + 1
        tab_id = f"Untitled-{tab_count}"
        self.notebook.add(frame, text=tab_id)
        self.notebook.select(frame)
        
        # Lưu liên kết giữa frame của notebook và widget editor bên trong nó
        self.editors[str(frame)] = editor

    def get_current_editor(self):
        """Lấy chính xác widget editor của tab đang được chọn"""
        try:
            current_tab = self.notebook.select()
            return self.editors[current_tab]
        except Exception:
            return None

    def read(self):
        editor = self.get_current_editor()
        if editor:
            return editor.get("1.0", "end-1c")
        return ""

    def auto_save(self, src_name:str="noname.cpp"):
        content = self.read()
        with open(src_name, "w", encoding="utf-8") as f:
            f.write(content)

    def save(self):
        name = fdl.asksaveasfilename(defaultextension=".cpp", filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")])
        if name:
            content = self.read()
            with open(name, "w", encoding="utf-8") as f:
                f.write(content)
            # Cập nhật lại tiêu đề Tab thành tên file vừa lưu
            current_tab = self.notebook.select()
            self.notebook.tab(current_tab, text=os.path.basename(name))

class console_log(st.ScrolledText):

    def __init__(self, parent, width, height, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg="#1E1E1E",
            fg="#FFFFFF",
            insertbackground="white",
        )
        self.config(font=("Consolas", 10))

        self.tag_config("stdout", foreground="#FFFFFF")
        self.tag_config("stderr", foreground="#FF5555")
        self.tag_config("system", foreground="#00FF00")

        # 📦 Safe queue for background threads to dump text data into
        self.console_queue = queue.Queue()

    def write(self, text, tag="stdout"):
        """Always execute this method on the MAIN loop thread."""
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text, tag)
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def clr_scr(self):
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED)

    def handle(self, process):
        """Starts the process background listeners safely."""
        self.clr_scr()
        self.write("⚡ Compiling and running code...\n", "system")

        # Start up your independent background stream monitors
        if process.stdout:
            threading.Thread(
                target=self._read_stream,
                args=(process.stdout, "stdout"),
                daemon=True,
            ).start()
        if process.stderr:
            threading.Thread(
                target=self._read_stream,
                args=(process.stderr, "stderr"),
                daemon=True,
            ).start()

        # 🔄 Launch Tkinter's continuous loop checker to consume the queue data safely
        self._check_console_queue()

    def _read_stream(self, stream, tag):
        """BACKGROUND THREAD: Blindly reads lines and puts them into the safe queue."""
        try:
            # Iterating through readline handles text lines efficiently as they output
            for line in iter(stream.readline, ""):
                if line:
                    self.console_queue.put((line, tag))
            stream.close()
        except Exception as e:
            self.console_queue.put(
                (f"\n❌ Stream parsing dropped: {str(e)}\n", "stderr")
            )

    def _check_console_queue(self):
        """MAIN THREAD: Safely flushes the queue text data into your UI elements."""
        try:
            # Drain out everything waiting in the queue without blocking the UI
            while True:
                text_chunk, tag = self.console_queue.get_nowait()
                self.write(text_chunk, tag)
                self.console_queue.task_done()
        except queue.Empty:
            # No text lines left in queue for this frame loop
            pass

        # Schedule the loop to execute check again in 50 milliseconds
        self.after(50, self._check_console_queue)

class MainUI: 
    def __init__(self, root, width, height, **kwargs):
        self.root = root
        self.width = width
        self.height = height
        
        self.csw = self.width * 0.3
        self.csh = self.height * 0.3
        self.idw = self.width * 0.7
        self.idh = self.height * 0.7
        
        self.ui_builder()

    def ui_builder(self):
        self.toolbar = tk.Frame(self.root, bg="#2D2D2D", height=40)
        self.toolbar.pack(fill=tk.X)
        
        self.run_btn = tk.Button(
            self.toolbar, 
            text="▶ Run Code", 
            bg="#1E7E34", 
            fg="white", 
            font=("Consolas", 10, "bold"),
            command=self.run
        )
        self.run_btn.pack(side=tk.LEFT, padx=15, pady=5)

        self.save_file = tk.Button(
            self.toolbar, 
            text="Save File", 
            bg="#007ACC", 
            fg="white", 
            font=("Consolas", 10, "bold"),
            command=lambda: self.ide.save(),
        )
        
        self.save_file.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.editor_frame = tk.Frame(self.root, width=int(self.idw), height=int(self.idh))
        self.editor_frame.pack(expand=True, fill=tk.BOTH)
        self.ide = file(self.editor_frame)
        
        self.console_frame = tk.Frame(self.root, width=int(self.csw), height=int(self.csh))
        self.console_frame.pack(expand=True, fill=tk.BOTH)
        self.console = console_log(self.console_frame, int(self.csw), int(self.csh))
        self.console.pack(expand=True, fill=tk.BOTH)

    def run(self):
        # Tự động lưu nội dung hiện tại vào file tạm noname.cpp trước khi chạy
        self.ide.auto_save()
        
        # Lệnh biên dịch đồng thời thực thi nếu thành công (Dùng cho môi trường Windows)
        # Biên dịch ra file noname.exe, nếu thành công (&&) thì chạy luôn file đó
        cmd = "g++ noname.cpp -o noname.exe && noname.exe"
        
        process = sp.Popen(
            cmd,
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            text=True,
            creationflags=sp.CREATE_NEW_CONSOLE
        )
        self.console.handle(process)
        proc = sp.Popen(
            "noname.exe",
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            text=True,  
        )
        self.console.handle(proc)
    