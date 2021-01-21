from gui.util.multiselect import Multiselect
from gui.util.script_progress import ScriptProgress
from gui.util.util import bind_button
from gui.util.labeled_entry import LabledEntry
from scripts.redvest_creator import redvest_creator
from scripts.util.util import parse_options, write_options
from tkinter import *
from tkinter import ttk

class RedvestCreatorScreen(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Parse redvest options
        self.options = parse_options("redvest_options.json")

        # Parent folder selection
        self.parent_entry = LabledEntry(self, title='Enter Course Folder', label='Course Folder Name', defaultEntry=self.options['parent-name'])
        self.parent_entry.grid(row=0, column=0, columnspan=2, sticky=(N, S, E, W), padx=20, pady=10)

        # Folder name selection
        self.folder_entry = LabledEntry(self, title='Create New Class Folder', label='New Folder Name', defaultEntry=self.options['folder-name'])
        self.folder_entry.grid(row=1, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Select Chartz multiselect
        self.select_chartz = Multiselect(self, input=self.options['chartz'],
                                        title='Select Chartz for Redvest',
                                        header='Chart Name',
                                        addText='Add Chart',
                                        height=7)
        self.select_chartz.grid(row=2, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Individual Sections
        sep_sec_frame = ttk.LabelFrame(self, text='Separated Section Parts')

        self.sep_sec = BooleanVar()
        self.sep_sec.set(self.options['individual-sections'])
        sep_sec_checkbox = ttk.Checkbutton(sep_sec_frame, text='Include Separated Section Parts', variable=self.sep_sec)
        sep_sec_checkbox.grid(row=0, column=0, padx=10, pady=5)
        sep_sec_frame.rowconfigure(0, weight='1')
        sep_sec_frame.columnconfigure(0, weight='1')

        sep_sec_frame.grid(row=3, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Run script/Close buttons       
        close_button = ttk.Button(self, text='Close', command=lambda: parent.master.destroy())
        bind_button(close_button)
        run_script_button = ttk.Button(self, text='Create Redvest Folder', command=self.run_script)
        bind_button(run_script_button)

        close_button.grid(row=4, column=0, sticky=(S, W), padx=20, pady=10)
        run_script_button.grid(row=4, column=1, sticky=(S, E), padx=20, pady=10)

        # Make resizeable
        for i in range(5):
            self.rowconfigure(i, weight='1')
        self.columnconfigure(1, weight='1')
    
    def run_script(self, *args):
        # Update and write to options
        self.options['parent-name'] = self.parent_entry.get_entry()
        self.options['folder-name'] = self.folder_entry.get_entry()
        self.options['chartz'] = self.select_chartz.get_chosen_values()
        self.options['individual-sections'] = self.sep_sec.get()
        write_options(self.options, "redvest_options.json")

        # Re-show main window
        def callback(code):
            self.master.master.deiconify()
            print(f"Thread Finished with code {code}")
        

        ScriptProgress(self, script=redvest_creator, callback=callback, title="Creating Redvest Folder", name="Redvest Creator")
        self.master.master.withdraw()