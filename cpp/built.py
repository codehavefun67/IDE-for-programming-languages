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
import tkinter as tk
import os
import subprocess as sp
import re
from tkinter import filedialog as fdl
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
        import re
        import tkinter as tk

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
                # FIX: Added ':' to the endswith check to accept access specifiers & labels safely!
                if not clean_line.endswith((';', '{', '}', ',', ':')) and not clean_line.startswith(('if', 'for', 'while', 'switch')):
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
        # Pass **kwargs through so any extra parameters don't break init
        super().__init__(
            parent,
            width=width,
            height=height,
            bg="#1E1E1E",
            fg="#FFFFFF",
            insertbackground="white",
            **kwargs,
        )
        self.config(font=("Consolas", 10))

        self.tag_config("stdout", foreground="#FFFFFF")
        self.tag_config("stderr", foreground="#FF5555")
        self.tag_config("system", foreground="#5DD40E")

        # Keeping the queue ONLY for capturing compiler warnings/errors safely
        self.console_queue = queue.Queue()

    def write(self, text, tag="stdout"):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text, tag)
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def clr_scr(self):
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED)

class MainUI:

    def __init__(self, root, width, height, **kwargs):
        self.root = root
        self.width = width
        self.height = height

        # Split window layouts dynamically
        self.csw = self.width * 0.5
        self.csh = self.height * 0.5
        self.idw = self.width * 0.5
        self.idh = self.height * 0.5

        self.ui_builder()
    def ui_builder(self):
        # 1. Toolbar layout (Fixed at the top)
        self.toolbar = tk.Frame(self.root, bg="#2D2D2D", height=40)
        self.toolbar.pack(fill=tk.X)
        
        self.com_btn = tk.Button(
            self.toolbar, 
            text="Compile", 
            bg="#007acc", 
            fg="white", 
            font=("Consolas", 10, "bold"),
            command=self.compile
        )
        self.com_btn.pack(side=tk.LEFT, padx=15, pady=5)

        self.save_file = tk.Button(
            self.toolbar, 
            text="Save File", 
            bg="#007ACC", 
            fg="white", 
            font=("Consolas", 10, "bold"),
            command=lambda: self.ide.save(),
        )
        self.save_file.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.run_btn = tk.Button(
            self.toolbar,
            text="Run Compiled",
            bg="#007acc",
            fg="white",
            font=("Consolas", 10, "bold"),
            command=self.run
        ) 
        self.run_btn.pack(side=tk.LEFT, padx=5, pady=5)
        # 2. Create a PanedWindow splitting vertically (Top vs Bottom)
        self.splitter = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=6, bg="#444444")
        self.splitter.pack(expand=True, fill=tk.BOTH)
        
        # 3. Editor Container Frame (Put inside the splitter)
        self.editor_frame = tk.Frame(self.splitter, bg="#1E1E1E")
        self.ide = file(self.editor_frame)
        
        # 4. Console Container Frame (Put inside the splitter)
        self.console_frame = tk.Frame(self.splitter, bg="#1E1E1E")
        # width/height here dictate text character layout grids
        self.console = console_log(self.console_frame, width=80, height=10)
        self.console.pack(expand=True, fill=tk.BOTH)
        
        # 📦 5. Add both frames safely without the invalid "-weight" option
        # minsize ensures neither panel can be squished completely to 0 pixels
        self.splitter.add(self.editor_frame, minsize=200)  
        self.splitter.add(self.console_frame, minsize=100)

    def compile(self):
        # 1. Trigger the text auto-saver
        self.ide.auto_save()

        current_dir = os.getcwd()
        batch_file = os.path.join(current_dir, "compiler.bat")
        compile_log_file = os.path.join(current_dir, "std_compile_out_err.txt")

        # Fallback if your custom compiler script isn't found
        if not os.path.exists(batch_file):
            self.console.clr_scr()
            self.console.write(
                f"Error: 'compiler.bat' not found in {current_dir}\n",
                "stderr",
            )
            return

        self.console.clr_scr()
        self.console.write(" Compiling code...\n", "system")

        # 2. Reset and clear old compilation logs
        try:
            open(compile_log_file, "w").close()
            self.compile_log_handle = open(compile_log_file, "w", encoding="utf-8")
        except Exception as e:
            self.console.write(f"❌ Failed to initialize log file: {str(e)}\n", "stderr")
            return

        # 3. Fire compiler.bat and dump streams straight into the log file
        self.compilation_process = sp.Popen(
            f'cmd /c "{batch_file}"',
            shell=True,
            stdout=self.compile_log_handle,
            stderr=self.compile_log_handle,
            cwd=current_dir,
            creationflags=sp.CREATE_NO_WINDOW,  # Keeps it completely silent
        )

        # 4. Initialize tracking positions and start the non-blocking tail loop
        self.compile_last_read_position = 0
        self._tail_compile_log(compile_log_file)

    def _tail_compile_log(self, log_file_path):
        """Reads new compilation messages from the log file without freezing Tkinter."""
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, "r", encoding="utf-8") as f:
                    f.seek(self.compile_last_read_position)
                    new_data = f.read()
                    self.compile_last_read_position = f.tell()
                
                # If g++ outputs errors or warnings, print them out instantly
                if new_data:
                    self.console.write(new_data, "stdout")
        except Exception as e:
            print(f"Compilation log tailing error: {e}")

        # Check if the compilation process is finished yet
        if self.compilation_process.poll() is None:
            # Still compiling! Poll again in 50ms without freezing the UI
            self.root.after(50, lambda: self._tail_compile_log(log_file_path))
        else:
            # Compilation finished! Clean up the write handle safely
            if hasattr(self, 'compile_log_handle') and not self.compile_log_handle.closed:
                self.compile_log_handle.close()
            
            # Verify if compilation successfully built the binary
            current_dir = os.getcwd()
            exe_file = os.path.join(current_dir, "noname.exe")
            if os.path.exists(exe_file) and os.path.getsize(exe_file) > 0:
                self.console.write("Compilation finished successfully!\n", "system")
            else:
                self.console.write("Compilation failed. Check syntax errors above.\n", "stderr")
        # 3. Wait safely on a small post-check to verify compilation output

    def run(self):
        self.console.clr_scr()
        self.console.write(" Running program...\n", "system")

        current_dir = os.getcwd()
        run_log_file = os.path.join(current_dir, "std_out_err.txt")

        # 2. Reset and clear old runtime logs
        try:
            open(run_log_file, "w").close()
            self.run_log_handle = open(run_log_file, "w", encoding="utf-8")
        except Exception as e:
            self.console.write(f"❌ Failed to initialize log file: {str(e)}\n", "stderr")
            return

        # 3. Fire noname.exe and dump streams straight into the runtime log file
        self.running_process = sp.Popen(
            ["noname.exe"],
            shell=True,
            stdout=self.run_log_handle,
            stderr=self.run_log_handle,
            cwd=current_dir,
            creationflags=sp.CREATE_NO_WINDOW,  # Keeps it completely silent
        )

        # 4. Initialize tracking positions and start the non-blocking tail loop
        self.run_last_read_position = 0
        self._tail_run_log(run_log_file)

    def _tail_run_log(self, log_file_path):
        """Reads new runtime messages from the log file without freezing Tkinter."""
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, "r", encoding="utf-8") as f:
                    f.seek(self.run_last_read_position)
                    new_data = f.read()
                    self.run_last_read_position = f.tell()
                
                # If the program outputs data, print it instantly
                if new_data:
                    self.console.write(new_data, "stdout")
        except Exception as e:
            print(f"Runtime log tailing error: {e}")

        # Check if the execution process is finished yet
        exit_code = self.running_process.poll()

        if exit_code is None:
            # Still running! Poll again in 50ms without freezing the UI
            self.root.after(50, lambda: self._tail_run_log(log_file_path))
        else:
            # Execution finished! Clean up the write handle safely
            if hasattr(self, 'run_log_handle') and not self.run_log_handle.closed:
                self.run_log_handle.close()
            
            # Final sweep to catch any last-second text flushes
            try:
                if os.path.exists(log_file_path):
                    with open(log_file_path, "r", encoding="utf-8") as f:
                        f.seek(self.run_last_read_position)
                        final_data = f.read()
                        if final_data:
                            self.console.write(final_data, "stdout")
            except Exception:
                pass

            # Print the final exit code status
            if exit_code == 0:
                self.console.write("\nProgram is done with exit code 0\n", "system")
            else:
                self.console.write(f"\nProgram exited with code: {exit_code}\n", "stderr")
