# Đây là 1  Module IDE mini tự làm về trình soạn thảo C++ đơn giản với Python.
# Trình soạn thảo IDE này dành cho người Việt Nam, nếu người nước ngoài muốn dùng thì 
# có thể xóa các dòng ghi chú này.
# Bản này là bản 1.0, nếu ai có góp ý xin gửi về email sau: duolingo1284user@gmail.com.
# Muốn sử dụng IDE này, bạn phải cài đặt MinGW và đảm bảo có g++
# Tôi sẽ phát hành thêm 1 bản IDE dành cho C, nếu ai cần học lập trình
# C++ cơ bản thì có thể sử dụng trực tiếp IDE này.
"""
Built-in functions for making a C++ IDE.
This module is for Vietnamese people, if non-Vietnamese people wants to use,
delete the comments above.
This is 1.0 version, if anyone have bugs or excepts, send via Discord: helofj_96789.
If you want to use this module, you MUST install MinGW and sure it has g++.exe.
I will deploy another module for C IDE, if who need to learn programming C++ basic
then you can use this module for building your own IDE.
"""
_version_ = 1.0

import sys as s
import tkinter as tk
import os
import subprocess as sp
import re, threading
from tkinter import filedialog as fdl
from tkinter import messagebox as msgb
from tkinter import ttk as t

from tkinter import scrolledtext as st
# Full C++

