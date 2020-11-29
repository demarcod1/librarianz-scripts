from gui.util.multiselect import Multiselect
from tkinter import *
from tkinter import ttk

class DownloadOptions(ttk.Frame):

    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Retrieve options
        self.options = options

        # Parts to download selection
        self.dl_selection = Multiselect(self, input=self.options['download-parts'],
                                    title='Select Parts to Download',
                                    header='Part Name',
                                    addText='Add Part',
                                    warn=False,
                                    height=10)
        self.dl_selection.grid(row=0, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Allow resizing
        self.rowconfigure(0, weight="1")
        self.columnconfigure(0, weight="1")
    
    def get_options(self):
        return { 'download-parts': self.dl_selection.get_chosen_values() }