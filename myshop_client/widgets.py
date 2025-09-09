from tkinter import ttk
from tkinter import *
from tkinter.messagebox import askquestion


class placeholderEntry(Entry):
    def __init__(self, master, placeholder='', cnf={}, fg='black',
                 fg_placeholder='grey50', *args, **kw):
        super().__init__(master, cnf={}, bg='white', *args, **kw)
        self.fg = fg
        self.show = kw.get('show','')
        self.fg_placeholder = fg_placeholder
        self.placeholder = placeholder
        self.bind('<FocusOut>', lambda event: self.fill_placeholder())
        self.bind('<FocusIn>', lambda event: self.clear_box())
        self.fill_placeholder()

    def clear_box(self):
        if not self.get() and super().get():
            self.config(show=self.show)
            self.config(fg=self.fg)
            self.delete(0,END)

    def fill_placeholder(self):
        content = self.get()
        if not content:
            self.config(show='')
            self.config(fg=self.fg_placeholder)
            self.insert(0, self.placeholder)
        else:
            self.config(fg=self.fg)
            self.config(show=self.show)
    
    def get(self):
        content = super().get()
        if content == self.placeholder:
            return ''
        return content

def EntryWithLabel(parent, label_text, textvariable='',variable_text='',label_cnf={},entry_cnf={},backgroud='skyblue',frame_name=''):
    if frame_name:
        frame = Frame(parent,name=frame_name,background=backgroud)
    else:
        frame = Frame(parent,background=backgroud)

    frame.pack(pady=5)
    
    label = Label(frame, text=label_text, width=20, anchor="e",cnf=label_cnf,background=backgroud)
    label.pack(side="left", padx=(0, 10))
    if textvariable:
        entry = Entry(frame,textvariable=textvariable,width=30,cnf=entry_cnf)
    else:
        entry = Entry(frame,textvariable=variable_text,width=30,cnf=entry_cnf)

    entry.pack(side="left", fill="x", expand=True)
    
    return entry

def ComboboxWithLabel(parent, label_text, textvariable='',variable_text='',label_cnf={},combox_cnf={},backgroud='skyblue',frame_name=''):
    if frame_name:
        frame =  Frame(parent,name=frame_name,background=backgroud)
    else:
        frame = Frame(parent,background=backgroud)

    frame.pack(pady=5)
    
    label = Label(frame, text=label_text, width=20, anchor="e",cnf=label_cnf,background=backgroud)
    label.pack(side="left", padx=(0, 10))
    if textvariable:
        combox = ttk.Combobox(frame,textvariable=textvariable,width=30,**combox_cnf)
    else:
        combox = ttk.Combobox(frame,extvariable=variable_text,width=30,**combox_cnf)
        
    combox.pack(side="left", fill="x", expand=True)
    
    return combox