class ide(st.ScrolledText):
    def __init__(self, root, width, height, state="normal"):
        super().__init__(root, wrap=tk.WORD, width=width, height=height,bg="#000000", fg="#FFFFFF", undo=True)
        self.config(state=state)
        self.root = root
        self.root.bind_all("<Control-n>", lambda new_file: self)
        self.config(state=tk.NORMAL)
        self.new_file_name = "noname.cpp"
        
        # Configure tags for syntax highlighting and error pointing
        self.tag_config("keyword", foreground="#0000FF", font=("Courier New", 10, "bold"))
        self.tag_config("type", foreground="#0000fF", font=("Courier New", 10, "bold"))
        self.tag_config("string", foreground="#A31515")
        self.tag_config("comment", foreground="#008000")
        self.tag_config("error", background="#FFCCCC", foreground="#FF0000", underline=True)
        
        # Simple real-time trigger
        self.bind("<KeyRelease>", lambda event: self.catch_error_syntax())

    def catch_error_syntax(self):
        # 1. Clear previous tags/errors
        for tag in ["keyword", "type", "string", "comment", "error"]:
            self.tag_remove(tag, "1.0", tk.END)
            
        content = self.get("1.0", "end-1c")
        lines = content.split('\n')
        
        # --- PHASE 1: BASIC SYNTAX HIGHLIGHTING ---
        keywords = r'\b(alignas|alignof|and|and_eq|asm|atomic_cancel|atomic_commit|atomic_noexcept|bitand|bitor|break|case|catch|class|co_await|co_return|co_yield|compl|concept|const_cast|continue|default|delete|do|dynamic_cast|else|enum|explicit|export|extern|final|for|friend|goto|if|import|inline|module|namespace|new|noexcept|not_eq|operator|or|or_eq|override|private|protected|public|reflexpr|register|reinterpret_cast|requires|return|sizeof|static|static_assert|static_cast|struct|switch|synchronized|template|this|thread_local|throw|transaction_safe|transaction_safe_dynamic|try|typedef|typeid|typename|union|using|virtual|while|xor|xor_eq)\b'

        types = r'\b(bool|char|char8_t|char16_t|char32_t|double|float|int|long|short|signed|unsigned|void|wchar_t|auto|decltype|constexpr|consteval|constinit|const|volatile|void|mutable|nullptr|true|false)\b'
        
        for row, line in enumerate(lines, start=1):
            for match in re.finditer(keywords, line):
                self.tag_add("keyword", f"{row}.{match.start()}", f"{row}.{match.end()}")
            for match in re.finditer(types, line):
                self.tag_add("type", f"{row}.{match.start()}", f"{row}.{match.end()}")
            for match in re.finditer(r'".*?"|\'.*?\'', line):
                self.tag_add("string", f"{row}.{match.start()}", f"{row}.{match.end()}")
            for match in re.finditer(r'//.*', line):
                self.tag_add("comment", f"{row}.{match.start()}", f"{row}.{match.end()}")

        # --- PHASE 2: ERROR CATCHING ---
            for row, line in enumerate(lines, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                    
                # Rule A: Check for outdated headers (like <iostream.h>)
                if clean_line.startswith("#include"):
                    invalid_header = re.search(r'<[a-zA-Z0-9_]+\.h>', clean_line)
                    if invalid_header:
                        start_col = line.find(invalid_header.group())
                        end_col = start_col + len(invalid_header.group())
                        self.tag_add("error", f"{row}.{start_col}", f"{row}.{end_col}")
                        continue 
                
                # Rule B: Check for missing semicolons
                if not clean_line.startswith(('#', '//', '/*', '*')):
                    if not clean_line.endswith((';', '{', '}', ',')) and not clean_line.startswith(('if', 'for', 'while', 'switch')):
                        
                        # 🔥 CRITICAL FIX: Get the cursor's current line
                        try:
                            current_cursor_line = int(self.index("insert").split('.')[0])
                        except Exception:
                            current_cursor_line = -1

                        # If the user is actively editing this line, DO NOT show a missing semicolon error yet!
                        if row == current_cursor_line:
                            continue

                        # Only highlight the last character of a completed line if it's not the active line
                        stripped_line = line.rstrip()
                        if len(stripped_line) > 0:
                            end_idx = len(stripped_line)
                            self.tag_add("error", f"{row}.{end_idx - 1}", f"{row}.{end_idx}")
    
class file:
    def __init__(self, root):
        self.root = root
        
        # Notebook container initialized properly
        self.notebook = t.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        self.new_tab = t.Button(self.root, text="New File", command=self.add_editor)
        self.new_tab.pack(pady=5)
        
        # Dynamic save button to test functionality
        self.save_btn = t.Button(self.root, text="Save As (.cpp)", command=self.save_file)
        self.save_btn.pack(pady=5)
        self.auto_save(self.get_current_code())
        self.add_editor()

    def add_editor(self):
        # Create the tab wrapper frame inside the notebook
        frame = t.Frame(self.notebook)
        
        # FIX 1: Parent is now 'frame' instead of 'self.root'
        editor = ide(frame, width=600, height=400) 
        editor.pack(expand=True, fill=tk.BOTH)
        
        tab_count = len(self.notebook.tabs()) + 1
        self.notebook.add(frame, text=f"Untitled-{tab_count}")
        self.notebook.select(frame)

    def save_file(self):
        """
        Reads the content of the currently open tab and saves it as a .cpp file.
        """
        try:
            current_tab_id = self.notebook.select()
            if not current_tab_id:
                msgb.showwarning("Warning", "No tabs open to save!")
                return
                
            current_tab_frame = self.notebook.nametowidget(current_tab_id)
            
            # FIX 2: This will no longer crash because 'editor' is safely inside 'frame' now!
            children = current_tab_frame.winfo_children()
            if not children:
                msgb.showerror("Error", "Could not locate the text editor widget context.")
                return
                
            editor_widget = children[0]
            file_content = editor_widget.get("1.0", "end-1c")
            
            file_path = fdl.asksaveasfilename(
                defaultextension=".cpp",
                filetypes=[("C++ Source Files", "*.cpp"), ("All Files", "*.*")],
                title="Save As..."
            )
            
            if file_path:
                # Use a local alias so you don't overwrite your own class namespace definition!
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
                
                file_name = os.path.basename(file_path)
                self.notebook.tab(current_tab_frame, text=file_name)
                msgb.showinfo("Success", f"File saved successfully:\n{file_name}")
                
        except Exception as e:
            msgb.showerror("Error", f"Failed to save file: {str(e)}")
    def get_current_editor_widget(self):
        """Finds and returns the ScrolledText/Text widget inside the active tab."""
        try:
            # 1. Get the widget name of the active tab from the notebook
            # Replace 'self.notebook' with whatever your tk.Notebook variable is named!
            current_tab_id = self.notebook.select() 
            
            # 2. Look up the actual tab frame object
            current_tab = self.notebook.nametowidget(current_tab_id)
            
            # 3. Find the text widget inside that tab frame. 
            # If your text box is stored in a dictionary or property (like tab.text_area), use that:
            if hasattr(current_tab, 'text_area'):
                return current_tab.text_area
                
            # Fallback: search the tab's children for any text/scrolledtext widget instance
            for child in current_tab.winfo_children():
                if isinstance(child, (tk.Text, st.ScrolledText)):
                    return child
        except Exception:
            pass
        return None
    def get_current_code(self):
        """
        Extracts the raw text content out of the text editor inside the active tab.
        """
        active = self.get_current_editor_widget()
        if active:
            return active.get("1.0", "end-1c")
        else:
            return ""
    def auto_save(self, code):
        current = "noname.cpp"
        with open(current, "w", encoding="utf-8") as temp:
            temp.write(code)
    
class console_log(st.ScrolledText):
    def __init__(self, parent, width, height):
        # Initialize the underlying ScrolledText area
        super().__init__(parent, width=width, height=height, bg="#1E1E1E", fg="#FFFFFF", insertbackground="white")
        self.config(font=("Consolas", 10))
        
        # Define output color tags
        self.tag_config("stdout", foreground="#FFFFFF")
        self.tag_config("stderr", foreground="#FF5555")  # Red for compilation/runtime errors
        self.tag_config("system", foreground="#00FF00")  # Green for status updates

    def write(self, text, tag="stdout"):
        """Safely appends text to the terminal frame and scrolls to the bottom."""
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text, tag)
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def clr_scr(self):
        """Clears the console screen."""
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED)

    def handle(self, process):
        """
        Accepts a live Popen object (compiling/running), clears the screen, 
        and reads its output streams asynchronously in background threads.
        """
        self.clr_scr()
        self.write("⚡ Processing build system streams...\n", "system")
        
        # Start reading stdout in a background thread if it exists
        if process.stdout:
            threading.Thread(target=self._read_stream, args=(process.stdout, "stdout"), daemon=True).start()
            
        # Start reading stderr in a background thread if it exists
        if process.stderr:
            threading.Thread(target=self._read_stream, args=(process.stderr, "stderr"), daemon=True).start()

    def _read_stream(self, stream, tag):
        """Continuously reads character by character from a pipe stream until it terminates."""
        while True:
            char = stream.read(1)
            if not char:
                break
            self.write(char, tag)
