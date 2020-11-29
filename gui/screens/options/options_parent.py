from gui.screens.options.toc_options import TOCOptions
from gui.screens.options.validate_options import ValidateOptions
from gui.screens.options.download_options import DownloadOptions
from gui.util.util import bind_button
from tkinter import *
from tkinter import ttk

class OptionsParent(Toplevel):

    def __init__(self, parent, options, callback, *args, **kwargs):
        Toplevel.__init__(self, parent)
        self.options = options
        self.callback = callback
        self.protocol("WM_DELETE_WINDOW", self.destroy_self)

        # Set title
        self.title("Folder Creator Options")
        self.minsize(600, 450)

        # Create notebook
        n = ttk.Notebook(self, width=600, height=450, padding=5)

        # Add each frame to the notebook
        self.download = DownloadOptions(n, self.options)
        self.verify = ValidateOptions(n, self.options)
        self.toc = TOCOptions(n, self.options)
        self.enumeration = ttk.Frame(n, border=10)
        self.dollies = ttk.Frame(n, border=5)
        self.rules = ttk.Frame(n, border=10)

        n.add(self.download, text='Download', underline=0)
        n.add(self.verify, text='Review', underline=0)
        n.add(self.toc, text='Table of Contents', underline=0)
        n.add(self.enumeration, text='Enumeration', underline=0)
        n.add(self.dollies, text='Dollies', underline=2)
        n.add(self.rules, text='Custom Rules', underline=0)

        n.select(kwargs.get('tab') or 0)

        n.enable_traversal()
        n.grid(row=0, column=0, columnspan=2, sticky=(N, E, S, W))

        # Add save and cancel buttons
        cancel_button = ttk.Button(self, text='Cancel', command=self.destroy_self)
        bind_button(cancel_button)
        save_button = ttk.Button(self, text='Save Settings', command=self.save_options)
        bind_button(save_button)

        cancel_button.grid(row=1, column=0, sticky=(S, W), padx=25, pady=15)
        save_button.grid(row=1, column=1, sticky=(S, E), padx=25, pady=15)

        # Allow resizing
        self.columnconfigure(0, weight='1')
        self.rowconfigure(0, weight='1')
    
    def destroy_self(self):
        self.callback()
        self.destroy()
    
    def save_options(self):
        print(self.download.get_dl_options())
        print(self.verify.get_validate_options())
        print(self.toc.get_toc_options())
        self.destroy_self()
    


