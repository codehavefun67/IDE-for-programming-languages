"""
Compiler for C/C++.
This module use subprocess and g++.exe, gcc.exe to compile C/C++ source code.
Anyone have bugs or exceptions can send the bug via Discord: helofj_96789.

"""
import os
from subprocess import run, TimeoutExpired

cmd = []
cmd_obj = []
compiled = False
def init():
    # Clear and populate lists to prevent duplicate additions if init is called twice
    cmd.clear()
    cmd_obj.clear()
    cmd.extend(["gcc -o {} {}", "g++ -o {} {}"])
    cmd_obj.extend(["gcc -c {} -o {}", "g++ -c {} -o {}"])

def compile(output: str, src: str, ctrl_char: str):
    global compiled
    ctrl = ctrl_char.strip()
    
    # Fix 1: Separate IF statements so compilation runs after deletion
    if os.path.exists(output):
        os.remove(output)
        
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source file not found: {src}")
        
    try:
        if ctrl == "c":
            if src.endswith(".c"):
                # Fix 2 & 3: Correct command index and proper timeout implementation
                run(cmd[0].format(output, src), shell=True, check=True, timeout=30)
            else:
                raise ValueError("File extension is not .c for C compilation")
        elif ctrl == "cpp":
            if src.endswith(".cpp"):
                run(cmd[1].format(output, src), shell=True, check=True, timeout=30)
            else:
                raise ValueError("File extension is not .cpp for C++ compilation")
        else:
            raise ValueError(f"Control character '{ctrl}' not defined")
            
    except TimeoutExpired:
        print("❌ Compilation timed out after 30 seconds.")
        return False
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        return False

    return True

def remove(*files):
    # Cleaned up loop over whatever arguments are passed
    for file in files:
        if os.path.exists(file):
            os.remove(file)  