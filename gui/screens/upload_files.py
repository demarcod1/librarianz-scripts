from gui.util.multiselect import Multiselect
from scripts.util.util import parse_options, write_options
from gui.util.script_progress import ScriptProgress
from gui.util.util import bind_button
from gui.util.select_directory import SelectDirectory
from scripts.upload_files import upload_files
from tkinter import *
from tkinter import ttk

class UploadFilesScreen(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Parse upload files options
        self.options = parse_options("upload_options.json")

        # Directory selection       
        self.select_directory = SelectDirectory(self, path=self.options["resources-directory"], title='Select Resources Folder')
        self.select_directory.grid(row=0, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Mode selection + title match checkbox
        self.mode = IntVar()
        self.mode.set(self.options["mode"])
        self.title_match = BooleanVar()
        self.title_match.set(self.options["require-titles-match"])
        mode_frame = ttk.Labelframe(self, text='Select Mode')
        update = ttk.Radiobutton(mode_frame, text='Update Files', variable=self.mode, value=0)
        add = ttk.Radiobutton(mode_frame, text='Add Files', variable=self.mode, value=1)
        update_and_add = ttk.Radiobutton(mode_frame, text='Add and Update', variable=self.mode, value=2)
        title_match_checkbox = ttk.Checkbutton(mode_frame, text='Enforce Matching Titles', variable=self.title_match)

        mode_frame.grid(row=1, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)
        update.grid(row=0, column=0)
        add.grid(row=0, column=1)
        update_and_add.grid(row=0, column=2)
        title_match_checkbox.grid(row=0, column=3, padx=20)

        # New chartz selection
        self.new_chartz = Multiselect(self, input=self.options['new-chartz'],
                                        title='Create New Chartz',
                                        key1='name', 
                                        key2='to',
                                        header='Chart Name',
                                        addText='Add New Chart',
                                        height=3)
        self.new_chartz.grid(row=2, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # File extensions selection
        self.file_extensions = Multiselect(self, input=self.options["supported-file-types"],
                                            title='Supported File Types',
                                            header='File Type',
                                            addText='Add File Type',
                                            warn=True,
                                            height=6)
        self.file_extensions.grid(row=3, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Run script/Close buttons
        close_button = ttk.Button(self, text='Close', command=lambda: parent.master.destroy())
        bind_button(close_button)
        run_script_button = ttk.Button(self, text='Upload Files', command=self.run_script)
        bind_button(run_script_button)

        close_button.grid(row=4, column=0, sticky=(S, W), padx=20, pady=10)
        run_script_button.grid(row=4, column=1, sticky=(S, E), padx=20, pady=10)

        # Allow resizing
        for row in range(5):
            self.rowconfigure(row, weight="1")
        self.columnconfigure(0, weight="1")
        for col in range(4):
            mode_frame.columnconfigure(col, weight="1", minsize="80")
        
    def run_script(self, *args):
        # Update and write to options
        self.options["mode"] = self.mode.get()
        self.options["require-titles-match"] = self.title_match.get()
        self.options["resources-directory"] = self.select_directory.get_path()
        self.options["new-chartz"] = self.new_chartz.get_chosen_values("name", "to")
        self.options["supported-file-types"] = self.file_extensions.get_chosen_values()
        write_options(self.options, "upload_options.json")

        # Re-show main window
        def callback(code):
            self.master.master.deiconify()
            print(f"Thread Finished with code {code}")
        

        ScriptProgress(self, script=upload_files, callback=callback, title="Uploading Files...", name="Upload Files", safe=self.options['mode'] == 0)
        self.master.master.withdraw()
