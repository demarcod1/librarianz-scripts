from tkinter import *
from tkinter import ttk

class FolderCreatorWorkflow(ttk.Labelframe):

    def __init__(self, parent, description, scriptButtonName, optionsCallback, scriptCallback, *args, **kwargs):
        # Initialize Superclass
        title = kwargs.get('title') or scriptButtonName
        relief = kwargs.get('relief')
        ttk.Labelframe.__init__(self, parent, text=title, relief=relief)

        # Add Description label
        desc_label = Text(self, wrap='word', font='TkTextFont', height=kwargs.get('height') or 5)
        desc_label.insert("1.0", description)
        desc_label['state'] = 'disabled'
        desc_label.grid(row=0, column=0, sticky=(N, S), padx=10, pady=5)

        # Add Settings button
        settings_button = ttk.Button(self, text='Settings', command=optionsCallback)
        settings_button.grid(row=1, column=0, sticky=(E, W), padx=10, pady=5)

        # Add Run Script button
        script_button = ttk.Button(self, text=scriptButtonName, command=scriptCallback)
        script_button.grid(row=2, column=0, sticky=(E, W), padx=10, pady=5)

        # Make resizeable
        self.columnconfigure(0, weight='1')
        for i in range(3): self.rowconfigure(i, weight='1')