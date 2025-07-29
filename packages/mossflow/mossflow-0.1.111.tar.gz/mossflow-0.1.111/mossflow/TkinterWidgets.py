import tkinter as tk
from tkhtmlview import HTMLLabel
from tkinter import ttk,colorchooser,messagebox
from tkinter import font as tkfont
from pyopengltk import OpenGLFrame
from OpenGL.GL import *
from OpenGL.WGL import *
import tifffile as tiff
from mossflow.numpyutils import Generate_heatmap
import numpy as np
import matplotlib.pyplot as plt
from math import pi, cos, sin
from PIL import Image, ImageDraw, ImageFont
import cv2
import time
import json
from tkinter import filedialog, messagebox
import os
import importlib.util
from importlib.resources import files, as_file
from pathlib import Path

def load_icon(iconpath='main.ico'):
    try:
        # 使用files() API (Python 3.9+)
        ref = files("mossflow.resources") / f"{iconpath}"
        with as_file(ref) as icon_path:
            return str(icon_path)  # 返回绝对路径
    except Exception as e:
        print(f"加载图标失败: {e}")
        return None
iconp=load_icon()
class NumericInputPad:
    def __init__(self, root, message=None):
        self.root = root
        self.root.title("NumericInputPad")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f5f5")
        
        self.message = message
        
        # 自定义字体
        self.display_font = tkfont.Font(family="Arial", size=28, weight="bold")
        self.button_font = tkfont.Font(family="Arial", size=18)
        self.special_button_font = tkfont.Font(family="Arial", size=14)
        
        # 显示区域
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        self.display = tk.Entry(
            root,
            textvariable=self.display_var,
            font=self.display_font,
            bd=2,
            relief=tk.FLAT,
            bg="#ffffff",
            fg="#333333",
            justify="right",
            insertwidth=0,
            readonlybackground="#ffffff",
        )
        self.display.grid(row=0, column=0, columnspan=4, padx=15, pady=(20, 15), ipady=12, sticky="ew")
        
        # 按钮样式配置
        self.button_config = {
            "font": self.button_font,
            "bd": 0,
            "relief": tk.RAISED,
            "height": 1,
            "width": 4,
            "activebackground": "#e0e0e0",
            "highlightthickness": 0,
            "highlightbackground": "#cccccc"
        }
        
        # 数字按钮布局
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2),
            ('0', 4, 1), ('.', 4, 2), ('-', 4, 0),
            ('⌫', 1, 3), ('C', 2, 3), ('确定', 3, 3, 2)
        ]
        
        # 创建按钮
        for button_info in buttons:
            text = button_info[0]
            row = button_info[1]
            col = button_info[2]
            rowspan = button_info[3] if len(button_info) > 3 else 1
            
            btn_style = self.button_config.copy()
            
            if text.isdigit():
                btn_style.update({"bg": "#ffffff", "fg": "#333333"})
            elif text in ['.', '-']:
                btn_style.update({"bg": "#f0f0f0", "fg": "#666666"})
            else:
                if text == '确定':
                    btn_style.update({
                        "bg": "#4CAF50", 
                        "fg": "white", 
                        "font": self.special_button_font,
                        "height": 3
                    })
                else:
                    btn_style.update({
                        "bg": "#e0e0e0", 
                        "fg": "#333333",
                        "font": self.special_button_font
                    })
            
            button = tk.Button(root, text=text, **btn_style)
            
            if rowspan > 1:
                button.grid(row=row, column=col, rowspan=rowspan, padx=5, pady=5, sticky="nswe")
            else:
                button.grid(row=row, column=col, padx=5, pady=5)
            
            button.bind("<Button-1>", lambda e, t=text: self.on_button_click(t))
        
        # 配置网格布局权重
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        
        # 初始化输入状态
        self.current_input = "0"
        self.has_decimal = False
    
    def on_button_click(self, button_text):
        if button_text.isdigit():
            self.process_digit(button_text)
        elif button_text == '.':
            self.process_decimal()
        elif button_text == '-':
            self.process_sign()
        elif button_text == '⌫':
            self.process_backspace()
        elif button_text == 'C':
            self.process_clear()
        elif button_text == '确定':
            self.process_confirm()
    
    def process_digit(self, digit):
        if self.current_input == "0":
            self.current_input = digit
        elif self.current_input == "-0":
            self.current_input = "-" + digit
        else:
            self.current_input += digit
        self.update_display()
    
    def process_decimal(self):
        if not self.has_decimal:
            # 如果当前是"0"或"-0"，在添加小数点前不需要保留0
            if self.current_input == "0":
                self.current_input = "0."
            elif self.current_input == "-0":
                self.current_input = "-0."
            else:
                self.current_input += '.'
            self.has_decimal = True
            self.update_display()
    
    def process_sign(self):
        if self.current_input.startswith('-'):
            self.current_input = self.current_input[1:]
        else:
            if self.current_input != "0":
                self.current_input = '-' + self.current_input
        self.update_display()
    
    def process_backspace(self):
        if len(self.current_input) > 1:
            # 检查是否删除了小数点
            if self.current_input[-1] == '.':
                self.has_decimal = False
            self.current_input = self.current_input[:-1]
            
            # 处理删除负号后的情况
            if self.current_input == "-":
                self.current_input = "0"
        else:
            self.current_input = "0"
            self.has_decimal = False
        
        self.update_display()
    
    def process_clear(self):
        self.current_input = "0"
        self.has_decimal = False
        self.update_display()
    
    def process_confirm(self):
        if self.message is None:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_input)
            messagebox.showinfo("Copy!", "Copied to clipboard!")
            self.root.destroy()  # 关闭数字键盘窗口   
            return
        else:
            self.message(self.current_input)
        self.root.destroy()  # 关闭数字键盘窗口
    def update_display(self):
        # 确保显示格式正确
        display_text = self.current_input
        
        # 处理".x"显示为"0.x"的情况
        if display_text.startswith('.') or (display_text.startswith('-') and display_text[1] == '.'):
            if display_text.startswith('-'):
                display_text = "-0" + display_text[1:]
            else:
                display_text = "0" + display_text
        
        # 处理只有负号的情况
        if display_text == "-":
            display_text = "-0"
        
        # 处理"-0"后面跟着数字的情况
        if display_text.startswith("-0") and len(display_text) > 2 and display_text[2] != '.':
            display_text = "-" + display_text[2:]
        
        # 更新显示和内部状态
        self.display_var.set(display_text)
        self.current_input = display_text
class IconCombo:
    def __init__(self,parent,defultlange,callback = None):
        self.langselector = ttk.Combobox(parent, state="readonly",values=['zh','en'], width=6)
        self.langselector.set(defultlange)
        self.langselector.pack(side='right', anchor='ne', padx=0, pady=0)
        self.langselector.bind("<<ComboboxSelected>>", callback)
    @classmethod
    def show(cls, parent, defultlange, callback=None):
        """显示语言选择窗口"""
        cls.instance = cls(parent, defultlange, callback)
        return cls.instance.langselector
class PlaceholderEntry(ttk.Frame):
    """
    一个带提示文字的输入框组件（基于Frame封装）
    - 支持 placeholder 提示
    - 支持 ttk 样式
    - 提供 get()/set() 方法操作文本
    """
    def __init__(self, master, placeholder="", **kwargs):
        super().__init__(master)
        
        # 默认配置
        self.placeholder = placeholder
        self.entry_var = tk.StringVar()
        
        # 创建 ttk 样式
        self.style = ttk.Style()
        self.style.configure("Placeholder.TEntry", foreground="grey")
        self.style.configure("Normal.TEntry", foreground="black")
        
        # 创建输入框
        self.entry = ttk.Entry(
            self,
            textvariable=self.entry_var,
            style="Placeholder.TEntry",
            **kwargs
        )
        self.entry.pack(fill="both", expand=True)
        
        # 初始化提示文字
        self._show_placeholder()
        
        # 绑定事件
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _show_placeholder(self):
        """显示提示文字"""
        self.entry_var.set(self.placeholder)
        self.entry.config(style="Placeholder.TEntry")
    
    def _hide_placeholder(self):
        """隐藏提示文字"""
        if self.entry_var.get() == self.placeholder:
            self.entry_var.set("")
        self.entry.config(style="Normal.TEntry")
    
    def _on_focus_in(self, event):
        """获得焦点时隐藏提示"""
        if self.entry_var.get() == self.placeholder:
            self._hide_placeholder()
    
    def _on_focus_out(self, event):
        """失去焦点时显示提示（如果内容为空）"""
        if not self.entry_var.get():
            self._show_placeholder()
    
    def get(self):
        """获取输入内容（自动过滤提示文字）"""
        text = self.entry_var.get()
        return "" if text == self.placeholder else text
    
    def set(self, text):
        """设置输入内容"""
        self.entry_var.set(text)
        self.entry.config(style="Normal.TEntry")
