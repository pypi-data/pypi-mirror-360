# simui/core.py

import tkinter as tk

class Ui:
    def __init__(self, title="SimUI App", size="400x300"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(size)

    def run(self):
        self.root.mainloop()


class label:
    def __init__(self, parent, txt="", size=12):
        self.widget = tk.Label(parent, text=txt, font=("Arial", size))
        self.widget.pack()


class btn:
    def __init__(self, parent, text="", cmd=None):
        self.widget = tk.Button(parent, text=text, command=cmd)
        self.widget.pack()


class entry:
    def __init__(self, parent, width=20, txt=""):
        self.var = tk.StringVar(value=txt)
        self.widget = tk.Entry(parent, textvariable=self.var, width=width)
        self.widget.pack()

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)


class checkbox:
    def __init__(self, parent, txt="", defu=False):
        self.var = tk.BooleanVar(value=defu)
        self.widget = tk.Checkbutton(parent, text=txt, variable=self.var)
        self.widget.pack()

    def get(self):
        return self.var.get()

    def set(self, val: bool):
        self.var.set(val)
class txt:
    def __init__(self, parent, width=40, height=5, txt=""):
        self.widget = tk.Text(parent, width=width, height=height)
        self.widget.pack()
        if txt:
            self.widget.insert("1.0", txt)

    def get(self):
        return self.widget.get("1.0", "end-1c")  # remove trailing newline

    def set(self, text):
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", text)

    def clear(self):
        self.widget.delete("1.0", "end")
class frame:
    def __init__(self, parent, bg=None, borderwidth=0, relief=None, padding=0):
        self.widget = tk.Frame(parent, bg=bg, borderwidth=borderwidth, relief=relief)
        self.widget.pack(padx=padding, pady=padding)

    def add(self, child_widget):
        # Automatically pack added child inside this frame
        child_widget.widget.pack()
class canvas:
    def __init__(self, parent, width=300, height=200, bg="white"):
        self.widget = tk.Canvas(parent, width=width, height=height, bg=bg)
        self.widget.pack()

    def create_line(self, x1, y1, x2, y2, color="black", width=1):
        self.widget.create_line(x1, y1, x2, y2, fill=color, width=width)

    def create_rect(self, x1, y1, x2, y2, color="black"):
        self.widget.create_rectangle(x1, y1, x2, y2, outline=color)

    def create_oval(self, x1, y1, x2, y2, color="black"):
        self.widget.create_oval(x1, y1, x2, y2, outline=color)

    def create_text(self, x, y, text, size=12, color="black"):
        self.widget.create_text(x, y, text=text, fill=color, font=("Arial", size))

    def clear(self):
        self.widget.delete("all")

class radiog:
    def __init__(self, parent, options, defu=None):
        self.var = tk.StringVar(value=defu if defu else options[0])
        self.buttons = []
        for option in options:
            btn = tk.Radiobutton(parent, text=option, variable=self.var, value=option)
            btn.pack(anchor="w")
            self.buttons.append(btn)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

class SimScale:
    def __init__(self, parent, from_=0, to=100, orient='horizontal', length=200, defu=None):
        self.var = tk.DoubleVar(value=defu if defu is not None else from_)
        self.widget = tk.Scale(
            parent, from_=from_, to=to, orient=orient,
            length=length, variable=self.var
        )
        self.widget.pack()

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

class listbox:
    def __init__(self, parent, items=None, height=5, select_mode="browse"):
        self.widget = tk.Listbox(parent, height=height, selectmode=select_mode)
        self.widget.pack()
        if items:
            for item in items:
                self.widget.insert(tk.END, item)

    def get(self):
        # Returns selected item(s)
        selection = self.widget.curselection()
        return [self.widget.get(i) for i in selection]

    def clear(self):
        self.widget.delete(0, tk.END)

    def add(self, item):
        self.widget.insert(tk.END, item)

    def delete(self, index):
        self.widget.delete(index)

