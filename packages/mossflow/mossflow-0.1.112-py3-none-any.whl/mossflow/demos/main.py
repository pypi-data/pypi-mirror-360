from mossflow.TkinterWidgets import FlowPlane as  plane
from mossflow.TkinterWidgets import load_icon
import tkinter as tk

import sys

def on_toplevel_close():
    print("Closing Toplevel window...")
    toplevel.destroy()  # 销毁Toplevel窗口
    root.destroy()      # 销毁root窗口，这将结束mainloop()
    
root = tk.Tk()
root.withdraw()  # Hide the root window
toplevel = tk.Toplevel(root,width=800, height=600)
toplevel.iconbitmap(load_icon())  # Set the icon for the window
toplevel.title("CvFlow")
toplevel.pack_propagate(False)  # Prevent the window from resizing to fit its contents
graphics_frame = plane(toplevel)
graphics_frame.pack(fill=tk.BOTH, expand=True)
toplevel.protocol("WM_DELETE_WINDOW", on_toplevel_close)


root.mainloop() 
print("Tkinter demo finished.")