class FlowPlane(OpenGLFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 语言设置
        self.language = 'zh'
        # 外观设置
        self.background_color = [0.11, 0.13, 0.22, 1.0]
        self.drawobjects = {}
        self.selectobjects = []
        # 部件初始化
        self.infolabel = tk.Label(self, text="Information", bg="black", fg="white")
        self.infolabel.pack(side='left',anchor='nw', padx=0, pady=0)
        self.infolabel.bind("<Double-Button-1>", self.copy_to_clipboard)
        # 动画使能
        self.animate = True
        # 窗口大小
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        # 缩放和位置变量
        self.scale = 1.0
        self.min_scale = 0.01
        self.max_scale = 100.0
        self.offset_x = 0#self.width / 2
        self.offset_y = 0#self.height / 2
        self.rotation_angle = 0  # 旋转角度（弧度）       
        # 鼠标跟踪
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.current_mouse_x = 0
        self.current_mouse_y = 0
        self.curent_img_x = 0
        self.curent_img_y = 0
        self.dragging = False     
        # 绑定事件
        self.bind("<Motion>", self.on_mouse_move)  # 鼠标移动事件
        self.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.bind("<Button-4>", self.on_mouse_wheel)    # Linux上滚
        self.bind("<Button-5>", self.on_mouse_wheel)    # Linux下滚
        self.bind("<ButtonPress-3>", self.on_button3_press) # 右键按下事件
        self.bind("<ButtonPress-2>", self.on_button2_press) # 中键按下事件
        self.bind("<B3-Motion>", self.on_mouseright_drag) # 右键拖动事件
        self.bind("<ButtonRelease-3>", self.on_button3_release) # 右键释放事件
        self.bind("<Button-1>", self.on_mouseleft_click)  # 左键单击事件
        self.bind("<Double-Button-1>", self.on_mouseleftdouble_click) # 左键双击事件
        self.bind("<Double-Button-3>", self.on_mouselrightdouble_click) # 右键双击事件

        self.bind("<Configure>", self.on_resize) # 窗口大小变化事件
        self.bind("<F5>", self.on_f5)  # F5键事件
        self.bind("<Delete>", self.on_delete)  # Delete键事件
        # 上下文菜单字典
        self.texts = {
            'zh':{
                'update_drawobjects_msg_title': "更新模块",
                'update_drawobjects_msg_content': "模块已存在，是否覆盖？",
                'update_drawobjects_msg_error': "模块名称不能为空。",
                'on_confirmbuttonclick_errormsg_title': "错误",
                'on_confirmbuttonclick_errormsg_content': "设置输入失败，请检查参数。",
                'add': "模块",
                'openfile': "打开文件",
                'langeuage': "语言",
                'setting': "设置",
                'file': "文件",
                'tiff': "TIFF",
                'loadtiff': "加载TIFF",
                'link': "链接",
                'basicline': "链接",
                'ifline': "条件分支",
                'script': "脚本",
                'tool': '工具',
                'calculator': "计算器",
                'numberkeyboard': "数字键盘",
            },
            'en':{
                'update_drawobjects_msg_title': "Update Module",
                'update_drawobjects_msg_content': "Module already exists. Overwrite?",
                'update_drawobjects_msg_error': "Module name cannot be empty.",
                'on_confirmbuttonclick_errormsg_title': "Error",
                'on_confirmbuttonclick_errormsg_content': "Failed to set input, please check parameters.",
                'add': "Module",
                'openfile': "Open File",
                'langeuage': "Language",
                'setting': "Settings",
                'file': "File",
                'tiff': "TIFF",
                'loadtiff': "Load TIFF",
                'link': "Link",
                'basicline': "Basic Line",
                'ifline': "If Line",
                'script': "Script",
                'tool': 'Tool',
                'calculator': "Calculator",
                'numberkeyboard': "Numeric Pad",
            }
        }
        # 上下文菜单
        self.context_menu = tk.Menu(self, tearoff=0)
        
        self.setting_menu = tk.Menu(self.context_menu, tearoff=0)
        self.add_menu = tk.Menu(self.context_menu, tearoff=0)
        self.link_menu = tk.Menu(self.context_menu, tearoff=0)
        self.tool_menu = tk.Menu(self.context_menu, tearoff=0)
        
        self.file_menu = tk.Menu(self.add_menu, tearoff=0)       
        self.tiff_menu = tk.Menu(self.add_menu, tearoff=0)
        
        self.setting_menu.add_cascade(label=self.texts[self.language]['langeuage'],command=lambda: IconCombo.show(self,defultlange=self.language,callback=self.on_language_change))  
        self.tool_menu.add_cascade(label=self.texts[self.language]['numberkeyboard'], command=lambda : NumericInputPad(self.crate_numericpad()))  # 添加计算器工具
        
        self.file_menu.add_cascade(label=self.texts[self.language]['openfile'], command=lambda : self.update_drawobjects(Graphics_OpenFileModule.from_userdefined(self,self.curent_img_x,self.curent_img_y,name=self.texts[self.language]['openfile'],message=self.on_message)))          
        self.tiff_menu.add_cascade(label=self.texts[self.language]['loadtiff'], command=lambda : self.update_drawobjects(Graphics_TiffModule.from_userdefined(self,self.curent_img_x,self.curent_img_y,name=self.texts[self.language]['loadtiff'],message=self.on_message)))
        self.link_menu.add_cascade(label=self.texts[self.language]['basicline'], command=lambda : self.update_drawobjects(Grpahics_WrapLineModule.from_userdefined(self,self.curent_img_x,self.curent_img_y,name=self.texts[self.language]['basicline'],message=self.on_message)))
        self.link_menu.add_cascade(label=self.texts[self.language]['ifline'], command=lambda : self.update_drawobjects(Grpahics_WrapIfLineModule.from_userdefined(self,self.curent_img_x,self.curent_img_y,name=self.texts[self.language]['ifline'],message=self.on_message)))  
            
        self.add_menu.add_cascade(label=self.texts[self.language]['file'], menu=self.file_menu)
        self.add_menu.add_cascade(label=self.texts[self.language]['tiff'], menu=self.tiff_menu)
        self.add_menu.add_cascade(label=self.texts[self.language]['script'], command=lambda :self.on_addscript())
        
        
        self.context_menu.add_cascade(label=self.texts[self.language]['setting'], menu=self.setting_menu)
        self.context_menu.add_cascade(label=self.texts[self.language]['add'], menu=self.add_menu)        
        self.context_menu.add_cascade(label=self.texts[self.language]['link'], menu=self.link_menu)
        self.context_menu.add_cascade(label=self.texts[self.language]['tool'], menu=self.tool_menu)
    def crate_numericpad(self):
        numericpad = tk.Toplevel(self)
        rootx = self.winfo_rootx()+self.winfo_width() - 370
        rooty = self.winfo_rooty()+self.winfo_height() - 500
        numericpad.geometry(f"360x480+{rootx}+{rooty}")      
        return numericpad
    def on_addscript(self):
        file_path = filedialog.askopenfilename(
            title="Open Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            spec = importlib.util.spec_from_file_location(f'{module_name}', file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            my_class = getattr(module, module_name)()
            rawname = getattr(my_class, 'rawname')
            zhname = getattr(my_class,'zhname')
            enname = getattr(my_class,'enname')
            self.texts['zh'][rawname] = zhname
            self.texts['en'][rawname] = enname
            self.update_drawobjects(my_class.from_userdefined(self,self.curent_img_x,self.curent_img_y,name=self.texts[self.language][rawname],message=self.on_message))
            # 这里可以添加后续处理代码，比如显示内容或进一步操作
    def on_language_change(self,event):
        """语言切换"""
        self.language = event.widget.get()  # 获取当前选择的语言
        for obj in self.drawobjects.values():
            if hasattr(obj, "language"):
                obj.language=self.language   
        event.widget.destroy()  # 销毁语言选择组件
        
        pass
    def update_drawobjects(self,module):
        """更新绘图对象"""
        keys = list(self.drawobjects.keys())
        if module.text in keys:
            if not messagebox.askyesno(self.texts[self.language]['update_drawobjects_msg_title'], self.texts[self.language]['update_drawobjects_msg_content']):
                return
            # If user selects Yes, allow overwrite (do nothing here, will overwrite below)
        else:
            if module.text == "":
                messagebox.showerror(self.texts[self.language]['update_drawobjects_msg_title'], self.texts[self.language]['update_drawobjects_msg_error'])
                return
        self.drawobjects[module.text] = module      
    # region Gobal Functions
    def on_message(self,module,operationcode:int,**kwargs):
        def on_objectselection(event):
            selected_index = modulecombo.current()
            if selected_index != -1:
                paramcombo['values'] = list(self.drawobjects[modulecombo.get()].parameters.keys())  # 更新输出选项
        def on_outputselection(event):
            pass
        def on_confirmbuttonclick(event):
            try:           
                selected_index = modulecombo.current()
                if selected_index != -1 and operationcode == 1:
                    paramname= kwargs['paramname']
                    keyname = kwargs['keyname']
                    setattr(module, paramname,self.drawobjects[modulecombo.get()]) # 赋值模块
                    setattr(module, keyname,paramcombo.get()) # 赋值模块
                    
                    kwargs['button'].config(text=f"{paramname}:   {getattr(module,paramname).text}\n    {gstr(getattr(module,keyname))}")  # 更新按钮文本
                    
                    window.destroy()
            except Exception as e:
                messagebox.showerror(self.texts['on_confirmbuttonclick_errormsg_title'], self.texts['on_confirmbuttonclick_errormsg_content'] + f"\n{e}")
        # 删除模块
        if operationcode == -1:
            del self.drawobjects[module.text]
            del module
            return
        # 修改模块名称
        if operationcode == -2:
            first_key = next((k for k, v in self.drawobjects.items() if v == module), None)
            self.drawobjects[module.text] = self.drawobjects.pop(first_key)  # 取出旧键值并赋给新键
            return
        elif operationcode == 1:
            pass
        window= tk.Toplevel(self)
        window.iconbitmap(iconp)  # 设置窗口图标
        
        modulecombo = ttk.Combobox(window, values=[key for key in self.drawobjects.keys() if not isinstance(self.drawobjects[key], (Grpahics_WrapIfLineModule,Grpahics_WrapLineModule))], state="readonly")
        modulecombo.bind("<<ComboboxSelected>>", on_objectselection)  # 绑定选择事件
        modulecombo.grid(column=0,row=0,pady=1)
        paramcombo = ttk.Combobox(window)
        paramcombo.bind("<<ComboboxSelected>>", on_outputselection)  # 绑定选择事件
        paramcombo.grid(column=0,row=1,pady=1)        
        confirmbutton = tk.Button(window, text="Confirm")
        confirmbutton.bind("<Button-1>", on_confirmbuttonclick)  # 绑定单击事件
        confirmbutton.grid(column=0,row=2,pady=1)
    def copy_to_clipboard(self,evetn):
        # 清空剪切板并复制标签内容
        self.clipboard_clear()
        self.clipboard_append(self.infolabel.cget("text"))
        messagebox.showinfo("Copy!", "Copied to clipboard!")
    # endregion
    # region GL functions
    def on_resize(self, event):
        try:
            self.tkMakeCurrent()
            self.width = event.width
            self.height = event.height

            # 防止初始化为0大小
            if self.width < 1 or self.height < 1:
                self.width, self.height = 800, 800
            glViewport(0, 0, self.width, self.height)
        except Exception as e:
            pass
        # version = glGetString(GL_VERSION)
        # if version:
        #     try:
        #         glViewport(0, 0, self.width, self.height)
        #     except Exception as e:
        #         messagebox.askquestion('Error',f"Error updating viewport: {e}", icon='error')
    def initgl(self):
        """初始化OpenGL和加载纹理"""
        self.tkMakeCurrent()
        glClearColor(self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3])
        # self.load_texture()     
    def redraw(self):
        """渲染纹理四边形"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3])

        if True:            
            # 设置投影矩阵
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(-self.width/2, self.width/2, self.height/2, -self.height/2,-1,1)
            
            # 设置模型视图矩阵
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # 应用缩放和平移
            glTranslatef(self.offset_x,self.offset_y, 0)
            glScalef(self.scale, self.scale, 1)
            glRotatef(self.rotation_angle*(180/pi), 0, 0, 1)
            keys = list(self.drawobjects.keys())
            for i,key in enumerate(keys):
                self.drawobjects[key].GLDraw()
            glColor3f(1.0, 1.0, 1.0)

    # endregion
    # region Mouse Event
    def on_mouse_move(self, event):
        """处理鼠标移动事件"""
        self.current_mouse_x = event.x
        self.current_mouse_y = event.y
        imgpos= self.WindowPos2GLPos(self.current_mouse_x, self.current_mouse_y)
        self.curent_img_x = imgpos[0]
        self.curent_img_y = imgpos[1]
        #self.infolabel.config(text= f"GLPosition {self.curent_img_x:.2f}, {self.curent_img_y:.2f},\nScale: {self.scale:.2f}, \nOffset: ({self.offset_x:.2f}, {self.offset_y:.2f})")
    def on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # 确定缩放方向
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):  # 上滚/放大
            zoom_factor = 1.1
        else:  # 下滚/缩小
            zoom_factor = 0.9
        
        # 应用缩放限制
        new_scale = self.scale * zoom_factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        
        self.scale = new_scale
        self.redraw() 
    def on_button3_press(self, event):
        """开始拖动"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.dragging = True
    def on_button2_press(self, event):
        self.tkMakeCurrent()
        glViewport(0, 0, self.width, self.height)
        self.reset_view()
        self.redraw()
    def on_mouseright_drag(self, event):
        """处理拖动"""
        if self.dragging and len(self.selectobjects)== 0:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            
            self.offset_x += dx
            self.offset_y += dy

            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            self.redraw()
        if self.dragging and len(self.selectobjects) > 0:
            lastglx,lastgly= self.WindowPos2GLPos(self.last_mouse_x, self.last_mouse_y)
            curglx,curgly= self.WindowPos2GLPos(event.x, event.y)
            for i in range(len(self.selectobjects)):
                self.selectobjects[i].x += curglx - lastglx
                self.selectobjects[i].y += curgly - lastgly
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            self.redraw()
    def on_mouseleft_click(self,event):
        """处理左键单击事件"""
        self.focus_force()
        # 获取鼠标在窗口中的位置
        mouse_x = event.x
        mouse_y = event.y
        keys = list(self.drawobjects.keys())
        for i,key in enumerate(keys):
            self.drawobjects[key].status = 'Normal'
        self.selectobjects.clear()
        # 计算鼠标在图片坐标系中的位置
        mouse_x_imgsystem,mouse_y_imgsystem= self.WindowPos2GLPos(mouse_x, mouse_y)
        for i,key in enumerate(keys):
            tryselectobjs= self.drawobjects[key].contains(mouse_x_imgsystem, mouse_y_imgsystem)
            if tryselectobjs is not None: 
                if isinstance(tryselectobjs, list):
                    self.selectobjects.extend(tryselectobjs)
                else:
                    self.selectobjects.append(tryselectobjs)
                self.infolabel.config(text= tryselectobjs.moudlestatus)
                break
            else:
                self.drawobjects[key].status = 'Normal'
        self.redraw()       
    def on_button3_release(self, event):
        """结束拖动"""
        self.dragging = False
    def on_mouseleftdouble_click(self,event):
        """处理左键双击事件"""
        # 打开上下文菜单
        # 获取鼠标在窗口中的位置
        mouse_x = event.x
        mouse_y = event.y
        keys = list(self.drawobjects.keys())
        for i,key in enumerate(keys):
            self.drawobjects[key].status = 'Normal'
        self.selectobjects.clear()
        # 计算鼠标在图片坐标系中的位置
        mouse_x_imgsystem,mouse_y_imgsystem= self.WindowPos2GLPos(mouse_x, mouse_y)
        for i,key in enumerate(keys):
            self.drawobjects[key].show_parameter_page(mouse_x_imgsystem, mouse_y_imgsystem,self)    
    def on_mouselrightdouble_click(self,event):
        """处理右键双击事件"""
        # 打开上下文菜单
        self.context_menu.entryconfig(0, label=self.texts[self.language]['setting'])
        self.context_menu.entryconfig(1, label=self.texts[self.language]['add'])
        self.context_menu.entryconfig(2, label=self.texts[self.language]['link'])   
        self.context_menu.entryconfig(3, label=self.texts[self.language]['tool'])
        
        self.tool_menu.entryconfig(0, label=self.texts[self.language]['numberkeyboard'])
        
        self.setting_menu.entryconfig(0, label=self.texts[self.language]['langeuage'])
        self.add_menu.entryconfig(0, label=self.texts[self.language]['file'])
        self.add_menu.entryconfig(2, label=self.texts[self.language]['script'])

        self.file_menu.entryconfig(0, label=self.texts[self.language]['openfile'])
        self.tiff_menu.entryconfig(0, label=self.texts[self.language]['loadtiff'])
        
        self.link_menu.entryconfig(0, label=self.texts[self.language]['basicline'])
        self.link_menu.entryconfig(1, label=self.texts[self.language]['ifline'])
        
        self.context_menu.post(event.x_root, event.y_root)    
    # endregion
    # region Keyboard Event
    def on_f5(self,event):
        """处理F5键事件"""
        if len(self.selectobjects)>0:
            for i in range(len(self.selectobjects)):
                self.selectobjects[i].run()
                self.infolabel.config(text= self.selectobjects[i].moudlestatus)
    def on_delete(self,event):
        """处理Delete键事件"""
        if len(self.selectobjects)>0:
            if tk.messagebox.askokcancel("Delete", "Are you sure you want to delete these modules?"):
                for i in range(len(self.selectobjects)):
                    del self.drawobjects[self.selectobjects[i].text]
                    del self.selectobjects[i]
                self.redraw()
    # endregion
    # region View Functions
    def reset_view(self):
        self.scale = 1.0
        self.offset_x = 0#self.width / 2
        self.offset_y = 0#self.height / 2
        self.curent_img_x =0
        self.curent_img_y =0
        self.current_mouse_x =0
        self.current_mouse_y =0
        self.redraw()
    def GLPos2WindowPos(self, x, y):
        """将图片坐标转换为窗口坐标，考虑旋转"""
        affine_matrix = np.array([
        [self.scale * cos(self.rotation_angle), -self.scale * sin(self.rotation_angle), self.offset_x],
        [self.scale * sin(self.rotation_angle), self.scale * cos(self.rotation_angle), self.offset_y],
        [0, 0, 1]])
        point = np.array([x, y, 1])
        transformed_point = np.dot(affine_matrix, point)
        return transformed_point[0]+self.width/2, transformed_point[1]+self.height/2
    def WindowPos2GLPos(self, x, y):
        """将窗口坐标转换为图片坐标，考虑旋转"""
        # 减去偏移
        x = x - self.width/2
        y = y - self.height/2
        affine_matrix = np.array([
        [self.scale * cos(self.rotation_angle), -self.scale * sin(self.rotation_angle), self.offset_x],
        [self.scale * sin(self.rotation_angle), self.scale * cos(self.rotation_angle), self.offset_y],
        [0, 0, 1]])
        point = np.array([x, y, 1])
        affine_matrix_inv=np.linalg.inv(affine_matrix)
        # 反向旋转
        transformed_point = np.dot(affine_matrix_inv, point)
        return transformed_point[0], transformed_point[1]
    # endregion
class TiffGLFrame(OpenGLFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.img_data=None
        self.img_texture_data=None

        self.infolabel = tk.Label(self, text="Information", bg="black", fg="white")
        self.infolabel.pack(anchor='nw', padx=10, pady=10)
        self.infolabel.bind("<Double-Button-1>", self.copy_to_clipboard)

        self.texture_id = None

        self.animate = True

        self.width = self.winfo_width()
        self.height = self.winfo_height()
        # 缩放和位置变量
        self.scale = 1.0
        self.min_scale = 0.01
        self.max_scale = 100.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # 鼠标跟踪
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.current_mouse_x = 0
        self.current_mouse_y = 0
        self.curent_img_x = 0
        self.curent_img_y = 0
        self.dragging = False
        
        # 绑定事件
        self.bind("<Motion>", self.on_mouse_move)  # 鼠标移动事件
        self.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.bind("<Button-4>", self.on_mouse_wheel)    # Linux上滚
        self.bind("<Button-5>", self.on_mouse_wheel)    # Linux下滚
        self.bind("<ButtonPress-1>", self.on_button1_press)
        self.bind("<ButtonPress-2>", self.on_button2_press)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<Configure>", self.on_resize)
    def copy_to_clipboard(self,evetn):
        # 清空剪切板并复制标签内容
        self.clipboard_clear()
        self.clipboard_append(self.infolabel.cget("text"))
        messagebox.showinfo("Copy!", "Copied to clipboard!")
    def on_resize(self, event):
        """处理窗口大小变化"""
        self.tkMakeCurrent()
        self.width = event.width
        self.height = event.height
        
        # 防止初始化为0大小
        if self.width < 1 or self.height < 1:
            self.width, self.height = 800, 800
        version = glGetString(GL_VERSION)
        if version:
            try:
                glViewport(0, 0, self.width, self.height)
            except Exception as e:
                messagebox.askquestion('Error',f"Error updating viewport: {e}", icon='error')
    def initgl(self):
        """初始化OpenGL和加载纹理"""
        self.tkMakeCurrent()
        glClearColor(0.2, 0.2, 0.2, 1.0)
        # self.load_texture()     
    def load_texture(self,width:int,height:int,img_texture_data:np.ndarray,format,pixel_format):
        """加载图片并创建OpenGL纹理"""
        try:
            if hasattr(self, 'texture_id') and self.texture_id is not None:glDeleteTextures(1, [self.texture_id])
            self.tkMakeCurrent()
            self.img_texture_data = img_texture_data
            self.texture_id = glGenTextures(1)

            glBindTexture(GL_TEXTURE_2D, self.texture_id)            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            

            
            glTexImage2D(GL_TEXTURE_2D, 0, format, width, height,
                         0, format, pixel_format, img_texture_data)
            
            self.img_width = width
            self.img_height = height

        except Exception as e:
            messagebox.askquestion('Error',f"Error updating viewport: {e},\n,{glGetError()}", icon='error')

            self.texture_id = None      
    def redraw(self):
        """渲染纹理四边形"""
        # wglMakeCurrent(self.winfo_id(), wglCreateContext(self.winfo_id))  # 设置当前上下文

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.2, 0.2, 0.2, 1.0)

        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            
            # 设置投影矩阵
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0, self.width, self.height, 0,-1,1)
            
            # 设置模型视图矩阵
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # 应用缩放和平移
            glTranslatef(self.offset_x,self.offset_y, 0)
            glScalef(self.scale, self.scale, 1)
            
            #glTranslatef(self.offset_x, self.offset_y, 0)

            # 绘制纹理四边形
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(0, 0)
            glTexCoord2f(1, 0); glVertex2f(self.img_width, 0)
            glTexCoord2f(1, 1); glVertex2f(self.img_width, self.img_height)
            glTexCoord2f(0, 1); glVertex2f(0, self.img_height)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)

            glBegin(GL_LINES)
            glColor3f(1.0, 0.0, 0.0)  # 设置线条颜色为红色 (R,G,B)
            # 定义线条的两个端点
            glVertex2f(0, 0)  # 起点 (x1, y1)
            glVertex2f(0, 100)    # 终点 (x2, y2)
            glColor3f(0.0, 0.0, 1.0)  # 设置线条颜色为红色 (R,G,B)
            glVertex2f(0, 0)  # 起点 (x1, y1)
            glVertex2f(100, 0) 
            glEnd()
            glColor3f(1.0, 1.0, 1.0)
    def on_mouse_move(self, event):
        """处理鼠标移动事件"""
        self.current_mouse_x = event.x
        self.current_mouse_y = event.y


        imgpos= self.WindowPos2ImagePos(self.current_mouse_x, self.current_mouse_y)
        self.curent_img_x = imgpos[0]
        self.curent_img_y = imgpos[1]
        if self.img_data is not None:
            self.curent_img_x = 0  if self.curent_img_x> self.img_width-1 or self.curent_img_x<0 else self.curent_img_x
            self.curent_img_y = 0  if self.curent_img_y> self.img_height-1 or self.curent_img_y<0 else self.curent_img_y
            currentvalue= self.img_data[int(self.curent_img_y), int(self.curent_img_x)]
            self.infolabel.config(text= f"CurrentPosition {self.curent_img_x:.2f}, {self.curent_img_y:.2f},\nImageValue {currentvalue}\nScale: {self.scale:.2f}, \nOffset: ({self.offset_x:.2f}, {self.offset_y:.2f})\nSize: ({self.img_width}, {self.img_height})")
    def on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # 获取鼠标在窗口中的位置
        mouse_x = event.x
        mouse_y = event.y
        
        # 计算鼠标在图片坐标系中的位置
        mouse_x_imgsystem = self.WindowPos2ImagePos(mouse_x, mouse_y)[0]
        mouse_y_imgsystem = self.WindowPos2ImagePos(mouse_x, mouse_y)[1]
        
        
        # 确定缩放方向
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):  # 上滚/放大
            zoom_factor = 1.1
        else:  # 下滚/缩小
            zoom_factor = 0.9
        
        # 应用缩放限制
        new_scale = self.scale * zoom_factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        newmouse_x_windowsystem = mouse_x_imgsystem * (new_scale -self.scale)
        newmouse_y_windowsystem = mouse_y_imgsystem * (new_scale -self.scale)



        # 计算新的偏移量，使鼠标位置保持在同一图片点上
        

        self.offset_x = -newmouse_x_windowsystem + self.offset_x
        self.offset_y = -newmouse_y_windowsystem + self.offset_y
        
        self.scale = new_scale
        self.redraw() 
    def on_button1_press(self, event):
        """开始拖动"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.dragging = True
    def on_button2_press(self, event):
        self.reset_view()
        self.redraw()
    def on_mouse_drag(self, event):
        """处理拖动"""
        if self.dragging:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            self.offset_x += dx
            self.offset_y += dy
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            self.redraw()
    def reset_view(self):
        if self.width / self.height > 1:
            self.scale = self.height / self.img_height
            self.offset_x = (self.width - self.img_width * self.scale) / 2
            self.offset_y = 0
            self.curent_img_x =0
            self.curent_img_y =0
            self.current_mouse_x =0
            self.current_mouse_y =0
        else:
            self.scale = self.width / self.img_width
            self.offset_x = 0
            self.offset_y = (self.height - self.img_height * self.scale) / 2
            self.curent_img_x =0
            self.curent_img_y =0
            self.current_mouse_x =0
            self.current_mouse_y =0
        self.redraw()
    def on_button_release(self, event):
        """结束拖动"""
        self.dragging = False
    def ImagePos2WindowPos(self, x, y):
        """将图片坐标转换为窗口坐标"""
        window_x = x * self.scale + self.offset_x
        window_y = y * self.scale + self.offset_y
        return window_x, window_y
    def WindowPos2ImagePos(self, x, y):
        """将窗口坐标转换为图片坐标"""
        image_x = (x - self.offset_x) / self.scale
        image_y = (y - self.offset_y) / self.scale
        return image_x, image_y
class TiffViewer(tk.Toplevel):
    def __init__(self,mainwindow):
        super().__init__(mainwindow)
        self.img_data = None
        self.img_texture_data = None
        self.rawimg = None
        self.pixel_format = None
        self.format = None
        self.title("Image Viewer")
        self.pack_propagate(False)  # 防止窗口大小自动调整
        self.geometry("800x800")
        self.gl_frame = TiffGLFrame(self)
        self.gl_frame.pack(fill=tk.BOTH, expand=True)
        self.context_menu = tk.Menu(self, tearoff=0)
        sub_file_menu = tk.Menu(self.context_menu, tearoff=0)
        sub_file_menu.add_command(label="Open", command=self.open_file)
        sub_file_menu.add_command(label="Save", command=self.save_image)
        self.context_menu.add_cascade(label="File", menu=sub_file_menu)   
        self.sampling_rate = 1
        sub_heatmaptexture_menu = tk.Menu(self.context_menu, tearoff=0)
        sub_heatmaptexture_menu.add_command(label="Heatmap", command=self.set_texture_heatmap)
        sub_heatmaptexture_menu.add_command(label="Raw", command=self.set_texture_raw)
        self.context_menu.add_cascade(label="Texture", menu=sub_heatmaptexture_menu)
        sub_samplingrate_menu = tk.Menu(self.context_menu, tearoff=0)
        sub_samplingrate_menu.add_command(label="1/1", command=lambda: self.on_sampleing_rate(1))
        sub_samplingrate_menu.add_command(label="1/2", command=lambda: self.on_sampleing_rate(2))
        sub_samplingrate_menu.add_command(label="1/4", command=lambda: self.on_sampleing_rate(4))
        sub_samplingrate_menu.add_command(label="1/8", command=lambda: self.on_sampleing_rate(8))
        sub_samplingrate_menu.add_command(label="1/16", command=lambda: self.on_sampleing_rate(16))
        self.context_menu.add_cascade(label="SamplingRate", menu=sub_samplingrate_menu)
        self.heatmap= Generate_heatmap(self.propertchanged)
        self.bind("<Button-3>", self.on_context_menu)
    def on_sampleing_rate(self,rate:int):
        self.sampling_rate = rate
        self.img_data = self.rawimg[::self.sampling_rate, ::self.sampling_rate]
        self.gl_frame.img_data= self.img_data
        if self.img_texture_data is not None:
            self.pixel_format = GL_FLOAT
            self.format = GL_RGBA
            self.gl_frame.img_data= self.img_data
            self.img_texture_data = self.heatmap.generate_heatmap(self.img_data,self.heatmap.colormap,self.heatmap.upper_bound,self.heatmap.lower_bound,self.heatmap.upper_colorbound,self.heatmap.lower_colorbound)
        else:
            self.pixel_format = GL_FLOAT
            self.format = GL_LUMINANCE
            self.gl_frame.img_data= self.img_data
            self.img_texture_data = self.img_data
        self.gl_frame.load_texture(self.img_data.shape[1], self.img_data.shape[0], self.img_texture_data, self.format, self.pixel_format)
        self.gl_frame.reset_view()
    def on_context_menu(self,event):
        # 显示上下文菜单
        self.context_menu.post(event.x_root, event.y_root)
    def save_image(self):
        """保存当前纹理为图片文件"""
        if self.img_texture_data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                try:
                    plt.imsave(file_path, np.squeeze(self.img_texture_data),format='png',cmap=self.heatmap.colormap)
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")
        else:
            messagebox.showwarning("Warning", "No image to save!")
    def open_file(self):
        """打开文件对话框，选择图片文件"""
        file_path = filedialog.askopenfilename(title="选择一个图片文件", filetypes=[("TIFF files", "*.tiff;*.tif")])
        if file_path:
            try:
                self.rawimg = tiff.imread(file_path)
                if self.rawimg.ndim == 3:
                    self.rawimg = self.rawimg[:, :, 0]  # 取第一个通道
                    self.format = GL_LUMINANCE
                    self.img_data = self.rawimg[::self.sampling_rate, ::self.sampling_rate]
                    self.pixel_format =GL_FLOAT
                    self.img_data = np.expand_dims(self.img_data, axis=-1)  # 添加一个维度以匹配GL_LUMINANCE的要求
                elif self.rawimg.ndim == 2:
                    self.format = GL_LUMINANCE
                    self.img_data = self.rawimg[::self.sampling_rate, ::self.sampling_rate]
                    self.pixel_format =GL_FLOAT
                    self.img_data = np.expand_dims(self.img_data, axis=-1)
                else:
                    raise ValueError(f"Unsupported image dim")
                self.gl_frame.img_data= self.img_data
                self.gl_frame.load_texture(self.img_data.shape[1], self.img_data.shape[0], self.img_data, self.format, self.pixel_format)
                self.gl_frame.reset_view()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
    def open_filepath(self,file_path:str):
        """打开文件对话框，选择图片文件"""
        if file_path:
            try:
                self.rawimg = tiff.imread(file_path)
                if self.rawimg.ndim == 3:
                    self.rawimg = self.rawimg[:, :, 0]  # 取第一个通道
                    self.format = GL_LUMINANCE
                    self.img_data = self.rawimg[::self.sampling_rate, ::self.sampling_rate]
                    self.pixel_format =GL_FLOAT
                    self.img_data = np.expand_dims(self.img_data, axis=-1)  # 添加一个维度以匹配GL_LUMINANCE的要求
                elif self.rawimg.ndim == 2:
                    self.format = GL_LUMINANCE
                    self.img_data = self.rawimg[::self.sampling_rate, ::self.sampling_rate]
                    self.pixel_format =GL_FLOAT
                    self.img_data = np.expand_dims(self.img_data, axis=-1)
                else:
                    raise ValueError(f"Unsupported image dim")
                self.gl_frame.img_data= self.img_data
                self.gl_frame.load_texture(self.img_data.shape[1], self.img_data.shape[0], self.img_data, self.format, self.pixel_format)
                self.gl_frame.reset_view()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
    def set_texture_heatmap(self):
        pagemaster = tk.Toplevel(self)
        pagemaster.title("Heatmap Parameter Page")
        self.page = self.heatmap.show_parameter_page(pagemaster)
        self.img_texture_data = self.heatmap.generate_heatmap(self.img_data,self.heatmap.colormap,self.heatmap.upper_bound, self.heatmap.lower_bound,self.heatmap.upper_colorbound,self.heatmap.lower_colorbound)
        self.pixel_format = GL_FLOAT
        self.format = GL_RGBA
        self.gl_frame.img_data= self.img_data
        self.gl_frame.load_texture(self.img_data.shape[1], self.img_data.shape[0], self.img_texture_data, self.format, self.pixel_format)
    def propertchanged(self,event):
        self.gl_frame.img_data= self.img_data
        self.img_texture_data = self.heatmap.generate_heatmap(self.img_data,self.heatmap.colormap,self.heatmap.upper_bound,self.heatmap.lower_bound,self.heatmap.upper_colorbound,self.heatmap.lower_colorbound)
        self.gl_frame.load_texture(self.img_data.shape[1], self.img_data.shape[0], self.img_texture_data, self.format, self.pixel_format)
    def set_texture_raw(self):
        self.img_texture_data = self.img_data
        self.gl_frame.img_data= self.img_data
        self.pixel_format = GL_FLOAT
        self.format = GL_LUMINANCE
        self.gl_frame.load_texture(self.img_data.shape[1], self.img_data.shape[0], self.img_texture_data, self.format, self.pixel_format)
class GraphicsCoorDinate2D():
    def __init__(self,x:int=0,y:int=0,radius:int=10,enable:bool=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.selectdistance = 10
        self.status = 'Normal'
        self.shape = 'Cross'
        self.normalcolor = [1.0, 1.0, 1.0]
        self.selectedcolor = [1.0, 0.0, 0.0]
        self.drawtext = False
        self.textscale = 0.5
        self.textcolor = [1.0, 1.0, 1.0,1.0]
        self.textthickness = 1
        self.enable = enable
    def get_font_path(self):
        platform_info = platform.PLATFORM.__str__()
        # 判断操作系统类型
        if platform_info.find("Win") != -1:
            return "C:\\Windows\\Fonts\\arrial.ttf"  # Windows 下的 Arial 字体路径
        elif platform_info.find("Linux") != -1:
            return "/usr/share/fonts/truetype/dejavu/Georgia.ttf"  # Linux 下的 DejaVu 字体路径
        else:
            raise Exception("Unsupported OS: " + platform.PLATFORM)
    def render_text(self, text, x, y):
        if self.drawtext is not True:
            return
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = self.textscale
        thickness = self.textthickness
        line_type = cv2.LINE_AA

        # 计算文本的大小
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

        # 创建图像，大小为文本大小加上边距
        padding = 2
        width = text_width + 2 * padding
        height = text_height + 2 * padding

        # 创建空白图像 (黑色背景)
        image = np.zeros((height, width, 4), dtype=np.uint8)

        # 计算文本的位置 (居中)
        text_x = padding
        text_y = text_height + padding

        # 在图像上添加文本
        cv2.putText(image, text, (text_x, text_y), font, font_scale,(int(self.textcolor[0]*255),int(self.textcolor[1]*255),int(self.textcolor[2]*255),int(self.textcolor[3]*255)), thickness, line_type)


        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.shape[1], image.shape[0], 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # 绘制四边形
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + image.shape[1], y)
        glTexCoord2f(1, 1); glVertex2f(x + image.shape[1], y + image.shape[0])
        glTexCoord2f(0, 1); glVertex2f(x, y + image.shape[0])
        glEnd()

        glDeleteTextures(1,[texture])

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
    def GLDraw(self):
        if self.shape == 'Cross':
            glBegin(GL_LINES)
            glColor3f(1.0, 0.0, 0.0)  
            glVertex2f(self.x, self.y)  
            glVertex2f(self.x+self.radius, self.y)   
            glColor3f(0.0, 0.0, 1.0)  
            glVertex2f(self.x, self.y)
            glVertex2f(self.x, self.y+self.radius)  
            glEnd()
        if self.shape == 'Circle':
            if self.status == 'Normal':
                glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])  
            else:
                glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])
            glBegin(GL_LINE_LOOP)
            for i in range(100):
                angle = 2 * pi * i / 100
                x_pos = self.x + self.radius * cos(angle)
                y_pos = self.y + self.radius * sin(angle)
                glVertex2f(x_pos, y_pos)
            glEnd()
            glColor3f(1.0, 1.0, 1.0)
        if self.shape == 'Square':
            if self.status == 'Normal':
                glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])
            else:
                glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])
            glBegin(GL_LINE_LOOP)
            glVertex2f(self.x-self.radius/2, self.y-self.radius/2)
            glVertex2f(self.x+self.radius/2, self.y-self.radius/2)
            glVertex2f(self.x+self.radius/2, self.y+self.radius/2)
            glVertex2f(self.x-self.radius/2, self.y+self.radius/2)
            glEnd()              
            glColor3f(1.0, 1.0, 1.0)
        
        self.render_text(f"{self.x:.2f},{self.y:.2f}", self.x, self.y+15)
    def contains(self,x:int,y:int):
        """判断点是否在坐标系内"""
        if self.enable is not True:
            return None
        distance = self.get_distance(x,y)
        res= distance <= self.selectdistance
        if res:
            self.status = 'Selected'
            return self
        else:
            self.status = 'Normal'
            return None
    def get_distance(self,x:int,y:int):
        """获取坐标系到点的距离"""
        distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
        return distance
    def show_parameter_page(self,x,y,parent):
        """判断点是否在坐标系内"""
        if self.enable is not True:
            return None
        distance = self.get_distance(x,y)
        res= distance <= self.selectdistance
        if res:
            return self.show_parameter_page(parent)
        else:
            return None
class GraphicsCircle2D():
    def __init__(self,name:str='Circle',x:int=0,y:int=0,radius:int=100,color:list=[1.0, 1.0, 1.0],segments:int=100,startangle:int=0,endangle:int=360,enable:bool=True):
        self.name = name
        self.circlecenter_point = GraphicsCoorDinate2D(x,y)
        self.radius_point = GraphicsCoorDinate2D(x,y+radius)
        self.selectedcolor = [1.0, 0.0, 0.0]
        self.normalcolor = color
        self.segments = segments
        self.startangle = startangle
        self.endangle = endangle
        self.status = 'Normal'
        self.selectdistance = 10     
        self.drawtext = True
        self.textscale = 0.5
        self.textcolor = [1.0, 1.0, 1.0,1.0]
        self.textthickness = 1  
        self.enable = enable
    def GLDraw(self):
        try:
            if self.status == 'Normal':
                glBegin(GL_LINE_STRIP)
                glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])
                start_index = int(self.startangle / 360 * self.segments)
                end_index = int(self.endangle / 360 * self.segments)
                self.radius = ((self.radius_point.x - self.circlecenter_point.x) ** 2 + (self.radius_point.y - self.circlecenter_point.y) ** 2) ** 0.5
                self.x = self.circlecenter_point.x
                self.y = self.circlecenter_point.y
                for i in range(start_index, end_index):
                    x = self.x + self.radius * cos(2 * pi * i / self.segments)
                    y = self.y + self.radius * sin(2 * pi * i / self.segments)
                    glVertex2f(x, y)
                glVertex2f(self.x + self.radius * cos(2 * pi * start_index / self.segments),
                           self.y + self.radius * sin(2 * pi * start_index / self.segments))
                glEnd()
                glColor3f(1.0, 1.0, 1.0)
            if self.status == 'Selected':
                glBegin(GL_LINES)
                glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])
                start_index = int(self.startangle / 360 * self.segments)
                end_index = int(self.endangle / 360 * self.segments)
                self.radius = ((self.radius_point.x - self.circlecenter_point.x) ** 2 + (self.radius_point.y - self.circlecenter_point.y) ** 2) ** 0.5
                self.x = self.circlecenter_point.x
                self.y = self.circlecenter_point.y
                for i in range(start_index, end_index):
                    x = self.x + self.radius * cos(2 * pi * i / self.segments)
                    y = self.y + self.radius * sin(2 * pi * i / self.segments)
                    glVertex2f(x, y)
                glEnd()

            glColor3f(1.0, 1.0, 1.0)
            self.circlecenter_point.GLDraw()
            self.radius_point.GLDraw()
            self.render_text(f"Name: {self.name}\nRadius: {self.radius:.3f}\nCenter: {self.x:.3f},{self.y:.3f}", self.x, self.y+15)
        except Exception as e:
            messagebox.askquestion('Error',f"Error updating viewport: {e},\n,{glGetError()}", icon='error')
    def render_text(self, text, x, y):
        if self.drawtext is not True:
            return
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor3f(1.0, 1.0, 1.0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = self.textscale
        thickness = self.textthickness
        line_type = cv2.LINE_AA
        lines = text.split('\n')
        # 计算文本的大小
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

        # 创建图像，大小为文本大小加上边距
        padding = 2
        width = text_width + 2 * padding
        height = text_height + 2 * padding

        # 创建空白图像 (黑色背景)
        image = np.zeros((height*len(lines), width, 4), dtype=np.uint8)
        for i, line in enumerate(lines):
            # 计算文本的位置 (居中)
            text_x = padding
            text_y = int(text_height * (i+1)) + padding

            # 在图像上添加文本
            cv2.putText(image, line, (text_x, text_y), font, font_scale,(int(self.textcolor[0]*255),int(self.textcolor[1]*255),int(self.textcolor[2]*255),int(self.textcolor[3]*255)), thickness, line_type)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.shape[1], image.shape[0], 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # 绘制四边形
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + image.shape[1], y)
        glTexCoord2f(1, 1); glVertex2f(x + image.shape[1], y + image.shape[0])
        glTexCoord2f(0, 1); glVertex2f(x, y + image.shape[0])
        glEnd()

        glDeleteTextures(1,[texture])

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)    
    def contains(self,x:int,y:int):
        """判断点是否在圆内"""
        if self.enable is not True:
            return None
        if self.circlecenter_point.contains(x,y) is not None:
            self.status = 'Selected'
            return [self.circlecenter_point,self.radius_point]
        else:
            if self.radius_point.contains(x,y) is not None:
                self.status = 'Selected'
                return self.radius_point
            else:
                return None
    def show_parameter_page(self,x,y,parent):
        """判断点是否在坐标系内"""
        if self.enable is not True:
            return None
        if self.circlecenter_point.contains(x,y) is not None:
            return self.show_parameter_page(parent)
        else:
            return None
class Graphics_ValueModule():
    def __init__(self,x:int=0,y:int=0,name:str='ValueModule',message=None):
        self.x = x
        self.y = y
        self.radius = 10
        self.text = name
        self.selectdistance = 10
        self.status = 'Normal'
        self.normalcolor = [0.0,0.5,0.5,1.0]
        self.selectedcolor = [1.0, 0.0, 0.0,1.0]
        self.statuscolor = [1.0, 0.0, 0.0,1.0]
        self.drawtext = True
        self.font_path = "C:\\Windows\\Fonts\\msyh.ttc"  # 微软雅黑字体
        self.font_size = 16
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.textcolor = [1.0, 1.0, 1.0,1.0]
        self.enable = True
        self.lastrunstatus = False
        self.textimage = None
        self.breifimage = None
        self.breifimage_visible = tk.IntVar()
        self.language = 'zh'
        self.spantime=0
        self.padding = 12
        self.get_image()
        self.message=message
        self.parameters={'lastrunstatus':self.lastrunstatus,}
        self.breifimagewidth = self.textimage.shape[1]
        self.breifimageheight = self.textimage.shape[0]*(self.textimage.shape[1]//self.breifimagewidth+1)
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
        self.texts = {}
        self.set_language(self.language)
        self.description_html = {
            'zh': 
                """
                <div style="
                    font-family: Arial, sans-serif;
                    background-color: #f0f8ff;
                    text-align: left;
                    padding: 10px;
                ">
                    <div style="
                        display: inline-block;
                        text-align: left;
                        padding: 10px;
                        border: 2px solid #4a90e2;
                        border-radius: 10px;
                        background-color: #ffffff;
                    ">
                        <h3 style="color: #4a90e2;">欢迎来到CVFLOW应用</h3>
                        <p style="font-size: 15px; color: #333;">我们很高兴见到您！</p>
                        <img src="{path}" alt="Title Icon" style="width: 100%; height: auto; margin-top: 5px;">

                    </div>
                </div>
                """.format(path=iconp),
            'en': 
                """
                <div style="
                    font-family: Arial, sans-serif;
                    background-color: #f0f8ff;
                    text-align: left;
                    padding: 10px;
                ">
                    <div style="
                        display: inline-block;
                        text-align: left;
                        padding: 10px;
                        border: 2px solid #4a90e2;
                        border-radius: 10px;
                        background-color: #ffffff;
                    ">
                        <h3 style="color: #4a90e2;">Welcome to Cvflow App</h3>
                        <p style="font-size: 15px; color: #333;">It's nice to see you here!</p>
                        <img src="{path}" alt="Title Icon" style="width: 100%; height: auto; margin-top: 5px;">
                
                    </div>
                </div>
                """.format(path=iconp)
        }
    @classmethod
    def from_userdefined(cls,master,x:int=0,y:int=0,name:str='ValueModule',message=None):
        toplevel= tk.Toplevel(master)
        toplevel.iconbitmap(iconp)
        toplevel.title("User Defined Module")
        
        inputbox = PlaceholderEntry(toplevel,placeholder=name,width=60)
             
        result=[]
        def on_submit():
            result.append(inputbox.get())  # 保存输入内容
            toplevel.destroy()  # 关闭窗口

        submit_btn = ttk.Button(toplevel, text="确定", command=on_submit)
        inputbox.pack(pady=10)
        submit_btn.pack(pady=10)

        rootx = master.winfo_rootx()
        rooty = master.winfo_rooty()
        toplevel.geometry(f"+{rootx}+{rooty}")  # 设置新窗口位置
        
        # 阻塞等待窗口关闭
        submit_btn.focus_set()  # 设置按钮为默认焦点
        toplevel.wait_window()

        # 窗口关闭后，检查用户是否输入了内容
        name = result[0] if result else ""
        return cls(x=x, y=y,name=name, message=message)
    def set_language(self,language:str):
        if language == 'zh':
            self.texts['color_choose']='颜色选择'
            self.texts['del_button']= '删除'
            self.texts['del_button_tip_title']='删除模块'
            self.texts['del_button_tip_content']='确定删除该模块吗？'
            self.texts['run_button']= '运行'
            self.texts['save_button']= '保存'
            self.texts['load_button']= '加载'
            self.texts['info_label']= '信息'
            self.texts['tab1']='视图'
            self.texts['tab2']='参数'
            self.texts['tab3']='说明'
            self.texts['name_label']='名称'
            self.texts['labelcolor']='标签颜色'
            self.texts['fontsize']='字体大小'
            self.texts['fontpath']='字体路径'
            self.texts['brifeimage']='显示简略图'
            self.texts['brifeimagewidth']='简略图宽度'
            self.texts['brifeimageheight']='简略图高度'
            self.texts['language']='语言'
            self.texts['load_button_tip_title']='错误'
            self.texts['load_button_tip_content']='加载模块失败，请检查模块文件是否存在或格式是否正确。'
            pass
        else:
            self.texts['color_choose']='Choose Color'
            self.texts['del_button']= 'Delete'
            self.texts['del_button_tip_title']='Delete Module'
            self.texts['del_button_tip_content']='Are you sure you want to delete this module?'
            self.texts['run_button']= 'Run'
            self.texts['save_button']= 'Save'
            self.texts['load_button']= 'Load'
            self.texts['info_label']= 'Info'
            self.texts['tab1']='View'
            self.texts['tab2']='Parameter'
            self.texts['tab3']='Description'
            self.texts['name_label']='Name'
            self.texts['labelcolor']='Label Color'
            self.texts['fontsize']='Font Size'
            self.texts['fontpath']='Font Path'
            self.texts['brifeimage']='Show Brife Image'
            self.texts['brifeimagewidth']='Brife Image Width'
            self.texts['brifeimageheight']='Brife Image Height'
            self.texts['language']='Language'
            self.texts['load_button_tip_title']='Error'
            self.texts['load_button_tip_content']='Failed to load module, please check if the module file exists or if the format is correct.'
            pass
    def get_image(self):
        
        self.font= ImageFont.truetype(self.font_path, self.font_size)
        # 设置字体路径，使用 Windows 系统的字体

        #self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.text=self.text.replace('\\n','\n')
        self.lines = self.text.split('\n')
        # 计算每行文本的大小并找到最大宽度
        
        text_widths = [self.font.getbbox(line)[2]-self.font.getbbox(line)[0] for line in self.lines]
        text_width = max(text_widths) if text_widths else 0        
                
        self.bbox= self.font.getbbox(self.text)
        self.width = text_width + 2 * self.padding
        self.height = (self.bbox[3]-self.bbox[1])*len(self.lines) + 2 * self.padding
        self.textimage = np.full((self.height, self.width, 4),(int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255),int(self.normalcolor[3]*255)), dtype=np.uint8)
        
        self.pil_image = Image.new("RGBA", (self.width, self.height), (int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255),int(self.normalcolor[3]*255)))
        self.textdraw = ImageDraw.Draw(self.pil_image)
    def get_inside_rect(self):
        x1 = self.x + self.padding
        y1 = self.y + self.padding
        x2 = self.x + self.width - self.padding
        y2 = self.y + self.height - self.padding
        return x1, y1, x2, y2
    def get_output_triangle(self):
        x1 = self.x + self.width/2
        y1 = self.y + self.height
        p1x = x1 + self.radius/2
        p1y = y1
        p2x = x1 - self.radius/2
        p2y = y1 
        p3x = x1
        p3y = y1 + self.radius/2
        return p1x, p1y, p2x, p2y, p3x, p3y
    def get_input_triangle(self):
        x1 = self.x + self.width/2
        y1 = self.y
        p1x = x1 + self.radius/2
        p1y = y1
        p2x = x1 - self.radius/2
        p2y = y1 
        p3x = x1
        p3y = y1 - self.radius/2
        return p1x, p1y, p2x, p2y, p3x, p3y
    def check_inside(self,x:int,y:int):
        """判断点是否在坐标系内"""
        if self.enable is not True:
            return None
        x1, y1, x2, y2 = self.get_inside_rect()
        if x1 <= x <= x2 and y1 <= y <= y2:
            self.status = 'Selected'
            return self
        else:
            self.status = 'Normal'
            return None
    def run(self):
        starttime = time.perf_counter()
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
        self.parameters['lastrunstatus']=self.lastrunstatus
    def show_parameter_page(self,x,y,parent):
        x1, y1, x2, y2 = self.get_inside_rect()
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            return
        def update_io():
            tab2.children.clear()
            keys = list(self.parameters.keys())
            for i,key in enumerate(keys):
                tk.Label(tab2, text=f"{key}\n    {gstr(self.parameters[key])}",anchor='w',justify='left').grid(row=i, column=0,sticky='ew' ,pady=5)
            pass
        def change_language():
            self.language = languages_commbox.get()
            self.set_language(self.language)
            run_button.config(text=self.texts['run_button'])
            del_button.config(text=self.texts['del_button'])
            save_button.config(text=self.texts['save_button'])
            load_button.config(text=self.texts['load_button'])
            info_label.config(text=self.texts['info_label'])
            notebook.tab(tab1, text=self.texts['tab1'])
            notebook.tab(tab2, text=self.texts['tab2'])
            notebook.tab(tab3, text=self.texts['tab3'])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            html_label.set_html(self.description_html[self.language])
        def check_language():
            self.set_language(self.language)
            run_button.config(text=self.texts['run_button'])
            del_button.config(text=self.texts['del_button'])
            save_button.config(text=self.texts['save_button'])
            load_button.config(text=self.texts['load_button'])
            info_label.config(text=self.texts['info_label'])
            notebook.tab(tab1, text=self.texts['tab1'])
            notebook.tab(tab2, text=self.texts['tab2'])
            notebook.tab(tab3, text=self.texts['tab3'])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            html_label.set_html(self.description_html[self.language])
        def choose_color():
            color = colorchooser.askcolor(color=(int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255)), title=self.texts['color_choose'])
            if color[0] is not None:
                self.normalcolor = [color[0][0]/255,color[0][1]/255,color[0][2]/255,1.0]
                button.config(bg=color[1])
        def run_button_click():
            self.run()
            info_label.config(text=f'Info: CT:{self.spantime:.4f}s')
            update_io()
        def del_button_click():
            if tk.messagebox.askokcancel(self.texts['del_button_tip_title'], self.texts['del_button_tip_content']):
                self.message(self,-1)
                window.destroy()
        window= tk.Toplevel(parent)
        window.title(self.text)
        window.iconbitmap(iconp)
        window.geometry(f'300x432+{parent.winfo_rootx()}+{parent.winfo_rooty()}')
        button_frame = tk.Frame(window)
        button_frame.pack(side='top', anchor='nw', pady=5)

        run_button = tk.Button(button_frame, text=self.texts['run_button'], command=run_button_click)
        run_button.pack(side='left', padx=1)

        del_button = tk.Button(button_frame, text=self.texts['del_button'], command=del_button_click)
        del_button.pack(side='left', padx=1)
        
        save_button = tk.Button(button_frame, text=self.texts['save_button'], command=self.save)
        save_button.pack(side='left', padx=1)
        
        load_button = tk.Button(button_frame, text=self.texts['load_button'], command=self.load)
        load_button.bind('<Button-1>',lambda event: self.load(),add=True)
        load_button.bind('<Button-1>',lambda event: update_io(),add=True)
        load_button.pack(side='left', padx=1)

        info_label = tk.Label(window,text=self.texts['info_label'])
        info_label.pack(side='bottom',anchor='sw')

        notebook = ttk.Notebook(window)
        notebook.pack(fill='both', expand=True)
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        notebook.add(tab1,text='View')
        notebook.add(tab2,text='Parameter')
        notebook.add(tab3,text='Description')
        
        frame = tk.Frame(tab1)
        frame.pack(padx=10, pady=10)
        tk.Label(frame, text="X:").grid(row=0, column=0, pady=5)
        x_entry = tk.Entry(frame)
        x_entry.insert(0, self.x)
        x_entry.grid(row=0, column=1, pady=5)
        x_entry.bind('<Return>', lambda event: setattr(self, 'x', int(x_entry.get())))
        tk.Label(frame, text="Y:").grid(row=1, column=0, pady=5)
        y_entry = tk.Entry(frame)
        y_entry.insert(0, self.y)
        y_entry.grid(row=1, column=1, pady=5)
        y_entry.bind('<Return>', lambda event: setattr(self, 'y', int(y_entry.get())))
        namelabel= tk.Label(frame, text=self.texts['name_label'])
        namelabel.grid(row=2, column=0, pady=5)
        text_entry = tk.Entry(frame)
        text_entry.delete(0, 'end')
        text_entry.insert(0, self.text)
        text_entry.grid(row=2, column=1, pady=5)
        text_entry.bind('<Return>',lambda event: setattr(self,'text',text_entry.get()),add=True)
        text_entry.bind('<Return>',lambda event: self.get_image(),add=True)
        text_entry.bind('<Return>',lambda event: self.message(self,-2),add=True)

        labelcolor=tk.Label(frame, text=self.texts['labelcolor'])
        labelcolor.grid(row=4, column=0, pady=5)
        button = tk.Button(frame, text=self.texts['color_choose'], command=choose_color)
        button.grid(row=4,column=1,pady=5)
        
        fontsize_label=tk.Label(frame, text=self.texts['fontsize'])
        fontsize_label.grid(row=5, column=0, pady=5)
        spinbox= tk.Spinbox(frame,from_=1,to=48)
        spinbox.delete(0, 'end')
        spinbox.insert(0, self.font_size)
        spinbox.bind('<Button-1>',lambda evemt: setattr(self,'font_size',int(spinbox.get())),add=True)
        spinbox.bind('<Button-1>',lambda evemt: self.get_image(),add=True)
        

        spinbox.grid(row=5,column=1,pady=5)
        
        
        fontpath_label=tk.Label(frame, text=self.texts['fontpath'])
        fontpath_label.grid(row=6, column=0, pady=5)
        fontscale_spinbox= tk.Entry(frame)
        fontscale_spinbox.delete(0, 'end')
        fontscale_spinbox.insert(0, self.font_path)
        fontscale_spinbox.bind('<Return>',lambda event: setattr(self,'font_path',fontscale_spinbox.get()),add=True)
        fontscale_spinbox.bind('<Return>',lambda event: self.get_image(),add=True)
        fontscale_spinbox.grid(row=6,column=1,pady=5)
        
        brieifimage_width = tk.Label(frame, text=self.texts['brifeimagewidth'])
        brieifimage_width.grid(row=7, column=0, pady=5)
        brieifimage_width_entry = tk.Entry(frame)
        brieifimage_width_entry.delete(0, 'end')
        brieifimage_width_entry.insert(0, self.breifimagewidth)
        brieifimage_width_entry.grid(row=7, column=1, pady=5)
        brieifimage_width_entry.bind('<Return>',lambda event: setattr(self,'breifimagewidth',int(brieifimage_width_entry.get())))
        
        brieifimage_height = tk.Label(frame, text=self.texts['brifeimageheight'])
        brieifimage_height.grid(row=8, column=0, pady=5)
        brieifimage_height_entry = tk.Entry(frame)
        brieifimage_height_entry.delete(0, 'end')
        brieifimage_height_entry.insert(0, self.breifimageheight)
        brieifimage_height_entry.grid(row=8, column=1, pady=5)
        brieifimage_height_entry.bind('<Return>',lambda event: setattr(self,'breifimageheight',int(brieifimage_height_entry.get())))
        
        breifimage_enbale = tk.Label(frame, text=self.texts['brifeimage'])
        breifimage_enbale.grid(row=9, column=0, pady=5)
        breifimage_enbale_checkbox = tk.Checkbutton(frame, variable= self.breifimage_visible, onvalue=1, offvalue=0)
        breifimage_enbale_checkbox.grid(row=9, column=1, pady=5)
        
        languages_lable = tk.Label(frame, text=self.texts['language'])
        languages_lable.grid(row=10, column=0, pady=5)
        languages_commbox = ttk.Combobox(frame,values= ['en', 'zh'], state='readonly', width=5)
        languages_commbox.set(self.language)
        languages_commbox.grid(row=10, column=1, pady=5)
        languages_commbox.bind('<<ComboboxSelected>>', lambda event: change_language(), add=True)
                  
        html_label = HTMLLabel(tab3, html=self.description_html[self.language])
        html_label.pack(fill=tk.BOTH, expand=True)
        
        check_language()        
        update_io()
    def render_text(self, x, y):
        if self.drawtext is not True:
            return
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor3f(1.0, 1.0, 1.0)        
                
        self.pil_image = Image.new("RGBA", (self.width, self.height), (int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255),int(self.normalcolor[3]*255)))
        self.textdraw = ImageDraw.Draw(self.pil_image)

        self.textdraw.text((self.padding, self.padding - self.bbox[1]), self.text, font=self.font, fill=(int(self.textcolor[0]*255),int(self.textcolor[1]*255),int(self.textcolor[2]*255),int(self.textcolor[3]*255)))

        self.textimage = np.array(self.pil_image)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.textimage.shape[1], self.textimage.shape[0], 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, self.textimage)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # 绘制四边形
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + self.textimage.shape[1], y)
        glTexCoord2f(1, 1); glVertex2f(x + self.textimage.shape[1], y + self.textimage.shape[0])
        glTexCoord2f(0, 1); glVertex2f(x, y + self.textimage.shape[0])
        glEnd()

        glDeleteTextures(1,[texture])

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)   
    def render_breifimage(self, x, y):
        if self.breifimage is None or self.breifimage_visible.get() == 0:
            return
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        breifimage_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, breifimage_texture)
        glColor3f(1.0, 1.0, 1.0)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.breifimage.shape[1], self.breifimage.shape[0], 
                     0, GL_LUMINANCE, GL_FLOAT, self.breifimage)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # 绘制四边形
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x + self.textimage.shape[1], y)
        glTexCoord2f(1, 0); glVertex2f(x + self.textimage.shape[1]+self.breifimagewidth, y)
        glTexCoord2f(1, 1); glVertex2f(x + self.textimage.shape[1]+self.breifimagewidth, y + self.breifimageheight)
        glTexCoord2f(0, 1); glVertex2f(x + self.textimage.shape[1], y + self.breifimageheight)
        glEnd()

        glDeleteTextures(1,[breifimage_texture])

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)  
    def GLDraw(self):
        if True:
            self.render_text(self.x, self.y)
            self.render_breifimage(self.x, self.y)
            if self.status == 'Normal':
                glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])
            else:
                glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])
            glBegin(GL_LINE_LOOP)
            glVertex2f(self.x, self.y)
            glVertex2f(self.x + self.textimage.shape[1], self.y)
            glVertex2f(self.x + self.textimage.shape[1], self.y + self.textimage.shape[0])
            glVertex2f(self.x, self.y + self.textimage.shape[0])
            glEnd()
            
            glColor3f(self.statuscolor[0], self.statuscolor[1], self.statuscolor[2])
            
            glBegin(GL_QUADS)
            glVertex2f(self.x-self.radius/2, self.y+2*self.radius-self.radius/2)
            glVertex2f(self.x+self.radius/2, self.y+2*self.radius-self.radius/2)
            glVertex2f(self.x+self.radius/2, self.y+2*self.radius+self.radius/2)
            glVertex2f(self.x-self.radius/2, self.y+2*self.radius+self.radius/2)
            glEnd()      
            
            glColor3f(1.0, 1.0, 1.0)     
    def contains(self,x:int,y:int):
        """判断点是否在坐标系内"""
        if self.enable is not True:
            return None
        return self.check_inside(x,y)
    def get_distance(self,x:int,y:int):
        """获取坐标系到点的距离"""
        distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
        return distance
    def save(self):
        """保存模块为JSON"""
        file_path = filedialog.asksaveasfilename(defaultextension=f"{self.text}.cvvm",
                                                 filetypes=[("JSON files", "*.cvvm"), ("All files", "*.*")])
        if file_path:
            try:
                # 只保存可序列化的属性
                data = {
                    "class": self.__class__.__name__,
                    "x": self.x,
                    "y": self.y,
                    "radius": self.radius,
                    "text": self.text,
                    "normalcolor": self.normalcolor,
                    "selectedcolor": self.selectedcolor,
                    "font_path": self.font_path,
                    "font_size": self.font_size,
                    "textcolor": self.textcolor,
                    "parameters": {k: None if isinstance(v, np.ndarray) else v for k, v in self.parameters.items()},
                    "breifimagewidth": self.breifimagewidth,
                    "breifimageheight": self.breifimageheight,
                    "status": self.status,
                    "language": self.language,
                }
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "Module saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save module: {e}")
    def load(self):
        """加载模块的JSON文件"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.cvvm"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data.get("class") != self.__class__.__name__:
                    messagebox.showerror(self.texts['load_button_tip_title'], self.texts['load_button_tip_content'])
                    return
                # 只加载可序列化的属性
                self.x = data.get("x", self.x)
                self.y = data.get("y", self.y)
                self.radius = data.get("radius", self.radius)
                self.text = data.get("text", self.text)
                self.normalcolor = data.get("normalcolor", self.normalcolor)
                self.selectedcolor = data.get("selectedcolor", self.selectedcolor)
                self.font_path = data.get("font_path", self.font_path)
                self.font_size = data.get("font_size", self.font_size)
                self.textcolor = data.get("textcolor", self.textcolor)
                self.parameters = data.get("parameters", {})
                self.breifimagewidth = data.get("breifimagewidth",self.breifimagewidth)
                self.breifimageheight = data.get("breifimageheight",self.breifimageheight)
                self.status = data.get("status",self.status)
                self.language = data.get("language",self.language)
                
        except Exception as e:
            messagebox.showerror(self.texts['load_button_tip_title'], self.texts['load_button_content'] + str(e))
