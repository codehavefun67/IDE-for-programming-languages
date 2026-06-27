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
IF you want to use this module, please install MinGW and sure it has g++.exe.
I will deploy another module for C IDE, if who need to learn programming C++ basic
then you can use this module for building your own IDE.
"""
ideversion = 1.0
import sys as s
import tkinter as tk
import os as o
import subprocess as sp
import re, threading
from tkinter import filedialog as fdl
from tkinter import messagebox as msgb
from tkinter import ttk as t
from compiler import *
from tkinter import scrolledtext as st
# Thiết lập đường dẫn tới các Lib và Bin
gcom = r"D:\msys64\ucrt64\bin\g++.exe"
libs = r"D:\msys64\ucrt64\include\c++\16.1.0"
class check_if_file_exists:
    def __init__(self, file_path):
        self.file_path = file_path
        self.check()
    def check(self, *file, n:int):
        self.target = list(file)
        self.num_files = n
        remove(self.target, self.num_files)

class ide(st.ScrolledText):
    def __init__(self, root, width, height, state="normal"):
        super().__init__(root, wrap=tk.WORD, width=width, height=height, undo=True)
        self.config(state=state)
        self.root = root
        self.root.bind_all("<Control-n>", lambda new_file: self)
        self.config(state=tk.NORMAL)
        self.new_file_name = "noname.cpp"
        
        # Configure tags for syntax highlighting and error pointing
        self.tag_config("keyword", foreground="#0000FF", font=("Courier New", 10, "bold"))
        self.tag_config("type", foreground="#2B91AF", font=("Courier New", 10, "bold"))
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
        keywords = r'\b(if|else|for|while|do|return|switch|case|break|continue|class|struct|namespace|using|public|private|protected|new|delete)\b'
        types = r'\b(int|float|double|char|bool|void|string|vector|auto|long|short|unsigned)\b'
        
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
                    continue # Skip further checks on this line
            
            # Rule B: Check for missing semicolons
            if not clean_line.startswith(('#', '//', '/*', '*')):
                if not clean_line.endswith((';', '{', '}', ',')) and not clean_line.startswith(('if', 'for', 'while', 'switch')):
                    end_idx = len(line)
                    self.tag_add("error", f"{row}.{end_idx - 1 if end_idx > 0 else 0}", f"{row}.{end_idx}")

        # Rule C: Check for Bracket Mismatches (), {}, []
        stack = []
        bracket_map = {')': '(', '}': '{', ']': '['}
        
        for row, line in enumerate(lines, start=1):
            for col, char in enumerate(line):
                current_index = f"{row}.{col}"
                current_tags = self.tag_names(current_index)
                if "string" in current_tags or "comment" in current_tags:
                    continue
                    
                if char in bracket_map.values():
                    stack.append((char, current_index))
                elif char in bracket_map.keys():
                    if stack and stack[-1][0] == bracket_map[char]:
                        stack.pop()
                    else:
                        self.tag_add("error", current_index, f"{row}.{col+1}")
                        
        for char, index in stack:
            line_num, col_num = map(int, index.split('.'))
            self.tag_add("error", index, f"{line_num}.{col_num+1}")

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
    def get_current_code(self):
        """
        Extracts the raw text content out of the text editor inside the active tab.
        """
        try:
            # 1. Get the Tkinter ID of the currently active tab
            current_tab_id = self.notebook.select()
            if not current_tab_id:
                return ""
                
            # 2. Convert that ID into the actual Frame object
            current_tab_frame = self.notebook.nametowidget(current_tab_id)
            
            # 3. Reach inside the Frame and grab your custom 'ide' text widget
            children = current_tab_frame.winfo_children()
            if not children:
                return ""
                
            editor_widget = children[0]
            
            # 4. Get all text from line 1 down to the very end (-1c drops the extra newline)
            return editor_widget.get("1.0", "end-1c")
            
        except Exception:
            return ""
class console_log(st.ScrolledText):
    def __init__(self, root, width, height, state="disabled"):
        super().__init__(root, wrap=tk.WORD, width=width, height=height)
        self.config(state=state, background="#1E1E1E", foreground="#FFFFFF", insertbackground="white")
        
        # Configure tags for nice looking terminal output
        self.tag_config("info", foreground="#00FF00")    # Green for status
        self.tag_config("error", foreground="#FF3333")   # Red for compiler errors
        self.tag_config("output", foreground="#FFFFFF")  # White for standard stdout

    def write(self, text, tag="output"):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text + "\n", tag)
        self.config(state=tk.DISABLED)
        self.see(tk.END)
        
    def clr_scr(self):
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED)

    def handle(self, event, code_content=""):
        """
        Handles 'compile' and 'run' events.
        code_content: Pass the string from your ide widget (ide.get("1.0", "end-1c"))
        """
        # Run the compilation/running on a separate thread to prevent Tkinter freezing
        threading.Thread(target=self._execute_workflow, args=(event, code_content), daemon=True).start()

    def _execute_workflow(self, event, code_content):
        file_name = "temp_program.cpp"
        exe_name = "temp_program.exe" if os.name == 'nt' else "./temp_program"

        if event in ["compile", "run"]:
            self.clr_scr()
            self.write("=== Compiling... ===", "info")
            
            # 1. Write content to a temporary C++ file
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(code_content)
            
            # 2. Invoke g++ Compiler
            # Adjust 'g++' if your environment uses a specific compiler path
            compile_process = compile()
            
            if compile_process.returncode != 0:
                self.write("❌ Compilation Failed!", "error")
                self.write(compile_process.stderr, "error")
                return False
            else:
                self.write("✔ Compilation Successful!", "info")
                
        if event == "run":
            self.write("\n=== Running Program... ===", "info")
            try:
                # 3. Execute the compiled binary
                run_process = sp.run(
                    [exe_name], 
                    capture_output=True, 
                    text=True,
                    timeout=5 # Safeguard against infinite loops in user code
                )
                
                if run_process.stdout:
                    self.write(run_process.stdout, "output")
                if run_process.stderr:
                    self.write(run_process.stderr, "error")
                    
                self.write(f"\nProcess finished with exit code {run_process.returncode}", "info")
                
            except sp.TimeoutExpired:
                self.write("\n❌ Error: Execution timed out (possible infinite loop).", "error")
            except Exception as e:
                self.write(f"\n❌ Execution Error: {str(e)}", "error")
class MainUI: 
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
        
        self.csw = self.width * 1.0  
        self.csh = self.height * 0.3
        self.idw = self.width * 1.0  
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
            command=self.trigger_run
        )
        self.run_btn.pack(side=tk.LEFT, padx=10, pady=5)

        # 2. Editor Section (Top Panel)
        self.editor_frame = tk.Frame(self.root, width=int(self.idw), height=int(self.idh))
        self.editor_frame.pack(expand=True, fill=tk.BOTH)
        self.ide = file(self.editor_frame)

        # 3. Terminal Section (Bottom Panel)
        self.console_frame = tk.Frame(self.root, width=int(self.csw), height=int(self.csh))
        self.console_frame.pack(expand=True, fill=tk.BOTH)
        self.console = console_log(self.console_frame, int(self.csw), int(self.csh))
        self.console.pack(expand=True, fill=tk.BOTH)

    def trigger_run(self):
        """Extracts code from the active tab and passes it to the console processor."""
        code_to_run = self.ide.get_current_code()
        
        if not code_to_run.strip():
            self.console.clr_scr()
            self.console.write("❌ Error: Cannot run an empty file!", "error")
            return
            
        # Call the handle function we built earlier for console_log
        self.console.handle("run", code_to_run)

    