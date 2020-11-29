from gui.util.multiselect import Multiselect
from tkinter import *
from tkinter import ttk

class ValidateOptions(ttk.Frame):

    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Retrieve options
        self.options = options

        # Parts to generate folders
        self.parts_selection = Multiselect(self, input=self.options['folder-parts'],
                                    title='Select Parts for Generating Folders',
                                    header='Part Name',
                                    addText='Add Part',
                                    warn='False',
                                    height=10)
        self.parts_selection.grid(row=0, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Choose whether or not to generate table of contents when running validation script
        gen_toc_frame = ttk.Labelframe(self, text='Sample Table of Contents for Validation Script')

        self.generate_toc = BooleanVar()
        self.generate_toc.set(options['toc']['generate-on-validation'])
        gen_toc_checkbox = ttk.Checkbutton(gen_toc_frame, text='Generate Sample Table of Contents', variable=self.generate_toc)
        gen_toc_checkbox.grid(row=0, column=0)

        gen_toc_frame.columnconfigure(0, weight='1')
        gen_toc_frame.rowconfigure(0, weight='1')
        gen_toc_frame.grid(row=1, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Allow resizing
        self.rowconfigure(0, weight="1")
        self.rowconfigure(1, weight="1")
        self.columnconfigure(0, weight="1")
    
    def get_validate_options(self):
        return ({ 'folder-parts': self.parts_selection.get_chosen_values() }, self.generate_toc.get())