class Grpahics_WrapLineModule(Graphics_ValueModule):
    def __init__(self,A:Graphics_ValueModule,B:Graphics_ValueModule,KeyA:str,KeyB:str,name:str='WrapLine',message=None):
        super().__init__(0,0,name,message)
        self.A = A
        self.B = B
        self.KyeA = KeyA
        self.KyeB = KeyB
        self.width = self.radius
        self.height = self.radius
        self.selectedcolor = [1.0, 0.0, 0.0,1.0]
        self.normalcolor = [1.0, 1.0, 1.0,1.0]
        self.status = 'Normal'
        self.selectdistance = 10
        self.parameters = {f'{self.A.text}': self.A.parameters[KeyA],f'{self.B.text}': self.B.parameters[KeyB]}
    @classmethod
    def from_userdefined(cls,master,x:int=0,y:int=0,name:str='ValueModule',message=None):
        toplevel= tk.Toplevel(master)
        toplevel.iconbitmap(iconp)
        toplevel.title("User Defined Module")
        inputbox = PlaceholderEntry(toplevel,placeholder=name,width=60)
        result=[]
        def on_submit():
            result.append(inputbox.get())  # 保存输入内容
            toplevel.destroy()  # 关闭窗口

        submit_btn = ttk.Button(toplevel, text="确定", command=on_submit)
        inputbox.pack(pady=10)
        submit_btn.pack(pady=10)

        # 阻塞等待窗口关闭
        submit_btn.focus_set()  # 设置按钮为默认焦点
        toplevel.wait_window()

        # 窗口关闭后，检查用户是否输入了内容
        name = result[0] if result else ""
        line=cls(A=Graphics_ValueModule(),B=Graphics_ValueModule(),KeyA='lastrunstatus',KeyB='lastrunstatus',name=name,message=message)
        line.x = x
        line.y = y
        line.show_parameter_page(x,y,master)
        return line
    def get_inside_rect(self):
        return self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius
    def bezier_curve_points(self, num_segments=50):
        """
        使用生成器生成贝塞尔曲线上的点。

        Args:
            control_points: 控制点列表，每个点是一个 (x, y) 元组。
            num_segments: 用于近似曲线的线段数量。

        Yields:
            (x, y) 元组，表示贝塞尔曲线上的点。
        """
        ox1,oy1,ox2,oy2,ox3,oy3= self.A.get_output_triangle()
        ix1,iy1,ix2,iy2,ix3,iy3= self.B.get_input_triangle()
        dy= (oy3-iy3)/2
        dx= (ox3-ix3)/2
        control_points = [(ox3,oy3),(ox3-dx/20,oy3-dy/2),(ix3+dx/20,iy3+dy/2),(ix3,iy3)]
        for i in range(num_segments + 1):
            t = float(i) / num_segments
            yield self.bezier_point(control_points, t)
    def bezier_point(self,control_points, t):
        """
        计算贝塞尔曲线上的一个点。

        Args:
            control_points: 控制点列表，每个点是一个 (x, y) 元组。
            t: 参数值，范围从 0.0 到 1.0，表示曲线上的位置。

        Returns:
            (x, y) 元组，表示曲线上的点。
        """

        n = len(control_points) - 1
        x = 0.0
        y = 0.0

        for i, point in enumerate(control_points):
            x += self.binomial_coefficient(n, i) * pow(1 - t, n - i) * pow(t, i) * point[0]
            y += self.binomial_coefficient(n, i) * pow(1 - t, n - i) * pow(t, i) * point[1]

        return x, y
    def binomial_coefficient(self,n, k):
        """
        计算二项式系数 (n choose k)。
        """
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        if k > n // 2:
            k = n - k
        result = 1
        for i in range(k):
            result = result * (n - i) // (i + 1)
        return result
    def GLDraw(self):
        if self.status == 'Normal':
            glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])
        else:
            glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])
        
        if self.A is None or self.B is None:
            glBegin(GL_LINE_STRIP)
            glVertex2f(self.x-self.radius*2, self.y-self.radius*2)
            glVertex2f(self.x+self.radius*2, self.y-self.radius*2)
            glVertex2f(self.x+self.radius*2, self.y+self.radius*2)
            glVertex2f(self.x-self.radius*2, self.y+self.radius*2)
            glEnd()        
            return    
            
            
        glBegin(GL_LINE_STRIP)
        for index,point in enumerate(self.bezier_curve_points()):
            glVertex2f(point[0], point[1])
            if index == 25:
                self.x = point[0]
                self.y = point[1]
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(self.x-self.radius/2, self.y-self.radius/2)
        glVertex2f(self.x+self.radius/2, self.y-self.radius/2)
        glVertex2f(self.x+self.radius/2, self.y+self.radius/2)
        glVertex2f(self.x-self.radius/2, self.y+self.radius/2)        
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)     
        if self.A.parameters[self.KyeA] is not None:
            # Draw output triangle
            p1x, p1y, p2x, p2y, p3x, p3y = self.A.get_output_triangle()
            glBegin(GL_LINE_LOOP)
            glVertex2f(p1x, p1y)
            glVertex2f(p2x, p2y)
            glVertex2f(p3x, p3y)
            glEnd()
        if self.B.parameters[self.KyeB] is not None:
            # Draw input triangle
            p1x, p1y, p2x, p2y, p3x, p3y = self.B.get_input_triangle()
            glBegin(GL_LINE_LOOP)
            glVertex2f(p1x, p1y)
            glVertex2f(p2x, p2y)
            glVertex2f(p3x, p3y)
            glEnd()
        
        glColor3f(1.0, 1.0, 1.0)
    def run(self):
        starttime = time.perf_counter()
        try:
            self.B.parameters[self.KyeB]=self.A.parameters[self.KyeA]
            self.lastrunstatus = True
        except Exception as e:
            self.lastrunstatus = False
            messagebox.showerror("Error", f"Failed to set line parameters: {e}")
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
    def save(self):
        """保存模块为JSON"""
        file_path = filedialog.asksaveasfilename(defaultextension=f"{self.text}.cvlm",
                                                 filetypes=[("JSON files", "*.cvlm"), ("All files", "*.*")])
        if file_path:
            try:
                # 只保存可序列化的属性
                data = {
                    "class": self.__class__.__name__,
                    "x": self.x,
                    "y": self.y,
                    "radius": self.radius,
                    "text": self.text,
                    "normalcolor": self.normalcolor,
                    "selectedcolor": self.selectedcolor,
                    "font_path": self.font_path,
                    "font_size": self.font_size,
                    "textcolor": self.textcolor,
                    "parameters": self.parameters,
                    "breifimagewidth": self.breifimagewidth,
                    "breifimageheight": self.breifimageheight,
                    "language": self.language,
                    "status": self.status,
                    "KeyA": self.KyeA,
                    "KeyB": self.KyeB,
                    "A": self.A.text,
                    "B": self.B.text,
                }
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "Module saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save module: {e}")
    def load(self,modules):
        """加载模块的JSON文件"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.cvlm"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data.get("class") != self.__class__.__name__:
                    messagebox.showerror(self.texts['load_button_tip_title'], self.texts['load_button_content'])
                    return
                # 只加载可序列化的属性
                self.x = data.get("x", self.x)
                self.y = data.get("y", self.y)
                self.radius = data.get("radius", self.radius)
                self.text = data.get("text", self.text)
                self.normalcolor = data.get("normalcolor", self.normalcolor)
                self.selectedcolor = data.get("selectedcolor", self.selectedcolor)
                self.font_path = data.get("font_path", self.font_path)
                self.font_size = data.get("font_size", self.font_size)
                self.textcolor = data.get("textcolor", self.textcolor)
                self.parameters = data.get("parameters", {})
                self.breifimagewidth = data.get("breifimagewidth",self.breifimagewidth)
                self.breifimageheight = data.get("breifimageheight",self.breifimageheight)
                self.language = data.get("language", self.language)
                self.status = data.get("status",self.status)
                self.KyeA = data.get("KeyA",self.KyeA)
                self.KyeB = data.get("KeyB",self.KyeB)
                self.A = modules[data.get("A",self.A.text)]
                self.B = modules[data.get("B",self.B.text)]
        except Exception as e:
            messagebox.showerror(self.texts['load_button_tip_title'], self.texts['load_button_content'] + str(e))        
    def show_parameter_page(self,x,y,parent):
        x1, y1, x2, y2 = self.get_inside_rect()
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            return
        def update_io():
            buttona.config(text=f"A:   {self.A.text}\n    {gstr(self.A.parameters[self.KyeA])}")
            buttonb.config(text=f"B:   {self.B.text}\n    {gstr(self.B.parameters[self.KyeB])}")       
        def change_language():
            self.language = languages_commbox.get()
            self.set_language(self.language)
            run_button.config(text=self.texts['run_button'])
            del_button.config(text=self.texts['del_button'])
            save_button.config(text=self.texts['save_button'])
            load_button.config(text=self.texts['load_button'])
            info_label.config(text=self.texts['info_label'])
            notebook.tab(tab1, text=self.texts['tab1'])
            notebook.tab(tab2, text=self.texts['tab2'])
            notebook.tab(tab3, text=self.texts['tab3'])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            htmllabel.set_html(self.description_html[self.language])
        def check_language():
            self.set_language(self.language)
            run_button.config(text=self.texts['run_button'])
            del_button.config(text=self.texts['del_button'])
            save_button.config(text=self.texts['save_button'])
            load_button.config(text=self.texts['load_button'])
            info_label.config(text=self.texts['info_label'])
            notebook.tab(tab1, text=self.texts['tab1'])
            notebook.tab(tab2, text=self.texts['tab2'])
            notebook.tab(tab3, text=self.texts['tab3'])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            htmllabel.set_html(self.description_html[self.language])

        def choose_color():
            color = colorchooser.askcolor(color=(int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255)), title="Choose Color")
            if color[0] is not None:
                self.normalcolor = [color[0][0]/255,color[0][1]/255,color[0][2]/255,1.0]
                button.config(bg=color[1])
        def run_button_click():
            self.run()
            info_label.config(text=f'Info: CT:{self.spantime:.4f}s')
            update_io()
        def del_button_click():
            if tk.messagebox.askokcancel(self.texts['del_button_tip_title'], self.texts['del_button_tip_content']):
                self.message(self,-1)
                window.destroy()
        window= tk.Toplevel(parent)
        window.title(self.text)
        window.iconbitmap(iconp)
        rootx = parent.winfo_rootx()
        rooty = parent.winfo_rooty()
        window.geometry(f'300x432+{rootx}+{rooty}')

        button_frame = tk.Frame(window)
        button_frame.pack(side='top', anchor='nw', pady=5)

        run_button = tk.Button(button_frame, text=self.texts['run_button'], command=run_button_click)
        run_button.pack(side='left', padx=1)

        del_button = tk.Button(button_frame, text=self.texts['del_button'], command=del_button_click)
        del_button.pack(side='left', padx=1)
        
        save_button = tk.Button(button_frame, text=self.texts['save_button'], command=self.save)
        save_button.pack(side='left', padx=1)
        
        load_button = tk.Button(button_frame, text=self.texts['load_button'], command=self.load)
        load_button.bind('<Button-1>',lambda event: self.load(),add=True)
        load_button.bind('<Button-1>',lambda event: update_io(),add=True)
        load_button.pack(side='left', padx=1)

        info_label = tk.Label(window,text=self.texts['info_label'])
        info_label.pack(side='bottom',anchor='sw')

        notebook = ttk.Notebook(window)
        notebook.pack(fill='both', expand=True)
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)

        notebook.add(tab1,text=self.texts['tab1'])
        notebook.add(tab2,text=self.texts['tab2'])
        notebook.add(tab3,text=self.texts['tab3'])

        frame = tk.Frame(tab1)
        frame.pack(padx=10, pady=10)
        tk.Label(frame, text="X:").grid(row=0, column=0, pady=5)
        x_entry = tk.Entry(frame)
        x_entry.insert(0, self.x)
        x_entry.grid(row=0, column=1, pady=5)
        x_entry.bind('<Return>', lambda event: setattr(self, 'x', int(x_entry.get())))
        tk.Label(frame, text="Y:").grid(row=1, column=0, pady=5)
        y_entry = tk.Entry(frame)
        y_entry.insert(0, self.y)
        y_entry.grid(row=1, column=1, pady=5)
        y_entry.bind('<Return>', lambda event: setattr(self, 'y', int(y_entry.get())))
        namelabel=tk.Label(frame, text=self.texts['name_label'])
        namelabel.grid(row=2, column=0, pady=5)
        text_entry = tk.Entry(frame)
        text_entry.delete(0, 'end')
        text_entry.insert(0, self.text)
        text_entry.grid(row=2, column=1, pady=5)
        text_entry.bind('<Return>',lambda event: setattr(self,'text',text_entry.get()),add=True)
        text_entry.bind('<Return>',lambda event: self.get_image(),add=True)
        text_entry.bind('<Return>',lambda event: self.message(self,-2),add=True)

        labelcolor=tk.Label(frame, text=self.texts['labelcolor'])
        labelcolor.grid(row=4, column=0, pady=5)
        button = tk.Button(frame, text=self.texts['color_choose'], command=choose_color)
        button.grid(row=4,column=1,pady=5)
        
        fontsize_label=tk.Label(frame, text=self.texts['fontsize'])
        fontsize_label.grid(row=5, column=0, pady=5)
        spinbox= tk.Spinbox(frame,from_=1,to=48)
        spinbox.delete(0, 'end')
        spinbox.insert(0, self.font_size)
        spinbox.bind('<Button-1>',lambda evemt: setattr(self,'font_size',int(spinbox.get())),add=True)
        spinbox.bind('<Button-1>',lambda evemt: self.get_image(),add=True)

        spinbox.grid(row=5,column=1,pady=5)
        
        
        fontpath_label=tk.Label(frame, text=self.texts['fontpath'])
        fontpath_label.grid(row=6, column=0, pady=5)
        fontscale_spinbox= tk.Entry(frame)
        fontscale_spinbox.delete(0, 'end')
        fontscale_spinbox.insert(0, self.font_path)
        fontscale_spinbox.bind('<Return>',lambda event: setattr(self,'font_path',fontscale_spinbox.get()),add=True)
        fontscale_spinbox.bind('<Return>',lambda event: self.get_image(),add=True)
        fontscale_spinbox.grid(row=6,column=1,pady=5)
        
        brieifimage_width = tk.Label(frame, text=self.texts['brifeimagewidth'])
        brieifimage_width.grid(row=7, column=0, pady=5)
        brieifimage_width_entry = tk.Entry(frame)
        brieifimage_width_entry.delete(0, 'end')
        brieifimage_width_entry.insert(0, self.breifimagewidth)
        brieifimage_width_entry.grid(row=7, column=1, pady=5)
        brieifimage_width_entry.bind('<Return>',lambda event: setattr(self,'breifimagewidth',int(brieifimage_width_entry.get())))
        
        brieifimage_height = tk.Label(frame, text=self.texts['brifeimageheight'])
        brieifimage_height.grid(row=8, column=0, pady=5)
        brieifimage_height_entry = tk.Entry(frame)
        brieifimage_height_entry.delete(0, 'end')
        brieifimage_height_entry.insert(0, self.breifimageheight)
        brieifimage_height_entry.grid(row=8, column=1, pady=5)
        brieifimage_height_entry.bind('<Return>',lambda event: setattr(self,'breifimageheight',int(brieifimage_height_entry.get())))
        
        breifimage_enbale = tk.Label(frame, text=self.texts['brifeimage'])
        breifimage_enbale.grid(row=9, column=0, pady=5)
        breifimage_enbale_checkbox = tk.Checkbutton(frame, variable= self.breifimage_visible, onvalue=1, offvalue=0)
        breifimage_enbale_checkbox.grid(row=9, column=1, pady=5)    
        
        languages_lable = tk.Label(frame, text=self.texts['language'])
        languages_lable.grid(row=10, column=0, pady=5)
        languages_commbox = ttk.Combobox(frame,values= ['en', 'zh'], state='readonly', width=5)
        languages_commbox.set(self.language)
        languages_commbox.grid(row=10, column=1, pady=5)
        languages_commbox.bind('<<ComboboxSelected>>', lambda event: change_language(), add=True)
                
        buttona=tk.Button(tab2, text=f"A:   {self.A.text}\n    {gstr(self.A.parameters[self.KyeA])}",justify='left',anchor='w')
        buttona.grid(row=0, column=0,sticky='ew' ,pady=5)
        buttona.bind('<Button-1>',lambda event: self.message(self,1,**dict([('paramname','A'),('keyname','KyeA'),('button',buttona)])),add=True)

        buttonb=tk.Button(tab2, text=f"B:   {self.B.text}\n    {gstr(self.B.parameters[self.KyeB])}",justify='left',anchor='w')
        buttonb.grid(row=1, column=0,sticky='ew' ,pady=5)
        buttonb.bind('<Button-1>',lambda event: self.message(self,1,**dict([('paramname','B'),('keyname','KyeB'),('button',buttonb)])),add=True) 
        
        htmllabel= HTMLLabel(tab3, html=self.description_html[self.language])
        htmllabel.pack(fill=tk.BOTH, expand=True)              
        
        notebook.select(tab2)
        
        check_language()
        update_io()
class Grpahics_WrapIfLineModule(Graphics_ValueModule):
    def __init__(self,A:Graphics_ValueModule,B:Graphics_ValueModule,C:Graphics_ValueModule,KeyA:str,KeyB:str,KeyC:str,name:str='WrapLine',message=None):
        super().__init__((A.x+B.x)/2,(A.y+B.y)/2,name,message)
        self.A = A
        self.B = B
        self.C = C
        self.KyeA = KeyA
        self.KyeB = KeyB
        self.KyeC = KeyC
        self.width = self.radius
        self.height = self.radius
        self.selectedcolor = [1.0, 0.0, 0.0,1.0]
        self.normalcolor = [1.0, 1.0, 1.0,1.0]
        self.status = 'Normal'
        self.selectdistance = 10
        self.result = None
        self.parameters = {f'{self.A.text}': self.A.parameters[KeyA],f'{self.B.text}': self.B.parameters[KeyB],f'{self.C.text}': self.C.parameters[KeyC]}
    @classmethod
    def from_userdefined(cls,master,x:int=0,y:int=0,name:str='ValueModule',message=None):
        toplevel= tk.Toplevel(master)
        toplevel.iconbitmap(iconp)
        toplevel.title("User Defined Module")
        inputbox = PlaceholderEntry(toplevel,placeholder=name,width=60)
        result=[]
        def on_submit():
            result.append(inputbox.get())  # 保存输入内容
            toplevel.destroy()  # 关闭窗口

        submit_btn = ttk.Button(toplevel, text="确定", command=on_submit)
        inputbox.pack(pady=10)
        submit_btn.pack(pady=10)

        # 阻塞等待窗口关闭
        submit_btn.focus_set()  # 设置按钮为默认焦点
        toplevel.wait_window()

        # 窗口关闭后，检查用户是否输入了内容
        name = result[0] if result else ""
        line=cls(A=Graphics_ValueModule(),B=Graphics_ValueModule(),C=Graphics_ValueModule(),KeyA='lastrunstatus',KeyB='lastrunstatus',KeyC='lastrunstatus',name=name,message=message)
        line.x = x
        line.y = y
        line.show_parameter_page(x,y,master)
        return line
    def get_inside_rect(self):
        return self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius
    def bezier_curve_pointsA(self, num_segments=50):
        """
        使用生成器生成贝塞尔曲线上的点。

        Args:
            control_points: 控制点列表，每个点是一个 (x, y) 元组。
            num_segments: 用于近似曲线的线段数量。

        Yields:
            (x, y) 元组，表示贝塞尔曲线上的点。
        """
        ax1,ay1,ax2,ay2,ax3,ay3= self.A.get_output_triangle()
        bx1,by1,bx2,by2,bx3,by3= self.B.get_input_triangle()
        cx1,cy1,cx2,cy2,cx3,cy3= self.C.get_input_triangle()
        dx3= (ax3+bx3+cx3)/3
        dy3= (ay3+by3+cy3)/3
        
        dy= (ay3-dy3)/2
        dx= (ax3-dx3)/2
        control_points = [(ax3,ay3),(ax3-dx/20,ay3-dy/2),(dx3+dx/20,dy3+dy/2),(dx3,dy3)]
        for i in range(num_segments + 1):
            t = float(i) / num_segments
            yield self.bezier_point(control_points, t)
    def bezier_curve_pointsB(self, num_segments=50):
        """
        使用生成器生成贝塞尔曲线上的点。

        Args:
            control_points: 控制点列表，每个点是一个 (x, y) 元组。
            num_segments: 用于近似曲线的线段数量。

        Yields:
            (x, y) 元组，表示贝塞尔曲线上的点。
        """
        ax1,ay1,ax2,ay2,ax3,ay3= self.A.get_output_triangle()
        bx1,by1,bx2,by2,bx3,by3= self.B.get_input_triangle()
        cx1,cy1,cx2,cy2,cx3,cy3= self.C.get_input_triangle()
        dx3= (ax3+bx3+cx3)/3
        dy3= (ay3+by3+cy3)/3
        
        dy= (dy3-by3)/2
        dx= (dx3-bx3)/2
        control_points = [(dx3,dy3),(dx3-dx/20,dy3-dy/2),(bx3+dx/20,by3+dy/2),(bx3,by3)]
        for i in range(num_segments + 1):
            t = float(i) / num_segments
            yield self.bezier_point(control_points, t)
    def bezier_curve_pointsC(self, num_segments=50):
        """
        使用生成器生成贝塞尔曲线上的点。

        Args:
            control_points: 控制点列表，每个点是一个 (x, y) 元组。
            num_segments: 用于近似曲线的线段数量。

        Yields:
            (x, y) 元组，表示贝塞尔曲线上的点。
        """
        ax1,ay1,ax2,ay2,ax3,ay3= self.A.get_output_triangle()
        bx1,by1,bx2,by2,bx3,by3= self.B.get_input_triangle()
        cx1,cy1,cx2,cy2,cx3,cy3= self.C.get_input_triangle()
        dx3= (ax3+bx3+cx3)/3
        dy3= (ay3+by3+cy3)/3
        self.x = dx3
        self.y = dy3
        dy= (dy3-cy3)/2
        dx= (dx3-cx3)/2
        control_points = [(dx3,dy3),(dx3-dx/20,dy3-dy/2),(cx3+dx/20,cy3+dy/2),(cx3,cy3)]
        for i in range(num_segments + 1):
            t = float(i) / num_segments
            yield self.bezier_point(control_points, t)
    def bezier_point(self,control_points, t):
        """
        计算贝塞尔曲线上的一个点。

        Args:
            control_points: 控制点列表，每个点是一个 (x, y) 元组。
            t: 参数值，范围从 0.0 到 1.0，表示曲线上的位置。

        Returns:
            (x, y) 元组，表示曲线上的点。
        """

        n = len(control_points) - 1
        x = 0.0
        y = 0.0

        for i, point in enumerate(control_points):
            x += self.binomial_coefficient(n, i) * pow(1 - t, n - i) * pow(t, i) * point[0]
            y += self.binomial_coefficient(n, i) * pow(1 - t, n - i) * pow(t, i) * point[1]

        return x, y
    def binomial_coefficient(self,n, k):
        """
        计算二项式系数 (n choose k)。
        """
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        if k > n // 2:
            k = n - k
        result = 1
        for i in range(k):
            result = result * (n - i) // (i + 1)
        return result
    def GLDraw(self):     
        if self.status == 'Normal':
            glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])
        else:
            glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])    
        if self.A is None or self.B is None or self.C is None:
            glBegin(GL_LINE_STRIP)
            glVertex2f(self.x-self.radius*2, self.y-self.radius*2)
            glVertex2f(self.x+self.radius*2, self.y-self.radius*2)
            glVertex2f(self.x+self.radius*2, self.y+self.radius*2)
            glVertex2f(self.x-self.radius*2, self.y+self.radius*2)
            glEnd()        
            return
        glBegin(GL_LINE_STRIP)
        for index,point in enumerate(self.bezier_curve_pointsA()):
            glVertex2f(point[0], point[1])
        glEnd()
        glBegin(GL_LINE_STRIP)
        if not self.result:
            glColor3f(0.5,0.5,0.5)
        else:
            glColor3f(1.0,1.0,1.0)
        for index,point in enumerate(self.bezier_curve_pointsB()):
            glVertex2f(point[0], point[1])
        glEnd()
        glBegin(GL_LINE_STRIP)
        if  self.result:
            glColor3f(0.5,0.5,0.5)
        else:
            glColor3f(1.0,1.0,1.0)            
        for index,point in enumerate(self.bezier_curve_pointsC()):
            glVertex2f(point[0], point[1])
        glEnd()
        glBegin(GL_QUADS)
        glColor3f(0.0,1.0,0.0)
        glVertex2f(self.x-self.radius/2, self.y-self.radius/2)
        glVertex2f(self.x, self.y-self.radius/2)
        glVertex2f(self.x, self.y+self.radius/2)
        glVertex2f(self.x-self.radius/2, self.y+self.radius/2)        
        glEnd()
        glBegin(GL_QUADS)
        glColor3f(1.0,0.0,0.0)
        glVertex2f(self.x, self.y-self.radius/2)
        glVertex2f(self.x+self.radius/2, self.y-self.radius/2)
        glVertex2f(self.x+self.radius/2, self.y+self.radius/2)
        glVertex2f(self.x, self.y+self.radius/2)        
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)     
        if self.A.parameters[self.KyeA] is not None:
            # Draw output triangle
            p1x, p1y, p2x, p2y, p3x, p3y = self.A.get_output_triangle()
            glBegin(GL_LINE_LOOP)
            glVertex2f(p1x, p1y)
            glVertex2f(p2x, p2y)
            glVertex2f(p3x, p3y)
            glEnd()        
        if self.B.parameters[self.KyeB] is not None:
            p1x, p1y, p2x, p2y, p3x, p3y = self.B.get_input_triangle()
            glBegin(GL_LINE_LOOP)
            glVertex2f(p1x, p1y)
            glVertex2f(p2x, p2y)
            glVertex2f(p3x, p3y)
            glEnd()
        if self.C.parameters[self.KyeC] is not None:
            p1x, p1y, p2x, p2y, p3x, p3y = self.C.get_input_triangle()
            glBegin(GL_LINE_LOOP)
            glVertex2f(p1x, p1y)
            glVertex2f(p2x, p2y)
            glVertex2f(p3x, p3y)
            glEnd()
        glColor3f(1.0, 1.0, 1.0)
    def run(self):
        starttime = time.perf_counter()
        try:
            if self.A.parameters[self.KyeA] is True:
                self.result = True
            else:
                self.result = False
            self.lastrunstatus = True
        except Exception as e:
            self.lastrunstatus = False
            messagebox.showerror("Error", f"Failed to set line parameters: {e}")
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
    def save(self):
        """保存模块为JSON"""
        file_path = filedialog.asksaveasfilename(defaultextension=f"{self.text}.cvlm",
                                                 filetypes=[("JSON files", "*.cvlm"), ("All files", "*.*")])
        if file_path:
            try:
                # 只保存可序列化的属性
                data = {
                    "class": self.__class__.__name__,
                    "x": self.x,
                    "y": self.y,
                    "radius": self.radius,
                    "text": self.text,
                    "normalcolor": self.normalcolor,
                    "selectedcolor": self.selectedcolor,
                    "font_path": self.font_path,
                    "font_size": self.font_size,
                    "textcolor": self.textcolor,
                    "parameters": self.parameters,
                    "breifimagewidth": self.breifimagewidth,
                    "breifimageheight": self.breifimageheight,
                    "language": self.language,
                    "status": self.status,
                    "result": self.result,
                    "KeyA": self.KyeA,
                    "KeyB": self.KyeB,
                    "KeyC": self.KyeC,
                    "A": self.A.text,
                    "B": self.B.text,
                    "C": self.C.text,
                }
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "Module saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save module: {e}")
    def load(self,modules):
        """加载模块的JSON文件"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.cvlm"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data.get("class") != self.__class__.__name__:
                    messagebox.showerror(self.texts['load_button_tip_title'], self.texts['load_button_content'])
                    return
                # 只加载可序列化的属性
                self.x = data.get("x", self.x)
                self.y = data.get("y", self.y)
                self.radius = data.get("radius", self.radius)
                self.text = data.get("text", self.text)
                self.normalcolor = data.get("normalcolor", self.normalcolor)
                self.selectedcolor = data.get("selectedcolor", self.selectedcolor)
                self.font_path = data.get("font_path", self.font_path)
                self.font_size = data.get("font_size", self.font_size)
                self.textcolor = data.get("textcolor", self.textcolor)
                self.parameters = data.get("parameters", {})
                self.breifimagewidth = data.get("breifimagewidth",self.breifimagewidth)
                self.breifimageheight = data.get("breifimageheight",self.breifimageheight)
                self.language = data.get("language", self.language)
                self.status = data.get("status",self.status)
                self.result = data.get("result",self.result)
                self.KyeA = data.get("KeyA",self.KyeA)
                self.KyeB = data.get("KeyB",self.KyeB)
                self.KyeC = data.get("KeyC",self.KyeC)
                self.A = modules[data.get("A",self.A.text)]
                self.B = modules[data.get("B",self.B.text)]
                self.C = modules[data.get("C",self.C.text)]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load module: {e}")        
    def show_parameter_page(self,x,y,parent):
        x1, y1, x2, y2 = self.get_inside_rect()
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            return
        def update_io():
            buttona.config(text=f"A:   {self.A.text}\n    {gstr(self.A.parameters[self.KyeA])}")
            buttonb.config(text=f"B:   {self.B.text}\n    {gstr(self.B.parameters[self.KyeB])}")       
            buttonb.config(text=f"C:   {self.C.text}\n    {gstr(self.C.parameters[self.KyeC])}")       
            pass
        def change_language():
            self.language = languages_commbox.get()
            self.set_language(self.language)
            run_button.config(text=self.texts['run_button'])
            del_button.config(text=self.texts['del_button'])
            save_button.config(text=self.texts['save_button'])
            load_button.config(text=self.texts['load_button'])
            info_label.config(text=self.texts['info_label'])
            notebook.tab(tab1, text=self.texts['tab1'])
            notebook.tab(tab2, text=self.texts['tab2'])
            notebook.tab(tab3, text=self.texts['tab3'])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
        def check_language():
            self.set_language(self.language)
            run_button.config(text=self.texts['run_button'])
            del_button.config(text=self.texts['del_button'])
            save_button.config(text=self.texts['save_button'])
            load_button.config(text=self.texts['load_button'])
            info_label.config(text=self.texts['info_label'])
            notebook.tab(tab1, text=self.texts['tab1'])
            notebook.tab(tab2, text=self.texts['tab2'])
            notebook.tab(tab3, text=self.texts['tab3'])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            htmllabel.set_html(self.description_html[self.language])

        def choose_color():
            color = colorchooser.askcolor(color=(int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255)), title="Choose Color")
            if color[0] is not None:
                self.normalcolor = [color[0][0]/255,color[0][1]/255,color[0][2]/255,1.0]
                button.config(bg=color[1])
        def run_button_click():
            self.run()
            info_label.config(text=f'Info: CT:{self.spantime:.4f}s')
            update_io()
        def del_button_click():
            if tk.messagebox.askokcancel(self.texts['del_button_tip_title'], self.texts['del_button_tip_content']):
                self.message(self,-1)
                window.destroy()
        window= tk.Toplevel(parent)
        window.title(self.text)
        window.iconbitmap(iconp)
        rootx= parent.winfo_rootx()
        rooty= parent.winfo_rooty()
        window.geometry(f'300x432+{rootx}+{rooty}')

        button_frame = tk.Frame(window)
        button_frame.pack(side='top', anchor='nw', pady=5)

        run_button = tk.Button(button_frame, text=self.texts['run_button'], command=run_button_click)
        run_button.pack(side='left', padx=1)

        del_button = tk.Button(button_frame, text=self.texts['del_button'], command=del_button_click)
        del_button.pack(side='left', padx=1)
        
        save_button = tk.Button(button_frame, text=self.texts['save_button'], command=self.save)
        save_button.pack(side='left', padx=1)
        
        load_button = tk.Button(button_frame, text=self.texts['load_button'])
        load_button.bind('<Button-1>',lambda event: self.load(),add=True)
        load_button.bind('<Button-1>',lambda event: update_io(),add=True)
        load_button.pack(side='left', padx=1)

        info_label = tk.Label(window,text=self.texts['info_label'])
        info_label.pack(side='bottom',anchor='sw')

        notebook = ttk.Notebook(window)
        notebook.pack(fill='both', expand=True)
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        
        notebook.add(tab1,text=self.texts['tab1'])
        notebook.add(tab2,text=self.texts['tab2'])
        notebook.add(tab3,text=self.texts['tab3'])

        frame = tk.Frame(tab1)
        frame.pack(padx=10, pady=10)
        tk.Label(frame, text="X:").grid(row=0, column=0, pady=5)
        x_entry = tk.Entry(frame)
        x_entry.insert(0, self.x)
        x_entry.grid(row=0, column=1, pady=5)
        x_entry.bind('<Return>', lambda event: setattr(self, 'x', int(x_entry.get())))
        tk.Label(frame, text="Y:").grid(row=1, column=0, pady=5)
        y_entry = tk.Entry(frame)
        y_entry.insert(0, self.y)
        y_entry.grid(row=1, column=1, pady=5)
        y_entry.bind('<Return>', lambda event: setattr(self, 'y', int(y_entry.get())))
        namelabel=tk.Label(frame, text=self.texts['name_label'])
        namelabel.grid(row=2, column=0, pady=5)
        text_entry = tk.Entry(frame)
        text_entry.delete(0, 'end')
        text_entry.insert(0, self.text)
        text_entry.grid(row=2, column=1, pady=5)
        text_entry.bind('<Return>',lambda event: setattr(self,'text',text_entry.get()),add=True)
        text_entry.bind('<Return>',lambda event: self.get_image(),add=True)
        text_entry.bind('<Return>',lambda event: self.message(self,-2),add=True)

        labelcolor=tk.Label(frame, text=self.texts['labelcolor'])
        labelcolor.grid(row=4, column=0, pady=5)
        button = tk.Button(frame, text=self.texts['color_choose'], command=choose_color)
        button.grid(row=4,column=1,pady=5)
        
        fontsize_label=tk.Label(frame, text=self.texts['fontsize'])
        fontsize_label.grid(row=5, column=0, pady=5)
        spinbox= tk.Spinbox(frame,from_=1,to=48)
        spinbox.delete(0, 'end')
        spinbox.insert(0, self.font_size)
        spinbox.bind('<Button-1>',lambda evemt: setattr(self,'font_size',int(spinbox.get())),add=True)
        spinbox.bind('<Button-1>',lambda evemt: self.get_image(),add=True)

        spinbox.grid(row=5,column=1,pady=5)
        
        
        fontpath_label=tk.Label(frame, text=self.texts['fontpath'])
        fontpath_label.grid(row=6, column=0, pady=5)
        fontscale_spinbox= tk.Entry(frame)
        fontscale_spinbox.delete(0, 'end')
        fontscale_spinbox.insert(0, self.font_path)
        fontscale_spinbox.bind('<Return>',lambda event: setattr(self,'font_path',fontscale_spinbox.get()),add=True)
        fontscale_spinbox.bind('<Return>',lambda event: self.get_image(),add=True)
        fontscale_spinbox.grid(row=6,column=1,pady=5)
        
        brieifimage_width = tk.Label(frame, text=self.texts['brifeimagewidth'])
        brieifimage_width.grid(row=7, column=0, pady=5)
        brieifimage_width_entry = tk.Entry(frame)
        brieifimage_width_entry.delete(0, 'end')
        brieifimage_width_entry.insert(0, self.breifimagewidth)
        brieifimage_width_entry.grid(row=7, column=1, pady=5)
        brieifimage_width_entry.bind('<Return>',lambda event: setattr(self,'breifimagewidth',int(brieifimage_width_entry.get())))
        
        brieifimage_height = tk.Label(frame, text=self.texts['brifeimageheight'])
        brieifimage_height.grid(row=8, column=0, pady=5)
        brieifimage_height_entry = tk.Entry(frame)
        brieifimage_height_entry.delete(0, 'end')
        brieifimage_height_entry.insert(0, self.breifimageheight)
        brieifimage_height_entry.grid(row=8, column=1, pady=5)
        brieifimage_height_entry.bind('<Return>',lambda event: setattr(self,'breifimageheight',int(brieifimage_height_entry.get())))
        
        breifimage_enbale = tk.Label(frame, text=self.texts['brifeimage'])
        breifimage_enbale.grid(row=9, column=0, pady=5)
        breifimage_enbale_checkbox = tk.Checkbutton(frame, variable= self.breifimage_visible, onvalue=1, offvalue=0)
        breifimage_enbale_checkbox.grid(row=9, column=1, pady=5)    
        
        languages_lable = tk.Label(frame, text=self.texts['language'])
        languages_lable.grid(row=10, column=0, pady=5)
        languages_commbox = ttk.Combobox(frame,values= ['en', 'zh'], state='readonly', width=5)
        languages_commbox.set(self.language)
        languages_commbox.grid(row=10, column=1, pady=5)
        languages_commbox.bind('<<ComboboxSelected>>', lambda event: change_language(), add=True)
        
        buttona=tk.Button(tab2, text=f"A:   {self.A.text}\n    {gstr(self.A.parameters[self.KyeA])}",justify='left',anchor='w')
        buttona.grid(row=0, column=0,sticky='ew' ,pady=5)
        buttona.bind('<Button-1>',lambda event: self.message(self,1,**dict([('paramname','A'),('keyname','KyeA'),('button',buttona)])),add=True)

        buttonb=tk.Button(tab2, text=f"B:   {self.B.text}\n    {gstr(self.B.parameters[self.KyeB])}",justify='left',anchor='w')
        buttonb.grid(row=1, column=0,sticky='ew' ,pady=5)
        buttonb.bind('<Button-1>',lambda event: self.message(self,1,**dict([('paramname','B'),('keyname','KyeB'),('button',buttonb)])),add=True) 
        
        buttonc=tk.Button(tab2, text=f"C:   {self.C.text}\n    {gstr(self.C.parameters[self.KyeC])}",justify='left',anchor='w')
        buttonc.grid(row=2, column=0,sticky='ew' ,pady=5)
        buttonc.bind('<Button-1>',lambda event: self.message(self,1,**dict([('paramname','C'),('keyname','KyeC'),('button',buttonc)])),add=True)
        
        htmllabel= HTMLLabel(tab3, html=self.description_html[self.language])
        htmllabel.pack(fill=tk.BOTH, expand=True)

        notebook.select(tab2)  # 默认选中第二个标签页
        
        check_language()
        update_io()
