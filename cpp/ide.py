from built import *;from built import _version_
from tkinter import Tk
import sys as s
from datetime import datetime

lsit = [
  f"Running on {s.platform.title()}",
  f"Version: {_version_}",
  f"os: Windows",
  f"dev: True",
  f"Time: {datetime.now()}"
]

if __name__ == "__main__":
    try:
        for i in lsit:
            print(i)
        root = Tk()
        app = MainUI(root, 1920, 1080) # Điều chỉnh độ phân giải phù hợp để hiển thị ban đầu
        root.title("CArt")       
        root.mainloop()
    
    except Exception as e:
        print("\n" + "="*50)
        print("🚨 CRITICAL STARTUP ERROR DETECTED:")
        print("="*50)
        import traceback
        traceback.print_exc()
        print("="*50)
        input("\nPress ENTER to close this window...")
