import tkinter
import tkinter.filedialog
import tkinter.ttk

import pygame
from init import *

if is_windows:
    import win32gui

ok = False
text = ''


def _size(w: int, h: int) -> str:
    if is_windows:
        rect = win32gui.GetWindowRect(win32gui.FindWindow(
            None, pygame.display.get_caption()[0]))
        return f'{w}x{h}+{int(rect[0]+rect[2]-w)//2}+{int(rect[1]+rect[3]-h)//2}'
    else:
        return f'{w}x{h}'


def choose(msg: str, title: str, choices: list, default: int = 0) -> str:
    """
    单选框。
    """
    global text
    text = ''

    tk = tkinter.Tk()
    tk.geometry(_size(400, 200))
    tk.resizable(0, 0)
    tk.title(title)

    tkinter.Label(tk, text=msg).pack(pady=5)
    inp = tkinter.Listbox(tk, height=7)
    inp.pack(fill='x')
    inp.focus_set()
    if len(choices) > 7:
        bar = tkinter.Scrollbar(tk, commond=inp.yview)
        bar.pack(fill='y', side='right')
        inp.config(yscrollcommand=bar.set)

    for i in choices:
        inp.insert(tkinter.END, i)
    inp.select_set(default, default)

    def submit():
        global text
        user_choice = inp.curselection()
        if user_choice:
            text = choices[user_choice[0]]
        tk.destroy()

    tk.bind('<Return>', lambda x: submit())
    tkinter.Button(tk, text='确认', command=submit, width=10).pack(pady=5)
    tkinter.mainloop()
    return text


def folder(title: str) -> str:
    """
    选择文件夹。
    """
    tk = tkinter.Tk()
    tk.withdraw()
    filename = tkinter.filedialog.askdirectory(title=title)
    tk.destroy()
    return filename


def input(msg: str, title: str) -> None:
    """
    输入框。
    """
    global text
    text = ''

    tk = tkinter.Tk()
    tk.geometry(_size(400, 110))
    tk.resizable(0, 0)
    tk.title(title)

    tkinter.Label(tk, text=msg).pack(pady=5)
    inp = tkinter.Entry(tk, width=50)
    inp.focus_force()
    inp.pack(pady=5)

    def submit():
        global text
        text = inp.get()
        tk.destroy()

    tk.bind('<Return>', lambda x: submit())
    tkinter.Button(tk, text='确认', command=submit, width=10).pack(pady=5)
    tkinter.mainloop()
    return text


def open(title: str, name: str, type: str) -> str:
    """
    打开文件。
    """
    tk = tkinter.Tk()
    tk.withdraw()
    file = tkinter.filedialog.askopenfilename(
        title=title, filetypes=[(name, type)])
    tk.destroy()
    return file


def print(msg: str, title: str) -> None:
    """
    提示框。
    """
    tk = tkinter.Tk()
    tk.geometry(_size(400, 80))
    tk.resizable(0, 0)
    tk.title(title)
    tk.focus_force()

    tkinter.Label(tk, text=msg).pack(pady=5)
    tk.bind('<Return>', lambda x: tk.destroy())
    tkinter.Button(tk, text='确认', command=tk.destroy,
                   width=10).pack(pady=5)

    tkinter.mainloop()


def save(title: str, default: str, name: str, type: str) -> str:
    """
    保存文件。
    """
    tk = tkinter.Tk()
    tk.withdraw()
    filename = tkinter.filedialog.asksaveasfilename(
        title=title, filetypes=[(name, type)], initialfile=default)
    tk.destroy()
    return filename


def yesno(msg: str, title: str) -> None:
    """
    确认框。
    """
    global ok
    ok = False
    tk = tkinter.Tk()
    tk.geometry(_size(400, 80))
    tk.resizable(0, 0)
    tk.title(title)
    tk.focus_force()

    tkinter.Label(tk, text=msg).pack(pady=5)

    def yes():
        global ok
        ok = True
        tk.destroy()

    tk.bind('<Return>', lambda x: yes())
    tkinter.Button(tk, text='确认', command=yes, width=10).pack(
        side='left', padx=5, pady=5)
    tkinter.Button(tk, text='取消', command=tk.destroy,
                   width=10).pack(side='right', padx=5, pady=5)
    tkinter.mainloop()
    return ok