class Graphics_OpenFileModule(Graphics_ValueModule):
    def __init__(self,x:int=0,y:int=0,name:str='OpenFile',message=None):
        super().__init__(x,y,name,message)
        self.parameters={'filename':None,'lastrunstatus':self.lastrunstatus}
    def run(self):
        starttime = time.perf_counter()
        self.statuscolor = [1.0, 1.0, 0.0]
        """打开文件对话框，选择图片文件"""
        try:
            reslut = filedialog.askopenfilename(title="Open File", filetypes=[("All Files", "*.*")])
            if reslut:
                self.parameters['filename']=reslut
                self.lastrunstatus = True
                self.statuscolor = [0.0, 1.0, 0.0]
            else:
                self.lastrunstatus = False
                self.statuscolor = [1.0, 0.0, 0.0]
        except Exception as e:
            self.lastrunstatus = False
            self.statuscolor = [1.0, 0.0, 0.0]
            messagebox.showerror("Error", f"Failed to load image: {e}")
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
        self.parameters['lastrunstatus']=self.lastrunstatus
class Graphics_TiffModule(Graphics_ValueModule):
    def __init__(self,x:int=0,y:int=0,name:str='LoadTiff',message=None):
        super().__init__(x,y,name,message)
        self.breifimage_visible = tk.IntVar(value=1)
        self.parameters={'filename':None,'lastrunstatus':self.lastrunstatus}
    def run(self):
        starttime = time.perf_counter()
        self.statuscolor = [1.0, 1.0, 0.0]
        """打开文件对话框，选择图片文件"""
        try:
            self.rawimg = tiff.imread(self.parameters['filename'])
            if self.rawimg.ndim == 3:
                self.rawimg = self.rawimg[:, :, 0]  # 取第一个通道
                self.format = GL_LUMINANCE
                self.pixel_format =GL_FLOAT
                self.parameters['image']=np.expand_dims(self.rawimg, axis=-1)  # 添加一个维度以匹配GL_LUMINANCE的要求
                self.breifimage = self.parameters['image'][::16, ::16]  # 下采样
                self.lastrunstatus = True
                self.statuscolor = [0.0, 1.0, 0.0]
            elif self.rawimg.ndim == 2:
                self.format = GL_LUMINANCE
                self.pixel_format =GL_FLOAT
                self.parameters['image']=np.expand_dims(self.rawimg, axis=-1)
                self.breifimage = self.parameters['image'][::16, ::16]  # 下采样
                self.lastrunstatus = True
                self.statuscolor = [0.0, 1.0, 0.0]
            else:
                self.lastrunstatus = False
                self.breifimage = None
                self.statuscolor = [1.0, 0.0, 0.0]
        except Exception as e:
            self.breifimage = None
            self.lastrunstatus = False
            self.statuscolor = [1.0, 0.0, 0.0]
            messagebox.showerror("Error", f"Failed to load image: {e}")
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
        self.parameters['lastrunstatus']=self.lastrunstatus
def gstr(object):
    if isinstance(object,np.ndarray):
        return str(object.shape)
    else:
        return str(object)
        
