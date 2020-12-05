from tkinter import *
from tkinter import ttk

class LabledEntry(ttk.Labelframe):

    def __init__(self, parent, *args, **kwargs):
        # Initialize superclass
        title = kwargs.get('title') or 'Labeled Entry'
        relief = kwargs.get('relief')
        ttk.Labelframe.__init__(self, parent, text=title, relief=relief)

        # Add label
        label_text = (kwargs.get('label') or "Entry Description") + ':'
        label = ttk.Label(self, text=label_text, justify='right')
        label.grid(row=0, column=0, sticky=E, padx=10, pady=5)

        # Add text entry
        self.entry_text = StringVar()
        width = kwargs.get('width') or 40
        self.entry_text.set(kwargs.get('defaultEntry') or '')
        entry = ttk.Entry(self, textvariable=self.entry_text, width=width)
        entry.grid(row=0, column=1, sticky=W, padx=10, pady=5)

        # Make resizeable
        self.rowconfigure(0, weight='1')
        for col in (0, 1): self.columnconfigure(col, weight='1')
    
    def get_entry(self):
        return self.entry_text.get()