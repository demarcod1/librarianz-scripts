from gui.util.script_progress import ScriptProgress
from gui.util.util import bind_button
from gui.util.select_directory import SelectDirectory
from scripts.upload_files import upload_files
from tkinter import *
from tkinter import ttk

class UploadFilesScreen(Frame):

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        # Directory selection       
        select_directory = SelectDirectory(self, path="../hello/world")
        select_directory.grid(row=0, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Mode selection + title match checkbox
        self.mode = IntVar()
        self.title_match = BooleanVar()
        self.title_match.set(True)
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

        # Run script/Close buttons
        run_script_button = ttk.Button(self, text='Upload Files', command=self.run_script)
        bind_button(run_script_button)
        close_button = ttk.Button(self, text='Close', command=lambda: parent.master.destroy())
        bind_button(close_button)

        close_button.grid(row=2, column=0, sticky=(S, W), padx=20, pady=10)
        run_script_button.grid(row=2, column=1, sticky=(S, E), padx=20, pady=10)


        # Allow resizing
        self.grid(row=0, column=0, sticky=(N, E, S, W))
        self.rowconfigure(0, weight="1")
        self.rowconfigure(1, weight="1")
        self.columnconfigure(0, weight="1")
        for col in range(4):
            mode_frame.columnconfigure(col, weight="1", minsize="80")
        
    def run_script(self, *args):
        # Re-show main window
        def callback(code):
            self.master.master.deiconify()
            print(f"Thread Finished with code {code}")
        

        script_progress = ScriptProgress(self, script=upload_files, callback=callback, title="Uploading Files...", name="Upload Files")
        self.master.master.withdraw()
