from gui.screens.options.util.order_select import OrderSelect
from gui.util.select_directory import SelectDirectory
from tkinter import *
from tkinter import ttk

class FillerOptions(ttk.Frame):

    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # List of different position values
        filler_positions = ["Before Lettered Chartz", "After Lettered Chartz", "After Numbered Chartz", "End of Folder", "Interlaced with Numbered Chartz"]

        # Filler Directory selection
        self.filler_dir = SelectDirectory(self, title='Select Filler Directory', path=options["filler"]["directory"])
        self.filler_dir.grid(row=0, column=0, columnspan=2, sticky=(N, S, E, W), padx=20, pady=10)

        # Filler position multiselect
        position_frame = ttk.LabelFrame(self, text='Position in Folder')

        self.position = ttk.Combobox(position_frame, values=filler_positions)
        self.position.current(options['filler']['position'])
        self.position.grid(row=0, column=0, padx=10, pady=5, sticky=(E, W))
        self.position.state(['readonly'])
        self.position.bind("<<ComboboxSelected>>", lambda _: self.position.master.focus_set())
        position_frame.rowconfigure(0, weight='1')
        position_frame.columnconfigure(0, weight='1')

        position_frame.grid(row=1, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Include Filler checkbox
        include_filler_frame = ttk.LabelFrame(self, text='Include Filler in Output Folder')

        self.include = BooleanVar()
        self.include.set(options['filler']['include'])
        include = ttk.Checkbutton(include_filler_frame, text='Include Filler', variable=self.include)
        include.grid(row=0, column=0, padx=10, pady=5)
        include_filler_frame.rowconfigure(0, weight='1')
        include_filler_frame.columnconfigure(0, weight='1')

        include_filler_frame.grid(row=1, column=1, sticky=(N, E, S, W), padx=20, pady=10)

        # Filler order selection
        self.order = OrderSelect(self, options, pathfn=self.filler_dir.get_path)

        self.order.grid(row=2, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        for i in range(3):
            self.rowconfigure(i, weight='1')
        for i in range(2):
            self.columnconfigure(i, weight='1')
    
    def get_filler_options(self):
        return {
            "filler": {
                "directory": self.filler_dir.get_path(),
                "include": self.include.get(),
                "order": self.order.get_ordered_list(),
                "position": self.position.current()
            }
        }