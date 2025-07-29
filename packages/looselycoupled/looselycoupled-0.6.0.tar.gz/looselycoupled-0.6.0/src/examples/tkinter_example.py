#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import logging
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox

try:
    Module = object
except ImportError:
    pass


standalone = False
logger = logging.getLogger(__name__);


def init_gui(enqueuing_func=None):
    '''Initialize the GUI objects'''
    root = tk.Tk()
    top = TkinterExample(root, enqueuing_func)
    return root, top

def run_gui(root):
    '''Start and run the GUI event loop'''
    root.focus()
    root.mainloop()


class TkinterExample(Module):
    '''Module for the Tk-based main window'''

    def __init__(self, top, enqueuing_func = None):
        '''Configure and populate the toplevel window'''
        # Init member variables and properties
        self.name = 'gui'
        self.enqueuing_func = enqueuing_func
        self.buttons = dict()
        # Prepare Tk
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == 'win32':
            self.style.theme_use('winnative')
        self.style.configure('.', background=_bgcolor)
        self.style.configure('.', foreground=_fgcolor)
        self.style.map('.', background=[('selected', _compcolor), ('active', _ana2color)])
        # Window configuration
        self.top = top
        top.geometry('780x540+100+80')
        top.title('TKinter Example')
        self.configure_design(top, ['background', 'highlightbackground', 'highlightcolor'])
        top.minsize(700, 450)
        top.maxsize(1920, 1080)
        top.grid_rowconfigure(1, weight=1, minsize=250)
        top.grid_rowconfigure(2, weight=6, minsize=0) # minsize 0 or 80 - depending on whether code frame shall be able to be hidden completely
        for i in range(1, 6):
            top.grid_columnconfigure(i, weight=0, minsize=128)
        top.grid_columnconfigure(6, weight=1, minsize=30)
        # Variables
        self.values_inputs = [ tk.BooleanVar(name='input{0}'.format(i)) for i in range(8) ]
        self.values_motors = [ tk.IntVar(name='motor{0}'.format(i)) for i in range(4) ]
        # Window's controls
        self.insert_button(top, 0.135, 0.1, 'ButtonLeftProjector', '< Projector', rectangle=True)
        self.insert_button(top, 0.435, 0.1, 'ButtonRightProjector', 'Projector >', rectangle=True)
        self.insert_button(top, 0.3, 0.2, 'ButtonSwitchProjectors', 'Switch P')
        self.insert_button(top, 0.3, 0.35, 'ButtonSwitchDisplays', 'Switch D')
        self.insert_button(top, 0.2, 0.45, 'ButtonLeftMute', 'Mute')
        self.insert_button(top, 0.4, 0.45, 'ButtonRightMute', 'Mute')
        self.insert_button(top, 0.1, 0.6, 'ButtonLeftUSBC', 'USB-C')
        self.insert_button(top, 0.2, 0.6, 'ButtonLeftHDMI', 'HDMI 1')
        self.insert_button(top, 0.4, 0.6, 'ButtonRightUSBC', 'USB-C')
        self.insert_button(top, 0.5, 0.6, 'ButtonRightHDMI', 'HDMI 2')
        # Window's controls, right column
        self.insert_button(top, 0.7, 0.1, 'ButtonVolumeInc', '+')
        self.insert_button(top, 0.7, 0.25, 'ButtonVolumeDefault', 'Default')
        self.insert_button(top, 0.7, 0.4, 'ButtonVolumeDec', '-')
        self.insert_button(top, 0.68, 0.6, 'ButtonOff', 'Off', rectangle=True)

    def insert_button(self, parent, relx, rely, name, caption, rectangle=False):
        self.buttons[name] = button = tk.Button(parent, text=caption)
        button.place(relx=relx, rely=rely, height=50, width=75 if rectangle else 50)
        self.configure_design(button, ['activebackground', 'activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        button.configure(pady='0')
        button.bind("<ButtonPress-1>", lambda event: self.on_button_event(event, name, True))
        button.bind("<ButtonRelease-1>", lambda event: self.on_button_event(event, name, False))
        self.set_button_color(name)

    def on_button_event(self, event, name, rising_edge):
        #tk.messagebox.showinfo(title=name, message=str(rising_edge) + ' ' + str(event))
        if standalone:
            self.set_button_color(name, rising_edge)

    def set_button_color(self, name, active=False):
        if name == 'ButtonLeftProjector':  # green
            color = '#44ff44' if active else '#22a922'
        elif name == 'ButtonRightProjector':  # blue
            color = '#5588ff' if active else '#2222cc'
        elif (name == 'ButtonLeftMute') or (name == 'ButtonRightMute'):  # yellow
            color = '#ffff44' if active else '#d9d988'
        elif name == 'ButtonOff':  # red
            color = '#ff4444' if active else '#a92222'
        else:
            color = '#fdfdfd' if active else '#d9d9d9'
        self.buttons[name].configure(background=color)
        self.buttons[name].configure(activebackground=color)

    def configure_design(self, ctrl, attrs):
        '''Configure the given control's parameters to values set centrally in this method'''
        if 'activebackground' in attrs:
            ctrl.configure(activebackground='#ececec')
        if 'activeforeground' in attrs:
            ctrl.configure(activeforeground='#000000')
        if 'background' in attrs:
            ctrl.configure(background='#d9d9d9')
        if 'borderwidth' in attrs:
            ctrl.configure(borderwidth='2')
        if 'font' in attrs:
            ctrl.configure(font='TkDefaultFont')
        if 'foreground' in attrs:
            ctrl.configure(foreground='#000000') # black
        if 'disabledforeground' in attrs:
            ctrl.configure(disabledforeground='#a3a3a3')
        if 'highlightbackground' in attrs:
            ctrl.configure(highlightbackground='#d9d9d9')
        if 'highlightcolor' in attrs:
            ctrl.configure(highlightcolor='black')
        if 'insertbackground' in attrs:
            ctrl.configure(insertbackground='black')
        if 'relief' in attrs:
            ctrl.configure(relief='groove')
        if 'selectbackground' in attrs:
            ctrl.configure(selectbackground='#c4c4c4')
        if 'selectforeground' in attrs:
            ctrl.configure(selectforeground='black')
        if 'troughcolor' in attrs:
            ctrl.configure(troughcolor='#d9d9d9')


if __name__ == '__main__':
    standalone = True
    root, _ = init_gui()
    run_gui(root)
