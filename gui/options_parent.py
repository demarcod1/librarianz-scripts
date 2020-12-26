from gui.screens.options.filler_options import FillerOptions
from gui.screens.options.rules_options import RulesOptions
from scripts.util.util import write_options
from gui.screens.options.pages_options import PagesOptions
from gui.screens.options.dollie_options import DollieOptions
from gui.screens.options.chartz_options import ChartzOptions
from gui.screens.options.toc_options import TOCOptions
from gui.screens.options.validate_options import ValidateOptions
from gui.screens.options.download_options import DownloadOptions
from gui.util.util import bind_button
from tkinter import *
from tkinter import ttk

class OptionsParent(Toplevel):

    def __init__(self, parent, options, callback, *args, **kwargs):
        Toplevel.__init__(self, parent)
        self.options: Dict = options
        self.callback = callback
        self.protocol("WM_DELETE_WINDOW", self.destroy_self)

        # Set title
        self.title("Folder Creator Options")
        self.lift()
        self.focus_force()
        self.minsize(600, 525)

        # Create mainframe
        mainframe = ttk.Frame(self)

        # Create notebook
        n = ttk.Notebook(mainframe, width=600, height=450, padding=5)

        # Add each frame to the notebook
        self.download = DownloadOptions(n, self.options)
        self.verify = ValidateOptions(n, self.options)
        self.pages = PagesOptions(n, self.options)
        self.filler = FillerOptions(n, self.options)
        self.toc = TOCOptions(n, self.options)
        self.chartz = ChartzOptions(n, self.options)
        self.dollies = DollieOptions(n, self.options)
        self.rules = RulesOptions(n, self.options)

        n.add(self.download, text='Download', underline=0)
        n.add(self.verify, text='Review', underline=0)
        n.add(self.chartz, text='Chartz', underline=0)
        n.add(self.dollies, text='Dollies', underline=2)
        n.add(self.filler, text='Filler', underline=0)
        n.add(self.toc, text='Table of Contents', underline=0)
        n.add(self.pages, text='Pages', underline=0)
        n.add(self.rules, text='Custom Rules', underline=1)   

        n.select(kwargs.get('tab') or 0)

        n.enable_traversal()
        n.grid(row=0, column=0, columnspan=2, sticky=(N, E, S, W))

        # Add save and cancel buttons
        cancel_button = ttk.Button(mainframe, text='Cancel', command=self.destroy_self)
        bind_button(cancel_button)
        save_button = ttk.Button(mainframe, text='Save Settings', command=self.save_options)
        bind_button(save_button)

        cancel_button.grid(row=1, column=0, sticky=(S, W), padx=25, pady=15)
        save_button.grid(row=1, column=1, sticky=(S, E), padx=25, pady=15)

        # Allow resizing
        mainframe.columnconfigure(0, weight='1')
        mainframe.rowconfigure(0, weight='1')
        mainframe.grid(row=0, column=0, sticky=(N, E, S, W))
        self.columnconfigure(0, weight='1')
        self.rowconfigure(0, weight='1')
    
    def destroy_self(self):
        self.callback()
        self.destroy()
    
    def save_options(self):
        val_options = self.verify.get_validate_options()
        toc_options = self.toc.get_toc_options()
        toc_options.update({'generate-on-validation': val_options[1]})

        self.options.update(val_options[0])
        self.options.update({ 'toc': toc_options })
        self.options.update(self.download.get_dl_options())
        self.options.update(self.chartz.get_chart_options())
        self.options.update(self.dollies.get_dollie_options())
        self.options.update(self.pages.get_page_options())
        self.options.update(self.rules.get_rule_options())
        self.options.update(self.filler.get_filler_options())
        
        write_options(self.options, "folder_creator_options.json")

        self.destroy_self()
    


