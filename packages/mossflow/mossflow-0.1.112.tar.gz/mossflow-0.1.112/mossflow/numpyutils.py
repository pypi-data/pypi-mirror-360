import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tkinter as tk
from tkinter import ttk
class Sequential_Colormaps:
    viridis='viridis'
    plasma='plasma'
    inferno='inferno'
    magma='magma'
    greys ='Greys'
    rainbow='rainbow' 
    def __init__(self):
        pass
def call_method(obj, method_name, *args, **kwargs):
    method = getattr(obj, method_name, None)
    if callable(method):
        return method(*args, **kwargs)  # 传递参数
    else:
        raise ValueError(f"Method '{method_name}' not found.")
class Generate_heatmap:
    def __init__(self,changed,colormap:str=Sequential_Colormaps.rainbow,upper_bound:float=1000, lower_bound:float=-1000,upper_colorbound:int=90,lower_colorbound:int=10):
        self.colormap=colormap
        self.upper_bound=upper_bound
        self.lower_bound=lower_bound
        self.upper_colorbound=upper_colorbound
        self.lower_colorbound=lower_colorbound
        self.propertchanged=changed
    def generate_heatmap(self,data:np.ndarray,colormap:str=Sequential_Colormaps.rainbow,upper_bound:float=1000, lower_bound:float=-1000,upper_colorbound:int=90,lower_colorbound:int=10)->np.ndarray:
    # 将浮点数数组归一化到 [0, 1] 之间
        data=np.where((data > upper_bound)|(data< lower_bound), np.nan, data)  # 将0替换为NaN
        clean_data = data[~np.isnan(data)]  # 仅保留非 NaN 值

        lower_bound = np.percentile(clean_data, lower_colorbound)
        upper_bound = np.percentile(clean_data, upper_colorbound)
        data = np.clip(data, lower_bound, upper_bound)

        normalized_data = (data - lower_bound) / (upper_bound- lower_bound)
        # 使用 matplotlib 创建热度图
        return call_method(cm,colormap,normalized_data)     # cm.plasma(normalized_data)  # 使用 Viridis 颜色映射

    def show_parameter_page(self, parent):
        frame = tk.Frame(parent)
        frame.pack(padx=10, pady=10)
        maps= ["viridis", "plasma", "inferno", "magma", "Greys","rainbow"]
        # Colormap 选择
        tk.Label(frame, text="选择 Colormap:").grid(row=0, column=0, pady=5)
        # colormap_var = tk.StringVar(value=self.colormap)
        colormap_combobox = ttk.Combobox(frame, state="readonly",values=["viridis", "plasma", "inferno", "magma", "Greys","rainbow"])
        colormap_combobox.grid(row=0, column=1, pady=5)
        colormap_combobox.current(maps.index(self.colormap))  # 设置默认值为第一个选项
        colormap_combobox.bind("<<ComboboxSelected>>",self.colormapchanged ,add=True)
        colormap_combobox.bind("<<ComboboxSelected>>", self.propertchanged,add=True)

        # 上界输入
        tk.Label(frame, text="上界:").grid(row=1, column=0, pady=5)
        upper_bound_entry = tk.Entry(frame)
        upper_bound_entry.insert(0, self.upper_bound)
        upper_bound_entry.grid(row=1, column=1, pady=5)
        upper_bound_entry.bind("<Return>", self.upper_bound_changed,add=True)
        upper_bound_entry.bind("<Return>", self.propertchanged,add=True)

        # 下界输入
        tk.Label(frame, text="下界:").grid(row=2, column=0, pady=5)
        lower_bound_entry = tk.Entry(frame)
        lower_bound_entry.insert(0, self.lower_bound)
        lower_bound_entry.grid(row=2, column=1, pady=5)
        lower_bound_entry.bind("<Return>", self.lower_bound_changed,add=True)
        lower_bound_entry.bind("<Return>", self.propertchanged,add=True)

        # 上色界限输入
        tk.Label(frame, text="上色界限:").grid(row=3, column=0, pady=5)
        upper_colorbound_entry = tk.Entry(frame)
        upper_colorbound_entry.insert(0, self.upper_colorbound)
        upper_colorbound_entry.grid(row=3, column=1, pady=5)
        upper_colorbound_entry.bind("<Return>", self.upper_colorbound_changed,add=True)
        upper_colorbound_entry.bind("<Return>", self.propertchanged,add=True)
        upper_colorbound_scale = tk.Scale(frame, from_=0, to=100, orient='horizontal', command=lambda val: upper_colorbound_entry.delete(0, tk.END) or upper_colorbound_entry.insert(0, val))
        upper_colorbound_scale.grid(row=3, column=2, padx=5)
        upper_colorbound_scale.set(self.upper_colorbound)
        upper_colorbound_scale.bind("<ButtonRelease-1>",self.upper_colorbound_scale_changed,add=True)
        upper_colorbound_scale.bind("<ButtonRelease-1>",self.propertchanged,add=True)

        # 下色界限输入
        tk.Label(frame, text="下色界限:").grid(row=4, column=0, pady=5)
        lower_colorbound_entry = tk.Entry(frame)
        lower_colorbound_entry.insert(0, self.lower_colorbound)  # 默认值
        lower_colorbound_entry.grid(row=4, column=1, pady=5)
        lower_colorbound_entry.bind("<Return>", self.lower_colorbound_changed,add=True)
        lower_colorbound_entry.bind("<Return>", self.propertchanged,add=True)
        lower_colorbound_scale = tk.Scale(frame, from_=0, to=100, orient='horizontal', command=lambda val: lower_colorbound_entry.delete(0, tk.END) or lower_colorbound_entry.insert(0, val))
        lower_colorbound_scale.grid(row=4, column=2, padx=5)
        lower_colorbound_scale.set(self.lower_colorbound)
        lower_colorbound_scale.bind("<ButtonRelease-1>",self.lower_colorbound_scale_changed,add=True)
        lower_colorbound_scale.bind("<ButtonRelease-1>",self.propertchanged,add=True)

        
        self.page=frame
        return frame
    def colormapchanged(self,event):
        self.colormap = event.widget.get()
    def upper_bound_changed(self,event):
        self.upper_bound = float(event.widget.get())
    def lower_bound_changed(self,event):
        self.lower_bound = float(event.widget.get())
    def upper_colorbound_changed(self,event):
        self.upper_colorbound = int(event.widget.get())
    def lower_colorbound_changed(self,event):
        self.lower_colorbound = int(event.widget.get())
    def upper_colorbound_scale_changed(self,event):
        self.upper_colorbound = int(event.widget.get())
    def lower_colorbound_scale_changed(self,event):
        self.lower_colorbound = int(event.widget.get())