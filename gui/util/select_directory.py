from gui.util.util import bind_button
from tkinter import *
from tkinter import ttk, filedialog

class SelectDirectory(ttk.Labelframe):

    def __init__(self, parent, *args, **kwargs):
        self.title = kwargs.get("title") or "Select Folder"
        relief = kwargs.get("relief") or "solid"
        self.path = kwargs.get("path") or "No Path Specified"

        ttk.Labelframe.__init__(self, parent, relief=relief, text=self.title)

        # Textbox that contains the path
        self.path_textbox = Text(self, width=40, height=1, wrap="none", font='TkDefaultFont')
        self.path_textbox.insert("1.0", self.path)
        self.path_textbox["state"] = "disabled"
        self.path_textbox.grid(column=0, row=0, padx=10, pady=5, sticky=(E, W))

        # Button that prompts user for a new path
        path_button = ttk.Button(self, text="Choose Folder", command=self.choose_folder)
        path_button.grid(column=1, row=0, padx=10, pady=5, sticky=(E, W))
        bind_button(path_button)

        # Allow this to be resizeable
        self.rowconfigure(0, weight='1')
        self.columnconfigure(0, weight="1", minsize=200)
        self.columnconfigure(1, weight="1", minsize=30)
   
    def choose_folder(self, *args):
        dirname = filedialog.askdirectory(initialdir=self.path, title=self.title)
        if not dirname: return

        # Update textbox
        self.path = dirname
        self.path_textbox["state"] = "normal"
        self.path_textbox.delete("1.0", "end")
        self.path_textbox.insert("1.0", self.path)
        self.path_textbox["state"] = "disabled"

    def get_path(self):
        return self.path