class MainUI: 
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
        
        self.csw = self.width * 0.3 
        self.csh = self.height * 0.3
        self.idw = self.width * 0.7
        self.idh = self.height * 0.7
        
        self.ui_builder()

    def ui_builder(self):
        # 1. Create a Top Toolbar for Action Buttons
        self.toolbar = tk.Frame(self.root, bg="#2D2D2D", height=40)
        self.toolbar.pack(fill=tk.X)
        
        # ▶ RUN BUTTON: Calls the execute trigger
        self.run_btn = tk.Button(
            self.toolbar, 
            text="▶ Run Code", 
            bg="#1E7E34", 
            fg="white", 
            font=("Arial", 10, "bold"),
            command=lambda:self.run
        )
        self.save_file = tk.Button(
            self.toolbar, 
            text="Save File", 
            bg="#FFFFFF", 
            fg="white", 
            font=("Arial", 10, "bold"),
            command=self.save,
        )
        self.run_btn.pack(side=tk.LEFT, padx=10, pady=5)
        self.save_file.pack(side=tk.LEFT, padx=15, pady=5)
        # 2. Editor Section (Top Panel)
        self.editor_frame = tk.Frame(self.root, width=int(self.idw), height=int(self.idh))
        self.editor_frame.pack(expand=True, fill=tk.BOTH)
        self.ide = file(self.editor_frame)
        self.ide.auto_save(self.ide.get_current_code())
        # 3. Terminal Section (Bottom Panel)
        self.console_frame = tk.Frame(self.root, width=int(self.csw), height=int(self.csh))
        self.console_frame.pack(expand=True, fill=tk.BOTH)
        self.console = console_log(self.console_frame, int(self.csw), int(self.csh))
        self.console.pack(expand=True, fill=tk.BOTH)
    def save(self):
        f = fdl.asksaveasfilename(defaultextension=["C++ files (*.cpp)", "Any (*.*)"])
        with open(f, "w") as file:
            code = self.ide.get_current_code()
            file.write(code)
        return True
    def run(self,output:str, src="noname.cpp"):
        process = sp.Popen(["g++", "-o", output, src])
        self.console.handle(process)

    