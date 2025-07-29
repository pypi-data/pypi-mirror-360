from OpenGL.GL import *
from OpenGL.WGL import *
import cv2 as cv
import tkinter as tk
import time
from tkinter import messagebox
import numpy as np
from mossflow.TkinterWidgets import Graphics_ValueModule,gstr
from tkhtmlview import HTMLLabel
from tkinter import ttk,colorchooser


class Graphics_RGBImageModule(Graphics_ValueModule):
    def __init__(self,x:int=0,y:int=0,name:str='LoadRGBImage',message=None):
        super().__init__(x,y,name,message)
        self.breifimage_visible = tk.IntVar(value=1)
        self.parameters={'filename':None,'lastrunstatus':self.lastrunstatus}
        self.rawname = 'loadrgbimg'
        self.zhname = '加载RGB图像'
        self.enname = 'Load RGB Image'
        self.imreadflaglang ={
            'zh':'读取标志',
            'en':'Read Flag'
        }
        self.tab4lang={
            'zh':'功能',
            'en':'Function'
        }
        self.imreadflag = 'IMREAD_COLOR'
    def run(self):
        starttime = time.perf_counter()
        self.statuscolor = [1.0, 1.0, 0.0]
        """打开文件对话框，选择图片文件"""
        try:
            with open(self.parameters['filename'], 'rb') as f:
                img_data = np.frombuffer(f.read(), dtype=np.uint8)
                self.rawimg = cv.imdecode(img_data,getattr(cv, self.imreadflag))
            if self.rawimg.ndim == 2:
                self.format = GL_LUMINANCE
                self.pixel_format =GL_UNSIGNED_BYTE
                self.parameters['image']=np.expand_dims(self.rawimg, axis=-1)  # 添加一个维度以匹配GL_LUMINANCE的要求
                self.breifimage = self.parameters['image'][::16, ::16]  # 下采样
                self.lastrunstatus = True
                self.statuscolor = [0.0, 1.0, 0.0]
            elif self.rawimg.ndim == 3 and self.rawimg.shape[2] == 3:
                self.format = GL_RGB
                self.pixel_format =GL_UNSIGNED_BYTE
                self.parameters['image']=np.expand_dims(self.rawimg, axis=-1)
                self.breifimage = self.parameters['image'][::16, ::16]  # 下采样
                self.lastrunstatus = True
                self.statuscolor = [0.0, 1.0, 0.0]
            elif self.rawimg.ndim == 3 and self.rawimg.shape[2] == 4:
                self.format = GL_RGBA
                self.pixel_format =GL_UNSIGNED_BYTE
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
    def render_breifimage(self, x, y):
        if self.breifimage is None or self.breifimage_visible.get() == 0:
            return
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        breifimage_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, breifimage_texture)
        glColor3f(1.0, 1.0, 1.0)

        glTexImage2D(GL_TEXTURE_2D, 0, self.format, self.breifimage.shape[1], self.breifimage.shape[0], 
                     0, self.format, self.pixel_format, self.breifimage)
        
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
            notebook.tab(tab4, text=self.tab4lang[self.language])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            imread_flag_lable.config(text=self.imreadflaglang[self.language])
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
            notebook.tab(tab4, text=self.tab4lang[self.language])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            imread_flag_lable.config(text=self.imreadflaglang[self.language])
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
        #window.iconbitmap('main.ico') set a icon for the window
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
        tab4 = ttk.Frame(notebook)
        notebook.add(tab1,text='View')
        notebook.add(tab2,text='Parameter')
        notebook.add(tab4,text='Function')
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
                  
        funframe = tk.Frame(tab4)
        funframe.pack(padx=10, pady=10)
        imread_flag_lable = tk.Label(funframe,text=self.imreadflaglang[self.language])
        imread_flag_lable.grid(row=0, column=0, pady=1,sticky='ew')
        imread_flag_commbox = ttk.Combobox(funframe, values=['IMREAD_COLOR', 'IMREAD_GRAYSCALE', 'IMREAD_UNCHANGED','IMREAD_ANYDEPTH','IMREAD_ANYCOLOR'], state='readonly', width=20)
        imread_flag_commbox.set(self.imreadflag)
        imread_flag_commbox.grid(row=0,column=1,pady=1,sticky='ew')
        imread_flag_commbox.bind('<<ComboboxSelected>>', lambda event: setattr(self, 'imreadflag',  imread_flag_commbox.get()), add=True)
                  
        html_label = HTMLLabel(tab3, html=self.description_html[self.language])
        html_label.pack(fill=tk.BOTH, expand=True)
        
        check_language()        
        update_io()