class spinbox:
    def __init__(self, parent, from_=0, to=10, width=5, defu=None, values=None):
        """
        - If `values` is provided (list/tuple), spinbox cycles through them.
        - Otherwise numeric from `from_` to `to`.
        """
        self.var = tk.StringVar()
        if values:
            self.widget = tk.Spinbox(parent, values=values, textvariable=self.var, width=width)
            self.var.set(defu if defu in values else values[0])
        else:
            self.widget = tk.Spinbox(parent, from_=from_, to=to, textvariable=self.var, width=width)
            self.var.set(str(defu if defu is not None else from_))
        self.widget.pack()

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(str(value))

class scrollbar:
    def __init__(self, parent, orient='vertical', target_widget=None):
        self.widget = tk.Scrollbar(parent, orient=orient)
        self.widget.pack(side='right' if orient == 'vertical' else 'bottom', fill='y' if orient == 'vertical' else 'x')
        
        if target_widget:
            # Connect scrollbar to the target widget's yview/xview
            if orient == 'vertical':
                target_widget.config(yscrollcommand=self.widget.set)
                self.widget.config(command=target_widget.yview)
            else:
                target_widget.config(xscrollcommand=self.widget.set)
                self.widget.config(command=target_widget.xview)

class menu:
    def __init__(self, app):
        self.menubar = tk.Menu(app.root)
        app.root.config(menu=self.menubar)
        self.menus = {}

    def add_menu(self, label):
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=label, menu=menu)
        self.menus[label] = menu
        return menu

    def add_command(self, menu_label, label, command=None):
        menu = self.menus.get(menu_label)
        if menu:
            menu.add_command(label=label, command=command)

    def add_separator(self, menu_label):
        menu = self.menus.get(menu_label)
        if menu:
            menu.add_separator()

class menubtn:
    def __init__(self, parent, label="", menu_items=None):
        """
        menu_items: list of tuples (label, command)
        """
        self.widget = tk.Menubutton(parent, text=label, relief=tk.RAISED)
        self.menu = tk.Menu(self.widget, tearoff=0)
        self.widget.config(menu=self.menu)
        self.widget.pack()

        if menu_items:
            for item_label, cmd in menu_items:
                self.menu.add_command(label=item_label, command=cmd)

import tkinter.messagebox as mb

class message:
    @staticmethod
    def info(title, message):
        mb.showinfo(title, message)

    @staticmethod
    def warning(title, message):
        mb.showwarning(title, message)

    @staticmethod
    def error(title, message):
        mb.showerror(title, message)

    @staticmethod
    def ask_yes_no(title, message):
        return mb.askyesno(title, message)

    @staticmethod
    def ask_ok_cancel(title, message):
        return mb.askokcancel(title, message)

class panedwindow:
    def __init__(self, parent, orient='horizontal'):
        orient = orient.lower()
        if orient not in ('horizontal', 'vertical'):
            raise ValueError("orient must be 'horizontal' or 'vertical'")
        self.widget = tk.PanedWindow(parent, orient=tk.HORIZONTAL if orient == 'horizontal' else tk.VERTICAL)
        self.widget.pack(fill='both', expand=True)

    def add(self, child_widget):
        self.widget.add(child_widget.widget)

    def remove(self, child_widget):
        self.widget.forget(child_widget.widget)

class labelframe:
    def __init__(self, parent, text="", padding=5, borderwidth=2, relief="groove"):
        self.widget = tk.LabelFrame(parent, text=text, borderwidth=borderwidth, relief=relief, padx=padding, pady=padding)
        self.widget.pack()

    def add(self, child_widget):
        # Pack child widget inside the labelframe
        child_widget.widget.pack()

class optionmenu:
    def __init__(self, parent, options, defu=None):
        self.var = tk.StringVar(value=defu if defu else options[0])
        self.widget = tk.OptionMenu(parent, self.var, *options)
        self.widget.pack()

    def get(self):
        return self.var.get()

    def set(self, value):
        if value in self.widget['menu'].entrycget(0, 'label') or value in self.widget['menu'].entryconfigure():
            self.var.set(value)
        else:
            self.var.set(value)  # Set anyway; validation not strict here

class toplevel:
    def __init__(self, parent, title="New Window", size="300x200"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(size)

    def show(self):
        self.window.deiconify()

    def hide(self):
        self.window.withdraw()

    def close(self):
        self.window.destroy()

    def add(self, child_widget):
        child_widget.widget.pack()