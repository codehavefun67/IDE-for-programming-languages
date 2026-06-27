from built import *
from tkinter import Tk

if __name__ == "__main__":
  try:
    root = Tk(screenName="C++IDE", baseName="Cide")
    app = MainUI(root, 1920, 1080)
    root.mainloop()
  except Exception as e:
        print("\n" + "="*50)
        print("🚨 CRITICAL STARTUP ERROR DETECTED:")
        print("="*50)
        import traceback
        traceback.print_exc()
        print("="*50)
        input("\nPress ENTER to close this window...")